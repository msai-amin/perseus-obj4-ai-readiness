#!/usr/bin/env python3
"""
Updated Course Queries for Corrected University Hierarchy
Provides accurate queries that reflect the proper hierarchy: University -> Departments -> Programs
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

class UpdatedCourseQueries:
    """Updated queries that reflect the corrected university hierarchy."""
    
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
    
    def get_corrected_hierarchy_queries(self) -> Dict[str, str]:
        """Get queries that reflect the corrected hierarchy."""
        
        queries = {
            'total_universities': """
                MATCH (u:University)
                RETURN count(u) as total_universities
            """,
            
            'universities_with_departments': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)
                RETURN count(DISTINCT u) as universities_with_departments
            """,
            
            'universities_with_programs': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                RETURN count(DISTINCT u) as universities_with_programs
            """,
            
            'ai_ml_universities': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'ai'
                   OR toLower(p.description) CONTAINS 'ml'
                RETURN count(DISTINCT u) as universities_with_ai_ml
            """,
            
            'gis_universities': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'geographic information'
                   OR toLower(p.description) CONTAINS 'geospatial'
                   OR toLower(p.description) CONTAINS 'spatial analysis'
                RETURN count(DISTINCT u) as universities_with_gis
            """,
            
            'drone_uav_universities': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'uav'
                   OR toLower(p.description) CONTAINS 'unmanned aerial'
                   OR toLower(p.description) CONTAINS 'aerial'
                RETURN count(DISTINCT u) as universities_with_drones
            """,
            
            'remote_sensing_universities': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'remote sensing'
                   OR toLower(p.description) CONTAINS 'satellite imagery'
                   OR toLower(p.description) CONTAINS 'aerial imagery'
                RETURN count(DISTINCT u) as universities_with_remote_sensing
            """,
            
            'detailed_university_programs': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'remote sensing'
                   OR toLower(p.description) CONTAINS 'ai'
                   OR toLower(p.description) CONTAINS 'ml'
                RETURN u.name as university_name,
                       d.name as department_name,
                       p.name as program_name,
                       p.description as program_description
                ORDER BY u.name, d.name, p.name
            """,
            
            'technology_departments': """
                MATCH (d:Department)
                WHERE toLower(d.description) CONTAINS 'artificial intelligence' 
                   OR toLower(d.description) CONTAINS 'machine learning'
                   OR toLower(d.description) CONTAINS 'data science'
                   OR toLower(d.description) CONTAINS 'gis'
                   OR toLower(d.description) CONTAINS 'computer science'
                   OR toLower(d.description) CONTAINS 'computing'
                   OR toLower(d.description) CONTAINS 'geospatial'
                RETURN d.name as department_name,
                       d.description as department_description
                ORDER BY d.name
            """,
            
            'university_hierarchy_summary': """
                MATCH (u:University)
                OPTIONAL MATCH (u)-[:LOCATED_IN]->(d:Department)
                OPTIONAL MATCH (d)-[:OFFERS]->(p:Program)
                RETURN u.name as university_name,
                       count(DISTINCT d) as department_count,
                       count(DISTINCT p) as program_count
                ORDER BY university_name
            """,
            
            'technology_program_breakdown': """
                MATCH (u:University)-[:LOCATED_IN]->(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'remote sensing'
                WITH u.name as university_name, count(p) as tech_programs
                RETURN university_name, tech_programs
                ORDER BY tech_programs DESC
            """
        }
        
        return queries
    
    def execute_hierarchy_analysis(self) -> Dict[str, Any]:
        """Execute comprehensive hierarchy analysis."""
        logger.info("Executing hierarchy analysis...")
        
        queries = self.get_corrected_hierarchy_queries()
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
    
    def calculate_accurate_proportions(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate accurate proportions based on corrected hierarchy."""
        logger.info("Calculating accurate proportions...")
        
        proportions = {}
        
        # Get total universities
        total_universities = 0
        if 'total_universities' in results and results['total_universities']:
            total_universities = results['total_universities'][0].get('total_universities', 0)
        
        # Calculate proportions for each technology
        technology_queries = {
            'AI_ML': 'ai_ml_universities',
            'GIS': 'gis_universities',
            'Drones_UAV': 'drone_uav_universities',
            'Remote_Sensing': 'remote_sensing_universities'
        }
        
        for tech_name, query_name in technology_queries.items():
            if query_name in results and results[query_name]:
                universities_count = results[query_name][0].get(f'universities_with_{query_name.split("_")[0]}', 0)
                proportion = (universities_count / total_universities * 100) if total_universities > 0 else 0
                
                proportions[tech_name] = {
                    'universities_offering': universities_count,
                    'total_universities': total_universities,
                    'proportion_percentage': proportion
                }
        
        return proportions
    
    def generate_detailed_report(self, results: Dict[str, List[Dict]], proportions: Dict[str, Any]) -> str:
        """Generate detailed report with corrected hierarchy data."""
        
        report_lines = [
            "# Updated University Course Proportions Report",
            "",
            "## Corrected Hierarchy Analysis",
            "",
            "### Database Overview",
            f"- Total Universities: {results.get('total_universities', [{}])[0].get('total_universities', 0)}",
            f"- Universities with Departments: {results.get('universities_with_departments', [{}])[0].get('universities_with_departments', 0)}",
            f"- Universities with Programs: {results.get('universities_with_programs', [{}])[0].get('universities_with_programs', 0)}",
            "",
            "### Technology Course Proportions (Corrected)",
            ""
        ]
        
        # Add proportions table
        report_lines.extend([
            "| Technology | Universities Offering | Total Universities | Proportion |",
            "|------------|---------------------|-------------------|------------|"
        ])
        
        for tech_name, data in proportions.items():
            tech_display = tech_name.replace('_', ' ').title()
            universities = data['universities_offering']
            total = data['total_universities']
            proportion = data['proportion_percentage']
            report_lines.append(f"| {tech_display} | {universities} | {total} | {proportion:.1f}% |")
        
        # Add detailed program breakdown
        if 'detailed_university_programs' in results:
            report_lines.extend([
                "",
                "### Detailed University Programs",
                ""
            ])
            
            for i, program in enumerate(results['detailed_university_programs'][:20]):  # Show first 20
                report_lines.append(
                    f"{i+1}. **{program.get('university_name', 'Unknown')}** - "
                    f"{program.get('department_name', 'Unknown')} - "
                    f"{program.get('program_name', 'Unknown')}"
                )
            
            if len(results['detailed_university_programs']) > 20:
                report_lines.append(f"... and {len(results['detailed_university_programs']) - 20} more programs")
        
        # Add technology department breakdown
        if 'technology_departments' in results:
            report_lines.extend([
                "",
                "### Technology-Focused Departments",
                ""
            ])
            
            for dept in results['technology_departments'][:10]:  # Show first 10
                report_lines.append(f"- **{dept.get('department_name', 'Unknown')}**")
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], proportions: Dict[str, Any], output_dir: Path = None):
        """Save analysis results to files."""
        if output_dir is None:
            output_dir = Path('data/outputs')
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive results
        with open(output_dir / 'corrected_hierarchy_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save proportions as CSV
        proportions_data = []
        for category, data in proportions.items():
            proportions_data.append({
                'Technology_Category': category,
                'Universities_Offering': data['universities_offering'],
                'Total_Universities': data['total_universities'],
                'Proportion_Percentage': data['proportion_percentage']
            })
        
        if proportions_data:
            df_proportions = pd.DataFrame(proportions_data)
            df_proportions.to_csv(output_dir / 'corrected_technology_proportions.csv', index=False)
        
        # Save detailed program data
        if 'detailed_university_programs' in results:
            program_data = []
            for program in results['detailed_university_programs']:
                program_data.append({
                    'University': program.get('university_name', 'Unknown'),
                    'Department': program.get('department_name', 'Unknown'),
                    'Program': program.get('program_name', 'Unknown'),
                    'Description': program.get('program_description', 'Unknown')
                })
            
            df_programs = pd.DataFrame(program_data)
            df_programs.to_csv(output_dir / 'corrected_university_programs.csv', index=False)
        
        # Save queries
        queries = self.get_corrected_hierarchy_queries()
        with open(output_dir / 'corrected_hierarchy_queries.cypher', 'w') as f:
            f.write("-- Corrected Hierarchy Queries for University Course Analysis\n")
            f.write("-- Generated by UpdatedCourseQueries\n\n")
            
            for query_name, query in queries.items():
                f.write(f"-- {query_name}\n")
                f.write(query.strip() + "\n\n")
        
        logger.info(f"Results saved to {output_dir}")
    
    def print_summary(self, results: Dict[str, List[Dict]], proportions: Dict[str, Any]):
        """Print a summary of the corrected analysis."""
        print("\n" + "="*80)
        print("CORRECTED UNIVERSITY HIERARCHY ANALYSIS")
        print("="*80)
        
        # Database overview
        total_universities = results.get('total_universities', [{}])[0].get('total_universities', 0)
        universities_with_departments = results.get('universities_with_departments', [{}])[0].get('universities_with_departments', 0)
        universities_with_programs = results.get('universities_with_programs', [{}])[0].get('universities_with_programs', 0)
        
        print(f"\n📊 DATABASE OVERVIEW:")
        print(f"   • Total Universities: {total_universities}")
        print(f"   • Universities with Departments: {universities_with_departments}")
        print(f"   • Universities with Programs: {universities_with_programs}")
        
        # Technology proportions
        print(f"\n🎯 TECHNOLOGY COURSE PROPORTIONS (CORRECTED):")
        print(f"   {'Technology':<20} {'Universities':<15} {'Proportion':<15}")
        print(f"   {'-'*20} {'-'*15} {'-'*15}")
        
        for category, data in proportions.items():
            category_name = category.replace('_', ' ').title()
            universities = data['universities_offering']
            proportion = data['proportion_percentage']
            print(f"   {category_name:<20} {universities:<15} {proportion:>6.1f}%")
        
        # Detailed program count
        if 'detailed_university_programs' in results:
            program_count = len(results['detailed_university_programs'])
            print(f"\n📚 DETAILED PROGRAMS:")
            print(f"   • Technology Programs Found: {program_count}")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection."""
        self.driver.close()

def main():
    """Main execution function."""
    try:
        logger.info("Starting corrected hierarchy analysis...")
        
        # Initialize analyzer
        analyzer = UpdatedCourseQueries()
        
        # Execute analysis
        results = analyzer.execute_hierarchy_analysis()
        
        # Calculate proportions
        proportions = analyzer.calculate_accurate_proportions(results)
        
        # Generate report
        report = analyzer.generate_detailed_report(results, proportions)
        
        # Save results
        analyzer.save_results(results, proportions)
        
        # Print summary
        analyzer.print_summary(results, proportions)
        
        # Save report
        output_dir = Path('data/outputs')
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / 'corrected_hierarchy_report.md', 'w') as f:
            f.write(report)
        
        logger.info("Corrected hierarchy analysis completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Corrected hierarchy analysis failed: {e}")
        return 1
    
    finally:
        if 'analyzer' in locals():
            analyzer.close()

if __name__ == "__main__":
    sys.exit(main()) 