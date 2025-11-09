#!/bin/bash
# Export all Google Sheets-backed BigQuery tables to CSV backups
# Run this periodically to maintain backups of fragile Sheets data

set -e

PROJECT_ID="eavs-392800"
BACKUP_DIR="/Users/frydaguedes/Projects/eavs-data/data/backups/google_sheets"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "================================================"
echo "Exporting Google Sheets-backed tables to CSV"
echo "Project: $PROJECT_ID"
echo "Backup Directory: $BACKUP_DIR"
echo "================================================"

# Export Policy Tables
echo ""
echo "Exporting policy tables..."
bq query --project_id=$PROJECT_ID --use_legacy_sql=false --format=csv \
  "SELECT * FROM \`$PROJECT_ID.vrl_internal_datasets.policy_2020\`" \
  > "$BACKUP_DIR/policy_2020_backup.csv"
echo "✓ policy_2020 exported"

bq query --project_id=$PROJECT_ID --use_legacy_sql=false --format=csv \
  "SELECT * FROM \`$PROJECT_ID.vrl_internal_datasets.policy_2022\`" \
  > "$BACKUP_DIR/policy_2022_backup.csv"
echo "✓ policy_2022 exported"

# Export EAVS 2022 data (most recent before 2024)
echo ""
echo "Exporting EAVS 2022 tables..."
for table in eavs_county_22_a_reg eavs_county_22_b_uocava eavs_county_22_c_mail eavs_county_22_f1_participation; do
  echo "  Exporting $table..."
  bq query --project_id=$PROJECT_ID --use_legacy_sql=false --format=csv \
    "SELECT * FROM \`$PROJECT_ID.eavs_2022.$table\`" \
    > "$BACKUP_DIR/${table}_backup.csv"
  echo "  ✓ $table exported"
done

# Export EAVS 2020 data
echo ""
echo "Exporting EAVS 2020 tables..."
for table in eavs_county_20_a_reg eavs_county_20_b_uocava eavs_county_20_c_mail eavs_county_20_f1_participation; do
  echo "  Exporting $table..."
  bq query --project_id=$PROJECT_ID --use_legacy_sql=false --format=csv \
    "SELECT * FROM \`$PROJECT_ID.eavs_2020.$table\`" \
    > "$BACKUP_DIR/${table}_backup.csv"
  echo "  ✓ $table exported"
done

echo ""
echo "================================================"
echo "Backup complete!"
echo "Backup location: $BACKUP_DIR"
echo ""
echo "File sizes:"
ls -lh "$BACKUP_DIR"/*.csv | awk '{print $9, $5}'
echo "================================================"

# Add to git (important!)
echo ""
echo "Adding backups to git..."
cd /Users/frydaguedes/Projects/eavs-data
git add data/backups/google_sheets/*.csv
echo "✓ Backups staged for commit"
echo ""
echo "NEXT STEP: Commit these backups to version control:"
echo "  git commit -m \"Backup Google Sheets data - $(date +%Y-%m-%d)\""
