# Research Question Analysis Procedure Guide

## Overview
This document captures the standardized procedure applied to all Research Questions (RQs) in the KG-perseus project. This procedure ensures consistency, accuracy, and reproducibility across all analyses.

## Standard RQ Analysis Procedure

### 1. Initial Setup and Data Source Identification
- **Neo4j Database Connection**: Establish connection to the graph database using the `neo4j` Python driver
- **Data Source Assessment**: Identify primary and secondary data sources for the specific RQ
- **Technology Categories**: Define the five standard technology categories:
  - AI/ML Technologies
  - Geospatial Technologies  
  - Drones/UAV Technologies
  - Remote Sensing Technologies
  - Data Analytics Technologies

### 2. Data Extraction and Validation
- **Primary Data Query**: Execute Cypher queries to extract relevant data from Neo4j
- **Data Validation**: Cross-reference extracted data with authoritative sources
- **Quality Control**: Verify data accuracy and completeness
- **Error Correction**: Address any data quality issues identified

### 3. Analysis Implementation
- **Python Script Creation**: Develop analysis script following the standard class structure:
  ```python
  class RQ[Number][Description]Analyzer:
      def __init__(self, uri, user, password)
      def connect(self)
      def close(self)
      def [primary_analysis_method](self)
      def [secondary_analysis_method](self)
      def create_visualizations(self)
      def print_detailed_results(self)
      def save_results(self)
      def run_complete_analysis(self)
  ```
- **Statistical Analysis**: Perform relevant statistical tests and calculations
- **Pattern Identification**: Identify trends and correlations in the data

### 4. Visualization and Output Generation
- **Chart Creation**: Generate 4-5 standard visualizations using matplotlib/seaborn:
  - Primary data distribution charts
  - Technology integration patterns
  - Correlation analysis charts
  - Summary statistics charts
- **Data Export**: Save results to CSV files in `data/outputs/`
- **Image Export**: Save visualizations to `visualizations/` directory

### 5. Documentation and Reporting
- **Methodology Documentation**: Create comprehensive documentation in `docs/` directory
- **LaTeX Report Generation**: Produce APA-style LaTeX documents in `LaTex/` directory
- **Executive Summary**: Create concise summary documents
- **Cypher Query Documentation**: Document all database queries used

## RQ-Specific Procedures Applied

### RQ4: Geospatial and AI Technology Integration
- **Data Source**: Neo4j database with university-technology relationships
- **Analysis Focus**: University-level technology adoption patterns
- **Key Metrics**: Technology mention counts, adoption rates, university rankings
- **Output**: Technology integration rankings and adoption patterns

### RQ5: SAF Program Type and Technology Correlation
- **Data Source**: Hybrid approach (verified SAF programs + Neo4j technology data)
- **Analysis Focus**: Program type correlation with technology integration
- **Key Metrics**: Program counts by type, technology adoption rates by program type
- **Output**: SAF program type technology correlation analysis

## Standard File Naming Convention
- **Analysis Scripts**: `src/analysis/rq[number]_[description].py`
- **Documentation**: `docs/RQ[number]_[description].md`
- **LaTeX Reports**: `LaTex/RQ[number]_[description].tex`
- **Output Data**: `data/outputs/rq[number]_[description].csv`
- **Visualizations**: `visualizations/rq[number]_[description].png`

## Technology Stack
- **Database**: Neo4j graph database
- **Programming**: Python 3.x
- **Key Libraries**: 
  - `neo4j` (database driver)
  - `pandas` (data manipulation)
  - `matplotlib` (visualization)
  - `seaborn` (enhanced visualization)
- **Documentation**: Markdown, LaTeX
- **Version Control**: Git

## Quality Assurance Steps
1. **Data Validation**: Cross-reference with authoritative sources
2. **Peer Review**: Verify analysis methodology and results
3. **Error Correction**: Address and document any issues found
4. **Consistency Check**: Ensure alignment with previous RQ analyses
5. **Documentation Review**: Verify completeness of all outputs

## Common Pitfalls and Solutions
- **Data Inflation**: Always validate program counts against authoritative sources
- **Missing Data**: Implement robust error handling for incomplete datasets
- **Visualization Errors**: Add checks for edge cases (e.g., zero values)
- **Database Connection Issues**: Implement proper connection management and error handling

## Next Steps for New Chat
When opening a new chat, provide this document and specify:
1. Which RQ to work on next
2. Any specific modifications needed to the standard procedure
3. Current project status and completed RQs
4. Any specific data quality issues or requirements

This will ensure continuity and consistency across chat sessions.
