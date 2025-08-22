#!/usr/bin/env python3
"""
Program Level Technology Adoption Analysis
Analyzes how technology adoption patterns vary by program level (undergraduate vs. graduate)
"""

import pandas as pd
import json
from neo4j import GraphDatabase
from typing import Dict, List, Any, Tuple
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProgramLevelAnalysis:
    """Analyze technology adoption patterns by program level."""
    
    def __init__(self, uri: str = "bolt://localhost:7689", 
                 username: str = "neo4j", 
                 password: str = "perseus2025"):
        """Initialize with database connection."""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.results = {}
        
        # Technology categories for analysis
        self.technology_categories = {
            'AI_ML': [
                'artificial intelligence', 'ai', 'machine learning', 'ml', 
                'deep learning', 'neural networks', 'data science', 'predictive analytics',
                'computer vision', 'natural language processing', 'nlp'
            ],
            'GIS': [
                'geographic information systems', 'gis', 'geospatial', 'spatial analysis',
                'cartography', 'mapping', 'remote sensing', 'satellite imagery'
            ],
            'Drones_UAV': [
                'drone', 'uav', 'unmanned aerial vehicle', 'aerial photography',
                'drone technology', 'uav applications', 'aerial mapping'
            ],
            'Remote_Sensing': [
                'remote sensing', 'satellite imagery', 'aerial imagery', 'sensor data',
                'image processing', 'spectral analysis', 'multispectral'
            ],
            'Data_Analytics': [
                'data analytics', 'statistical analysis', 'big data', 'data mining',
                'business intelligence', 'analytics', 'data visualization'
            ]
        }
    
    def run_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a Cypher query and return results."""
        try:
            with self.driver.session() as session:
                if parameters:
                    result = session.run(query, parameters)
                else:
                    result = session.run(query)
                return result.data()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def get_program_level_queries(self) -> Dict[str, str]:
        """Get queries for program level analysis."""
        
        queries = {
            'total_programs_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE p.name IS NOT NULL
                WITH p.name as program_name, 
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level
                RETURN program_level, count(program_name) as program_count
                ORDER BY program_level
            """,
            
            'ai_ml_programs_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'ai'
                   OR toLower(p.description) CONTAINS 'ml')
                WITH p.name as program_name, p.description as description,
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level
                RETURN program_level, count(program_name) as ai_ml_programs
                ORDER BY program_level
            """,
            
            'gis_programs_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'geographic information'
                   OR toLower(p.description) CONTAINS 'geospatial'
                   OR toLower(p.description) CONTAINS 'spatial analysis')
                WITH p.name as program_name, p.description as description,
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level
                RETURN program_level, count(program_name) as gis_programs
                ORDER BY program_level
            """,
            
            'drone_programs_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'uav'
                   OR toLower(p.description) CONTAINS 'unmanned aerial'
                   OR toLower(p.description) CONTAINS 'aerial')
                WITH p.name as program_name, p.description as description,
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level
                RETURN program_level, count(program_name) as drone_programs
                ORDER BY program_level
            """,
            
            'remote_sensing_programs_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'remote sensing'
                   OR toLower(p.description) CONTAINS 'satellite imagery'
                   OR toLower(p.description) CONTAINS 'aerial imagery')
                WITH p.name as program_name, p.description as description,
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level
                RETURN program_level, count(program_name) as remote_sensing_programs
                ORDER BY program_level
            """,
            
            'detailed_programs_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'ai'
                   OR toLower(p.description) CONTAINS 'ml'
                   OR toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'geographic information'
                   OR toLower(p.description) CONTAINS 'geospatial'
                   OR toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'uav'
                   OR toLower(p.description) CONTAINS 'remote sensing')
                WITH u.name as university_name, d.name as department_name, p.name as program_name, p.description as description,
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level
                RETURN university_name, department_name, program_name, program_level, description
                ORDER BY university_name, program_level, program_name
            """,
            
            'universities_with_undergraduate_tech': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'ai'
                   OR toLower(p.description) CONTAINS 'ml'
                   OR toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'geographic information'
                   OR toLower(p.description) CONTAINS 'geospatial'
                   OR toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'uav'
                   OR toLower(p.description) CONTAINS 'remote sensing')
                AND (toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate')
                RETURN count(DISTINCT u) as universities_with_undergraduate_tech
            """,
            
            'universities_with_graduate_tech': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE (toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'ai'
                   OR toLower(p.description) CONTAINS 'ml'
                   OR toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'geographic information'
                   OR toLower(p.description) CONTAINS 'geospatial'
                   OR toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'uav'
                   OR toLower(p.description) CONTAINS 'remote sensing')
                AND (toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral')
                RETURN count(DISTINCT u) as universities_with_graduate_tech
            """,
            
            'technology_breakdown_by_level': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE p.name IS NOT NULL
                WITH p.name as program_name, p.description as description,
                     CASE 
                         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' THEN 'Undergraduate'
                         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR toLower(p.name) CONTAINS 'graduate' THEN 'Graduate'
                         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' THEN 'Graduate'
                         ELSE 'Other'
                     END as program_level,
                     CASE 
                         WHEN toLower(description) CONTAINS 'artificial intelligence' OR toLower(description) CONTAINS 'machine learning' OR toLower(description) CONTAINS 'ai' OR toLower(description) CONTAINS 'ml' THEN 'AI_ML'
                         WHEN toLower(description) CONTAINS 'gis' OR toLower(description) CONTAINS 'geographic information' OR toLower(description) CONTAINS 'geospatial' THEN 'GIS'
                         WHEN toLower(description) CONTAINS 'drone' OR toLower(description) CONTAINS 'uav' OR toLower(description) CONTAINS 'unmanned aerial' THEN 'Drones_UAV'
                         WHEN toLower(description) CONTAINS 'remote sensing' OR toLower(description) CONTAINS 'satellite imagery' THEN 'Remote_Sensing'
                         ELSE 'Other'
                     END as technology_category
                WHERE technology_category <> 'Other'
                RETURN program_level, technology_category, count(program_name) as program_count
                ORDER BY program_level, technology_category
            """
        }
        
        return queries
    
    def execute_program_level_analysis(self) -> Dict[str, Any]:
        """Execute comprehensive program level analysis."""
        logger.info("Executing program level analysis...")
        
        queries = self.get_program_level_queries()
        results = {}
        
        for query_name, query in queries.items():
            try:
                result = self.run_query(query)
                results[query_name] = result
                logger.info(f"Executed {query_name}: {len(result)} results")
            except Exception as e:
                logger.error(f"Error executing {query_name}: {e}")
                results[query_name] = []
        
        return results
    
    def calculate_program_level_proportions(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate proportions by program level."""
        logger.info("Calculating program level proportions...")
        
        proportions = {}
        
        # Get total programs by level
        total_programs_by_level = {}
        if 'total_programs_by_level' in results:
            for row in results['total_programs_by_level']:
                level = row.get('program_level', 'Unknown')
                count = row.get('program_count', 0)
                total_programs_by_level[level] = count
        
        # Calculate technology proportions by level
        technology_queries = {
            'AI_ML': 'ai_ml_programs_by_level',
            'GIS': 'gis_programs_by_level',
            'Drones_UAV': 'drone_programs_by_level',
            'Remote_Sensing': 'remote_sensing_programs_by_level'
        }
        
        for tech_name, query_name in technology_queries.items():
            if query_name in results:
                tech_proportions = {}
                for row in results[query_name]:
                    level = row.get('program_level', 'Unknown')
                    tech_count = row.get(f'{query_name.split("_")[0]}_programs', 0)
                    total_count = total_programs_by_level.get(level, 0)
                    
                    if total_count > 0:
                        proportion = (tech_count / total_count) * 100
                    else:
                        proportion = 0
                    
                    tech_proportions[level] = {
                        'technology_programs': tech_count,
                        'total_programs': total_count,
                        'proportion_percentage': proportion
                    }
                
                proportions[tech_name] = tech_proportions
        
        return proportions
    
    def generate_program_level_report(self, results: Dict[str, List[Dict]], proportions: Dict[str, Any]) -> str:
        """Generate comprehensive program level report."""
        
        report_lines = [
            "# Program Level Technology Adoption Analysis",
            "",
            "## Research Question",
            "How do adoption patterns vary by program level (undergraduate vs. graduate)?",
            "",
            "## Database Overview",
            ""
        ]
        
        # Add total programs by level
        if 'total_programs_by_level' in results:
            report_lines.append("### Total Programs by Level")
            report_lines.append("")
            for row in results['total_programs_by_level']:
                level = row.get('program_level', 'Unknown')
                count = row.get('program_count', 0)
                report_lines.append(f"- **{level}**: {count} programs")
            report_lines.append("")
        
        # Add technology breakdown by level
        if 'technology_breakdown_by_level' in results:
            report_lines.append("### Technology Programs by Level")
            report_lines.append("")
            report_lines.append("| Program Level | Technology | Program Count |")
            report_lines.append("|---------------|------------|---------------|")
            
            for row in results['technology_breakdown_by_level']:
                level = row.get('program_level', 'Unknown')
                tech = row.get('technology_category', 'Unknown')
                count = row.get('program_count', 0)
                report_lines.append(f"| {level} | {tech} | {count} |")
            report_lines.append("")
        
        # Add proportions analysis
        report_lines.append("### Technology Adoption Proportions by Program Level")
        report_lines.append("")
        
        for tech_name, level_data in proportions.items():
            report_lines.append(f"#### {tech_name.replace('_', ' ')}")
            report_lines.append("")
            for level, data in level_data.items():
                tech_programs = data['technology_programs']
                total_programs = data['total_programs']
                proportion = data['proportion_percentage']
                report_lines.append(f"- **{level}**: {tech_programs} programs out of {total_programs} total ({proportion:.1f}%)")
            report_lines.append("")
        
        # Add detailed program analysis
        if 'detailed_programs_by_level' in results:
            report_lines.append("### Detailed Program Analysis by Level")
            report_lines.append("")
            
            # Group by program level
            programs_by_level = {}
            for row in results['detailed_programs_by_level']:
                level = row.get('program_level', 'Unknown')
                if level not in programs_by_level:
                    programs_by_level[level] = []
                programs_by_level[level].append(row)
            
            for level, programs in programs_by_level.items():
                report_lines.append(f"#### {level} Programs")
                report_lines.append("")
                for i, program in enumerate(programs[:10]):  # Show first 10
                    university = program.get('university_name', 'Unknown')
                    department = program.get('department_name', 'Unknown')
                    program_name = program.get('program_name', 'Unknown')
                    report_lines.append(f"{i+1}. **{university}** - {department} - {program_name}")
                
                if len(programs) > 10:
                    report_lines.append(f"... and {len(programs) - 10} more programs")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], proportions: Dict[str, Any], output_dir: Path = None):
        """Save analysis results to files."""
        if output_dir is None:
            output_dir = Path('data/outputs')
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive results
        with open(output_dir / 'program_level_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save proportions as CSV
        proportions_data = []
        for tech_name, level_data in proportions.items():
            for level, data in level_data.items():
                proportions_data.append({
                    'Technology_Category': tech_name,
                    'Program_Level': level,
                    'Technology_Programs': data['technology_programs'],
                    'Total_Programs': data['total_programs'],
                    'Proportion_Percentage': data['proportion_percentage']
                })
        
        if proportions_data:
            df_proportions = pd.DataFrame(proportions_data)
            df_proportions.to_csv(output_dir / 'program_level_proportions.csv', index=False)
        
        # Save detailed program data
        if 'detailed_programs_by_level' in results:
            program_data = []
            for program in results['detailed_programs_by_level']:
                program_data.append({
                    'University': program.get('university_name', 'Unknown'),
                    'Department': program.get('department_name', 'Unknown'),
                    'Program': program.get('program_name', 'Unknown'),
                    'Program_Level': program.get('program_level', 'Unknown'),
                    'Description': program.get('description', 'Unknown')
                })
            
            df_programs = pd.DataFrame(program_data)
            df_programs.to_csv(output_dir / 'program_level_detailed_programs.csv', index=False)
        
        # Save queries
        queries = self.get_program_level_queries()
        with open(output_dir / 'program_level_queries.cypher', 'w') as f:
            f.write("-- Program Level Technology Adoption Queries\n")
            f.write("-- Generated by ProgramLevelAnalysis\n\n")
            
            for query_name, query in queries.items():
                f.write(f"-- {query_name}\n")
                f.write(query.strip() + "\n\n")
        
        logger.info(f"Results saved to {output_dir}")
    
    def print_summary(self, results: Dict[str, List[Dict]], proportions: Dict[str, Any]):
        """Print a summary of the program level analysis."""
        print("\n" + "="*80)
        print("PROGRAM LEVEL TECHNOLOGY ADOPTION ANALYSIS")
        print("="*80)
        
        # Total programs by level
        if 'total_programs_by_level' in results:
            print(f"\n📊 TOTAL PROGRAMS BY LEVEL:")
            for row in results['total_programs_by_level']:
                level = row.get('program_level', 'Unknown')
                count = row.get('program_count', 0)
                print(f"   • {level}: {count} programs")
        
        # Technology breakdown
        if 'technology_breakdown_by_level' in results:
            print(f"\n🎯 TECHNOLOGY PROGRAMS BY LEVEL:")
            for row in results['technology_breakdown_by_level']:
                level = row.get('program_level', 'Unknown')
                tech = row.get('technology_category', 'Unknown')
                count = row.get('program_count', 0)
                print(f"   • {level} - {tech}: {count} programs")
        
        # Proportions summary
        print(f"\n📈 ADOPTION PROPORTIONS BY PROGRAM LEVEL:")
        for tech_name, level_data in proportions.items():
            tech_display = tech_name.replace('_', ' ').title()
            print(f"   {tech_display}:")
            for level, data in level_data.items():
                proportion = data['proportion_percentage']
                tech_programs = data['technology_programs']
                total_programs = data['total_programs']
                print(f"     • {level}: {proportion:.1f}% ({tech_programs}/{total_programs})")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection."""
        self.driver.close()

def main():
    """Main execution function."""
    try:
        logger.info("Starting program level analysis...")
        
        # Initialize analyzer
        analyzer = ProgramLevelAnalysis()
        
        # Execute analysis
        results = analyzer.execute_program_level_analysis()
        
        # Calculate proportions
        proportions = analyzer.calculate_program_level_proportions(results)
        
        # Generate report
        report = analyzer.generate_program_level_report(results, proportions)
        
        # Save results
        analyzer.save_results(results, proportions)
        
        # Print summary
        analyzer.print_summary(results, proportions)
        
        # Save report
        output_dir = Path('data/outputs')
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / 'program_level_analysis_report.md', 'w') as f:
            f.write(report)
        
        logger.info("Program level analysis completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Program level analysis failed: {e}")
        return 1
    
    finally:
        if 'analyzer' in locals():
            analyzer.close()

if __name__ == "__main__":
    sys.exit(main()) 