#!/usr/bin/env python3
"""
Database Setup Script for KG-Perseus Project

This script initializes a Neo4j database with the extracted university data.
It creates the database schema and imports data from JSON files.

Usage:
    python database_setup.py --uri <neo4j_uri> --user <username> --password <password>
    
Example:
    python database_setup.py --uri bolt://localhost:7687 --user neo4j --password password
"""

import json
import argparse
import os
from pathlib import Path
from neo4j import GraphDatabase
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Initialize Neo4j database with KG-Perseus data"""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize database connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user
        self.password = password
        
    def close(self):
        """Close database connection"""
        self.driver.close()
        
    def create_constraints(self):
        """Create database constraints and indexes"""
        with self.driver.session() as session:
            # Create constraints for unique properties
            constraints = [
                "CREATE CONSTRAINT university_name IF NOT EXISTS FOR (u:University) REQUIRE u.name IS UNIQUE",
                "CREATE CONSTRAINT program_name IF NOT EXISTS FOR (p:Program) REQUIRE p.name IS UNIQUE",
                "CREATE CONSTRAINT faculty_name IF NOT EXISTS FOR (f:Faculty) REQUIRE f.name IS UNIQUE",
                "CREATE CONSTRAINT department_name IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE",
                "CREATE CONSTRAINT course_name IF NOT EXISTS FOR (c:Course) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT research_center_name IF NOT EXISTS FOR (rc:ResearchCenter) REQUIRE rc.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint already exists or failed: {e}")
                    
    def create_indexes(self):
        """Create database indexes for better performance"""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX university_type IF NOT EXISTS FOR (u:University) ON (u.type)",
                "CREATE INDEX program_level IF NOT EXISTS FOR (p:Program) ON (p.level)",
                "CREATE INDEX program_type IF NOT EXISTS FOR (p:Program) ON (p.type)",
                "CREATE INDEX faculty_research_area IF NOT EXISTS FOR (f:Faculty) ON (f.research_area)",
                "CREATE INDEX course_technology IF NOT EXISTS FOR (c:Course) ON (c.technology_focus)",
                "CREATE INDEX research_center_focus IF NOT EXISTS FOR (rc:ResearchCenter) ON (rc.technology_focus)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"Created index: {index}")
                except Exception as e:
                    logger.warning(f"Index already exists or failed: {e}")
                    
    def clear_database(self):
        """Clear existing data (optional)"""
        with self.driver.session() as session:
            try:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Cleared existing database")
            except Exception as e:
                logger.error(f"Failed to clear database: {e}")
                
    def import_university_data(self, data_dir: str = "extracted_university_data"):
        """Import university data from JSON files"""
        data_path = Path(data_dir)
        if not data_path.exists():
            logger.error(f"Data directory {data_dir} not found")
            return
            
        json_files = list(data_path.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files to import")
        
        for json_file in json_files:
            if json_file.name == "extraction_summary_report.json":
                continue  # Skip summary file
                
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self._import_university_file(data, json_file.name)
                logger.info(f"Imported {json_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to import {json_file.name}: {e}")
                
    def _import_university_file(self, data: Dict[str, Any], filename: str):
        """Import data from a single university JSON file"""
        with self.driver.session() as session:
            # Extract university name from filename
            university_name = filename.replace('_extracted_data.json', '').replace('_', ' ').title()
            
            # Create university node
            session.run("""
                MERGE (u:University {name: $name})
                SET u.source_file = $filename
            """, name=university_name, filename=filename)
            
            # Import programs
            if 'programs' in data:
                for program in data['programs']:
                    self._import_program(session, program, university_name)
                    
            # Import faculty
            if 'faculty' in data:
                for faculty_member in data['faculty']:
                    self._import_faculty(session, faculty_member, university_name)
                    
            # Import research centers
            if 'research_centers' in data:
                for center in data['research_centers']:
                    self._import_research_center(session, center, university_name)
                    
            # Import courses
            if 'courses' in data:
                for course in data['courses']:
                    self._import_course(session, course, university_name)
                    
    def _import_program(self, session, program: Dict[str, Any], university_name: str):
        """Import a program node"""
        if 'name' not in program:
            return
            
        # Determine program level and type
        level = self._classify_program_level(program['name'])
        program_type = self._classify_program_type(program['name'])
        
        session.run("""
            MERGE (p:Program {name: $name})
            SET p.level = $level, p.type = $type
            WITH p
            MATCH (u:University {name: $university})
            MERGE (u)-[:OFFERS]->(p)
        """, name=program['name'], level=level, type=program_type, university=university_name)
        
    def _import_faculty(self, session, faculty: Dict[str, Any], university_name: str):
        """Import a faculty member node"""
        if 'name' not in faculty:
            return
            
        session.run("""
            MERGE (f:Faculty {name: $name})
            SET f.research_area = $research_area
            WITH f
            MATCH (u:University {name: $university})
            MERGE (u)-[:HAS]->(f)
        """, name=faculty['name'], 
                   research_area=faculty.get('research_area', 'Unknown'),
                   university=university_name)
        
    def _import_research_center(self, session, center: Dict[str, Any], university_name: str):
        """Import a research center node"""
        if 'name' not in center:
            return
            
        # Determine technology focus
        focus = self._classify_technology_focus(center['name'])
        
        session.run("""
            MERGE (rc:ResearchCenter {name: $name})
            SET rc.technology_focus = $focus
            WITH rc
            MATCH (u:University {name: $university})
            MERGE (u)-[:HAS]->(rc)
        """, name=center['name'], focus=focus, university=university_name)
        
    def _import_course(self, session, course: Dict[str, Any], university_name: str):
        """Import a course node"""
        if 'name' not in course:
            return
            
        # Determine technology focus
        focus = self._classify_technology_focus(course.get('description', ''))
        
        session.run("""
            MERGE (c:Course {name: $name})
            SET c.technology_focus = $focus, c.description = $description
            WITH c
            MATCH (u:University {name: $university})
            MERGE (u)-[:OFFERS]->(c)
        """, name=course['name'], 
                   focus=focus,
                   description=course.get('description', ''),
                   university=university_name)
        
    def _classify_program_level(self, program_name: str) -> str:
        """Classify program level based on name"""
        name_lower = program_name.lower()
        if any(word in name_lower for word in ['bachelor', 'bs', 'ba', 'undergraduate', 'associate']):
            return 'Undergraduate'
        elif any(word in name_lower for word in ['master', 'ms', 'ma', 'mba', 'graduate']):
            return 'Master'
        elif any(word in name_lower for word in ['phd', 'ph.d.', 'doctorate', 'doctoral']):
            return 'Doctoral'
        else:
            return 'Unknown'
            
    def _classify_program_type(self, program_name: str) -> str:
        """Classify program type based on name"""
        name_lower = program_name.lower()
        if any(word in name_lower for word in ['forestry', 'forest', 'natural resource', 'environmental']):
            return 'Forestry/Environmental'
        elif any(word in name_lower for word in ['geography', 'geospatial', 'gis']):
            return 'Geography/Geospatial'
        elif any(word in name_lower for word in ['computer science', 'data science', 'informatics']):
            return 'Computer Science/Data Science'
        else:
            return 'Other'
            
    def _classify_technology_focus(self, text: str) -> str:
        """Classify technology focus based on text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            return 'AI/ML'
        elif any(word in text_lower for word in ['gis', 'geospatial', 'geographic', 'spatial']):
            return 'GIS'
        elif any(word in text_lower for word in ['remote sensing', 'satellite', 'aerial', 'sensor']):
            return 'Remote Sensing'
        elif any(word in text_lower for word in ['drone', 'uav', 'unmanned aerial']):
            return 'Drones/UAV'
        else:
            return 'Other'
            
    def verify_import(self):
        """Verify the imported data"""
        with self.driver.session() as session:
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as node_type, count(n) as count
                ORDER BY count DESC
            """)
            
            logger.info("Database import verification:")
            for record in result:
                logger.info(f"  {record['node_type']}: {record['count']}")
                
            # Count relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """)
            
            logger.info("Relationship counts:")
            for record in result:
                logger.info(f"  {record['relationship_type']}: {record['count']}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize Neo4j database with KG-Perseus data')
    parser.add_argument('--uri', required=True, help='Neo4j database URI')
    parser.add_argument('--user', required=True, help='Neo4j username')
    parser.add_argument('--password', required=True, help='Neo4j password')
    parser.add_argument('--clear', action='store_true', help='Clear existing database before import')
    parser.add_argument('--data-dir', default='extracted_university_data', help='Directory containing JSON data files')
    
    args = parser.parse_args()
    
    # Initialize database
    initializer = DatabaseInitializer(args.uri, args.user, args.password)
    
    try:
        logger.info("Starting database initialization...")
        
        if args.clear:
            initializer.clear_database()
            
        # Create schema
        logger.info("Creating database schema...")
        initializer.create_constraints()
        initializer.create_indexes()
        
        # Import data
        logger.info("Importing university data...")
        initializer.import_university_data(args.data_dir)
        
        # Verify import
        logger.info("Verifying import...")
        initializer.verify_import()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        initializer.close()

if __name__ == "__main__":
    main()
