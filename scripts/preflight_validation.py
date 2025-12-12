#!/usr/bin/env python3
"""
Pre-Flight Validation for EAVS Data Load

Validates CSV files before uploading to ensure:
1. CSV headers match expected field mappings
2. Files exist and are readable
3. Basic data quality checks (row counts, required fields)

This catches errors BEFORE the load process starts, saving time and preventing
partial loads with bad data.

Usage:
    python scripts/preflight_validation.py 2024 /path/to/2024/data
    python scripts/preflight_validation.py 2024 /path/to/2024/data --strict
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import yaml
from typing import Dict, List, Tuple, Set

# Section to file mappings (matches load_eavs_year.py)
FILE_MAPPINGS = {
    'a_reg': 'Section A_ Registration/A. Registration.csv',
    'b_uocava': 'Section B_ UOCAVA/B. UOCAVA.csv',
    'c_mail': 'Section C_ Mail/C. Absentee _ Mail.csv',
    'f1_participation': 'Section F1_ Participation*/F1. Participation and Method.csv'
}

# Map section codes to field mapping keys
SECTION_TO_MAPPING = {
    'a_reg': 'registration_mappings',
    'b_uocava': 'uocava_mappings',
    'c_mail': 'mail_mappings',
    'f1_participation': 'participation_mappings'
}


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def load_field_mappings(config_path: Path) -> dict:
    """Load field mappings from YAML config."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def find_csv_file(data_dir: Path, relative_path: str) -> Path:
    """Find CSV file, handling wildcards in path."""
    if '*' in relative_path:
        pattern = relative_path.replace('*', '')
        matching_dirs = list(data_dir.glob(pattern))
        if not matching_dirs:
            return None
        # Take first match and look for CSV
        search_dir = matching_dirs[0]
        csv_files = list(search_dir.glob('*.csv'))
        if csv_files:
            return csv_files[0]
        return None
    else:
        file_path = data_dir / relative_path
        return file_path if file_path.exists() else None


def get_csv_headers(csv_file: Path) -> List[str]:
    """Read CSV headers without loading entire file."""
    try:
        df = pd.read_csv(csv_file, nrows=0)
        return list(df.columns)
    except Exception as e:
        print(f"{Colors.RED}Error reading CSV: {e}{Colors.END}")
        return []


def validate_section(
    year: str,
    section_code: str,
    csv_file: Path,
    field_mappings: dict,
    strict: bool = False
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a single section's CSV against field mappings.

    Returns:
        (success, warnings, errors)
    """
    warnings = []
    errors = []

    # Get mapping key for this section
    mapping_key = SECTION_TO_MAPPING.get(section_code)
    if not mapping_key:
        errors.append(f"Unknown section: {section_code}")
        return False, warnings, errors

    # Get expected fields for this year
    section_mappings = field_mappings.get(mapping_key, {})
    year_mappings = section_mappings.get(year) or section_mappings.get(int(year))

    if not year_mappings:
        errors.append(f"No field mappings found for {year} in {mapping_key}")
        return False, warnings, errors

    # Get actual CSV headers
    csv_headers = get_csv_headers(csv_file)
    if not csv_headers:
        errors.append("Could not read CSV headers")
        return False, warnings, errors

    csv_headers_lower = [h.lower() for h in csv_headers]

    # Check each mapped field
    missing_fields = []
    null_mapped_fields = []

    for standard_field, source_field in year_mappings.items():
        if source_field is None or source_field == 'null':
            null_mapped_fields.append(standard_field)
            continue

        # Check if source field exists in CSV
        if source_field not in csv_headers:
            # Try case-insensitive match
            if source_field.lower() not in csv_headers_lower:
                missing_fields.append(f"{standard_field} (expects: {source_field})")

    # Report null-mapped fields
    if null_mapped_fields and not strict:
        warnings.append(f"{len(null_mapped_fields)} fields mapped to NULL (expected for this year)")

    # Report missing fields
    if missing_fields:
        errors.append(f"Missing {len(missing_fields)} expected fields:")
        for field in missing_fields[:10]:  # Show first 10
            errors.append(f"  - {field}")
        if len(missing_fields) > 10:
            errors.append(f"  ... and {len(missing_fields) - 10} more")

    # Check for extra fields in CSV not in mapping
    mapped_source_fields = {
        v for v in year_mappings.values()
        if v is not None and v != 'null'
    }
    extra_fields = set(csv_headers) - mapped_source_fields

    if extra_fields and strict:
        warnings.append(f"{len(extra_fields)} unmapped fields in CSV (may be new data):")
        for field in sorted(list(extra_fields))[:5]:
            warnings.append(f"  - {field}")
        if len(extra_fields) > 5:
            warnings.append(f"  ... and {len(extra_fields) - 5} more")

    success = len(errors) == 0
    return success, warnings, errors


def validate_data_quality(csv_file: Path) -> Tuple[List[str], List[str]]:
    """
    Basic data quality checks.

    Returns:
        (warnings, errors)
    """
    warnings = []
    errors = []

    try:
        # Read small sample
        df = pd.read_csv(csv_file, nrows=10)

        # Check if file has data
        total_rows = sum(1 for _ in open(csv_file)) - 1  # Subtract header
        if total_rows == 0:
            errors.append("CSV file is empty (no data rows)")
        elif total_rows < 10:
            warnings.append(f"Only {total_rows} rows (expected ~3,000 for county data)")

        # Check for required-looking columns
        headers = list(df.columns)
        has_fips = any('fips' in h.lower() for h in headers)
        has_state = any('state' in h.lower() for h in headers)
        has_county = any('county' in h.lower() for h in headers)

        if not has_fips and not (has_state and has_county):
            warnings.append("No FIPS or state/county columns detected (may be intentional)")

    except Exception as e:
        errors.append(f"Error checking data quality: {e}")

    return warnings, errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate EAVS CSV files before loading'
    )
    parser.add_argument('year', help='Year to validate (e.g., 2024)')
    parser.add_argument('data_dir', help='Path to data directory')
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: warn about unmapped fields'
    )
    parser.add_argument(
        '--config',
        default='config/field_mappings.yaml',
        help='Path to field mappings config (default: config/field_mappings.yaml)'
    )

    args = parser.parse_args()

    year = args.year
    data_dir = Path(args.data_dir)
    config_path = Path(__file__).parent.parent / args.config

    print("=" * 80)
    print(f"{Colors.BOLD}EAVS Data Pre-Flight Validation{Colors.END}")
    print("=" * 80)
    print(f"\nYear: {year}")
    print(f"Data directory: {data_dir}")
    print(f"Config: {config_path}")
    print(f"Mode: {'STRICT' if args.strict else 'NORMAL'}")

    # Load field mappings
    try:
        field_mappings = load_field_mappings(config_path)
        print(f"{Colors.GREEN}✓{Colors.END} Loaded field mappings")
    except Exception as e:
        print(f"{Colors.RED}✗ Error loading config: {e}{Colors.END}")
        sys.exit(1)

    # Validate data directory exists
    if not data_dir.exists():
        print(f"{Colors.RED}✗ Data directory not found: {data_dir}{Colors.END}")
        sys.exit(1)

    print(f"{Colors.GREEN}✓{Colors.END} Data directory exists\n")

    # Validate each section
    results = {}

    for section_code, relative_path in FILE_MAPPINGS.items():
        print("=" * 80)
        print(f"{Colors.BOLD}Section: {section_code.upper()}{Colors.END}")
        print("=" * 80)

        # Find CSV file
        csv_file = find_csv_file(data_dir, relative_path)

        if not csv_file:
            print(f"{Colors.RED}✗ File not found: {relative_path}{Colors.END}")
            results[section_code] = {'success': False, 'reason': 'File not found'}
            continue

        print(f"File: {csv_file.name}")

        # Validate headers against mappings
        success, warnings, errors = validate_section(
            year, section_code, csv_file, field_mappings, args.strict
        )

        # Data quality checks
        dq_warnings, dq_errors = validate_data_quality(csv_file)
        warnings.extend(dq_warnings)
        errors.extend(dq_errors)

        # Print results
        if errors:
            print(f"\n{Colors.RED}✗ ERRORS:{Colors.END}")
            for error in errors:
                print(f"  {error}")

        if warnings:
            print(f"\n{Colors.YELLOW}⚠ WARNINGS:{Colors.END}")
            for warning in warnings:
                print(f"  {warning}")

        if success and not warnings:
            print(f"\n{Colors.GREEN}✓ All checks passed{Colors.END}")
        elif success:
            print(f"\n{Colors.YELLOW}✓ Validation passed with warnings{Colors.END}")
        else:
            print(f"\n{Colors.RED}✗ Validation failed{Colors.END}")

        results[section_code] = {
            'success': success,
            'warnings': len(warnings),
            'errors': len(errors)
        }

    # Summary
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}SUMMARY{Colors.END}")
    print("=" * 80)

    total = len(results)
    passed = sum(1 for r in results.values() if r['success'])
    failed = total - passed
    total_warnings = sum(r.get('warnings', 0) for r in results.values())
    total_errors = sum(r.get('errors', 0) for r in results.values())

    print(f"\nSections: {passed}/{total} passed")
    print(f"Warnings: {total_warnings}")
    print(f"Errors: {total_errors}")

    if failed == 0 and total_warnings == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.END}")
        print(f"\n{Colors.GREEN}Ready to load data:{Colors.END}")
        print(f"  python scripts/load_eavs_year.py {year} {data_dir}")
        sys.exit(0)
    elif failed == 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}✓ VALIDATION PASSED WITH WARNINGS{Colors.END}")
        print(f"\nYou can proceed, but review warnings above.")
        print(f"  python scripts/load_eavs_year.py {year} {data_dir}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ VALIDATION FAILED{Colors.END}")
        print(f"\nFix errors above before loading data.")
        print(f"Common fixes:")
        print(f"  1. Update config/field_mappings.yaml with correct field names for {year}")
        print(f"  2. Verify CSV files are in correct directories")
        print(f"  3. Check CSV files for corruption or encoding issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
