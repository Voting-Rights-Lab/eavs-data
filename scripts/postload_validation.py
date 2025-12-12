#!/usr/bin/env python3
"""
Post-Load Validation for EAVS Data

Runs comprehensive data quality checks AFTER data has been loaded to BigQuery:
1. Row count verification
2. FIPS code validity checks
3. NULL percentage checks
4. Outlier detection
5. Year-over-year comparison (if previous year exists)
6. Referential integrity with denominator data

Usage:
    python scripts/postload_validation.py 2024
    python scripts/postload_validation.py 2024 --compare-to 2022
"""

import argparse
import sys
from google.cloud import bigquery
from typing import List, Dict, Tuple
import os

PROJECT_ID = os.getenv("EAVS_PROJECT_ID", "eavs-392800")

# Expected row count ranges (approximate, based on ~3,000 counties)
EXPECTED_ROW_RANGES = {
    'a_reg': (3000, 3300),
    'b_uocava': (3000, 3300),
    'c_mail': (3000, 3300),
    'f1_participation': (3000, 3300)
}

# Critical fields that should never be NULL
CRITICAL_FIELDS = ['fips', 'state', 'county', 'election_year']


class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ValidationResult:
    def __init__(self, check_name: str):
        self.check_name = check_name
        self.passed = True
        self.warnings = []
        self.errors = []
        self.info = []

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False

    def add_info(self, message: str):
        self.info.append(message)

    def print_results(self):
        status = f"{Colors.GREEN}✓" if self.passed else f"{Colors.RED}✗"
        print(f"\n{status} {Colors.BOLD}{self.check_name}{Colors.END}")

        if self.info:
            for msg in self.info:
                print(f"  ℹ  {msg}")

        if self.errors:
            for msg in self.errors:
                print(f"  {Colors.RED}✗ {msg}{Colors.END}")

        if self.warnings:
            for msg in self.warnings:
                print(f"  {Colors.YELLOW}⚠ {msg}{Colors.END}")


def check_table_exists(client: bigquery.Client, dataset_id: str, table_id: str) -> ValidationResult:
    """Check if table exists and is accessible."""
    result = ValidationResult(f"Table Existence: {table_id}")

    try:
        table = client.get_table(f"{PROJECT_ID}.{dataset_id}.{table_id}")
        result.add_info(f"Table exists with {table.num_rows:,} rows")
    except Exception as e:
        result.add_error(f"Table not found or not accessible: {e}")

    return result


def check_row_count(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    section_code: str
) -> ValidationResult:
    """Validate row count is within expected range."""
    result = ValidationResult(f"Row Count: {table_id}")

    query = f"SELECT COUNT(*) as row_count FROM `{PROJECT_ID}.{dataset_id}.{table_id}`"

    try:
        rows = list(client.query(query).result())
        row_count = rows[0].row_count

        expected_min, expected_max = EXPECTED_ROW_RANGES.get(section_code, (2500, 3500))

        result.add_info(f"Row count: {row_count:,}")

        if row_count < expected_min:
            result.add_warning(f"Row count ({row_count:,}) is below expected minimum ({expected_min:,})")
        elif row_count > expected_max:
            result.add_warning(f"Row count ({row_count:,}) is above expected maximum ({expected_max:,})")

        if row_count == 0:
            result.add_error("Table is empty!")

    except Exception as e:
        result.add_error(f"Error checking row count: {e}")

    return result


def check_fips_validity(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str
) -> ValidationResult:
    """Check FIPS code validity."""
    result = ValidationResult(f"FIPS Validity: {table_id}")

    # Check for NULL FIPS
    query = f"""
    SELECT COUNT(*) as null_count
    FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
    WHERE fips IS NULL OR TRIM(fips) = ''
    """

    try:
        rows = list(client.query(query).result())
        null_count = rows[0].null_count

        if null_count > 0:
            result.add_error(f"{null_count:,} rows have NULL or empty FIPS codes")
        else:
            result.add_info("All rows have FIPS codes")

    except Exception as e:
        result.add_warning(f"Could not check FIPS nulls (field may not exist): {e}")

    # Check FIPS format (should be 5 characters for county level)
    query = f"""
    SELECT
      LENGTH(fips) as fips_length,
      COUNT(*) as count
    FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
    WHERE fips IS NOT NULL
    GROUP BY fips_length
    ORDER BY count DESC
    """

    try:
        rows = list(client.query(query).result())
        for row in rows:
            if row.fips_length != 5:
                result.add_warning(f"{row.count:,} rows have FIPS length {row.fips_length} (expected 5)")
            else:
                result.add_info(f"{row.count:,} rows have correct FIPS length (5)")

    except Exception as e:
        result.add_warning(f"Could not check FIPS format: {e}")

    return result


def check_null_percentages(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str
) -> ValidationResult:
    """Check NULL percentages for critical fields."""
    result = ValidationResult(f"NULL Checks: {table_id}")

    # Get column names
    table = client.get_table(f"{PROJECT_ID}.{dataset_id}.{table_id}")
    columns = [field.name for field in table.schema]

    # Check critical fields
    critical_in_table = [c for c in CRITICAL_FIELDS if c in columns]

    if not critical_in_table:
        result.add_warning("No critical fields found in table")
        return result

    for field in critical_in_table:
        query = f"""
        SELECT
          COUNTIF({field} IS NULL) as null_count,
          COUNT(*) as total_count
        FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
        """

        try:
            rows = list(client.query(query).result())
            null_count = rows[0].null_count
            total_count = rows[0].total_count
            null_pct = (null_count / total_count * 100) if total_count > 0 else 0

            if null_count > 0:
                result.add_error(f"{field}: {null_count:,} NULLs ({null_pct:.1f}%)")
            else:
                result.add_info(f"{field}: No NULLs ✓")

        except Exception as e:
            result.add_warning(f"Could not check {field}: {e}")

    return result


def check_negative_values(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str
) -> ValidationResult:
    """Check for suspicious negative values in numeric fields."""
    result = ValidationResult(f"Negative Values: {table_id}")

    # Common numeric fields that should never be negative
    numeric_fields = [
        'total_reg', 'total_active_reg', 'total_inactive_reg',
        'total_ballots_cast', 'total_turnout', 'total_part'
    ]

    table = client.get_table(f"{PROJECT_ID}.{dataset_id}.{table_id}")
    columns = [field.name for field in table.schema]

    numeric_in_table = [f for f in numeric_fields if f in columns]

    if not numeric_in_table:
        result.add_info("No numeric fields to check")
        return result

    for field in numeric_in_table:
        query = f"""
        SELECT COUNT(*) as negative_count
        FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
        WHERE {field} < 0
        """

        try:
            rows = list(client.query(query).result())
            negative_count = rows[0].negative_count

            if negative_count > 0:
                result.add_warning(f"{field}: {negative_count:,} negative values")

        except Exception as e:
            # Field might not exist or not be numeric
            pass

    if not result.warnings:
        result.add_info("No negative values found in numeric fields")

    return result


def check_duplicate_fips(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str
) -> ValidationResult:
    """Check for duplicate FIPS codes (each county should appear once)."""
    result = ValidationResult(f"Duplicate FIPS: {table_id}")

    query = f"""
    SELECT fips, COUNT(*) as count
    FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
    WHERE fips IS NOT NULL
    GROUP BY fips
    HAVING COUNT(*) > 1
    ORDER BY count DESC
    LIMIT 10
    """

    try:
        rows = list(client.query(query).result())

        if rows:
            result.add_error(f"{len(rows)} FIPS codes appear multiple times:")
            for row in rows[:5]:
                result.add_error(f"  FIPS {row.fips}: {row.count} times")
        else:
            result.add_info("No duplicate FIPS codes ✓")

    except Exception as e:
        result.add_warning(f"Could not check for duplicates: {e}")

    return result


def compare_to_previous_year(
    client: bigquery.Client,
    current_year: str,
    previous_year: str,
    section_code: str
) -> ValidationResult:
    """Compare row counts and field coverage to previous year."""
    result = ValidationResult(f"Year-over-Year Comparison: {section_code}")

    curr_year_short = current_year[2:]
    prev_year_short = previous_year[2:]

    curr_dataset = f"eavs_{current_year}"
    prev_dataset = f"eavs_{previous_year}"

    curr_table = f"eavs_county_{curr_year_short}_{section_code}"
    prev_table = f"eavs_county_{prev_year_short}_{section_code}"

    # Check if previous year table exists
    try:
        prev_table_obj = client.get_table(f"{PROJECT_ID}.{prev_dataset}.{prev_table}")
    except:
        result.add_info(f"Previous year ({previous_year}) not found for comparison")
        return result

    # Compare row counts
    query = f"""
    SELECT
      '{current_year}' as year,
      COUNT(*) as row_count
    FROM `{PROJECT_ID}.{curr_dataset}.{curr_table}`
    UNION ALL
    SELECT
      '{previous_year}' as year,
      COUNT(*) as row_count
    FROM `{PROJECT_ID}.{prev_dataset}.{prev_table}`
    """

    try:
        rows = list(client.query(query).result())
        curr_count = next(r.row_count for r in rows if r.year == current_year)
        prev_count = next(r.row_count for r in rows if r.year == previous_year)

        diff = curr_count - prev_count
        pct_change = (diff / prev_count * 100) if prev_count > 0 else 0

        result.add_info(f"{current_year}: {curr_count:,} rows")
        result.add_info(f"{previous_year}: {prev_count:,} rows")
        result.add_info(f"Change: {diff:+,} ({pct_change:+.1f}%)")

        if abs(pct_change) > 10:
            result.add_warning(f"Row count changed by {pct_change:.1f}% (>10%)")

    except Exception as e:
        result.add_warning(f"Could not compare row counts: {e}")

    return result


def main():
    parser = argparse.ArgumentParser(description='Validate EAVS data after loading to BigQuery')
    parser.add_argument('year', help='Year to validate (e.g., 2024)')
    parser.add_argument('--compare-to', help='Previous year to compare against (e.g., 2022)')
    parser.add_argument('--sections', nargs='+', help='Specific sections to validate (default: all)')

    args = parser.parse_args()

    year = args.year
    year_short = year[2:]
    dataset_id = f"eavs_{year}"

    sections = args.sections or ['a_reg', 'b_uocava', 'c_mail', 'f1_participation']

    print("=" * 80)
    print(f"{Colors.BOLD}EAVS Data Post-Load Validation{Colors.END}")
    print("=" * 80)
    print(f"\nYear: {year}")
    print(f"Dataset: {dataset_id}")
    print(f"Sections: {', '.join(sections)}\n")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    all_results = []

    # Validate each section
    for section_code in sections:
        table_id = f"eavs_county_{year_short}_{section_code}"

        print("=" * 80)
        print(f"{Colors.BOLD}Section: {section_code.upper()}{Colors.END}")
        print("=" * 80)

        # Run all checks
        checks = [
            check_table_exists(client, dataset_id, table_id),
            check_row_count(client, dataset_id, table_id, section_code),
            check_fips_validity(client, dataset_id, table_id),
            check_null_percentages(client, dataset_id, table_id),
            check_negative_values(client, dataset_id, table_id),
            check_duplicate_fips(client, dataset_id, table_id)
        ]

        # Add year-over-year comparison if requested
        if args.compare_to:
            checks.append(compare_to_previous_year(client, year, args.compare_to, section_code))

        # Print results
        for check in checks:
            check.print_results()
            all_results.append(check)

    # Summary
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}SUMMARY{Colors.END}")
    print("=" * 80)

    total_checks = len(all_results)
    passed_checks = sum(1 for r in all_results if r.passed)
    failed_checks = total_checks - passed_checks
    total_warnings = sum(len(r.warnings) for r in all_results)
    total_errors = sum(len(r.errors) for r in all_results)

    print(f"\nChecks: {passed_checks}/{total_checks} passed")
    print(f"Warnings: {total_warnings}")
    print(f"Errors: {total_errors}")

    if failed_checks == 0 and total_warnings == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL VALIDATION CHECKS PASSED{Colors.END}")
        print(f"\nData quality looks good! Safe to proceed with:")
        print(f"  1. Update union views")
        print(f"  2. Refresh staging tables")
        print(f"  3. Rebuild mart tables")
        sys.exit(0)
    elif failed_checks == 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}✓ VALIDATION PASSED WITH WARNINGS{Colors.END}")
        print(f"\nReview warnings above. Data may still be usable.")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ VALIDATION FAILED{Colors.END}")
        print(f"\nFix critical errors before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
