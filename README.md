# KG-Perseus: Knowledge Graph Analysis Project

A comprehensive analysis of university programs, faculty, and technology integration using Neo4j graph database and advanced analytics.

## Project Overview

KG-Perseus analyzes the integration of emerging technologies (AI/ML, GIS, Remote Sensing, Drones) in academic programs across universities. The project examines program structures, faculty expertise, research infrastructure, and cross-department collaboration patterns.

## Current Research Questions (RQs)

### RQ8: Program Level and Type Technology Correlation
**Question**: To what extent are drone/GIS/AI topics correlated with the level (undergraduate, master's, or doctoral) and type of academic programs?

### RQ9: Research Centers and Labs Analysis  
**Question**: How many programs are associated with research centers or labs devoted to GIS, AI, Remote Sensing?

### RQ10: Faculty Cross-Department Appointments
**Question**: How many faculty members have appointments (joint or otherwise) with computer science, engineering, or data science departments?

## Project Structure

```
KG-perseus/
├── current_rqs/           # Current research question implementations
│   ├── rq8/              # RQ8: Program Level Technology Correlation
│   ├── rq9/              # RQ9: Research Centers and Labs
│   └── rq10/             # RQ10: Faculty Cross-Department Appointments
├── src/                   # Source code
│   ├── analysis/         # Current RQ analysis scripts
│   ├── data_processing/  # Data processing utilities
│   ├── database/         # Database interaction scripts
│   └── utils/            # Utility functions
├── data/                  # Data files
│   ├── outputs/          # Current RQ Cypher queries
│   ├── processed/        # Processed data files
│   └── raw/              # Raw data files
├── docs/                  # Documentation
│   ├── current_rqs/      # Current RQ documentation
│   └── university-profiles/ # University profile data
├── LaTex/                 # LaTeX reports
│   └── current_rqs/      # Current RQ LaTeX files
├── archive/               # Archived files and previous versions
├── config/                # Configuration files
├── requirements.txt       # Python dependencies
└── setup.py              # Project setup
```

## Quick Start

### Prerequisites
- Python 3.8+
- Neo4j Database
- Required Python packages (see requirements.txt)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd KG-perseus

# Install dependencies
pip install -r requirements.txt

# Configure database connection
cp .env.example .env
# Edit .env with your Neo4j credentials
```

### Running Analysis
Each RQ can be executed independently:

```bash
# RQ8: Program Level Technology Correlation
python src/analysis/rq8_program_level_technology_correlation.py

# RQ9: Research Centers and Labs
python src/analysis/rq9_research_centers_labs_analysis.py

# RQ10: Faculty Cross-Department Appointments
python src/analysis/rq10_faculty_cross_department_appointments.py
```

## Database Schema

The project uses a Neo4j graph database with the following main entities:
- **University**: Higher education institutions
- **Program**: Academic programs and degrees
- **Faculty**: Academic staff members
- **Department**: Academic departments
- **Technology**: Technologies and tools
- **ResearchArea**: Research domains and specializations

## Key Relationships
- `[:OFFERS]` - University offers Program
- `[:APPOINTED_TO]` - Faculty appointed to Department
- `[:USES_TECHNOLOGY]` - Program/Department uses Technology
- `[:HAS_RESEARCH_AREA]` - Faculty/Department has Research Area
- `[:HAS]` - University has Department

## Outputs

Each RQ generates:
- **Cypher Queries**: Data extraction scripts
- **Python Analysis**: Comprehensive analysis scripts
- **Documentation**: Detailed methodology and results
- **LaTeX Reports**: Publication-ready reports in APA style
- **Data Files**: CSV exports and visualizations

## Archive

Previous versions and experimental files are stored in the `archive/` directory:
- `old_analysis_scripts/` - Previous analysis implementations
- `old_latex_files/` - Previous LaTeX reports
- `old_docs/` - Previous documentation
- `old_data_outputs/` - Previous data outputs
- `old_uml_files/` - Previous UML models
- `old_visualization_scripts/` - Previous visualization scripts

## Contributing

1. Follow the established RQ analysis procedure
2. Maintain consistent file naming conventions
3. Update documentation for any changes
4. Archive old versions before major updates

## License

[Add your license information here]

## Contact

[Add your contact information here]
