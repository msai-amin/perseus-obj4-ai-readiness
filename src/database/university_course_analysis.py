#!/usr/bin/env python3
"""
KG-Perseus University Course Analysis
Comprehensive analysis of university course offerings in AI, GIS, and other technologies.
This script provides the most accurate data on what proportion of universities offer courses in various technologies.
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

class UniversityCourseAnalyzer:
    """Comprehensive analysis of university course offerings in technology areas."""
    
    def __init__(self, uri: str = "bolt://localhost:7689", 
                 username: str = "neo4j", 
                 password: str = "perseus2025"):
        """Initialize the analyzer with database connection."""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.results = {}
        
        # Define technology categories and their keywords
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
    
    def get_database_overview(self) -> Dict[str, Any]:
        """Get overview of database structure and content."""
        logger.info("Getting database overview...")
        
        queries = {
            'total_universities': "MATCH (u:University) RETURN count(u) as count",
            'total_departments': "MATCH (d:Department) RETURN count(d) as count",
            'total_programs': "MATCH (p:Program) RETURN count(p) as count",
            'total_research_areas': "MATCH (r:Research_Area) RETURN count(r) as count",
            'node_labels': "CALL db.labels() YIELD label RETURN collect(label) as labels",
            'relationship_types': "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
        }
        
        overview = {}
        for name, query in queries.items():
            result = self.run_query(query)
            if result:
                overview[name] = result[0]
        
        return overview
    
    def analyze_program_courses(self) -> Dict[str, Any]:
        """Analyze courses offered within programs."""
        logger.info("Analyzing program courses...")
        
        # Query 1: Get all programs with course information
        query1 = """
        MATCH (p:Program)
        WHERE p.courses IS NOT NULL OR p.course_list IS NOT NULL OR p.course_requirements IS NOT NULL
        RETURN p.name as program_name, 
               p.courses as courses,
               p.course_list as course_list,
               p.course_requirements as course_requirements,
               p.description as description
        """
        
        # Query 2: Get programs by department
        query2 = """
        MATCH (d:Department)-[:OFFERS]->(p:Program)
        WHERE p.courses IS NOT NULL OR p.course_list IS NOT NULL
        RETURN d.name as department_name,
               p.name as program_name,
               p.courses as courses,
               p.course_list as course_list
        """
        
        # Query 3: Get universities with programs that have courses
        query3 = """
        MATCH (u:University)-[:LOCATED_IN]-(d:Department)-[:OFFERS]->(p:Program)
        WHERE p.courses IS NOT NULL OR p.course_list IS NOT NULL
        RETURN u.name as university_name,
               d.name as department_name,
               p.name as program_name,
               p.courses as courses,
               p.course_list as course_list
        """
        
        results = {
            'programs_with_courses': self.run_query(query1),
            'department_programs': self.run_query(query2),
            'university_programs': self.run_query(query3)
        }
        
        return results
    
    def identify_technology_courses(self, course_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify technology-related courses from program data."""
        logger.info("Identifying technology courses...")
        
        technology_courses = {category: [] for category in self.technology_categories.keys()}
        
        for program in course_data:
            # Extract course information from various possible fields
            courses_text = ""
            if program.get('courses'):
                courses_text += str(program['courses']) + " "
            if program.get('course_list'):
                courses_text += str(program['course_list']) + " "
            if program.get('course_requirements'):
                courses_text += str(program['course_requirements']) + " "
            if program.get('description'):
                courses_text += str(program['description']) + " "
            
            courses_text = courses_text.lower()
            
            # Check each technology category
            for category, keywords in self.technology_categories.items():
                for keyword in keywords:
                    if keyword in courses_text:
                        technology_courses[category].append({
                            'program_name': program.get('program_name', 'Unknown'),
                            'university': program.get('university_name', 'Unknown'),
                            'department': program.get('department_name', 'Unknown'),
                            'matched_keyword': keyword,
                            'course_text': courses_text[:200] + "..." if len(courses_text) > 200 else courses_text
                        })
                        break  # Only count once per category per program
        
        return technology_courses
    
    def calculate_university_proportions(self, technology_courses: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Calculate what proportion of universities offer courses in each technology."""
        logger.info("Calculating university proportions...")
        
        # Get total number of universities
        total_universities_query = "MATCH (u:University) RETURN count(u) as total"
        total_result = self.run_query(total_universities_query)
        total_universities = total_result[0]['total'] if total_result else 0
        
        proportions = {}
        
        for category, courses in technology_courses.items():
            # Get unique universities offering courses in this category
            universities_in_category = set()
            for course in courses:
                if course.get('university') and course['university'] != 'Unknown':
                    universities_in_category.add(course['university'])
            
            proportion = len(universities_in_category) / total_universities * 100 if total_universities > 0 else 0
            
            proportions[category] = {
                'universities_offering': len(universities_in_category),
                'total_universities': total_universities,
                'proportion_percentage': proportion,
                'universities_list': list(universities_in_category)
            }
        
        return proportions
    
    def get_detailed_course_analysis(self) -> Dict[str, Any]:
        """Get detailed analysis of course offerings by technology."""
        logger.info("Getting detailed course analysis...")
        
        # Query for programs with technology-related descriptions
        query = """
        MATCH (p:Program)
        WHERE toLower(p.description) CONTAINS 'artificial intelligence' 
           OR toLower(p.description) CONTAINS 'machine learning'
           OR toLower(p.description) CONTAINS 'data science'
           OR toLower(p.description) CONTAINS 'gis'
           OR toLower(p.description) CONTAINS 'geographic information'
           OR toLower(p.description) CONTAINS 'remote sensing'
           OR toLower(p.description) CONTAINS 'drone'
           OR toLower(p.description) CONTAINS 'uav'
        RETURN p.name as program_name,
               p.description as description,
               p.level as level,
               p.type as type
        """
        
        technology_programs = self.run_query(query)
        
        # Categorize programs by technology
        categorized_programs = {category: [] for category in self.technology_categories.keys()}
        
        for program in technology_programs:
            description = program.get('description', '').lower()
            
            for category, keywords in self.technology_categories.items():
                for keyword in keywords:
                    if keyword in description:
                        categorized_programs[category].append(program)
                        break
        
        return categorized_programs
    
    def analyze_department_technology_focus(self) -> Dict[str, Any]:
        """Analyze which departments focus on technology areas."""
        logger.info("Analyzing department technology focus...")
        
        query = """
        MATCH (d:Department)
        WHERE toLower(d.description) CONTAINS 'artificial intelligence' 
           OR toLower(d.description) CONTAINS 'machine learning'
           OR toLower(d.description) CONTAINS 'data science'
           OR toLower(d.description) CONTAINS 'gis'
           OR toLower(d.description) CONTAINS 'geographic information'
           OR toLower(d.description) CONTAINS 'remote sensing'
           OR toLower(d.description) CONTAINS 'drone'
           OR toLower(d.description) CONTAINS 'uav'
           OR toLower(d.description) CONTAINS 'computer science'
           OR toLower(d.description) CONTAINS 'computing'
        RETURN d.name as department_name,
               d.description as description,
               d.location as location
        """
        
        technology_departments = self.run_query(query)
        
        # Categorize departments by technology focus
        categorized_departments = {category: [] for category in self.technology_categories.keys()}
        
        for dept in technology_departments:
            description = dept.get('description', '').lower()
            
            for category, keywords in self.technology_categories.items():
                for keyword in keywords:
                    if keyword in description:
                        categorized_departments[category].append(dept)
                        break
        
        return categorized_departments
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive report on university course offerings."""
        logger.info("Generating comprehensive report...")
        
        # Get database overview
        overview = self.get_database_overview()
        
        # Analyze program courses
        program_analysis = self.analyze_program_courses()
        
        # Identify technology courses
        technology_courses = self.identify_technology_courses(program_analysis['university_programs'])
        
        # Calculate proportions
        proportions = self.calculate_university_proportions(technology_courses)
        
        # Get detailed analysis
        detailed_analysis = self.get_detailed_course_analysis()
        
        # Analyze department focus
        department_analysis = self.analyze_department_technology_focus()
        
        # Compile comprehensive report
        report = {
            'database_overview': overview,
            'technology_proportions': proportions,
            'technology_courses': technology_courses,
            'detailed_analysis': detailed_analysis,
            'department_analysis': department_analysis,
            'summary': {
                'total_universities': overview.get('total_universities', {}).get('count', 0),
                'total_departments': overview.get('total_departments', {}).get('count', 0),
                'total_programs': overview.get('total_programs', {}).get('count', 0),
                'technology_categories_analyzed': len(self.technology_categories),
                'universities_with_technology_courses': sum(1 for cat in proportions.values() if cat['universities_offering'] > 0)
            }
        }
        
        return report
    
    def save_results(self, results: Dict[str, Any], output_dir: Path = None):
        """Save analysis results to files."""
        if output_dir is None:
            output_dir = Path('data/outputs')
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save comprehensive report
        with open(output_dir / 'university_course_analysis_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save proportions as CSV
        proportions_data = []
        for category, data in results['technology_proportions'].items():
            proportions_data.append({
                'Technology_Category': category,
                'Universities_Offering': data['universities_offering'],
                'Total_Universities': data['total_universities'],
                'Proportion_Percentage': data['proportion_percentage'],
                'Universities_List': ', '.join(data['universities_list'])
            })
        
        df_proportions = pd.DataFrame(proportions_data)
        df_proportions.to_csv(output_dir / 'university_technology_proportions.csv', index=False)
        
        # Save detailed course data
        course_data = []
        for category, courses in results['technology_courses'].items():
            for course in courses:
                course_data.append({
                    'Technology_Category': category,
                    'University': course['university'],
                    'Department': course['department'],
                    'Program': course['program_name'],
                    'Matched_Keyword': course['matched_keyword']
                })
        
        df_courses = pd.DataFrame(course_data)
        df_courses.to_csv(output_dir / 'technology_courses_detailed.csv', index=False)
        
        logger.info(f"Results saved to {output_dir}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of the analysis results."""
        print("\n" + "="*80)
        print("UNIVERSITY COURSE OFFERINGS ANALYSIS")
        print("="*80)
        
        # Database overview
        overview = results['database_overview']
        print(f"\n📊 DATABASE OVERVIEW:")
        print(f"   • Total Universities: {overview.get('total_universities', {}).get('count', 0)}")
        print(f"   • Total Departments: {overview.get('total_departments', {}).get('count', 0)}")
        print(f"   • Total Programs: {overview.get('total_programs', {}).get('count', 0)}")
        print(f"   • Total Research Areas: {overview.get('total_research_areas', {}).get('count', 0)}")
        
        # Technology proportions
        print(f"\n🎯 TECHNOLOGY COURSE PROPORTIONS:")
        print(f"   {'Technology':<20} {'Universities':<15} {'Proportion':<15}")
        print(f"   {'-'*20} {'-'*15} {'-'*15}")
        
        for category, data in results['technology_proportions'].items():
            category_name = category.replace('_', ' ').title()
            universities = data['universities_offering']
            proportion = data['proportion_percentage']
            print(f"   {category_name:<20} {universities:<15} {proportion:>6.1f}%")
        
        # Summary statistics
        summary = results['summary']
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"   • Technology Categories Analyzed: {summary['technology_categories_analyzed']}")
        print(f"   • Universities with Technology Courses: {summary['universities_with_technology_courses']}")
        
        # Most common technology
        proportions = results['technology_proportions']
        if proportions:
            most_common = max(proportions.items(), key=lambda x: x[1]['proportion_percentage'])
            print(f"   • Most Common Technology: {most_common[0].replace('_', ' ').title()} ({most_common[1]['proportion_percentage']:.1f}%)")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection."""
        self.driver.close()

def main():
    """Main execution function."""
    try:
        logger.info("Starting university course analysis...")
        
        # Initialize analyzer
        analyzer = UniversityCourseAnalyzer()
        
        # Generate comprehensive report
        results = analyzer.generate_comprehensive_report()
        
        # Save results
        analyzer.save_results(results)
        
        # Print summary
        analyzer.print_summary(results)
        
        logger.info("Analysis completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1
    
    finally:
        if 'analyzer' in locals():
            analyzer.close()

if __name__ == "__main__":
    sys.exit(main()) 