#!/usr/bin/env python3
"""
Load 2024 Denominator Data (CVAP and VEP) to BigQuery

This script loads 2024 CVAP (ACS 2019-2023) and VEP data into BigQuery by:
1. Uploading CSV files to GCS
2. Loading from GCS to BigQuery native tables
3. Updating union views to include 2024
4. Refreshing materialized staging tables

Usage:
    python scripts/load_denominators_2024.py --cvap-csv <path> --vep-csv <path>
"""

import argparse
import logging
import os
from pathlib import Path
from google.cloud import bigquery
from google.cloud import storage
from google.api_core.exceptions import NotFound

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ID = "eavs-392800"
GCS_BUCKET = "eavs-data-files-2024"
ACS_DATASET = "acs"
VEP_DATASET = "us_elections_vep"


def upload_to_gcs(local_file: Path, gcs_path: str) -> str:
    """Upload a file to GCS"""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)

    logger.info(f"Uploading {local_file} to gs://{GCS_BUCKET}/{gcs_path}")
    blob.upload_from_filename(str(local_file))

    gcs_uri = f"gs://{GCS_BUCKET}/{gcs_path}"
    logger.info(f"✓ Uploaded to {gcs_uri}")
    return gcs_uri


def load_csv_to_bigquery(
    client: bigquery.Client,
    gcs_uri: str,
    dataset_id: str,
    table_id: str,
    skip_leading_rows: int = 1
):
    """Load a CSV from GCS into a native BigQuery table"""

    full_table_id = f"{PROJECT_ID}.{dataset_id}.{table_id}"

    # Configure load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=skip_leading_rows,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    try:
        # Start the load job
        logger.info(f"Loading {gcs_uri} to {full_table_id}...")
        load_job = client.load_table_from_uri(
            gcs_uri, full_table_id, job_config=job_config
        )

        # Wait for job to complete
        load_job.result()

        # Get table info
        table = client.get_table(full_table_id)
        logger.info(f"✓ Loaded {table.num_rows:,} rows to {full_table_id}")

        return table

    except Exception as e:
        logger.error(f"Error loading table {full_table_id}: {e}")
        raise


def update_acs_population_union_view(client: bigquery.Client):
    """Update the acs_population_union view to include 2024 data"""

    view_id = f"{PROJECT_ID}.eavs_analytics.acs_population_union"

    try:
        # Get existing view
        view = client.get_table(view_id)
        existing_sql = view.view_query

        # Check if 2024 is already included
        if "'2024'" in existing_sql or "acs_2024" in existing_sql:
            logger.info("✓ acs_population_union already includes 2024 data")
            return

        # Generate the new CTE for 2024
        # NOTE: 2019-2023 Census file doesn't have 'state' column, extract from geoname
        new_cte = """  acs_2024 AS (
  SELECT
    '2024' AS election_year,
    GEOID,
    lntitle AS LNTITLE,
    TRIM(SPLIT(geoname, ',')[SAFE_OFFSET(1)]) AS state,
    geoname AS county_name,
    tot_est AS acs_total_population,
    adu_est AS acs_adult_population,
    cit_est AS acs_citizen_population,
    cvap_est AS acs_cvap_population
  FROM
    `eavs-392800.acs.acs_2019-2023_county_cvap` )"""

        # Insert the new CTE after acs_2021
        import re

        # Find the acs_2021 CTE (ends with the closing paren and comma)
        pattern = r"(acs_2021 AS \((?:[^)]|\)(?!\s*,))*\)\s*,)"
        match = re.search(pattern, existing_sql, re.DOTALL)

        if match:
            insert_pos = match.end()
            # Add the new CTE after acs_2021
            updated_sql = existing_sql[:insert_pos] + "\n" + new_cte + "," + existing_sql[insert_pos:]

            # Now add acs_2024 to the union_all CTE
            # Find where acs_2021 is selected in union_all
            union_pattern = r"(SELECT\s+\*\s+FROM\s+acs_2021)"
            union_match = re.search(union_pattern, updated_sql, re.IGNORECASE)

            if union_match:
                # Insert UNION ALL after the acs_2021 SELECT
                union_pos = union_match.end()
                union_statement = "\n    UNION ALL\n    SELECT\n      *\n    FROM\n      acs_2024"
                updated_sql = updated_sql[:union_pos] + union_statement + updated_sql[union_pos:]

                # Update the view
                view.view_query = updated_sql
                view = client.update_table(view, ["view_query"])
                logger.info(f"✓ Updated acs_population_union view with 2024 data")
            else:
                logger.error("Could not find acs_2021 SELECT in union_all")
                _save_sql_to_file(updated_sql, "acs_population_union_MANUAL.sql")
        else:
            logger.error("Could not find acs_2021 CTE in view SQL")
            _save_sql_to_file(existing_sql, "acs_population_union_current.sql")

    except Exception as e:
        logger.error(f"Error updating acs_population_union view: {e}")
        logger.info("You may need to update the view manually in BigQuery Console")


def update_vep_union_view(client: bigquery.Client):
    """Update the vep_union view to include 2024 data"""

    view_id = f"{PROJECT_ID}.eavs_analytics.vep_union"

    try:
        # Get existing view
        view = client.get_table(view_id)
        existing_sql = view.view_query

        # Check if 2024 is already included
        if "'2024'" in existing_sql or "vep_2024" in existing_sql:
            logger.info("✓ vep_union already includes 2024 data")
            return

        # Generate the new CTE for 2024
        # NOTE: 2024 file has UPPERCASE column names: STATE_ABV and VEP
        new_cte = """  vep_2024 as (
  select
  "2024" as election_year,
  STATE_ABV as state_abbr,
  VEP as VEP
  from
  `eavs-392800.us_elections_vep.vep_2024`

  )"""

        # Insert the new CTE at the beginning (after WITH)
        import re

        # Find where to insert (after "with ")
        pattern = r"(with\s+)"
        match = re.search(pattern, existing_sql, re.IGNORECASE)

        if match:
            insert_pos = match.end()
            # Add the new CTE first
            updated_sql = existing_sql[:insert_pos] + new_cte + "\n\n  , " + existing_sql[insert_pos:]

            # Add the UNION ALL at the beginning of the select statements
            # Find the first "select * from vep_"
            select_pattern = r"(\s+select \* from vep_\d{4})"
            select_match = re.search(select_pattern, updated_sql, re.IGNORECASE)

            if select_match:
                # Insert before the first select
                select_pos = select_match.start()
                union_statement = "\n    select * from vep_2024\n    UNION ALL"
                updated_sql = updated_sql[:select_pos] + union_statement + updated_sql[select_pos:]

                # Update the view
                view.view_query = updated_sql
                view = client.update_table(view, ["view_query"])
                logger.info(f"✓ Updated vep_union view with 2024 data")
            else:
                logger.error("Could not find select pattern in view SQL")
                _save_sql_to_file(updated_sql, "vep_union_MANUAL.sql")
        else:
            logger.error("Could not find WITH clause in view SQL")
            _save_sql_to_file(existing_sql, "vep_union_current.sql")

    except Exception as e:
        logger.error(f"Error updating vep_union view: {e}")
        logger.info("You may need to update the view manually in BigQuery Console")


def _save_sql_to_file(sql: str, filename: str):
    """Save SQL to a file for manual review"""
    output_dir = Path(__file__).parent.parent / "sql" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / filename

    with open(output_file, 'w') as f:
        f.write(sql)

    logger.info(f"Saved SQL to {output_file} for manual review")


def refresh_materialized_tables(client: bigquery.Client):
    """Refresh the materialized staging tables"""

    tables_to_refresh = [
        ("eavs_analytics", "stg_acs_population_union", "acs_population_union"),
        ("eavs_analytics", "stg_vep_union", "vep_union"),
    ]

    for dataset, staging_table, source_view in tables_to_refresh:
        logger.info(f"Refreshing {staging_table}...")

        query = f"""
        CREATE OR REPLACE TABLE `{PROJECT_ID}.{dataset}.{staging_table}` AS
        SELECT * FROM `{PROJECT_ID}.{dataset}.{source_view}`
        """

        try:
            query_job = client.query(query)
            query_job.result()  # Wait for completion

            # Get row count
            table = client.get_table(f"{PROJECT_ID}.{dataset}.{staging_table}")
            logger.info(f"✓ Refreshed {staging_table} ({table.num_rows:,} rows)")

        except Exception as e:
            logger.error(f"Error refreshing {staging_table}: {e}")


def validate_2024_data(client: bigquery.Client):
    """Validate that 2024 data is loaded correctly"""

    logger.info("\n=== Validating 2024 Denominator Data ===\n")

    # Check CVAP data
    try:
        cvap_query = """
        SELECT
          COUNT(*) as county_count,
          COUNT(DISTINCT state) as state_count,
          SUM(acs_cvap_population) as total_cvap
        FROM `eavs-392800.eavs_analytics.stg_acs_population_union`
        WHERE election_year = '2024'
        """

        result = client.query(cvap_query).result()
        for row in result:
            logger.info(f"✓ CVAP 2024 Data:")
            logger.info(f"  - Counties: {row.county_count:,}")
            logger.info(f"  - States: {row.state_count}")
            logger.info(f"  - Total CVAP: {row.total_cvap:,}")

            if row.county_count < 3000:
                logger.warning(f"  ⚠ Expected ~3,220 counties, found {row.county_count}")

    except Exception as e:
        logger.error(f"Error validating CVAP data: {e}")

    # Check VEP data
    try:
        vep_query = """
        SELECT
          COUNT(*) as state_count,
          SUM(VEP) as total_vep
        FROM `eavs-392800.eavs_analytics.stg_vep_union`
        WHERE election_year = '2024'
        """

        result = client.query(vep_query).result()
        for row in result:
            logger.info(f"\n✓ VEP 2024 Data:")
            logger.info(f"  - States: {row.state_count}")
            logger.info(f"  - Total VEP: {row.total_vep:,}")

            if row.state_count < 50:
                logger.warning(f"  ⚠ Expected ~51 states (+ DC), found {row.state_count}")

    except Exception as e:
        logger.error(f"Error validating VEP data: {e}")

    # Check all available years
    try:
        years_query = """
        SELECT DISTINCT election_year
        FROM `eavs-392800.eavs_analytics.stg_acs_population_union`
        ORDER BY election_year
        """

        result = client.query(years_query).result()
        years = [row.election_year for row in result]
        logger.info(f"\n✓ Available CVAP years: {', '.join(years)}")

    except Exception as e:
        logger.error(f"Error checking available years: {e}")


def main():
    parser = argparse.ArgumentParser(description='Load 2024 denominator data to BigQuery')
    parser.add_argument('--cvap-csv', type=Path, help='Path to ACS 2019-2023 CVAP CSV file')
    parser.add_argument('--vep-csv', type=Path, help='Path to 2024 VEP CSV file')
    parser.add_argument('--skip-upload', action='store_true', help='Skip uploading to GCS (assume already uploaded)')
    parser.add_argument('--skip-load', action='store_true', help='Skip loading to BigQuery (assume tables exist)')
    parser.add_argument('--skip-views', action='store_true', help='Skip updating union views')
    parser.add_argument('--refresh-only', action='store_true', help='Only refresh materialized tables')

    args = parser.parse_args()

    # Initialize clients
    client = bigquery.Client(project=PROJECT_ID)
    logger.info(f"Connected to project: {PROJECT_ID}")

    if args.refresh_only:
        logger.info("\n=== Refreshing Materialized Tables ===\n")
        refresh_materialized_tables(client)
        validate_2024_data(client)
        return

    # Validate inputs
    if not args.skip_upload and not args.skip_load:
        if not args.cvap_csv or not args.vep_csv:
            parser.error("--cvap-csv and --vep-csv are required unless --skip-upload and --skip-load are used")

        if not args.cvap_csv.exists():
            parser.error(f"CVAP file not found: {args.cvap_csv}")

        if not args.vep_csv.exists():
            parser.error(f"VEP file not found: {args.vep_csv}")

    # Step 1: Upload to GCS
    cvap_gcs_uri = None
    vep_gcs_uri = None

    if not args.skip_upload:
        logger.info("\n=== Uploading to GCS ===\n")

        if args.cvap_csv:
            cvap_gcs_uri = upload_to_gcs(
                args.cvap_csv,
                "denominators/2024/acs_2019-2023_county_cvap.csv"
            )

        if args.vep_csv:
            vep_gcs_uri = upload_to_gcs(
                args.vep_csv,
                "denominators/2024/vep_2024.csv"
            )
    else:
        cvap_gcs_uri = f"gs://{GCS_BUCKET}/denominators/2024/acs_2019-2023_county_cvap.csv"
        vep_gcs_uri = f"gs://{GCS_BUCKET}/denominators/2024/vep_2024.csv"

    # Step 2: Load to BigQuery
    if not args.skip_load:
        logger.info("\n=== Loading to BigQuery ===\n")

        if cvap_gcs_uri:
            load_csv_to_bigquery(
                client,
                cvap_gcs_uri,
                ACS_DATASET,
                "acs_2019-2023_county_cvap"
            )

        if vep_gcs_uri:
            load_csv_to_bigquery(
                client,
                vep_gcs_uri,
                VEP_DATASET,
                "vep_2024"
            )

    # Step 3: Update union views
    if not args.skip_views:
        logger.info("\n=== Updating Union Views ===\n")
        update_acs_population_union_view(client)
        update_vep_union_view(client)

    # Step 4: Refresh materialized tables
    logger.info("\n=== Refreshing Materialized Tables ===\n")
    refresh_materialized_tables(client)

    # Step 5: Validate data
    validate_2024_data(client)

    logger.info("\n=== Done! ===\n")
    logger.info("Next steps:")
    logger.info("1. Verify data looks correct in BigQuery Console")
    logger.info("2. Update any downstream mart tables or dashboards")
    logger.info("3. Document any changes in CLAUDE.md")


if __name__ == "__main__":
    main()
