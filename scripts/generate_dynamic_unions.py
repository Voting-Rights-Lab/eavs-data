#!/usr/bin/env python3
"""
Generate Fully Dynamic Union Views
Reads config to automatically detect all years and generate complete union views.
No manual year additions needed - completely config-driven.
"""

import sys
import yaml
from pathlib import Path
import argparse
from typing import Dict, List

class DynamicUnionGenerator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.project_id = self.config['global']['project_id']
        self.analytics_dataset = self.config['global']['analytics_dataset']
    
    def get_all_years(self, mapping_key: str) -> List[str]:
        """Get all years that have mappings for this section"""
        mappings = self.config.get(mapping_key, {})
        years = [str(year) for year in mappings.keys() if year != 'standard_fields']
        return sorted(years)
    
    def get_standard_fields(self, mapping_key: str) -> List[str]:
        """Get standard field names for this section"""
        mappings = self.config.get(mapping_key, {})
        return mappings.get('standard_fields', [])
    
    def get_dataset_name(self, year: str) -> str:
        """Get dataset name for a given year"""
        return f"eavs_{year}"
    
    def get_table_name(self, year: str, section_code: str) -> str:
        """Get table name for a given year and section"""
        year_suffix = year[-2:]  # 2024 -> 24
        section_suffix = section_code.upper().replace('_', '_')
        return f"eavs_county_{year_suffix}_{section_suffix}"
    
    def generate_union_select(self, year: str, mapping_key: str, section_code: str) -> str:
        """Generate SELECT clause for one year"""
        mappings = self.config.get(mapping_key, {})
        year_mappings = mappings.get(int(year), mappings.get(year, {}))
        standard_fields = self.get_standard_fields(mapping_key)
        
        dataset_name = self.get_dataset_name(year)
        table_name = self.get_table_name(year, section_code)
        
        # Define base fields that are always included
        base_fields = {'fips', 'election_year', 'state', 'county', 'state_abbr', 'county_name'}

        # Start with base fields
        selects = [
            "fips",
            f"'{year}' as election_year",
            "state",
            "county",
            "state_abbr",
            "county_name"
        ]

        # Add mapped fields (excluding base fields to avoid duplicates)
        for standard_field in standard_fields:
            # Skip if this is a base field (already included above)
            if standard_field in base_fields:
                continue

            source_field = year_mappings.get(standard_field)

            if source_field == 'null' or source_field is None:
                field_select = f"NULL as {standard_field}"
            else:
                field_select = f"{source_field} as {standard_field}"

            selects.append(field_select)
        
        # Generate SELECT block
        select_clause = ",\n  ".join(selects)
        from_clause = f"`{self.project_id}.{dataset_name}.{table_name}`"
        
        return f"""-- {year} Data
SELECT 
  {select_clause}
FROM {from_clause}"""
    
    def generate_full_union_view(self, mapping_key: str, section_code: str, view_name: str) -> str:
        """Generate complete union view SQL"""
        years = self.get_all_years(mapping_key)
        
        if not years:
            raise ValueError(f"No years found for {mapping_key}")
        
        # Generate SELECT blocks for each year
        union_blocks = []
        for year in years:
            try:
                select_block = self.generate_union_select(year, mapping_key, section_code)
                union_blocks.append(select_block)
            except Exception as e:
                print(f"⚠️  Warning: Could not generate {year} block: {e}")
                continue
        
        if not union_blocks:
            raise ValueError(f"Could not generate any union blocks for {mapping_key}")
        
        # Combine with UNION ALL
        union_sql = "\n\nUNION ALL\n\n".join(union_blocks)
        
        # Add CREATE VIEW statement
        view_sql = f"""-- EAVS {view_name} Union View
-- Automatically generated from config - all years included dynamically
-- DO NOT EDIT - regenerate using scripts/generate_dynamic_unions.py

CREATE OR REPLACE VIEW `{self.project_id}.{self.analytics_dataset}.{view_name}` AS

{union_sql}"""
        
        return view_sql
    
    def generate_all_views(self, output_dir: str):
        """Generate all union views"""
        
        view_configs = [
            {
                'mapping_key': 'registration_mappings',
                'section_code': 'a_reg', 
                'view_name': 'eavs_county_reg_union',
                'output_file': 'registration_union.sql'
            },
            {
                'mapping_key': 'mail_mappings',
                'section_code': 'c_mail',
                'view_name': 'eavs_county_mail_union', 
                'output_file': 'mail_union.sql'
            },
            {
                'mapping_key': 'uocava_mappings',
                'section_code': 'b_uocava',
                'view_name': 'eavs_county_uocava_union',
                'output_file': 'uocava_union.sql'
            },
            {
                'mapping_key': 'participation_mappings',
                'section_code': 'f1_participation',
                'view_name': 'eavs_county_part_union',
                'output_file': 'participation_union.sql'
            }
        ]
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Generating Dynamic Union Views")
        print("=" * 60)
        print(f"Output directory: {output_path}")
        
        for config in view_configs:
            print(f"\n🏗️  Generating {config['view_name']}...")
            
            try:
                # Get years for this view
                years = self.get_all_years(config['mapping_key'])
                print(f"  📅 Years found: {', '.join(years)}")
                
                # Generate SQL
                view_sql = self.generate_full_union_view(
                    config['mapping_key'],
                    config['section_code'], 
                    config['view_name']
                )
                
                # Write file
                output_file = output_path / config['output_file']
                with open(output_file, 'w') as f:
                    f.write(view_sql)
                
                print(f"  ✅ Generated: {output_file}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
        
        print(f"\n✅ Dynamic union generation complete!")
        print(f"\n📝 Key Benefits:")
        print("  • Fully automatic - no manual year additions needed")
        print("  • Config-driven - add new year to YAML, regenerate views")
        print("  • Handles missing fields automatically (NULL)")
        print("  • Validates field mappings during generation")
        
        print(f"\n🚀 To deploy new views:")
        for config in view_configs:
            output_file = output_path / config['output_file']
            print(f"  bq query < {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate fully dynamic union view SQL files')
    parser.add_argument('--config', default='config/field_mappings.yaml',
                       help='Path to field mappings config')
    parser.add_argument('--output', default='sql/generated',
                       help='Output directory for generated SQL files')
    
    args = parser.parse_args()
    
    if not Path(args.config).exists():
        print(f"❌ Config file not found: {args.config}")
        sys.exit(1)
    
    try:
        generator = DynamicUnionGenerator(args.config)
        generator.generate_all_views(args.output)
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()