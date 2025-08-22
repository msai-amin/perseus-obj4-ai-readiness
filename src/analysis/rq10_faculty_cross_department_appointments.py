#!/usr/bin/env python3
"""
RQ10: Faculty Cross-Department Appointments Analysis
How many faculty members have appointments (joint or otherwise) with computer science, 
engineering, or data science departments?

This script analyzes faculty appointments across different department types and provides
comprehensive insights into cross-department faculty distribution and characteristics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from neo4j import GraphDatabase
import numpy as np
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RQ10FacultyCrossDepartmentAppointmentsAnalyzer:
    """Analyzer for RQ10: Faculty Cross-Department Appointments Analysis"""
    
    def __init__(self, uri, user, password):
        """Initialize the RQ10 Faculty Cross-Department Appointments Analyzer"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user
        self.password = password
        
    def close(self):
        """Close the database connection"""
        self.driver.close()
        
    def verify_database(self, session):
        """Verify database structure and content"""
        try:
            result = session.run("MATCH (n) RETURN labels(n) as node_types, count(n) as count ORDER BY count DESC")
            node_counts = [(record["node_types"], record["count"]) for record in result]
            logger.info(f"Database verification completed. Node types and counts: {node_counts}")
            return node_counts
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return []
    
    def get_total_faculty_count(self, session):
        """Get total faculty count"""
        try:
            result = session.run("MATCH (f:Faculty) RETURN count(f) as total_faculty")
            total = result.single()["total_faculty"]
            logger.info(f"Total faculty count: {total}")
            return total
        except Exception as e:
            logger.error(f"Failed to get total faculty count: {e}")
            return 0
    
    def get_faculty_department_appointments(self, session):
        """Get all faculty department appointments"""
        try:
            result = session.run("""
                MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
                RETURN f.name as faculty_name, d.name as department_name, d.category as department_category
                ORDER BY faculty_name
            """)
            appointments = [(record["faculty_name"], record["department_name"], record["department_category"]) 
                          for record in result]
            logger.info(f"Retrieved {len(appointments)} faculty department appointments")
            return appointments
        except Exception as e:
            logger.error(f"Failed to get faculty department appointments: {e}")
            return []
    
    def classify_department_type(self, department_name: str) -> str:
        """Classify department by type based on name"""
        dept_lower = department_name.lower()
        
        if any(keyword in dept_lower for keyword in ['computer science', 'cs', 'computing', 'informatics']):
            return 'Computer Science'
        elif any(keyword in dept_lower for keyword in ['engineering', 'eng', 'mechanical', 'electrical', 
                                                     'civil', 'chemical', 'biomedical', 'environmental']):
            return 'Engineering'
        elif any(keyword in dept_lower for keyword in ['data science', 'data', 'analytics', 'statistics', 
                                                     'biostatistics', 'quantitative']):
            return 'Data Science'
        else:
            return 'Other'
    
    def get_cross_department_faculty(self, session):
        """Get faculty with cross-department appointments"""
        try:
            result = session.run("""
                MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
                WITH f.name as faculty_name, 
                     CASE 
                         WHEN toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
                              toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics' THEN 'Computer Science'
                         WHEN toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
                              toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
                              toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
                              toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental' THEN 'Engineering'
                         WHEN toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
                              toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
                              toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative' THEN 'Data Science'
                         ELSE 'Other'
                     END as department_category
                WHERE department_category IN ['Computer Science', 'Engineering', 'Data Science']
                RETURN department_category, count(DISTINCT faculty_name) as faculty_count
                ORDER BY faculty_count DESC
            """)
            
            cross_dept_data = [(record["department_category"], record["faculty_count"]) for record in result]
            logger.info(f"Retrieved cross-department faculty data: {cross_dept_data}")
            return cross_dept_data
        except Exception as e:
            logger.error(f"Failed to get cross-department faculty data: {e}")
            return []
    
    def get_multiple_appointments_faculty(self, session):
        """Get faculty with multiple department appointments"""
        try:
            result = session.run("""
                MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
                WITH f.name as faculty_name, collect(d.name) as departments
                WHERE size(departments) > 1
                RETURN faculty_name, departments, size(departments) as appointment_count
                ORDER BY appointment_count DESC, faculty_name
            """)
            
            multiple_appointments = [(record["faculty_name"], record["departments"], record["appointment_count"]) 
                                   for record in result]
            logger.info(f"Retrieved {len(multiple_appointments)} faculty with multiple appointments")
            return multiple_appointments
        except Exception as e:
            logger.error(f"Failed to get multiple appointments faculty: {e}")
            return []
    
    def get_university_cross_department_distribution(self, session):
        """Get university-level cross-department faculty distribution"""
        try:
            result = session.run("""
                MATCH (u:University)-[:HAS]->(d:Department)<-[:APPOINTED_TO]-(f:Faculty)
                WITH u.name as university_name, d.name as department_name, f.name as faculty_name,
                     CASE 
                         WHEN toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
                              toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics' THEN 'Computer Science'
                         WHEN toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
                              toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
                              toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
                              toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental' THEN 'Engineering'
                         WHEN toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
                              toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
                              toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative' THEN 'Data Science'
                         ELSE 'Other'
                     END as department_category
                WHERE department_category IN ['Computer Science', 'Engineering', 'Data Science']
                RETURN university_name, department_category, count(DISTINCT faculty_name) as faculty_count
                ORDER BY university_name, department_category
            """)
            
            univ_distribution = [(record["university_name"], record["department_category"], record["faculty_count"]) 
                                for record in result]
            logger.info(f"Retrieved university-level cross-department distribution: {len(univ_distribution)} records")
            return univ_distribution
        except Exception as e:
            logger.error(f"Failed to get university cross-department distribution: {e}")
            return []
    
    def get_faculty_technology_integration(self, session):
        """Get faculty technology integration with cross-department appointments"""
        try:
            result = session.run("""
                MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)-[:USES_TECHNOLOGY]->(t:Technology)
                WHERE toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'engineering' OR 
                      toLower(d.name) CONTAINS 'data science'
                RETURN f.name as faculty_name, d.name as department_name, t.name as technology_name, t.category as technology_category
                ORDER BY faculty_name, technology_name
            """)
            
            tech_integration = [(record["faculty_name"], record["department_name"], 
                               record["technology_name"], record["technology_category"]) for record in result]
            logger.info(f"Retrieved faculty technology integration data: {len(tech_integration)} records")
            return tech_integration
        except Exception as e:
            logger.error(f"Failed to get faculty technology integration: {e}")
            return []
    
    def get_faculty_research_areas(self, session):
        """Get cross-department faculty by research area"""
        try:
            result = session.run("""
                MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)-[:HAS_RESEARCH_AREA]->(ra:ResearchArea)
                WHERE toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'engineering' OR 
                      toLower(d.name) CONTAINS 'data science'
                RETURN f.name as faculty_name, d.name as department_name, ra.name as research_area
                ORDER BY faculty_name, research_area
            """)
            
            research_areas = [(record["faculty_name"], record["department_name"], record["research_area"]) 
                             for record in result]
            logger.info(f"Retrieved faculty research areas data: {len(research_areas)} records")
            return research_areas
        except Exception as e:
            logger.error(f"Failed to get faculty research areas: {e}")
            return []
    
    def get_summary_statistics(self, session):
        """Get summary statistics for cross-department faculty"""
        try:
            result = session.run("""
                MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
                WITH f.name as faculty_name, 
                     CASE 
                         WHEN toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
                              toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics' THEN 'Computer Science'
                         WHEN toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
                              toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
                              toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
                              toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental' THEN 'Engineering'
                         WHEN toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
                              toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
                              toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative' THEN 'Data Science'
                         ELSE 'Other'
                     END as department_category
                WHERE department_category IN ['Computer Science', 'Engineering', 'Data Science']
                RETURN department_category, 
                       count(DISTINCT faculty_name) as faculty_count,
                       round(count(DISTINCT faculty_name) * 100.0 / (MATCH (f2:Faculty) RETURN count(f2))[0], 2) as percentage_of_total_faculty
                ORDER BY faculty_count DESC
            """)
            
            summary_stats = [(record["department_category"], record["faculty_count"], record["percentage_of_total_faculty"]) 
                            for record in result]
            logger.info(f"Retrieved summary statistics: {summary_stats}")
            return summary_stats
        except Exception as e:
            logger.error(f"Failed to get summary statistics: {e}")
            return []
    
    def create_visualizations(self, cross_dept_data, univ_distribution, multiple_appointments, 
                            tech_integration, research_areas):
        """Create comprehensive visualizations for RQ10"""
        try:
            # Set up the plotting style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create a 3x3 subplot layout
            fig, axes = plt.subplots(3, 3, figsize=(20, 16))
            fig.suptitle('RQ10: Faculty Cross-Department Appointments Analysis', fontsize=16, fontweight='bold')
            
            # 1. Cross-Department Faculty Distribution (Top Left)
            if cross_dept_data:
                dept_types, faculty_counts = zip(*cross_dept_data)
                axes[0, 0].bar(dept_types, faculty_counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
                axes[0, 0].set_title('Faculty Distribution by Department Type')
                axes[0, 0].set_ylabel('Number of Faculty')
                axes[0, 0].tick_params(axis='x', rotation=45)
                for i, v in enumerate(faculty_counts):
                    axes[0, 0].text(i, v + 0.5, str(v), ha='center', va='bottom')
            
            # 2. University-Level Distribution Heatmap (Top Center)
            if univ_distribution:
                univ_df = pd.DataFrame(univ_distribution, columns=['University', 'Department', 'Faculty_Count'])
                pivot_df = univ_df.pivot(index='University', columns='Department', values='Faculty_Count').fillna(0)
                
                if not pivot_df.empty:
                    sns.heatmap(pivot_df, annot=True, fmt='g', cmap='YlOrRd', ax=axes[0, 1])
                    axes[0, 1].set_title('University Cross-Department Faculty Distribution')
                    axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Multiple Appointments Distribution (Top Right)
            if multiple_appointments:
                appointment_counts = [record[2] for record in multiple_appointments]
                unique_counts, counts = np.unique(appointment_counts, return_counts=True)
                axes[0, 2].bar(unique_counts, counts, color='#96CEB4')
                axes[0, 2].set_title('Faculty with Multiple Department Appointments')
                axes[0, 2].set_xlabel('Number of Appointments')
                axes[0, 2].set_ylabel('Number of Faculty')
                for i, v in enumerate(counts):
                    axes[0, 2].text(unique_counts[i], v + 0.1, str(v), ha='center', va='bottom')
            
            # 4. Technology Integration by Department (Middle Left)
            if tech_integration:
                tech_df = pd.DataFrame(tech_integration, columns=['Faculty', 'Department', 'Technology', 'Category'])
                dept_tech_counts = tech_df.groupby('Department').size()
                axes[1, 0].pie(dept_tech_counts.values, labels=dept_tech_counts.index, autopct='%1.1f%%')
                axes[1, 0].set_title('Technology Integration by Department')
            
            # 5. Research Areas Distribution (Middle Center)
            if research_areas:
                research_df = pd.DataFrame(research_areas, columns=['Faculty', 'Department', 'Research_Area'])
                research_counts = research_df['Research_Area'].value_counts().head(10)
                axes[1, 1].barh(range(len(research_counts)), research_counts.values, color='#FFEAA7')
                axes[1, 1].set_yticks(range(len(research_counts)))
                axes[1, 1].set_yticklabels(research_counts.index)
                axes[1, 1].set_title('Top 10 Research Areas (Cross-Department Faculty)')
                axes[1, 1].set_xlabel('Number of Faculty')
            
            # 6. Department Technology Categories (Middle Right)
            if tech_integration:
                tech_df = pd.DataFrame(tech_integration, columns=['Faculty', 'Department', 'Technology', 'Category'])
                category_counts = tech_df['Category'].value_counts()
                axes[1, 2].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
                axes[1, 2].set_title('Technology Categories Used by Cross-Department Faculty')
            
            # 7. Faculty Appointment Patterns (Bottom Left)
            if multiple_appointments:
                dept_combinations = [', '.join(sorted(record[1])) for record in multiple_appointments]
                combination_counts = pd.Series(dept_combinations).value_counts().head(8)
                axes[2, 0].barh(range(len(combination_counts)), combination_counts.values, color='#DDA0DD')
                axes[2, 0].set_yticks(range(len(combination_counts)))
                axes[2, 0].set_yticklabels(combination_counts.index)
                axes[2, 0].set_title('Most Common Department Combinations')
                axes[2, 0].set_xlabel('Number of Faculty')
            
            # 8. Cross-Department Faculty by University (Bottom Center)
            if univ_distribution:
                univ_df = pd.DataFrame(univ_distribution, columns=['University', 'Department', 'Faculty_Count'])
                univ_totals = univ_df.groupby('University')['Faculty_Count'].sum().sort_values(ascending=False).head(10)
                axes[2, 1].bar(range(len(univ_totals)), univ_totals.values, color='#98D8C8')
                axes[2, 1].set_xticks(range(len(univ_totals)))
                axes[2, 1].set_xticklabels(univ_totals.index, rotation=45, ha='right')
                axes[2, 1].set_title('Top 10 Universities by Cross-Department Faculty')
                axes[2, 1].set_ylabel('Total Cross-Department Faculty')
                for i, v in enumerate(univ_totals.values):
                    axes[2, 1].text(i, v + 0.1, str(int(v)), ha='center', va='bottom')
            
            # 9. Summary Statistics (Bottom Right)
            if cross_dept_data:
                dept_types, faculty_counts = zip(*cross_dept_data)
                total_cross_dept = sum(faculty_counts)
                axes[2, 2].text(0.5, 0.7, f'Total Cross-Department\nFaculty: {total_cross_dept}', 
                                ha='center', va='center', fontsize=14, fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
                
                if multiple_appointments:
                    multi_appt_count = len(multiple_appointments)
                    axes[2, 2].text(0.5, 0.5, f'Faculty with Multiple\nAppointments: {multi_appt_count}', 
                                    ha='center', va='center', fontsize=12,
                                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
                
                if tech_integration:
                    tech_faculty_count = len(set([record[0] for record in tech_integration]))
                    axes[2, 2].text(0.5, 0.3, f'Faculty Using\nTechnologies: {tech_faculty_count}', 
                                    ha='center', va='center', fontsize=12,
                                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
                
                axes[2, 2].set_title('Summary Statistics')
                axes[2, 2].axis('off')
            
            plt.tight_layout()
            plt.savefig('rq10_faculty_cross_department_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            logger.info("Visualizations created and saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to create visualizations: {e}")
    
    def run_analysis(self):
        """Run the complete RQ10 analysis"""
        try:
            with self.driver.session() as session:
                logger.info("Starting RQ10: Faculty Cross-Department Appointments Analysis")
                
                # Verify database
                node_counts = self.verify_database(session)
                
                # Get basic counts
                total_faculty = self.get_total_faculty_count(session)
                
                # Get all data
                faculty_appointments = self.get_faculty_department_appointments(session)
                cross_dept_data = self.get_cross_department_faculty(session)
                multiple_appointments = self.get_multiple_appointments_faculty(session)
                univ_distribution = self.get_university_cross_department_distribution(session)
                tech_integration = self.get_faculty_technology_integration(session)
                research_areas = self.get_faculty_research_areas(session)
                summary_stats = self.get_summary_statistics(session)
                
                # Create DataFrames for analysis
                cross_dept_df = pd.DataFrame(cross_dept_data, columns=['Department_Type', 'Faculty_Count'])
                multiple_appt_df = pd.DataFrame(multiple_appointments, columns=['Faculty_Name', 'Departments', 'Appointment_Count'])
                univ_dist_df = pd.DataFrame(univ_distribution, columns=['University', 'Department_Type', 'Faculty_Count'])
                tech_integration_df = pd.DataFrame(tech_integration, columns=['Faculty_Name', 'Department', 'Technology', 'Category'])
                research_areas_df = pd.DataFrame(research_areas, columns=['Faculty_Name', 'Department', 'Research_Area'])
                summary_stats_df = pd.DataFrame(summary_stats, columns=['Department_Type', 'Faculty_Count', 'Percentage'])
                
                # Print results
                print("\n" + "="*80)
                print("RQ10: FACULTY CROSS-DEPARTMENT APPOINTMENTS ANALYSIS")
                print("="*80)
                
                print(f"\nTotal Faculty in Database: {total_faculty}")
                print(f"Faculty with Department Appointments: {len(faculty_appointments)}")
                
                print("\n" + "-"*60)
                print("CROSS-DEPARTMENT FACULTY DISTRIBUTION")
                print("-"*60)
                print(cross_dept_df.to_string(index=False))
                
                print("\n" + "-"*60)
                print("FACULTY WITH MULTIPLE DEPARTMENT APPOINTMENTS")
                print("-"*60)
                if not multiple_appt_df.empty:
                    print(f"Total Faculty with Multiple Appointments: {len(multiple_appt_df)}")
                    print(multiple_appt_df.head(10).to_string(index=False))
                    if len(multiple_appt_df) > 10:
                        print(f"... and {len(multiple_appt_df) - 10} more")
                else:
                    print("No faculty found with multiple department appointments")
                
                print("\n" + "-"*60)
                print("UNIVERSITY-LEVEL CROSS-DEPARTMENT FACULTY DISTRIBUTION")
                print("-"*60)
                if not univ_dist_df.empty:
                    univ_totals = univ_dist_df.groupby('University')['Faculty_Count'].sum().sort_values(ascending=False)
                    print("Top 10 Universities by Cross-Department Faculty:")
                    for univ, count in univ_totals.head(10).items():
                        print(f"  {univ}: {int(count)} faculty")
                else:
                    print("No university-level distribution data available")
                
                print("\n" + "-"*60)
                print("TECHNOLOGY INTEGRATION BY CROSS-DEPARTMENT FACULTY")
                print("-"*60)
                if not tech_integration_df.empty:
                    tech_faculty_count = len(set(tech_integration_df['Faculty_Name']))
                    print(f"Cross-Department Faculty Using Technologies: {tech_faculty_count}")
                    
                    dept_tech_counts = tech_integration_df.groupby('Department').size()
                    print("\nTechnology Integration by Department:")
                    for dept, count in dept_tech_counts.items():
                        print(f"  {dept}: {count} technology relationships")
                else:
                    print("No technology integration data available")
                
                print("\n" + "-"*60)
                print("RESEARCH AREAS OF CROSS-DEPARTMENT FACULTY")
                print("-"*60)
                if not research_areas_df.empty:
                    research_counts = research_areas_df['Research_Area'].value_counts()
                    print("Top 10 Research Areas:")
                    for area, count in research_counts.head(10).items():
                        print(f"  {area}: {count} faculty")
                else:
                    print("No research area data available")
                
                print("\n" + "-"*60)
                print("SUMMARY STATISTICS")
                print("-"*60)
                print(summary_stats_df.to_string(index=False))
                
                # Create visualizations
                self.create_visualizations(cross_dept_data, univ_distribution, multiple_appointments, 
                                        tech_integration, research_areas)
                
                # Save results to CSV files
                cross_dept_df.to_csv('rq10_cross_department_faculty_distribution.csv', index=False)
                multiple_appt_df.to_csv('rq10_multiple_appointments_faculty.csv', index=False)
                univ_dist_df.to_csv('rq10_university_cross_department_distribution.csv', index=False)
                tech_integration_df.to_csv('rq10_faculty_technology_integration.csv', index=False)
                research_areas_df.to_csv('rq10_faculty_research_areas.csv', index=False)
                summary_stats_df.to_csv('rq10_summary_statistics.csv', index=False)
                
                logger.info("RQ10 analysis completed successfully")
                
                return {
                    'cross_dept_data': cross_dept_df,
                    'multiple_appointments': multiple_appt_df,
                    'university_distribution': univ_dist_df,
                    'technology_integration': tech_integration_df,
                    'research_areas': research_areas_df,
                    'summary_statistics': summary_stats_df
                }
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None

def main():
    """Main function to run the RQ10 analysis"""
    # Database connection parameters
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    
    try:
        # Create analyzer instance
        analyzer = RQ10FacultyCrossDepartmentAppointmentsAnalyzer(uri, user, password)
        
        # Run analysis
        results = analyzer.run_analysis()
        
        if results:
            print("\n" + "="*80)
            print("ANALYSIS COMPLETED SUCCESSFULLY")
            print("="*80)
            print("Results saved to CSV files:")
            print("  - rq10_cross_department_faculty_distribution.csv")
            print("  - rq10_multiple_appointments_faculty.csv")
            print("  - rq10_university_cross_department_distribution.csv")
            print("  - rq10_faculty_technology_integration.csv")
            print("  - rq10_faculty_research_areas.csv")
            print("  - rq10_summary_statistics.csv")
            print("  - rq10_faculty_cross_department_analysis.png")
        else:
            print("Analysis failed. Check logs for details.")
            
    except Exception as e:
        print(f"Error running analysis: {e}")
        logger.error(f"Main execution failed: {e}")
    
    finally:
        # Clean up
        if 'analyzer' in locals():
            analyzer.close()

if __name__ == "__main__":
    main()
