#!/usr/bin/env python3
"""
Validate that a year's data has been properly loaded into BigQuery
"""

import argparse
from google.cloud import bigquery

PROJECT_ID = "eavs-392800"

def validate_year(year):
    """Check that all expected tables and views exist for a year"""
    client = bigquery.Client(project=PROJECT_ID)
    year_short = year[-2:]
    
    print(f"\n🔍 Validating EAVS {year} data in BigQuery")
    print("=" * 50)
    
    # Check dataset exists
    dataset_id = f"eavs_{year}"
    try:
        dataset = client.get_dataset(dataset_id)
        print(f"✓ Dataset {dataset_id} exists")
    except:
        print(f"❌ Dataset {dataset_id} not found")
        return False
    
    # Check expected tables
    expected_tables = [
        f"eavs_county_{year_short}_a_reg",
        f"eavs_county_{year_short}_b_uocava", 
        f"eavs_county_{year_short}_c_mail",
        f"eavs_county_{year_short}_f1_participation"
    ]
    
    print(f"\nChecking tables:")
    tables = client.list_tables(dataset_id)
    table_names = [table.table_id for table in tables]
    
    for expected in expected_tables:
        if expected in table_names:
            # Get row count
            query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{dataset_id}.{expected}`"
            result = list(client.query(query).result())[0]
            print(f"  ✓ {expected}: {result.cnt:,} rows")
        else:
            print(f"  ⚠️  {expected}: not found")
    
    # Check if year appears in union views
    print(f"\nChecking union views:")
    views_to_check = [
        "eavs_county_reg_union",
        "eavs_county_uocava_union",
        "eavs_county_mail_union",
        "eavs_county_part_union"
    ]
    
    for view in views_to_check:
        query = f"""
        SELECT COUNT(*) as cnt 
        FROM `{PROJECT_ID}.eavs_analytics.{view}`
        WHERE election_year = '{year}'
        """
        try:
            result = list(client.query(query).result())[0]
            if result.cnt > 0:
                print(f"  ✓ {view}: {result.cnt:,} rows for {year}")
            else:
                print(f"  ⚠️  {view}: no data for {year} (view needs updating)")
        except:
            print(f"  ⚠️  {view}: error querying")
    
    print("\n" + "=" * 50)
    print("Validation complete!")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate EAVS year data in BigQuery')
    parser.add_argument('year', help='Year to validate (e.g., 2024)')
    args = parser.parse_args()
    
    validate_year(args.year)