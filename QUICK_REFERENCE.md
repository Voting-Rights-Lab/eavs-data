# EAVS Pipeline Quick Reference

## 🚀 Quick Commands

### Load new year (complete process)
```bash
python scripts/load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
```

### Refresh materialized tables only
```bash
python scripts/load_eavs_year.py 2024 /any/path --refresh-tables
```

### Check data files before loading
```bash
python scripts/check_data.py /Users/frydaguedes/Downloads/2024
```

### Validate year in BigQuery
```bash
python scripts/validate_year.py 2024
```

## 📁 Directory Structure
```
eavs-data/
├── scripts/              # All Python scripts
│   ├── load_eavs_year.py    # Main loader script
│   ├── check_data.py        # CSV validator
│   └── validate_year.py     # BigQuery validator
├── config/               # Configuration files
│   └── field_mappings.yaml  # Field mappings for all years
├── sql/                  # SQL files
│   ├── templates/           # Reusable SQL queries
│   └── view_updates/        # Generated view updates (created by script)
├── docs/                 # Documentation
│   ├── ANNUAL_CHECKLIST.md # Step-by-step checklist
│   └── *.md                # Other docs
└── logs/                 # Log files (gitignored)
```

## 🔑 Key BigQuery Locations

### Datasets
- **Year-specific**: `eavs_2016`, `eavs_2018`, `eavs_2020`, `eavs_2022`, `eavs_2024`
- **Analytics**: `eavs_analytics` (contains union views and marts)

### Important Views (in eavs_analytics)
- `eavs_county_reg_union` - Registration data all years
- `eavs_county_mail_union` - Mail voting data all years
- `eavs_county_uocava_union` - Military/overseas data all years
- `eavs_county_part_union` - Participation data all years

### Materialized Tables (in eavs_analytics)
- `stg_eavs_county_reg_union`
- `stg_eavs_county_mail_union`
- `stg_eavs_county_uocava_union`
- `stg_eavs_county_part_union`

### Analytics Marts (in eavs_analytics)
- `mart_eavs_analytics_county_rollup`
- `mart_eavs_analytics_state_rollup`

## 📊 Common SQL Queries

### Check available years
```sql
SELECT DISTINCT election_year 
FROM `eavs-392800.eavs_analytics.eavs_county_reg_union`
ORDER BY election_year DESC;
```

### Get county count for new year
```sql
SELECT COUNT(*) as counties, COUNT(DISTINCT state) as states
FROM `eavs-392800.eavs_2024.eavs_county_24_a_reg`;
```

### Verify data loaded
```sql
SELECT election_year, COUNT(*) as records
FROM `eavs-392800.eavs_analytics.stg_eavs_county_reg_union`
WHERE election_year = '2024'
GROUP BY election_year;
```

## 🔧 Troubleshooting

### Authentication Issues
```bash
# Check current account
gcloud auth list

# Re-authenticate
gcloud auth login fryda.guedes@contractor.votingrightslab.org
gcloud config set project eavs-392800
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### View Update Not Working
1. Check SQL syntax in generated file
2. Ensure table names match exactly
3. Verify CTE name is unique
4. Check UNION ALL is added

## 📝 Annual Workflow Summary

1. **Download data** from source
2. **Run loader script** → uploads to GCS, creates tables
3. **Update views** in BigQuery UI with generated SQL
4. **Refresh materialized tables** with --refresh-tables flag
5. **Update mart tables** if needed (manual in BigQuery)
6. **Verify dashboards** in Looker Studio

## 🔗 Important Links

- **BigQuery Console**: https://console.cloud.google.com/bigquery?project=eavs-392800
- **GCS Bucket**: https://console.cloud.google.com/storage/browser/eavs-data-files
- **Project**: eavs-392800

## 📧 Contact

Consultant: fryda.guedes@contractor.votingrightslab.org