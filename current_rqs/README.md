# Current Research Questions (RQs) - Organized Structure

This directory contains the most recent and accurate implementations of the research questions for the KG-Perseus project.

## Directory Structure

### RQ8: Program Level and Type Technology Correlation
**Question**: To what extent are drone/GIS/AI topics correlated with the level (undergraduate, master's, or doctoral) and type of academic programs?

**Files**:
- `rq8_program_level_technology_correlation.cypher` - Neo4j Cypher queries
- `rq8_program_level_technology_correlation.py` - Python analysis script
- `RQ8_PROGRAM_LEVEL_TECHNOLOGY_CORRELATION.md` - Complete documentation
- `RQ8_Program_Level_Technology_Correlation_Results.tex` - LaTeX report (APA style)
- `RQ8_COMPLETE_SUMMARY.md` - Executive summary
- `RQ8_Tables_Only.tex` - Tables in LaTeX format

### RQ9: Research Centers and Labs Analysis
**Question**: How many programs are associated with research centers or labs devoted to GIS, AI, Remote Sensing?

**Files**:
- `rq9_research_centers_labs_analysis.cypher` - Neo4j Cypher queries
- `rq9_research_centers_labs_analysis.py` - Python analysis script
- `RQ9_RESEARCH_CENTERS_LABS_ANALYSIS.md` - Complete documentation
- `RQ9_Research_Centers_Labs_Results.tex` - LaTeX report (APA style)
- `RQ9_COMPLETE_SUMMARY.md` - Executive summary
- `RQ9_Tables_Only.tex` - Tables in LaTeX format

### RQ10: Faculty Cross-Department Appointments
**Question**: How many faculty members have appointments (joint or otherwise) with computer science, engineering, or data science departments?

**Files**:
- `rq10_faculty_cross_department_appointments.cypher` - Neo4j Cypher queries
- `rq10_faculty_cross_department_appointments.py` - Python analysis script
- `RQ10_FACULTY_CROSS_DEPARTMENT_APPOINTMENTS.md` - Complete documentation
- `RQ10_Faculty_Cross_Department_Appointments_Results.tex` - LaTeX report (APA style)
- `RQ10_COMPLETE_SUMMARY.md` - Executive summary
- `RQ10_Tables_Only.tex` - Tables in LaTeX format

## Execution Instructions

Each RQ can be executed independently:

1. **Run Cypher Queries**: Execute the `.cypher` files in Neo4j to extract data
2. **Run Python Analysis**: Execute the `.py` files to perform analysis and generate visualizations
3. **Generate Reports**: Use the LaTeX files to compile final reports
4. **Review Results**: Check the generated CSV files and visualizations

## Database Requirements

- Neo4j Graph Database with the KG-Perseus schema
- Faculty, Department, University, Program, Technology, and ResearchArea nodes
- Appropriate relationships between these entities

## Notes

- These are the most recent and accurate implementations
- All files follow the standardized RQ analysis procedure
- Previous versions and experimental scripts have been moved to the `archive/` directory
- Each RQ is self-contained and can be run independently
