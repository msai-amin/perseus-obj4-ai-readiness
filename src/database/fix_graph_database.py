#!/usr/bin/env python3
"""
Script to fix missing OFFERS relationships between universities and departments
in the Neo4j knowledge graph database.

This script:
1. Loads the CSV file with department-university relationships
2. Runs Cypher commands with rate limiting
3. Verifies the fix
4. Tests the original query

Usage:
    python fix_graph_database.py
"""

import time
import subprocess
import sys
from pathlib import Path

def run_cypher_command(command, description, delay_seconds=5):
    """Run a Cypher command with error handling and delays."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        # Run the Cypher command using cypher-shell
        # Adjust the connection parameters as needed for your Neo4j setup
        result = subprocess.run([
            'cypher-shell',
            '-u', 'neo4j',  # Replace with your username
            '-p', 'password',  # Replace with your password
            '--format', 'table',
            '--non-interactive'
        ], input=command.encode(), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Success!")
            print(result.stdout)
        else:
            print("❌ Error:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Error: cypher-shell not found. Please install Neo4j Cypher Shell.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Wait before next command to respect rate limits
    print(f"⏳ Waiting {delay_seconds} seconds before next command...")
    time.sleep(delay_seconds)
    return True

def main():
    """Main function to fix the graph database."""
    print("🔧 Starting Neo4j Graph Database Fix")
    print("This will add missing OFFERS relationships between universities and departments")
    
    # Check if CSV file exists
    csv_file = Path("departments_universities.csv")
    if not csv_file.exists():
        print("❌ Error: departments_universities.csv not found!")
        print("Please ensure the CSV file is in the current directory.")
        return False
    
    # Step 1: Load CSV and create relationships
    step1_command = """
    USING PERIODIC COMMIT 50
    LOAD CSV WITH HEADERS FROM 'file:///departments_universities.csv' AS row
    MATCH (u:University), (d:Department)
    WHERE toLower(u.name) = toLower(row.university_name)
      AND toLower(d.name) = toLower(row.department_name)
    MERGE (u)-[:OFFERS]->(d)
    RETURN count(*) AS Relationships_Created;
    """
    
    if not run_cypher_command(step1_command, "Step 1: Creating OFFERS relationships", delay_seconds=10):
        return False
    
    # Step 2: Verify departments still missing connections
    step2_command = """
    MATCH (d:Department)
    WHERE NOT ( (:University)-[:OFFERS]->(d) )
    RETURN d.name AS Department_Name, d.description AS Department_Description
    ORDER BY d.name
    LIMIT 20;
    """
    
    if not run_cypher_command(step2_command, "Step 2: Checking for departments still missing university connections", delay_seconds=5):
        return False
    
    # Step 3: Count total relationships
    step3_command = """
    MATCH (u:University)-[:OFFERS]->(d:Department)
    RETURN count(*) AS Total_University_Department_Relationships;
    """
    
    if not run_cypher_command(step3_command, "Step 3: Counting total university-department relationships", delay_seconds=5):
        return False
    
    # Step 4: Test the original query
    step4_command = """
    MATCH (u:University)-[:OFFERS]->(d:Department)-[:EMPLOYS]->(f:Faculty)
    WHERE toLower(d.name) CONTAINS 'computer science'
       OR toLower(d.name) CONTAINS 'engineering'
       OR toLower(d.name) CONTAINS 'data science'
       OR toLower(d.description) CONTAINS 'computer science'
       OR toLower(d.description) CONTAINS 'engineering'
       OR toLower(d.description) CONTAINS 'data science'
    RETURN
      u.name AS University,
      d.name AS Department,
      f.name AS Faculty,
      f.description AS Faculty_Description
    ORDER BY University, Department, Faculty
    LIMIT 20;
    """
    
    if not run_cypher_command(step4_command, "Step 4: Testing the original query with university information", delay_seconds=5):
        return False
    
    # Step 5: Get final statistics
    step5_command = """
    MATCH (u:University)-[:OFFERS]->(d:Department)-[:EMPLOYS]->(f:Faculty)
    WHERE toLower(d.name) CONTAINS 'computer science'
       OR toLower(d.name) CONTAINS 'engineering'
       OR toLower(d.name) CONTAINS 'data science'
       OR toLower(d.description) CONTAINS 'computer science'
       OR toLower(d.description) CONTAINS 'engineering'
       OR toLower(d.description) CONTAINS 'data science'
    RETURN 
      count(DISTINCT f) AS Total_Faculty_With_CS_Engineering_DataScience_Appointments,
      count(DISTINCT u) AS Universities_With_Such_Faculty,
      count(DISTINCT d) AS Departments_Involved;
    """
    
    if not run_cypher_command(step5_command, "Step 5: Final statistics", delay_seconds=5):
        return False
    
    print("\n🎉 Graph database fix completed successfully!")
    print("Your queries should now show university information instead of 'Unknown University'.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 