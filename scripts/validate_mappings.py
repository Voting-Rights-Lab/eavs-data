#!/usr/bin/env python3
"""
EAVS Field Mapping Validator
Validates field mappings against actual data and generates corrected mappings
"""

import sys
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import json

class MappingValidator:
    def __init__(self, config_path: str, data_dir: str, year: str):
        self.year = year
        self.data_dir = Path(data_dir)
        
        # Load current configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get_actual_fields(self, section: str) -> List[str]:
        """Get actual field names from CSV file"""
        file_mapping = {
            'a_reg': f'Section A_ Registration/EAVS_county_{self.year[-2:]}_A_REG.csv',
            'b_uocava': f'Section B_ UOCAVA/EAVS_county_{self.year[-2:]}_B_UOCAVA.csv',
            'c_mail': f'Section C_ Mail/EAVS_county_{self.year[-2:]}_C_MAIL.csv',
            'f1_participation': f'Section F1_ Participation*/EAVS_county_{self.year[-2:]}_F1_PARTICIPATION.csv'
        }
        
        file_path = self.data_dir / file_mapping[section]
        
        # Handle wildcards
        if '*' in str(file_path):
            pattern = str(file_path).replace('*', '')
            matching_files = list(self.data_dir.glob('**/' + pattern.split('/')[-1]))
            if matching_files:
                file_path = matching_files[0]
            else:
                return []
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return []
        
        # Read just the header
        try:
            df = pd.read_csv(file_path, nrows=0)
            return list(df.columns)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return []
    
    def validate_section_mappings(self, section: str, mapping_key: str) -> Dict:
        """Validate mappings for a specific section"""
        print(f"\n🔍 Validating {section.upper()} mappings...")
        print("=" * 60)
        
        # Get actual fields in the data
        actual_fields = self.get_actual_fields(section)
        if not actual_fields:
            return {"error": f"Could not read fields for section {section}"}
        
        print(f"✓ Found {len(actual_fields)} fields in {section} data")
        
        # Get expected mappings from config
        mappings = self.config.get(mapping_key, {})
        year_mappings = mappings.get(int(self.year), mappings.get(self.year, {}))
        standard_fields = mappings.get('standard_fields', [])
        
        if not year_mappings:
            return {"error": f"No {self.year} mappings found for {mapping_key}"}
        
        print(f"✓ Found {len(year_mappings)} configured mappings")
        print(f"✓ Expected {len(standard_fields)} standard fields")
        
        # Validation results
        results = {
            "section": section,
            "total_actual_fields": len(actual_fields),
            "total_configured_mappings": len(year_mappings),
            "total_standard_fields": len(standard_fields),
            "valid_mappings": {},
            "invalid_mappings": {},
            "missing_mappings": [],
            "corrected_mappings": {},
            "sample_data": {}
        }
        
        # Check each configured mapping
        for standard_field, source_field in year_mappings.items():
            if source_field == 'null' or source_field is None:
                results["valid_mappings"][standard_field] = "null"
                continue
            
            if source_field in actual_fields:
                results["valid_mappings"][standard_field] = source_field
                print(f"  ✓ {standard_field} -> {source_field}")
            else:
                results["invalid_mappings"][standard_field] = source_field
                print(f"  ❌ {standard_field} -> {source_field} (NOT FOUND)")
                
                # Try to find a similar field
                similar = self.find_similar_field(source_field, actual_fields)
                if similar:
                    results["corrected_mappings"][standard_field] = similar
                    print(f"      💡 Did you mean: {similar}?")
        
        # Check for unmapped standard fields
        for standard_field in standard_fields:
            if standard_field not in year_mappings:
                results["missing_mappings"].append(standard_field)
                print(f"  ⚠️  Missing mapping for: {standard_field}")
        
        # Get sample data for first few rows
        try:
            file_path = self.data_dir / f"Section {section[0].upper()}*/EAVS_county_{self.year[-2:]}_{section.upper().replace('_', '_')}.csv"
            sample_df = pd.read_csv(str(file_path).replace('*', ''), nrows=3)
            results["sample_data"] = {
                col: sample_df[col].fillna('NULL').tolist()[:3] 
                for col in actual_fields[:10]  # First 10 columns
            }
        except:
            pass
        
        return results
    
    def find_similar_field(self, target: str, available_fields: List[str]) -> str:
        """Find similar field names using fuzzy matching"""
        target_lower = target.lower()
        
        # Exact match (case insensitive)
        for field in available_fields:
            if field.lower() == target_lower:
                return field
        
        # Contains match
        for field in available_fields:
            if target_lower in field.lower() or field.lower() in target_lower:
                return field
        
        # Common patterns
        patterns = {
            'total': ['total', 'tot'],
            'reject': ['reject', 'denied', 'invalid'],
            'count': ['count', 'cnt', 'total'],
            'mail': ['mail', 'absentee', 'post'],
            'uocava': ['uocava', 'military', 'overseas']
        }
        
        for pattern, alternatives in patterns.items():
            if pattern in target_lower:
                for alt in alternatives:
                    for field in available_fields:
                        if alt in field.lower():
                            return field
        
        return None
    
    def generate_corrected_config(self, validation_results: Dict) -> Dict:
        """Generate corrected YAML configuration"""
        corrected_config = {}
        
        for section_result in validation_results.values():
            if isinstance(section_result, dict) and 'section' in section_result:
                section = section_result['section']
                mapping_key = {
                    'a_reg': 'registration_mappings',
                    'b_uocava': 'uocava_mappings', 
                    'c_mail': 'mail_mappings',
                    'f1_participation': 'participation_mappings'
                }.get(section)
                
                if not mapping_key:
                    continue
                
                # Start with existing valid mappings
                year_mappings = {}
                year_mappings.update(section_result.get('valid_mappings', {}))
                
                # Add corrected mappings
                for field, corrected in section_result.get('corrected_mappings', {}).items():
                    year_mappings[field] = corrected
                
                # Add null for missing mappings
                for field in section_result.get('missing_mappings', []):
                    year_mappings[field] = 'null'
                
                if mapping_key not in corrected_config:
                    corrected_config[mapping_key] = {int(self.year): year_mappings}
                else:
                    corrected_config[mapping_key][int(self.year)] = year_mappings
        
        return corrected_config
    
    def run_validation(self) -> Dict:
        """Run complete validation for all sections"""
        print(f"🔍 EAVS {self.year} Field Mapping Validation")
        print("=" * 60)
        print(f"Data directory: {self.data_dir}")
        print(f"Year: {self.year}")
        
        sections_to_validate = [
            ('a_reg', 'registration_mappings'),
            ('b_uocava', 'uocava_mappings'),
            ('c_mail', 'mail_mappings'),
            ('f1_participation', 'participation_mappings')
        ]
        
        validation_results = {}
        
        for section, mapping_key in sections_to_validate:
            results = self.validate_section_mappings(section, mapping_key)
            validation_results[section] = results
        
        return validation_results
    
    def print_summary(self, validation_results: Dict):
        """Print validation summary"""
        print(f"\n📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        total_sections = len(validation_results)
        sections_with_errors = 0
        total_invalid = 0
        total_missing = 0
        total_corrected = 0
        
        for section, results in validation_results.items():
            if isinstance(results, dict) and 'invalid_mappings' in results:
                invalid_count = len(results.get('invalid_mappings', {}))
                missing_count = len(results.get('missing_mappings', []))
                corrected_count = len(results.get('corrected_mappings', {}))
                
                if invalid_count > 0 or missing_count > 0:
                    sections_with_errors += 1
                
                total_invalid += invalid_count
                total_missing += missing_count 
                total_corrected += corrected_count
                
                print(f"  {section.upper()}: {invalid_count} invalid, {missing_count} missing, {corrected_count} suggested fixes")
        
        print(f"\nOVERALL:")
        print(f"  Sections processed: {total_sections}")
        print(f"  Sections with issues: {sections_with_errors}")
        print(f"  Invalid mappings: {total_invalid}")
        print(f"  Missing mappings: {total_missing}")
        print(f"  Suggested corrections: {total_corrected}")
        
        if total_invalid == 0 and total_missing == 0:
            print(f"\n✅ All mappings are valid!")
        else:
            print(f"\n⚠️  Found {total_invalid + total_missing} mapping issues that need attention")

def main():
    parser = argparse.ArgumentParser(description='Validate EAVS field mappings')
    parser.add_argument('year', help='Election year (e.g., 2024)')
    parser.add_argument('data_dir', help='Directory containing EAVS data files')
    parser.add_argument('--config', default='config/field_mappings.yaml', 
                       help='Path to field mappings config')
    parser.add_argument('--output', help='Output corrected mappings to file')
    parser.add_argument('--format', choices=['yaml', 'json'], default='yaml',
                       help='Output format for corrected mappings')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = MappingValidator(args.config, args.data_dir, args.year)
    
    # Run validation
    results = validator.run_validation()
    
    # Print summary
    validator.print_summary(results)
    
    # Generate corrected config if requested
    if args.output:
        corrected = validator.generate_corrected_config(results)
        
        if args.format == 'json':
            with open(args.output, 'w') as f:
                json.dump(corrected, f, indent=2)
        else:
            with open(args.output, 'w') as f:
                yaml.dump(corrected, f, default_flow_style=False)
        
        print(f"\n📝 Corrected mappings saved to: {args.output}")
    
    # Return appropriate exit code
    has_errors = any(
        len(r.get('invalid_mappings', {})) > 0 or len(r.get('missing_mappings', [])) > 0
        for r in results.values() if isinstance(r, dict)
    )
    
    sys.exit(1 if has_errors else 0)

if __name__ == '__main__':
    main()