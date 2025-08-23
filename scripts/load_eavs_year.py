#!/usr/bin/env python3
"""
EAVS Annual Data Loader
Streamlined script for loading a new year of EAVS data into BigQuery

Usage:
    python load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
"""

import os
import sys
import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.exceptions import Conflict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GCS bucket name - using a consistent bucket for all years
GCS_BUCKET = "eavs-data-files"
PROJECT_ID = "eavs-392800"
ANALYTICS_DATASET = "eavs_analytics"


class EAVSLoader:
    """Load EAVS data for a specific year"""
    
    def __init__(self, year: str):
        self.year = year
        self.year_short = year[-2:]  # e.g., "24" from "2024"
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.storage_client = storage.Client(project=PROJECT_ID)
        
        # Load field mappings
        config_path = Path(__file__).parent / "config" / "field_mappings.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info(f"Initialized loader for year {year}")
    
    def create_gcs_bucket(self):
        """Create GCS bucket if it doesn't exist"""
        try:
            bucket = self.storage_client.create_bucket(
                GCS_BUCKET, 
                location="US"
            )
            logger.info(f"Created bucket: {GCS_BUCKET}")
        except Conflict:
            logger.info(f"Bucket {GCS_BUCKET} already exists")
        except Exception as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    def upload_files_to_gcs(self, data_dir: Path) -> dict:
        """Upload CSV files to GCS and return GCS paths"""
        bucket = self.storage_client.bucket(GCS_BUCKET)
        gcs_paths = {}
        
        # Define expected file locations
        file_mappings = {
            'a_reg': f'Section A_ Registration/EAVS_county_{self.year_short}_A_REG.csv',
            'b_uocava': f'Section B_ UOCAVA/EAVS_county_{self.year_short}_B_UOCAVA.csv',
            'c_mail': f'Section C_ Mail/EAVS_county_{self.year_short}_C_MAIL.csv',
            'd_polls': f'Section D_ Polling Places/EAVS_county_{self.year_short}_D_POLLS.csv',
            'e_provisional': f'Section E_ Provisional/EAVS_county_{self.year_short}_E_PROVISIONAL.csv',
            'f1_participation': f'Section F1_ Participation*/EAVS_county_{self.year_short}_F1_PARTICIPATION.csv',
            'f2_tech': f'Section F2_ Voting Technology/EAVS_county_{self.year_short}_F2_TECH.csv',
        }
        
        # Upload files that exist
        for section, relative_path in file_mappings.items():
            # Handle wildcards in path (like "Participation*")
            if '*' in relative_path:
                pattern = relative_path.replace('*', '')
                matching_files = list(data_dir.glob(pattern))
                if matching_files:
                    file_path = matching_files[0]
                else:
                    file_path = None
            else:
                file_path = data_dir / relative_path
            
            if file_path and file_path.exists():
                # Upload to GCS with year/section structure
                blob_name = f"{self.year}/{section}.csv"
                blob = bucket.blob(blob_name)
                
                logger.info(f"Uploading {file_path.name} to gs://{GCS_BUCKET}/{blob_name}")
                blob.upload_from_filename(str(file_path))
                
                gcs_paths[section] = f"gs://{GCS_BUCKET}/{blob_name}"
            else:
                logger.warning(f"File not found for section {section}: {relative_path}")
        
        return gcs_paths
    
    def create_bigquery_dataset(self):
        """Create BigQuery dataset for the year"""
        dataset_id = f"{PROJECT_ID}.eavs_{self.year}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        dataset.description = f"{self.year} EAVS County-level data"
        
        try:
            dataset = self.bq_client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Created/verified dataset: eavs_{self.year}")
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            raise
    
    def create_external_tables(self, gcs_paths: dict):
        """Create external tables pointing to GCS files"""
        for section, gcs_path in gcs_paths.items():
            table_name = f"eavs_county_{self.year_short}_{section}"
            table_id = f"{PROJECT_ID}.eavs_{self.year}.{table_name}"
            
            # Configure external table
            external_config = bigquery.ExternalConfig("CSV")
            external_config.source_uris = [gcs_path]
            external_config.autodetect = True
            external_config.options.skip_leading_rows = 1
            external_config.options.allow_quoted_newlines = True
            
            table = bigquery.Table(table_id)
            table.external_data_configuration = external_config
            
            try:
                table = self.bq_client.create_table(table, exists_ok=True)
                logger.info(f"Created external table: {table_name}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
    
    def update_union_views(self, gcs_paths: dict):
        """Actually update the union views in BigQuery"""
        logger.info("Updating union views with new year data...")
        
        view_mapping = {
            'a_reg': 'eavs_county_reg_union',
            'b_uocava': 'eavs_county_uocava_union',
            'c_mail': 'eavs_county_mail_union',
            'f1_participation': 'eavs_county_part_union'
        }
        
        for section, view_name in view_mapping.items():
            if section not in gcs_paths:
                continue
                
            try:
                # Get the existing view definition
                view_id = f"{PROJECT_ID}.{ANALYTICS_DATASET}.{view_name}"
                view = self.bq_client.get_table(view_id)
                existing_sql = view.view_query
                
                # Check if this year is already in the view
                if f"{section}_{self.year}" in existing_sql:
                    logger.info(f"✓ {view_name} already includes {self.year}")
                    continue
                
                # Generate the new CTE for this year
                new_cte = self._generate_year_cte(section)
                if not new_cte:
                    logger.warning(f"Could not generate CTE for {section}")
                    continue
                
                # Insert the new CTE into the existing SQL
                updated_sql = self._insert_cte_into_view(existing_sql, new_cte, section)
                
                # Update the view
                view.view_query = updated_sql
                view = self.bq_client.update_table(view, ["view_query"])
                logger.info(f"✓ Updated {view_name} with {self.year} data")
                
            except Exception as e:
                logger.error(f"Error updating {view_name}: {e}")
                logger.info("You may need to update this view manually")
    
    def _generate_year_cte(self, section: str) -> str:
        """Generate CTE for a specific section and year"""
        config_map = {
            'a_reg': 'registration_mappings',
            'b_uocava': 'uocava_mappings',
            'c_mail': 'mail_mappings',
            'f1_participation': 'participation_mappings'
        }
        
        config_key = config_map.get(section)
        if not config_key or config_key not in self.config:
            return None
        
        mappings = self.config[config_key]
        # Try both string and integer year keys (YAML may parse as int)
        year_fields = mappings.get(self.year, mappings.get(int(self.year), {}))
        
        if not year_fields:
            logger.warning(f"No field mappings for {section} in year {self.year}")
            return None
        
        # Build SELECT statement
        selections = [f"'{self.year}' AS election_year"]
        for standard_field in mappings.get('standard_fields', []):
            if standard_field == 'election_year':
                continue
            
            source_field = year_fields.get(standard_field)
            if source_field and source_field != 'null':
                selections.append(f"{source_field} AS {standard_field}")
            else:
                selections.append(f"NULL AS {standard_field}")
        
        # Generate CTE
        table_name = f"eavs_county_{self.year_short}_{section}"
        
        # Join selections with newlines
        selections_str = ',\n    '.join(selections)
        
        cte = f"""  {section}_{self.year} AS (
  SELECT
    {selections_str}
  FROM
    `eavs_{self.year}.{table_name}`
  )"""
        return cte
    
    def _insert_cte_into_view(self, existing_sql: str, new_cte: str, section: str) -> str:
        """Insert new CTE and UNION ALL into existing view SQL"""
        
        # Find the last year's CTE for this section to insert after
        import re
        
        # Find all existing years for this section
        pattern = section + r"_(\d{4}) AS \("
        years = re.findall(pattern, existing_sql)
        
        if years:
            # Insert after the last year
            last_year = sorted(years)[-1]
            insert_pattern = f"({section}_{last_year}" + r" AS \([^)]+\))"
            match = re.search(insert_pattern, existing_sql, re.DOTALL)
            
            if match:
                # Insert the new CTE after the last one
                insert_pos = match.end()
                # Add comma and newline before new CTE
                existing_sql = existing_sql[:insert_pos] + ",\n" + new_cte + existing_sql[insert_pos:]
        else:
            # This is the first year for this section, insert before union_all
            union_pattern = r"(,\s*union_all as \()"
            match = re.search(union_pattern, existing_sql)
            if match:
                insert_pos = match.start()
                existing_sql = existing_sql[:insert_pos] + ",\n" + new_cte + existing_sql[insert_pos:]
        
        # Add to UNION ALL
        union_addition = f"\nUNION ALL\nSELECT * FROM {section}_{self.year}"
        
        # Find the last SELECT in the union_all CTE
        last_select_pattern = r"(FROM\s+\w+_\d{4})\s*\)"
        matches = list(re.finditer(last_select_pattern, existing_sql))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            existing_sql = existing_sql[:insert_pos] + union_addition + existing_sql[insert_pos:]
        
        return existing_sql
    
    
    def refresh_materialized_tables(self):
        """Refresh materialized tables from views"""
        tables_to_refresh = {
            'stg_eavs_county_reg_union': 'eavs_county_reg_union',
            'stg_eavs_county_mail_union': 'eavs_county_mail_union',
            'stg_eavs_county_part_union': 'eavs_county_part_union',
            'stg_eavs_county_uocava_union': 'eavs_county_uocava_union'
        }
        
        for table_name, view_name in tables_to_refresh.items():
            query = f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.{ANALYTICS_DATASET}.{table_name}` AS
            SELECT * FROM `{PROJECT_ID}.{ANALYTICS_DATASET}.{view_name}`
            """
            
            try:
                logger.info(f"Refreshing {table_name}...")
                query_job = self.bq_client.query(query)
                query_job.result()
                logger.info(f"✓ Refreshed {table_name}")
            except Exception as e:
                logger.warning(f"Could not refresh {table_name}: {e}")
                logger.info("(This is expected if views haven't been updated yet)")
    
    def validate_data(self, gcs_paths: dict):
        """Validate uploaded data"""
        logger.info("\n=== Data Validation ===")
        
        for section in gcs_paths.keys():
            table_name = f"eavs_county_{self.year_short}_{section}"
            table_id = f"eavs_{self.year}.{table_name}"
            
            query = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
            
            try:
                result = self.bq_client.query(query).result()
                for row in result:
                    logger.info(f"✓ {table_name}: {row.row_count:,} rows")
            except Exception as e:
                logger.error(f"✗ Error validating {table_name}: {e}")
    
    def run(self, data_dir: str):
        """Run the complete loading process"""
        data_path = Path(data_dir)
        
        if not data_path.exists():
            logger.error(f"Data directory not found: {data_dir}")
            sys.exit(1)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Loading EAVS {self.year} data")
        logger.info(f"Data source: {data_dir}")
        logger.info(f"{'='*50}\n")
        
        # Step 1: Create GCS bucket
        logger.info("Step 1: Setting up GCS bucket")
        self.create_gcs_bucket()
        
        # Step 2: Upload files to GCS
        logger.info("\nStep 2: Uploading files to GCS")
        gcs_paths = self.upload_files_to_gcs(data_path)
        
        if not gcs_paths:
            logger.error("No files uploaded. Check your data directory structure.")
            sys.exit(1)
        
        # Step 3: Create BigQuery dataset
        logger.info("\nStep 3: Creating BigQuery dataset")
        self.create_bigquery_dataset()
        
        # Step 4: Create external tables
        logger.info("\nStep 4: Creating external tables")
        self.create_external_tables(gcs_paths)
        
        # Step 5: Update union views automatically
        logger.info("\nStep 5: Updating union views")
        self.update_union_views(gcs_paths)
        
        # Step 6: Validate data
        logger.info("\nStep 6: Validating data")
        self.validate_data(gcs_paths)
        
        # Step 7: Try to refresh materialized tables
        logger.info("\nStep 7: Refreshing materialized tables")
        self.refresh_materialized_tables()
        
        logger.info(f"\n{'='*50}")
        logger.info("✓ Data loading complete!")
        logger.info(f"{'='*50}")
        
        logger.info("\n📋 Next steps:")
        logger.info("1. Verify the data in BigQuery")
        logger.info("2. Check dashboards are showing new data")


def main():
    parser = argparse.ArgumentParser(
        description='Load EAVS data for a specific year',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
  python load_eavs_year.py 2024 /path/to/data --refresh-tables
        """
    )
    
    parser.add_argument('year', help='Election year (e.g., 2024)')
    parser.add_argument('data_dir', help='Directory containing EAVS data files')
    parser.add_argument('--refresh-tables', action='store_true',
                       help='Only refresh materialized tables (after updating views)')
    
    args = parser.parse_args()
    
    loader = EAVSLoader(args.year)
    
    if args.refresh_tables:
        logger.info("Refreshing materialized tables only...")
        loader.refresh_materialized_tables()
    else:
        loader.run(args.data_dir)


if __name__ == '__main__':
    main()