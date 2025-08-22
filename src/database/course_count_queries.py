from neo4j import GraphDatabase
import pandas as pd

# Neo4j connection
uri = "bolt://localhost:7689"
username = "neo4j"
password = "perseus2025"

driver = GraphDatabase.driver(uri, auth=(username, password))

def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        return result.data()

# Query 1: Total number of courses in the database
query1 = """
MATCH (c:Course)
RETURN count(c) as total_courses
"""

# Query 2: Courses by technology area
query2 = """
MATCH (c:Course)
WHERE toLower(c.name) CONTAINS 'ai' OR toLower(c.name) CONTAINS 'machine learning' 
   OR toLower(c.name) CONTAINS 'artificial intelligence' OR toLower(c.name) CONTAINS 'data science'
   OR toLower(c.name) CONTAINS 'gis' OR toLower(c.name) CONTAINS 'geographic information'
   OR toLower(c.name) CONTAINS 'remote sensing' OR toLower(c.name) CONTAINS 'drone'
   OR toLower(c.name) CONTAINS 'uav' OR toLower(c.name) CONTAINS 'unmanned aerial'
RETURN c.name as course_name, c.course_type as course_type, c.credits as credits
"""

# Query 3: Total number of universities
query3 = """
MATCH (u:University)
RETURN count(u) as total_universities
"""

# Query 4: Total number of programs
query4 = """
MATCH (p:Program)
RETURN count(p) as total_programs
"""

# Query 5: Courses with relationships to programs
query5 = """
MATCH (c:Course)-[r]-(p:Program)
RETURN count(DISTINCT c) as courses_with_program_relationships
"""

# Query 6: Detailed course breakdown
query6 = """
MATCH (c:Course)
OPTIONAL MATCH (c)-[r]-(p:Program)
RETURN c.name as course_name, 
       c.course_type as course_type,
       c.credits as credits,
       type(r) as relationship_type,
       p.name as program_name
ORDER BY c.name
"""

print("Running queries on Neo4j database...")
print("=" * 50)

# Execute queries
try:
    # Total courses
    result1 = run_query(query1)
    total_courses = result1[0]['total_courses']
    print(f"Total courses in database: {total_courses}")
    
    # Total universities
    result3 = run_query(query3)
    total_universities = result3[0]['total_universities']
    print(f"Total universities in database: {total_universities}")
    
    # Total programs
    result4 = run_query(query4)
    total_programs = result4[0]['total_programs']
    print(f"Total programs in database: {total_programs}")
    
    # Courses with program relationships
    result5 = run_query(query5)
    courses_with_relationships = result5[0]['courses_with_program_relationships']
    print(f"Courses with program relationships: {courses_with_relationships}")
    
    # Technology courses
    result2 = run_query(query2)
    tech_courses = len(result2)
    print(f"Technology-related courses found: {tech_courses}")
    
    # Detailed breakdown
    result6 = run_query(query6)
    print(f"\nDetailed course breakdown (showing first 20):")
    print("-" * 80)
    
    for i, course in enumerate(result6[:20]):
        print(f"{i+1}. {course['course_name']} | Type: {course['course_type']} | Credits: {course['credits']} | Relationship: {course['relationship_type']} | Program: {course['program_name']}")
    
    if len(result6) > 20:
        print(f"... and {len(result6) - 20} more courses")
    
    # Technology course details
    if result2:
        print(f"\nTechnology-related courses:")
        print("-" * 50)
        for i, course in enumerate(result2):
            print(f"{i+1}. {course['course_name']} | Type: {course['course_type']} | Credits: {course['credits']}")
    
    # Summary statistics
    print(f"\n" + "=" * 50)
    print("SUMMARY STATISTICS:")
    print(f"• Total Universities: {total_universities}")
    print(f"• Total Programs: {total_programs}")
    print(f"• Total Courses: {total_courses}")
    print(f"• Courses with Program Relationships: {courses_with_relationships}")
    print(f"• Technology-Related Courses: {tech_courses}")
    print(f"• Technology Course Percentage: {(tech_courses/total_courses*100):.1f}%" if total_courses > 0 else "N/A")

except Exception as e:
    print(f"Error running queries: {e}")

finally:
    driver.close()

print("Running graph structure investigation queries...")
print("=" * 50)

# 1. List all node labels
query_labels = """
CALL db.labels() YIELD label
RETURN label
"""

# 2. Check for course-like properties in Program nodes
query_program_course_props = """
MATCH (p:Program)
WITH p, [k IN keys(p) WHERE toLower(k) CONTAINS 'course'] AS course_keys
WHERE size(course_keys) > 0
RETURN p.name AS program_name, course_keys, [key IN course_keys | p[key]] AS course_values
LIMIT 20
"""

try:
    # 1. List all node labels
    labels = run_query(query_labels)
    print("Node labels in database:")
    for l in labels:
        print(f"- {l['label']}")
    print()

    # 2. Check for course-like properties in Program nodes
    print("Sample of Program nodes with course-like properties:")
    program_course_props = run_query(query_program_course_props)
    for entry in program_course_props:
        print(f"Program: {entry['program_name']}")
        print(f"Course-like keys: {entry['course_keys']}")
        print(f"Values: {entry['course_values']}")
        print("-")
    if not program_course_props:
        print("No Program nodes with course-like properties found.")

except Exception as e:
    print(f"Error running investigation queries: {e}")
finally:
    driver.close() 