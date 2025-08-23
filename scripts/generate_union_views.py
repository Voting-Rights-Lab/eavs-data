#!/usr/bin/env python3
"""
Generate Union View SQL Files
Takes SQL templates with {{field_name_year}} placeholders and generates actual SQL
using field mappings from the YAML configuration.
"""

import sys
import yaml
from pathlib import Path
import argparse
from typing import Dict, List

class UnionViewGenerator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def generate_view_sql(self, template_path: str, mapping_key: str, output_path: str):
        """Generate SQL view from template using field mappings"""
        
        # Read template
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Get field mappings for this section
        mappings = self.config.get(mapping_key, {})
        
        # Get all years available
        years = [str(year) for year in mappings.keys() if year != 'standard_fields']
        
        # Generate replacements for all field/year combinations
        replacements = {}
        
        for year in years:
            year_mappings = mappings.get(int(year), mappings.get(year, {}))
            
            for standard_field, source_field in year_mappings.items():
                placeholder = f"{{{{{standard_field}_{year}}}}}"
                
                if source_field == 'null' or source_field is None:
                    # Map to NULL for missing fields
                    replacement = "NULL"
                else:
                    # Map to actual source field name
                    replacement = source_field
                
                replacements[placeholder] = replacement
                print(f"  {placeholder} -> {replacement}")
        
        # Apply replacements
        generated_sql = template
        for placeholder, replacement in replacements.items():
            generated_sql = generated_sql.replace(placeholder, replacement)
        
        # Write generated SQL
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(generated_sql)
        
        print(f"✅ Generated: {output_path}")
        
        return generated_sql

def main():
    parser = argparse.ArgumentParser(description='Generate union view SQL files from templates')
    parser.add_argument('--config', default='config/field_mappings.yaml',
                       help='Path to field mappings config')
    parser.add_argument('--templates', default='sql/templates',
                       help='Directory containing SQL templates')
    parser.add_argument('--output', default='sql/generated',
                       help='Output directory for generated SQL files')
    
    args = parser.parse_args()
    
    generator = UnionViewGenerator(args.config)
    
    # Map of template files to their corresponding field mapping keys
    view_configs = [
        {
            'template': 'registration_union.sql',
            'mapping_key': 'registration_mappings',
            'output': 'registration_union.sql'
        },
        {
            'template': 'mail_union.sql', 
            'mapping_key': 'mail_mappings',
            'output': 'mail_union.sql'
        },
        {
            'template': 'uocava_union.sql',
            'mapping_key': 'uocava_mappings', 
            'output': 'uocava_union.sql'
        },
        {
            'template': 'participation_union.sql',
            'mapping_key': 'participation_mappings',
            'output': 'participation_union.sql'
        }
    ]
    
    print(f"🔧 Generating Union View SQL Files")
    print("=" * 60)
    
    templates_dir = Path(args.templates)
    output_dir = Path(args.output)
    
    for config in view_configs:
        print(f"\\n🏗️  Processing {config['template']}...")
        
        template_path = templates_dir / config['template']
        output_path = output_dir / config['output']
        
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            continue
            
        try:
            generator.generate_view_sql(
                str(template_path),
                config['mapping_key'], 
                str(output_path)
            )
        except Exception as e:
            print(f"❌ Error generating {config['template']}: {e}")
            continue
    
    print(f"\\n✅ Union view generation complete!")
    print(f"Generated SQL files are in: {output_dir}")
    print()
    print("Next steps:")
    print("1. Review generated SQL files")
    print("2. Deploy to BigQuery when ready:")
    print("   bq query < sql/generated/registration_union.sql")
    print("   bq query < sql/generated/mail_union.sql") 
    print("   bq query < sql/generated/uocava_union.sql")
    print("   bq query < sql/generated/participation_union.sql")

if __name__ == '__main__':
    main()