#!/bin/bash
# Script to update acs_population_union and vep_union views with 2024 data
# This uses bq query to get the current view, modifies it, and updates it

set -e  # Exit on error

PROJECT_ID="eavs-392800"
DATASET="eavs_analytics"

echo "=== Updating Denominator Union Views with 2024 Data ==="
echo ""

# Function to update acs_population_union
update_acs_view() {
    echo "Step 1: Getting current acs_population_union view SQL..."

    # Try to get the view definition
    if ! bq show --view "${PROJECT_ID}:${DATASET}.acs_population_union" > /tmp/acs_current.sql 2>&1; then
        echo "❌ Error: Cannot access acs_population_union view"
        echo "You may need to update this view manually in BigQuery Console"
        echo "See: sql/manual_updates/complete_acs_population_union_2024.sql"
        return 1
    fi

    echo "✓ Retrieved current view SQL"

    # The SQL modification would need to be done here
    # For now, direct user to manual update
    echo ""
    echo "⚠️  Please update the view manually using:"
    echo "    sql/manual_updates/complete_acs_population_union_2024.sql"
    echo ""
}

# Function to update vep_union
update_vep_view() {
    echo "Step 2: Getting current vep_union view SQL..."

    # Try to get the view definition
    if ! bq show --view "${PROJECT_ID}:${DATASET}.vep_union" > /tmp/vep_current.sql 2>&1; then
        echo "❌ Error: Cannot access vep_union view"
        echo "You may need to update this view manually in BigQuery Console"
        echo "See: sql/manual_updates/complete_vep_union_2024.sql"
        return 1
    fi

    echo "✓ Retrieved current view SQL"

    # The SQL modification would need to be done here
    # For now, direct user to manual update
    echo ""
    echo "⚠️  Please update the view manually using:"
    echo "    sql/manual_updates/complete_vep_union_2024.sql"
    echo ""
}

# Try to update views
update_acs_view
update_vep_view

echo "=== View Update Instructions ==="
echo ""
echo "Due to permission restrictions on Google Sheets-based views,"
echo "please update the views manually in BigQuery Console:"
echo ""
echo "1. Go to: https://console.cloud.google.com/bigquery?project=eavs-392800"
echo "2. Navigate to: eavs_analytics dataset"
echo "3. For acs_population_union:"
echo "   - Use SQL from: sql/manual_updates/complete_acs_population_union_2024.sql"
echo "4. For vep_union:"
echo "   - Use SQL from: sql/manual_updates/complete_vep_union_2024.sql"
echo ""
echo "After updating views, run:"
echo "  python scripts/load_denominators_2024.py --refresh-only"
echo ""
