# EAVS Scripts Guide

## Main Workflow Scripts (Use These)

### 1. `validate_mappings.py` - Field Validation
**When to use**: Before loading any new year data
**Purpose**: Check that field mappings in config match actual CSV column names

```bash
# Validate 2024 field mappings
python scripts/validate_mappings.py 2024 "/Users/frydaguedes/Downloads/2024"

# Save corrected mappings to file
python scripts/validate_mappings.py 2024 "/path/to/data" --output corrected_mappings.yaml
```

### 2. `load_eavs_year.py` - Main ETL Pipeline  
**When to use**: After field mappings are validated and corrected
**Purpose**: Complete data loading pipeline - uploads to GCS, creates BigQuery tables

```bash
# Load 2024 data (full pipeline)
python scripts/load_eavs_year.py 2024 "/Users/frydaguedes/Downloads/2024"

# Just update views (after methodology changes)
python scripts/load_eavs_year.py 2024 "/path/to/data" --update-views-only
```

### 3. `generate_dynamic_unions.py` - Union View Generator
**When to use**: After loading new year data and getting researcher guidance on methodology changes
**Purpose**: Generate SQL for union views that combine all years

```bash
# Generate union view SQL files
python scripts/generate_dynamic_unions.py --output sql/generated

# Deploy generated views to BigQuery
bq query < sql/generated/registration_union.sql
bq query < sql/generated/mail_union.sql
bq query < sql/generated/uocava_union.sql
bq query < sql/generated/participation_union.sql
```

## Annual Process Workflow

For each new EAVS year, follow this exact sequence:

### Step 1: Prepare Configuration
```bash
# 1. Create GCS bucket
export YEAR=2028
gsutil mb -p eavs-392800 gs://eavs-data-files-${YEAR}/

# 2. Add new year sections to config/field_mappings.yaml (all fields as null initially)
```

### Step 2: Validate Field Mappings
```bash
# 3. Run field validation
python scripts/validate_mappings.py 2028 "/path/to/2028/data"

# 4. Fix field mappings in config/field_mappings.yaml based on validation output
# 5. Re-run validation until all mappings are correct
```

### Step 3: Load Data
```bash
# 6. Load data into BigQuery
python scripts/load_eavs_year.py 2028 "/path/to/2028/data"
```

### Step 4: Update Union Views (After Researcher Review)
```bash
# 7. Generate and deploy union views
python scripts/generate_dynamic_unions.py
bq query < sql/generated/*.sql
```

## Utility Scripts (Optional)

### `check_data.py` - Data Quality Check
Quick data exploration and quality checks
```bash
python scripts/check_data.py 2024 "/path/to/data"
```

### `validate_year.py` - Year-Specific Validation
Additional validation for specific year data patterns
```bash  
python scripts/validate_year.py 2024
```

## Deprecated/Legacy Scripts

### `generate_union_views.py` - ⚠️ DEPRECATED
**Don't use**: Replaced by `generate_dynamic_unions.py`
**Why deprecated**: Required manual template editing for each new year

## Script Dependencies

All scripts require:
- `requirements.txt` packages installed
- Google Cloud authentication configured
- `config/field_mappings.yaml` properly configured

## Quick Reference

| Task | Script | Example |
|------|--------|---------|
| Validate field mappings | `validate_mappings.py` | `python scripts/validate_mappings.py 2024 "/data/path"` |
| Load new year data | `load_eavs_year.py` | `python scripts/load_eavs_year.py 2024 "/data/path"` |
| Generate union views | `generate_dynamic_unions.py` | `python scripts/generate_dynamic_unions.py` |
| Quick data check | `check_data.py` | `python scripts/check_data.py 2024 "/data/path"` |

## Error Troubleshooting

- **Authentication errors**: Run `gcloud auth application-default login`
- **Field mapping errors**: Check validation output, update config, re-run validation
- **BigQuery permission errors**: Verify you're using correct Google account
- **File not found errors**: Check data directory paths and file naming conventions