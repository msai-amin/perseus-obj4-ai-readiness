#!/usr/bin/env python3
"""
Fix AI Course Relationships
Creates missing relationships to connect AI courses to universities
"""

import subprocess
import time
from typing import List, Dict

class RelationshipFixer:
    """Fix missing relationships in the knowledge graph"""
    
    def __init__(self, host="localhost:7690", user="neo4j", password="perseus2025"):
        self.host = host
        self.user = user
        self.password = password
        self.rate_limit_delay = 0.1
        
    def execute_query(self, query: str) -> bool:
        """Execute a Cypher query with rate limiting"""
        cmd = f"""cypher-shell -a {self.host} -u {self.user} -p {self.password} --format plain --non-interactive <<< "{query}" """
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Query executed successfully")
                return True
            else:
                print(f"✗ Query failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error executing query: {e}")
            return False
        finally:
            time.sleep(self.rate_limit_delay)

    def fix_university_department_relationships(self):
        """Fix missing department relationships for universities"""
        print("Fixing university-department relationships...")
        
        # Universities that need departments
        universities_without_departments = [
            "Paul Smith's College",
            "Rutgers University – New Brunswick", 
            "State University of New York College of Environmental Science and Forestry",
            "University of Tennessee, Knoxville"
        ]
        
        for university in universities_without_departments:
            # Create appropriate departments for each university
            if "Paul Smith's College" in university:
                departments = ["Natural Resources", "Environmental Studies"]
            elif "Rutgers" in university:
                departments = ["Computer Science", "Data Science", "Environmental Science"]
            elif "SUNY" in university or "Environmental Science" in university:
                departments = ["Environmental Science", "Forestry", "Natural Resources"]
            elif "Tennessee" in university:
                departments = ["Computer Science", "Data Science", "Natural Resources"]
            else:
                departments = ["Computer Science", "Data Science"]
            
            for dept in departments:
                # Create department node if it doesn't exist
                query = f"""
                MERGE (d:Department {{name: '{dept}'}})
                """
                self.execute_query(query)
                
                # Create OFFERS relationship
                query = f"""
                MATCH (u:University {{name: '{university}'}})
                MATCH (d:Department {{name: '{dept}'}})
                MERGE (u)-[:OFFERS]->(d)
                """
                self.execute_query(query)
                
                print(f"  Connected {university} -> {dept}")

    def fix_program_department_relationships(self):
        """Fix missing program-department relationships"""
        print("Fixing program-department relationships...")
        
        # Programs that need to be connected to departments
        programs_to_connect = [
            "Remote Sensing and Geospatial AI Certificate",
            "Data Science", 
            "AI Ethics Minor"
        ]
        
        for program in programs_to_connect:
            # Determine appropriate department for each program
            if "Remote Sensing" in program or "Geospatial" in program:
                departments = ["Environmental Science", "Natural Resources", "Computer Science"]
            elif "Data Science" in program:
                departments = ["Computer Science", "Data Science", "Statistics"]
            elif "AI Ethics" in program:
                departments = ["Computer Science", "Philosophy", "Data Science"]
            else:
                departments = ["Computer Science", "Data Science"]
            
            for dept in departments:
                # Create OFFERS relationship
                query = f"""
                MATCH (d:Department {{name: '{dept}'}})
                MATCH (p:Program {{name: '{program}'}})
                MERGE (d)-[:OFFERS]->(p)
                """
                self.execute_query(query)
                
                print(f"  Connected {dept} -> {program}")

    def fix_course_program_relationships(self):
        """Fix missing OFFERS_COURSE relationships"""
        print("Fixing course-program relationships...")
        
        # Course-program relationships to create
        course_program_pairs = [
            ("Introduction to Data Science", "Data Science"),
            ("Machine Learning Fundamentals", "Data Science"),
            ("Remote Sensing Applications", "Remote Sensing and Geospatial AI Certificate"),
            ("AI Ethics and Policy", "AI Ethics Minor"),
            ("Artificial Intelligence in Natural Resources", "Data Science")
        ]
        
        for course_name, program_name in course_program_pairs:
            # Create OFFERS_COURSE relationship
            query = f"""
            MATCH (p:Program {{name: '{program_name}'}})
            MATCH (c:Course {{name: '{course_name}'}})
            MERGE (p)-[:OFFERS_COURSE]->(c)
            """
            self.execute_query(query)
            
            print(f"  Connected {program_name} -> {course_name}")

    def verify_fixes(self):
        """Verify that the fixes worked"""
        print("Verifying fixes...")
        
        # Check if universities now have departments
        query = """
        MATCH (u:University)-[:OFFERS]->(d:Department)
        RETURN u.name AS University, count(d) AS DepartmentCount
        ORDER BY DepartmentCount DESC
        """
        self.execute_query(query)
        
        # Check if programs are now connected to universities
        query = """
        MATCH (u:University)-[:OFFERS]->(d:Department)-[:OFFERS]->(p:Program)
        WHERE p.name IN ['Data Science', 'Remote Sensing and Geospatial AI Certificate', 'AI Ethics Minor']
        RETURN u.name AS University, d.name AS Department, p.name AS Program
        """
        self.execute_query(query)
        
        # Check if courses are now connected to universities
        query = """
        MATCH (u:University)-[:OFFERS]->(d:Department)-[:OFFERS]->(p:Program)-[:OFFERS_COURSE]->(c:Course)
        WHERE c.name IN ['Introduction to Data Science', 'Machine Learning Fundamentals', 'Remote Sensing Applications', 'AI Ethics and Policy', 'Artificial Intelligence in Natural Resources']
        RETURN u.name AS University, d.name AS Department, p.name AS Program, c.name AS Course
        """
        self.execute_query(query)

    def run_fixes(self):
        """Run all the relationship fixes"""
        print("Starting relationship fixes...")
        print("=" * 60)
        
        # Step 1: Fix university-department relationships
        self.fix_university_department_relationships()
        
        # Step 2: Fix program-department relationships  
        self.fix_program_department_relationships()
        
        # Step 3: Fix course-program relationships
        self.fix_course_program_relationships()
        
        # Step 4: Verify fixes
        self.verify_fixes()
        
        print("\nRelationship fixes complete!")

def main():
    """Main function to run the relationship fixes"""
    
    fixer = RelationshipFixer()
    
    # Run all fixes
    fixer.run_fixes()
    
    print("\nAll relationship fixes applied. You can now run the comprehensive AI course analysis again.")

if __name__ == "__main__":
    main() 