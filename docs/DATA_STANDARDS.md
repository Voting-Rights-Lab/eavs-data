# EAVS Data Analysis Standards

## Core Principles

### 1. Data Integrity
- **Never assume field names** - always validate against actual data
- **Map missing fields to NULL** - never guess at field names that don't exist
- **Document all mappings** - every field mapping must be verified against source data
- **Preserve original data** - raw tables should never be modified

### 2. Field Mapping Standards
- **Exact Match Only**: Field mappings must match actual column names in source data
- **Case Sensitivity**: Column names are case-sensitive and must match exactly
- **Null Handling**: If a standard field doesn't exist in a year, map to `null` explicitly
- **Documentation**: Every mapping decision must be documented with rationale

### 3. Data Validation Requirements

#### Pre-Load Validation
- [ ] Verify all expected files exist
- [ ] Check file formats and encoding
- [ ] Validate geographic identifiers (FIPS, state, county)
- [ ] Confirm column counts match expectations
- [ ] Check for duplicate rows

#### Post-Load Validation  
- [ ] Verify row counts match source files
- [ ] Check for NULL values in required fields
- [ ] Validate data types and ranges
- [ ] Cross-check totals and relationships
- [ ] Compare with previous years for consistency

#### Cross-Year Consistency
- [ ] Geographic coverage (same states/counties)
- [ ] Field definitions remain consistent
- [ ] Data ranges are reasonable
- [ ] Missing data patterns are documented

### 4. Union View Standards

#### Field Standardization
- All union views must have consistent schema across years
- Field names should be descriptive and consistent
- Data types must be compatible across all years
- Missing fields in any year must be explicitly handled as NULL

#### Required Fields for All Views
```sql
- fips (STRING): 5-digit FIPS code
- election_year (STRING): 4-digit election year  
- state (INTEGER): Numeric state code
- county (INTEGER): Numeric county code
- state_abbr (STRING): 2-letter state abbreviation
- county_name (STRING): Full county name
```

### 5. Quality Assurance Process

#### Stage 1: Source Data Analysis
1. **Inventory**: List all available files and sections
2. **Schema Analysis**: Extract all column names and types
3. **Content Review**: Check sample data for quality issues
4. **Comparison**: Compare with previous years

#### Stage 2: Mapping Validation
1. **Field Matching**: Verify each mapping against actual columns
2. **Missing Field Documentation**: Document why fields are NULL
3. **Business Logic Review**: Confirm mappings make analytical sense
4. **Researcher Confirmation**: Get sign-off from subject matter expert

#### Stage 3: Load Validation
1. **Row Count Verification**: Ensure no data loss during load
2. **Data Type Validation**: Confirm proper data type conversion
3. **Range Checks**: Verify numeric values are within expected ranges
4. **Relationship Validation**: Check cross-table consistency

#### Stage 4: Integration Testing
1. **Union View Testing**: Ensure new year integrates properly
2. **Historical Comparison**: Check trends make sense
3. **Dashboard Testing**: Verify visualizations work correctly
4. **Performance Testing**: Ensure queries remain performant

### 6. Documentation Requirements

#### Field Mapping Documentation
For each section, document:
- Source column name (exact)
- Target standardized name
- Data type and format
- Business meaning
- Special handling notes
- Reason if mapped to NULL

#### Data Quality Issues
Document any:
- Missing or incomplete data
- Unusual patterns or outliers  
- Changes from previous years
- Data collection methodology changes
- Known limitations or caveats

### 7. Error Handling Standards

#### Missing Data
- **Expected missing**: Map to NULL, document why
- **Unexpected missing**: Flag as data quality issue
- **Partial missing**: Investigate and document pattern

#### Data Type Mismatches
- **String to Numeric**: Validate conversion, handle non-numeric values
- **Date Formatting**: Standardize date formats across years
- **Boolean Logic**: Handle various representations of yes/no

#### Geographic Issues
- **Missing FIPS**: Flag for manual review
- **New Counties**: Document and validate
- **County Changes**: Handle mergers/splits appropriately

### 8. Validation Scripts Requirements

#### Automated Checks
- Row count validation
- Column name verification  
- Data type checking
- Range validation
- Cross-year consistency

#### Manual Review Points
- New field mappings
- Unusual data patterns
- Significant year-over-year changes
- Geographic coverage changes

### 9. Dashboard Integration Standards

#### Mart Table Requirements
- Must include all years with consistent schema
- Performance optimized (materialized, not views)
- Updated atomically (all-or-nothing)
- Indexed on common query patterns

#### Dashboard Validation
- Test with new year data
- Verify all filters work
- Check calculations and aggregations
- Validate geographic visualizations

### 10. Annual Process Checklist

#### Before Loading New Year
- [ ] Review data standards document
- [ ] Check for methodology changes
- [ ] Compare file structure with previous years
- [ ] Prepare validation criteria

#### During Loading Process
- [ ] Follow exact field mapping process
- [ ] Document all decisions and exceptions
- [ ] Run all validation scripts
- [ ] Get researcher confirmation on mappings

#### After Loading Complete
- [ ] Verify dashboard functionality
- [ ] Document any issues or changes
- [ ] Update this standards document if needed
- [ ] Prepare summary for stakeholders

## Common Data Quality Issues to Watch For

### Geographic Data
- FIPS code changes or errors
- County name variations  
- State-level aggregations
- Missing jurisdictions

### Numeric Data
- Negative values where impossible
- Values exceeding registered voters
- Suspicious zeros or missing patterns
- Calculation inconsistencies

### Categorical Data
- New category values
- Inconsistent formatting
- Missing category definitions
- Boolean field variations

### Temporal Data  
- Date format changes
- Time period coverage
- Election cycle variations
- Reporting deadline impacts

## Success Criteria

A successful EAVS data load must:
1. **Preserve Data Integrity**: No data loss or corruption
2. **Maintain Consistency**: Compatible with historical data
3. **Enable Analysis**: Support all required analytical use cases  
4. **Pass Validation**: Meet all quality checks
5. **Update Dashboards**: Visualizations work with new data
6. **Document Changes**: All decisions and issues recorded