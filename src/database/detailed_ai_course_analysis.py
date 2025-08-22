#!/usr/bin/env python3
"""
Detailed AI Course Analysis
Shows what AI-related courses were found and why they're not connected to universities
"""

import pandas as pd
import subprocess
import time
from typing import List, Dict

class DetailedAICourseAnalyzer:
    """Detailed analyzer to understand why AI courses aren't connected to universities"""
    
    def __init__(self, host="localhost:7690", user="neo4j", password="perseus2025"):
        self.host = host
        self.user = user
        self.password = password
        self.rate_limit_delay = 0.1
        
    def execute_query(self, query: str) -> List[Dict]:
        """Execute a Cypher query with rate limiting"""
        cmd = f"""cypher-shell -a {self.host} -u {self.user} -p {self.password} --format plain --non-interactive <<< "{query}" """
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return self.parse_cypher_output(result.stdout)
            else:
                print(f"Query failed: {result.stderr}")
                return []
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
        finally:
            time.sleep(self.rate_limit_delay)
    
    def parse_cypher_output(self, output: str) -> List[Dict]:
        """Parse Cypher output into list of dictionaries"""
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(', ')
        data = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split(', ', len(headers)-1)
                row = {}
                for i, header in enumerate(headers):
                    if i < len(values):
                        value = values[i].strip('"')
                        row[header] = value
                    else:
                        row[header] = ""
                data.append(row)
        
        return data

    def find_ai_courses(self) -> List[Dict]:
        """Find all AI-related courses"""
        print("Finding AI-related courses...")
        
        # Query 1: Direct keyword matching
        query = """
        MATCH (c:Course)
        WHERE toLower(c.name) CONTAINS 'ai' OR toLower(c.name) CONTAINS 'artificial intelligence' 
           OR toLower(c.name) CONTAINS 'machine learning' OR toLower(c.name) CONTAINS 'data science'
           OR toLower(c.name) CONTAINS 'gis' OR toLower(c.name) CONTAINS 'remote sensing'
           OR toLower(c.name) CONTAINS 'drone' OR toLower(c.description) CONTAINS 'ai'
           OR toLower(c.description) CONTAINS 'artificial intelligence' OR toLower(c.description) CONTAINS 'machine learning'
           OR toLower(c.description) CONTAINS 'data science' OR toLower(c.description) CONTAINS 'gis'
           OR toLower(c.description) CONTAINS 'remote sensing' OR toLower(c.description) CONTAINS 'drone'
        RETURN c.name AS Course_Name, c.description AS Description
        """
        courses = self.execute_query(query)
        
        print(f"Found {len(courses)} AI-related courses:")
        for course in courses:
            print(f"  - {course.get('Course_Name', 'Unknown')}")
        
        return courses

    def check_course_program_connections(self, courses: List[Dict]) -> List[Dict]:
        """Check how courses are connected to programs"""
        print("\nChecking course-program connections...")
        
        for course in courses:
            course_name = course.get('Course_Name', '')
            
            # Check CORE_FOR relationships
            query = f"""
            MATCH (c:Course {{name: '{course_name}'}})-[:CORE_FOR]->(p:Program)
            RETURN p.name AS Program_Name
            """
            core_programs = self.execute_query(query)
            
            # Check PREREQUISITE_FOR relationships
            query = f"""
            MATCH (c:Course {{name: '{course_name}'}})-[:PREREQUISITE_FOR]->(p:Program)
            RETURN p.name AS Program_Name
            """
            prereq_programs = self.execute_query(query)
            
            # Check OFFERS_COURSE relationships
            query = f"""
            MATCH (p:Program)-[:OFFERS_COURSE]->(c:Course {{name: '{course_name}'}})
            RETURN p.name AS Program_Name
            """
            offered_by_programs = self.execute_query(query)
            
            course['core_programs'] = [p.get('Program_Name', '') for p in core_programs]
            course['prereq_programs'] = [p.get('Program_Name', '') for p in prereq_programs]
            course['offered_by_programs'] = [p.get('Program_Name', '') for p in offered_by_programs]
            
            print(f"\nCourse: {course_name}")
            print(f"  Core for: {course['core_programs']}")
            print(f"  Prerequisite for: {course['prereq_programs']}")
            print(f"  Offered by: {course['offered_by_programs']}")
        
        return courses

    def check_program_university_connections(self, courses: List[Dict]) -> List[Dict]:
        """Check how programs are connected to universities"""
        print("\nChecking program-university connections...")
        
        all_programs = set()
        for course in courses:
            all_programs.update(course['core_programs'])
            all_programs.update(course['prereq_programs'])
            all_programs.update(course['offered_by_programs'])
        
        print(f"Found {len(all_programs)} unique programs:")
        for program in all_programs:
            if program:  # Skip empty strings
                print(f"  - {program}")
        
        # Check which programs are connected to universities
        connected_programs = []
        unconnected_programs = []
        
        for program in all_programs:
            if not program:
                continue
                
            query = f"""
            MATCH (u:University)-[:OFFERS]->(d:Department)-[:OFFERS]->(p:Program {{name: '{program}'}})
            RETURN u.name AS University, d.name AS Department
            """
            connections = self.execute_query(query)
            
            if connections:
                connected_programs.append({
                    'program': program,
                    'connections': connections
                })
                print(f"✓ {program} is connected to universities")
            else:
                unconnected_programs.append(program)
                print(f"✗ {program} is NOT connected to universities")
        
        return {
            'connected_programs': connected_programs,
            'unconnected_programs': unconnected_programs
        }

    def find_missing_relationships(self) -> Dict:
        """Find missing relationships that need to be created"""
        print("\nFinding missing relationships...")
        
        # Check which universities have departments
        query = """
        MATCH (u:University)-[:OFFERS]->(d:Department)
        RETURN u.name AS University, count(d) AS DepartmentCount
        ORDER BY DepartmentCount DESC
        """
        universities_with_departments = self.execute_query(query)
        
        # Check which universities don't have departments
        query = """
        MATCH (u:University)
        WHERE NOT (u)-[:OFFERS]->(:Department)
        RETURN u.name AS University
        """
        universities_without_departments = self.execute_query(query)
        
        # Check which programs exist but aren't connected to departments
        query = """
        MATCH (p:Program)
        WHERE NOT (:Department)-[:OFFERS]->(p)
        RETURN p.name AS Program
        """
        unconnected_programs = self.execute_query(query)
        
        return {
            'universities_with_departments': universities_with_departments,
            'universities_without_departments': universities_without_departments,
            'unconnected_programs': unconnected_programs
        }

    def generate_recommendations(self, courses: List[Dict], program_connections: Dict, missing_rels: Dict) -> str:
        """Generate recommendations for fixing the data"""
        
        recommendations = []
        recommendations.append("=" * 80)
        recommendations.append("RECOMMENDATIONS TO FIX AI COURSE ANALYSIS")
        recommendations.append("=" * 80)
        
        # Summary of findings
        recommendations.append(f"\nSUMMARY:")
        recommendations.append(f"- Found {len(courses)} AI-related courses")
        recommendations.append(f"- {len(program_connections['connected_programs'])} programs are connected to universities")
        recommendations.append(f"- {len(program_connections['unconnected_programs'])} programs are NOT connected to universities")
        recommendations.append(f"- {len(missing_rels['universities_without_departments'])} universities don't have departments")
        
        # Specific recommendations
        recommendations.append(f"\nSPECIFIC ACTIONS NEEDED:")
        
        if missing_rels['universities_without_departments']:
            recommendations.append(f"\n1. Add department relationships to universities:")
            for uni in missing_rels['universities_without_departments']:
                recommendations.append(f"   - {uni.get('University', 'Unknown')}")
        
        if program_connections['unconnected_programs']:
            recommendations.append(f"\n2. Connect programs to departments:")
            for program in program_connections['unconnected_programs']:
                recommendations.append(f"   - {program}")
        
        if courses:
            recommendations.append(f"\n3. Verify course-program relationships:")
            for course in courses:
                course_name = course.get('Course_Name', 'Unknown')
                if not course['core_programs'] and not course['prereq_programs'] and not course['offered_by_programs']:
                    recommendations.append(f"   - {course_name} has no program connections")
        
        recommendations.append(f"\n4. Create missing OFFERS_COURSE relationships:")
        for course in courses:
            course_name = course.get('Course_Name', 'Unknown')
            if course['core_programs'] or course['prereq_programs']:
                for program in course['core_programs'] + course['prereq_programs']:
                    if program:
                        recommendations.append(f"   - {program} -> {course_name}")
        
        return "\n".join(recommendations)

    def run_detailed_analysis(self):
        """Run the complete detailed analysis"""
        
        print("Starting Detailed AI Course Analysis...")
        print("=" * 60)
        
        # Step 1: Find AI courses
        courses = self.find_ai_courses()
        
        # Step 2: Check course-program connections
        courses_with_connections = self.check_course_program_connections(courses)
        
        # Step 3: Check program-university connections
        program_connections = self.check_program_university_connections(courses_with_connections)
        
        # Step 4: Find missing relationships
        missing_relationships = self.find_missing_relationships()
        
        # Step 5: Generate recommendations
        recommendations = self.generate_recommendations(courses_with_connections, program_connections, missing_relationships)
        
        # Print recommendations
        print("\n" + recommendations)
        
        # Save detailed results
        self.save_detailed_results(courses_with_connections, program_connections, missing_relationships, recommendations)
        
        return {
            'courses': courses_with_connections,
            'program_connections': program_connections,
            'missing_relationships': missing_relationships,
            'recommendations': recommendations
        }

    def save_detailed_results(self, courses: List[Dict], program_connections: Dict, missing_rels: Dict, recommendations: str):
        """Save detailed results to files"""
        
        # Save courses with their connections
        courses_data = []
        for course in courses:
            courses_data.append({
                'Course_Name': course.get('Course_Name', ''),
                'Description': course.get('Description', ''),
                'Core_Programs': ', '.join(course['core_programs']),
                'Prereq_Programs': ', '.join(course['prereq_programs']),
                'Offered_By_Programs': ', '.join(course['offered_by_programs'])
            })
        
        df_courses = pd.DataFrame(courses_data)
        df_courses.to_csv('detailed_ai_courses.csv', index=False)
        
        # Save program connections
        connected_data = []
        for prog in program_connections['connected_programs']:
            for conn in prog['connections']:
                connected_data.append({
                    'Program': prog['program'],
                    'University': conn.get('University', ''),
                    'Department': conn.get('Department', '')
                })
        
        df_connected = pd.DataFrame(connected_data)
        df_connected.to_csv('connected_programs.csv', index=False)
        
        # Save unconnected programs
        df_unconnected = pd.DataFrame(program_connections['unconnected_programs'], columns=['Program'])
        df_unconnected.to_csv('unconnected_programs.csv', index=False)
        
        # Save recommendations
        with open('ai_course_recommendations.txt', 'w') as f:
            f.write(recommendations)
        
        print("\nDetailed results saved to:")
        print("- detailed_ai_courses.csv")
        print("- connected_programs.csv")
        print("- unconnected_programs.csv")
        print("- ai_course_recommendations.txt")

def main():
    """Main function to run the detailed analysis"""
    
    analyzer = DetailedAICourseAnalyzer()
    
    # Run detailed analysis
    results = analyzer.run_detailed_analysis()
    
    print("\nDetailed analysis complete! Check the generated files for specific recommendations.")

if __name__ == "__main__":
    main() 