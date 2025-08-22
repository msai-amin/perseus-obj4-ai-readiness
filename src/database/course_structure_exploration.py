#!/usr/bin/env python3
"""
Course Structure Exploration
Thoroughly explore how courses are represented in the graph database
"""

from neo4j import GraphDatabase

class CourseStructureExplorer:
    def __init__(self, uri="bolt://localhost:7689", user="neo4j", password="perseus2025"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def explore(self):
        with self.driver.session() as session:
            print("=" * 80)
            print("COURSE STRUCTURE EXPLORATION")
            print("=" * 80)
            
            # 1. List all node labels
            print("\n1. NODE LABELS:")
            node_labels_query = "CALL db.labels() YIELD label RETURN label ORDER BY label"
            result = session.run(node_labels_query)
            for record in result:
                print(f"  Node Label: {record['label']}")
            
            # 2. List all relationship types
            print("\n2. RELATIONSHIP TYPES:")
            rel_types_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
            result = session.run(rel_types_query)
            for record in result:
                print(f"  Relationship Type: {record['relationshipType']}")
            
            # 3. Sample properties for Course nodes
            print("\n3. SAMPLE COURSE NODE PROPERTIES:")
            sample_course_query = "MATCH (c:Course) RETURN c LIMIT 5"
            result = session.run(sample_course_query)
            for record in result:
                print(f"  Course Node Properties: {dict(record['c'])}")
            
            # 4. Sample properties for Program nodes
            print("\n4. SAMPLE PROGRAM NODE PROPERTIES:")
            sample_program_query = "MATCH (p:Program) RETURN p LIMIT 5"
            result = session.run(sample_program_query)
            for record in result:
                print(f"  Program Node Properties: {dict(record['p'])}")
            
            # 5. Check for course-related properties in Program nodes
            print("\n5. COURSE-RELATED PROPERTIES IN PROGRAM NODES:")
            course_prop_query = "MATCH (p:Program) RETURN DISTINCT keys(p) as property_keys LIMIT 10"
            result = session.run(course_prop_query)
            for record in result:
                print(f"  Program Property Keys: {record['property_keys']}")
            
            # 6. Check for course-related relationships from Program nodes
            print("\n6. COURSE-RELATED RELATIONSHIPS FROM PROGRAM NODES:")
            program_course_rel_query = "MATCH (p:Program)-[r]->(n) RETURN DISTINCT type(r) as rel_type, labels(n) as node_labels LIMIT 20"
            result = session.run(program_course_rel_query)
            for record in result:
                print(f"  Relationship: {record['rel_type']} -> Node Labels: {record['node_labels']}")
            
            # 7. Check for course-related relationships to Program nodes
            print("\n7. COURSE-RELATED RELATIONSHIPS TO PROGRAM NODES:")
            program_course_rel_query = "MATCH (n)-[r]->(p:Program) RETURN DISTINCT type(r) as rel_type, labels(n) as node_labels LIMIT 20"
            result = session.run(program_course_rel_query)
            for record in result:
                print(f"  Relationship: {record['rel_type']} <- Node Labels: {record['node_labels']}")
            
            # 8. Check for course lists as properties (array or string) in Program nodes
            print("\n8. SAMPLE COURSE LIST PROPERTIES IN PROGRAM NODES:")
            course_list_query = "MATCH (p:Program) WHERE any(key IN keys(p) WHERE toLower(key) CONTAINS 'course') RETURN p LIMIT 5"
            result = session.run(course_list_query)
            for record in result:
                print(f"  Program with Course Property: {dict(record['p'])}")

def main():
    explorer = CourseStructureExplorer()
    try:
        explorer.explore()
    except Exception as e:
        print(f"Error during exploration: {e}")
    finally:
        explorer.close()

if __name__ == "__main__":
    main() 