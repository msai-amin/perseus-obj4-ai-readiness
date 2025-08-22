# RQ8: Program Level and Type Technology Correlation Analysis

## Research Question
**To what extent are drone/GIS/AI topics correlated with the level (undergraduate, master's, or doctoral) and type of academic programs?**

## Overview
This analysis examines the correlation between technology integration patterns and academic program characteristics, specifically focusing on how drone, GIS, and AI technologies are distributed across different program levels (undergraduate, master's, doctoral) and program types (forestry, natural resources, geospatial, etc.).

## Methodology

### Data Source
- **Primary Database**: Neo4j graph database containing university, program, and technology relationships
- **Data Scope**: Academic programs across 49 universities with forestry and related programs
- **Technology Categories**: AI/ML, GIS, Drones/UAV, Remote Sensing, Data Analytics

### Analysis Framework
The analysis follows a three-dimensional approach:

1. **Program Level Classification**: Undergraduate, Master, Doctoral
2. **Program Type Classification**: Forestry, Natural Resources, Geospatial, Data Science, Engineering, Business/Management, Science, Computer Science, Other
3. **Technology Integration Patterns**: By level, by type, and cross-correlation analysis

### Classification Methodology

#### Program Level Classification
Programs are classified based on keyword analysis of program names:
- **Undergraduate**: bachelor, bs, ba, undergraduate, associate, a.s., a.a.
- **Master**: master, ms, ma, mba, graduate, post-baccalaureate
- **Doctoral**: phd, ph.d., doctorate, doctoral, d.phil
- **Unknown**: Programs that don't match clear level indicators

#### Program Type Classification
Programs are classified based on disciplinary focus:
- **Forestry**: forestry, forest, silviculture
- **Natural Resources**: natural resource, environmental, ecology, conservation
- **Geospatial**: gis, geospatial, geographic, spatial
- **Data Science**: data science, analytics, informatics, computational
- **Engineering**: engineering, technology, technical
- **Business/Management**: business, management, administration, policy
- **Science**: science, scientific, research
- **Computer Science**: computer science, computing, software, programming
- **Other**: Programs that don't fit into specific categories

## Analysis Components

### 1. Program Level Technology Correlation
- Technology adoption rates by program level
- Technology distribution patterns across undergraduate, master's, and doctoral programs
- Statistical significance of level-based differences

### 2. Program Type Technology Correlation
- Technology integration patterns by disciplinary focus
- Comparative analysis across different academic domains
- Identification of technology-forward program types

### 3. Cross-Correlation Analysis
- Combined analysis of program level AND type
- Heatmap visualization of technology integration patterns
- Identification of high-technology program combinations

### 4. Specific Technology Focus
- **AI/ML Technology**: Distribution across program levels and types
- **GIS Technology**: Geospatial technology integration patterns
- **Drone/UAV Technology**: Emerging technology adoption analysis

## Data Extraction Queries

### Core Data Extraction
```cypher
MATCH (p:Program)
OPTIONAL MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
OPTIONAL MATCH (u:University)-[:OFFERS]->(p)
RETURN DISTINCT
       p.name as program_name,
       t.category as technology_category,
       u.name as university_name
ORDER BY u.name, p.name
```

### Program Level Classification
```cypher
MATCH (p:Program)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level
RETURN program_level, count(program_name) as program_count
ORDER BY program_level
```

### Program Type Classification
```cypher
MATCH (p:Program)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type
RETURN program_type, count(program_name) as program_count
ORDER BY program_count DESC
```

## Expected Outcomes

### Primary Findings
1. **Technology Adoption by Program Level**: Understanding how technology integration varies between undergraduate, master's, and doctoral programs
2. **Disciplinary Technology Patterns**: Identification of which program types are most technology-forward
3. **Cross-Correlation Insights**: Discovery of optimal program level and type combinations for technology integration

### Secondary Insights
1. **Educational Pathway Optimization**: Recommendations for technology-focused academic progression
2. **Curriculum Development Priorities**: Identification of areas needing enhanced technology integration
3. **Industry Alignment**: Understanding how academic technology preparation aligns with industry needs

## Visualization Components

### 1. Technology Adoption Rate Charts
- Bar charts showing technology adoption rates by program level
- Bar charts showing technology adoption rates by program type

### 2. Technology Distribution Charts
- Stacked bar charts showing technology distribution across program levels
- Stacked bar charts showing technology distribution across program types

### 3. Specific Technology Analysis
- Individual charts for AI/ML, GIS, and Drone/UAV technologies
- Distribution patterns across program levels and types

### 4. Cross-Correlation Heatmap
- Heatmap visualization showing technology integration by program level × type
- Color-coded intensity showing technology adoption levels

### 5. Summary Statistics Panel
- Comprehensive overview of analysis results
- Key metrics and findings summary

## Data Output Files

### CSV Outputs
- `rq8_program_level_analysis.csv`: Technology integration summary by program level
- `rq8_program_level_tech_counts.csv`: Detailed technology counts by program level
- `rq8_program_type_analysis.csv`: Technology integration summary by program type
- `rq8_program_type_tech_counts.csv`: Detailed technology counts by program type
- `rq8_cross_correlation_analysis.csv`: Cross-correlation analysis results
- `rq8_level_type_summary.csv`: Summary statistics by level and type
- `rq8_ai_ml_by_level.csv`: AI/ML technology distribution by program level
- `rq8_ai_ml_by_type.csv`: AI/ML technology distribution by program type
- `rq8_gis_by_level.csv`: GIS technology distribution by program level
- `rq8_gis_by_type.csv`: GIS technology distribution by program type
- `rq8_drones_uav_by_level.csv`: Drone/UAV technology distribution by program level
- `rq8_drones_uav_by_type.csv`: Drone/UAV technology distribution by program type

### Visualization Output
- `rq8_program_level_technology_correlation.png`: Comprehensive visualization dashboard

## Quality Assurance

### Data Validation
- Cross-reference program classifications with authoritative sources
- Verify technology categorization accuracy
- Validate program-university relationships

### Analysis Validation
- Statistical significance testing for correlations
- Cross-validation of classification algorithms
- Peer review of methodology and results

### Error Handling
- Robust handling of missing or incomplete data
- Graceful degradation for edge cases
- Comprehensive logging and error reporting

## Limitations and Considerations

### Data Quality
- Program name variations may affect classification accuracy
- Technology relationships may be incomplete or outdated
- University-program relationships may not capture all offerings

### Classification Challenges
- Some programs may span multiple categories
- Emerging program types may not fit existing classifications
- Technology categories may evolve over time

### Scope Limitations
- Analysis limited to programs in the database
- May not capture all technology integration methods
- Focus on specific technology categories may miss broader patterns

## Future Enhancements

### Methodological Improvements
- Machine learning-based program classification
- Dynamic technology category identification
- Temporal analysis of technology adoption trends

### Expanded Analysis
- Geographic distribution analysis
- Faculty expertise correlation
- Industry partnership analysis
- Student outcome correlation

### Integration Opportunities
- Cross-reference with course catalog data
- Integration with employment outcome data
- Comparison with international programs

## Conclusion

This analysis provides a comprehensive understanding of how technology integration varies across different academic program levels and types. The findings will inform curriculum development, program planning, and strategic decision-making in forestry and related academic programs.

The cross-correlation approach reveals complex patterns that single-dimensional analysis would miss, providing valuable insights for educational institutions seeking to optimize their technology integration strategies.
