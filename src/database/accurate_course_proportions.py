#!/usr/bin/env python3
"""
Accurate Course Proportions Analysis
Uses existing processed data to calculate the most accurate proportions of universities 
offering courses in AI, GIS, and other technologies.
"""

import pandas as pd
import json
from pathlib import Path
import logging
from typing import Dict, List, Any
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccurateCourseProportions:
    """Calculate accurate proportions of universities offering technology courses."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize with data directory."""
        self.data_dir = data_dir or Path('data/processed')
        self.results = {}
        
        # Technology categories for analysis
        self.technology_categories = {
            'AI_ML': ['artificial intelligence', 'ai', 'machine learning', 'ml', 'data science'],
            'GIS': ['gis', 'geographic information', 'geospatial', 'spatial analysis'],
            'Drones_UAV': ['drone', 'uav', 'unmanned aerial', 'aerial'],
            'Remote_Sensing': ['remote sensing', 'satellite imagery', 'aerial imagery'],
            'Data_Analytics': ['data analytics', 'statistical analysis', 'big data']
        }
    
    def load_existing_data(self) -> Dict[str, pd.DataFrame]:
        """Load existing processed data files."""
        logger.info("Loading existing processed data...")
        
        data_files = {
            'ai_course_analysis': 'ai_course_analysis.csv',
            'ai_course_adoption': 'ai_course_adoption_comprehensive_summary.csv',
            'program_level_breakdown': 'AI_Course_Program_Level_Breakdown.csv',
            'technology_breakdown': 'technology_breakdown_table.csv',
            'university_stats': 'university_statistics_table.csv'
        }
        
        loaded_data = {}
        for name, filename in data_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    loaded_data[name] = pd.read_csv(file_path)
                    logger.info(f"Loaded {name}: {len(loaded_data[name])} rows")
                except Exception as e:
                    logger.warning(f"Could not load {filename}: {e}")
            else:
                logger.warning(f"File not found: {filename}")
        
        return loaded_data
    
    def analyze_ai_course_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze AI course adoption data."""
        logger.info("Analyzing AI course data...")
        
        if data.empty:
            return {}
        
        # Get unique universities
        universities = data['University'].unique()
        total_universities = len(universities)
        
        # Count universities with AI courses
        universities_with_ai = data['University'].nunique()
        
        # Analyze by technology type
        technology_counts = {}
        for tech in ['AI', 'ML', 'Data Science', 'GIS', 'Remote Sensing']:
            tech_data = data[data['Course_Name'].str.contains(tech, case=False, na=False)]
            technology_counts[tech] = {
                'universities': tech_data['University'].nunique(),
                'courses': len(tech_data),
                'proportion': tech_data['University'].nunique() / total_universities * 100
            }
        
        return {
            'total_universities': total_universities,
            'universities_with_ai_courses': universities_with_ai,
            'ai_adoption_rate': universities_with_ai / total_universities * 100,
            'technology_breakdown': technology_counts,
            'universities_list': list(universities)
        }
    
    def analyze_program_level_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze program-level technology adoption."""
        logger.info("Analyzing program-level data...")
        
        if data.empty:
            return {}
        
        # Get total programs
        total_programs = int(data['Total Programs'].sum())
        
        # Analyze by program level
        level_analysis = {}
        for _, row in data.iterrows():
            level = row['Type']
            level_analysis[level] = {
                'count': int(row['Total Programs']),
                'ai_ml_programs': int(row['AI/ML Programs']),
                'gis_programs': int(row['GIS Programs']),
                'uav_drone_programs': int(row['UAV/Drone Programs']),
                'remote_sensing_programs': int(row['Remote Sensing Programs']),
                'any_technology_programs': int(row['Any Technology']),
                'ai_ml_percentage': float(row['AI/ML %']),
                'gis_percentage': float(row['GIS %']),
                'uav_drone_percentage': float(row['UAV/Drone %']),
                'remote_sensing_percentage': float(row['Remote Sensing %']),
                'any_technology_percentage': float(row['Any Technology %'])
            }
        
        # Overall technology adoption
        total_tech_programs = int(data['Any Technology'].sum())
        overall_adoption = total_tech_programs / total_programs * 100 if total_programs > 0 else 0
        
        return {
            'total_programs': total_programs,
            'technology_programs': total_tech_programs,
            'overall_adoption_rate': overall_adoption,
            'level_breakdown': level_analysis
        }
    
    def analyze_university_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze university-level statistics."""
        logger.info("Analyzing university statistics...")
        
        if data.empty:
            return {}
        
        # Extract statistics from the summary table
        stats = {}
        for _, row in data.iterrows():
            metric = row['Metric']
            count = int(row['Count'])  # Convert to Python int
            percentage = float(row['Percentage'])  # Convert to Python float
            
            if 'Total Universities' in metric:
                stats['total_universities'] = count
            elif 'Universities with Technology Courses' in metric:
                stats['universities_with_tech_courses'] = count
                stats['proportion_with_tech_courses'] = percentage
            elif 'Universities with AI/ML Courses' in metric:
                stats['universities_with_ai_ml'] = count
                stats['proportion_with_ai_ml'] = percentage
            elif 'Universities with GIS Courses' in metric:
                stats['universities_with_gis'] = count
                stats['proportion_with_gis'] = percentage
            elif 'Universities with Data Science Courses' in metric:
                stats['universities_with_data_science'] = count
                stats['proportion_with_data_science'] = percentage
            elif 'Universities with Remote Sensing Courses' in metric:
                stats['universities_with_remote_sensing'] = count
                stats['proportion_with_remote_sensing'] = percentage
            elif 'Universities with Drone/UAV Courses' in metric:
                stats['universities_with_drone_uav'] = count
                stats['proportion_with_drone_uav'] = percentage
        
        return stats
    
    def calculate_comprehensive_proportions(self, loaded_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate comprehensive proportions from all available data."""
        logger.info("Calculating comprehensive proportions...")
        
        results = {}
        
        # Analyze AI course data
        if 'ai_course_analysis' in loaded_data:
            results['ai_course_analysis'] = self.analyze_ai_course_data(loaded_data['ai_course_analysis'])
        
        # Analyze program level data
        if 'program_level_breakdown' in loaded_data:
            results['program_level_analysis'] = self.analyze_program_level_data(loaded_data['program_level_breakdown'])
        
        # Analyze university statistics
        if 'university_stats' in loaded_data:
            results['university_analysis'] = self.analyze_university_statistics(loaded_data['university_stats'])
        
        # Calculate overall proportions
        overall_proportions = {}
        
        # AI/ML proportion
        if 'ai_course_analysis' in results:
            ai_data = results['ai_course_analysis']
            overall_proportions['AI_ML'] = {
                'universities_offering': ai_data['universities_with_ai_courses'],
                'total_universities': ai_data['total_universities'],
                'proportion_percentage': ai_data['ai_adoption_rate']
            }
        
        # Technology programs proportion
        if 'university_analysis' in results:
            univ_data = results['university_analysis']
            overall_proportions['Technology_Courses'] = {
                'universities_offering': univ_data['universities_with_tech_courses'],
                'total_universities': univ_data['total_universities'],
                'proportion_percentage': univ_data['proportion_with_tech_courses']
            }
            overall_proportions['AI_ML_Courses'] = {
                'universities_offering': univ_data['universities_with_ai_ml'],
                'total_universities': univ_data['total_universities'],
                'proportion_percentage': univ_data['proportion_with_ai_ml']
            }
            overall_proportions['GIS_Courses'] = {
                'universities_offering': univ_data['universities_with_gis'],
                'total_universities': univ_data['total_universities'],
                'proportion_percentage': univ_data['proportion_with_gis']
            }
            overall_proportions['Data_Science_Courses'] = {
                'universities_offering': univ_data['universities_with_data_science'],
                'total_universities': univ_data['total_universities'],
                'proportion_percentage': univ_data['proportion_with_data_science']
            }
            overall_proportions['Remote_Sensing_Courses'] = {
                'universities_offering': univ_data['universities_with_remote_sensing'],
                'total_universities': univ_data['total_universities'],
                'proportion_percentage': univ_data['proportion_with_remote_sensing']
            }
            overall_proportions['Drone_UAV_Courses'] = {
                'universities_offering': univ_data['universities_with_drone_uav'],
                'total_universities': univ_data['total_universities'],
                'proportion_percentage': univ_data['proportion_with_drone_uav']
            }
        
        results['overall_proportions'] = overall_proportions
        
        return results
    
    def generate_detailed_queries(self) -> Dict[str, str]:
        """Generate explicit Cypher queries for database analysis."""
        logger.info("Generating explicit Cypher queries...")
        
        queries = {
            'total_universities': """
                MATCH (u:University)
                RETURN count(u) as total_universities
            """,
            
            'universities_with_ai_courses': """
                MATCH (u:University)-[:LOCATED_IN]-(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'ai'
                RETURN count(DISTINCT u) as universities_with_ai
            """,
            
            'universities_with_gis_courses': """
                MATCH (u:University)-[:LOCATED_IN]-(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'geographic information'
                   OR toLower(p.description) CONTAINS 'geospatial'
                RETURN count(DISTINCT u) as universities_with_gis
            """,
            
            'universities_with_drone_courses': """
                MATCH (u:University)-[:LOCATED_IN]-(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'uav'
                   OR toLower(p.description) CONTAINS 'unmanned aerial'
                RETURN count(DISTINCT u) as universities_with_drones
            """,
            
            'universities_with_remote_sensing': """
                MATCH (u:University)-[:LOCATED_IN]-(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'remote sensing'
                   OR toLower(p.description) CONTAINS 'satellite imagery'
                RETURN count(DISTINCT u) as universities_with_remote_sensing
            """,
            
            'detailed_technology_programs': """
                MATCH (u:University)-[:LOCATED_IN]-(d:Department)-[:OFFERS]->(p:Program)
                WHERE toLower(p.description) CONTAINS 'artificial intelligence' 
                   OR toLower(p.description) CONTAINS 'machine learning'
                   OR toLower(p.description) CONTAINS 'data science'
                   OR toLower(p.description) CONTAINS 'gis'
                   OR toLower(p.description) CONTAINS 'drone'
                   OR toLower(p.description) CONTAINS 'remote sensing'
                RETURN u.name as university_name,
                       d.name as department_name,
                       p.name as program_name,
                       p.description as description
                ORDER BY u.name, d.name
            """,
            
            'technology_departments': """
                MATCH (d:Department)
                WHERE toLower(d.description) CONTAINS 'artificial intelligence' 
                   OR toLower(d.description) CONTAINS 'machine learning'
                   OR toLower(d.description) CONTAINS 'data science'
                   OR toLower(d.description) CONTAINS 'gis'
                   OR toLower(d.description) CONTAINS 'computer science'
                   OR toLower(d.description) CONTAINS 'computing'
                RETURN d.name as department_name,
                       d.description as description
                ORDER BY d.name
            """
        }
        
        return queries
    
    def save_results(self, results: Dict[str, Any], output_dir: Path = None):
        """Save analysis results to files."""
        if output_dir is None:
            output_dir = Path('data/outputs')
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive report
        with open(output_dir / 'accurate_course_proportions_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save proportions as CSV
        proportions_data = []
        if 'overall_proportions' in results:
            for category, data in results['overall_proportions'].items():
                proportions_data.append({
                    'Technology_Category': category,
                    'Universities_Offering': data['universities_offering'],
                    'Total_Universities': data['total_universities'],
                    'Proportion_Percentage': data['proportion_percentage']
                })
        
        if proportions_data:
            df_proportions = pd.DataFrame(proportions_data)
            df_proportions.to_csv(output_dir / 'accurate_technology_proportions.csv', index=False)
        
        # Save queries
        queries = self.generate_detailed_queries()
        with open(output_dir / 'explicit_database_queries.cypher', 'w') as f:
            f.write("-- Explicit Cypher Queries for University Course Analysis\n")
            f.write("-- Generated by AccurateCourseProportions\n\n")
            
            for query_name, query in queries.items():
                f.write(f"-- {query_name}\n")
                f.write(query.strip() + "\n\n")
        
        logger.info(f"Results saved to {output_dir}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a comprehensive summary of the analysis."""
        print("\n" + "="*80)
        print("ACCURATE UNIVERSITY COURSE PROPORTIONS ANALYSIS")
        print("="*80)
        
        # Overall proportions
        if 'overall_proportions' in results:
            print(f"\n🎯 TECHNOLOGY COURSE PROPORTIONS:")
            print(f"   {'Technology':<25} {'Universities':<15} {'Proportion':<15}")
            print(f"   {'-'*25} {'-'*15} {'-'*15}")
            
            for category, data in results['overall_proportions'].items():
                category_name = category.replace('_', ' ').title()
                universities = data['universities_offering']
                proportion = data['proportion_percentage']
                print(f"   {category_name:<25} {universities:<15} {proportion:>6.1f}%")
        
        # AI course analysis
        if 'ai_course_analysis' in results:
            ai_data = results['ai_course_analysis']
            print(f"\n🤖 AI COURSE ANALYSIS:")
            print(f"   • Total Universities: {ai_data['total_universities']}")
            print(f"   • Universities with AI Courses: {ai_data['universities_with_ai_courses']}")
            print(f"   • AI Adoption Rate: {ai_data['ai_adoption_rate']:.1f}%")
            
            if 'technology_breakdown' in ai_data:
                print(f"   • Technology Breakdown:")
                for tech, stats in ai_data['technology_breakdown'].items():
                    print(f"     - {tech}: {stats['universities']} universities ({stats['proportion']:.1f}%)")
        
        # Program level analysis
        if 'program_level_analysis' in results:
            prog_data = results['program_level_analysis']
            print(f"\n📚 PROGRAM LEVEL ANALYSIS:")
            print(f"   • Total Programs: {prog_data['total_programs']}")
            print(f"   • Technology Programs: {prog_data['technology_programs']}")
            print(f"   • Overall Technology Adoption: {prog_data['overall_adoption_rate']:.1f}%")
            
            if 'level_breakdown' in prog_data:
                print(f"   • By Program Level:")
                for level, stats in prog_data['level_breakdown'].items():
                    print(f"     - {level}: {stats['any_technology_programs']}/{stats['count']} programs ({stats['any_technology_percentage']:.1f}%)")
                    print(f"       • AI/ML: {stats['ai_ml_programs']} programs ({stats['ai_ml_percentage']:.1f}%)")
                    print(f"       • GIS: {stats['gis_programs']} programs ({stats['gis_percentage']:.1f}%)")
                    print(f"       • Remote Sensing: {stats['remote_sensing_programs']} programs ({stats['remote_sensing_percentage']:.1f}%)")
                    print(f"       • UAV/Drone: {stats['uav_drone_programs']} programs ({stats['uav_drone_percentage']:.1f}%)")
        
        # University analysis
        if 'university_analysis' in results:
            univ_data = results['university_analysis']
            print(f"\n🏫 UNIVERSITY ANALYSIS:")
            print(f"   • Total Universities: {univ_data['total_universities']}")
            print(f"   • Universities with Technology Courses: {univ_data['universities_with_tech_courses']}")
            print(f"   • Proportion with Technology Courses: {univ_data['proportion_with_tech_courses']:.1f}%")
            print(f"   • Universities with AI/ML Courses: {univ_data['universities_with_ai_ml']}")
            print(f"   • Universities with GIS Courses: {univ_data['universities_with_gis']}")
            print(f"   • Universities with Data Science Courses: {univ_data['universities_with_data_science']}")
            print(f"   • Universities with Remote Sensing Courses: {univ_data['universities_with_remote_sensing']}")
            print(f"   • Universities with Drone/UAV Courses: {univ_data['universities_with_drone_uav']}")
        
        print("\n" + "="*80)
        print("📋 EXPLICIT QUERIES GENERATED:")
        print("   • Check data/outputs/explicit_database_queries.cypher")
        print("   • Use these queries to verify results in Neo4j")
        print("="*80)

def main():
    """Main execution function."""
    try:
        logger.info("Starting accurate course proportions analysis...")
        
        # Initialize analyzer
        analyzer = AccurateCourseProportions()
        
        # Load existing data
        loaded_data = analyzer.load_existing_data()
        
        if not loaded_data:
            logger.error("No data files found for analysis")
            return 1
        
        # Calculate comprehensive proportions
        results = analyzer.calculate_comprehensive_proportions(loaded_data)
        
        # Save results
        analyzer.save_results(results)
        
        # Print summary
        analyzer.print_summary(results)
        
        logger.info("Analysis completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 