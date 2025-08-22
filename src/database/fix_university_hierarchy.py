#!/usr/bin/env python3
"""
Fix University Hierarchy in Graph Database
Rectifies inconsistencies between university profiles and graph database structure.
Ensures proper hierarchy: University -> Departments -> Programs
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from neo4j import GraphDatabase
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversityHierarchyFixer:
    """Fix inconsistencies between university profiles and graph database."""
    
    def __init__(self, profiles_dir: Path = None, graph_db_dir: Path = None):
        """Initialize with directories."""
        self.profiles_dir = profiles_dir or Path('docs')
        self.graph_db_dir = graph_db_dir or Path('data/raw')
        self.fixes_applied = []
        
    def extract_university_name_from_filename(self, filename: str) -> str:
        """Extract university name from markdown filename."""
        # Remove .md extension
        name = filename.replace('.md', '')
        
        # Handle special cases
        name_mapping = {
            'AlabamaAnMUniversity.md': 'Alabama A&M University',
            'AuburnUniversity.md': 'Auburn University',
            'Cal Poly Humboldt.md': 'Cal Poly Humboldt',
            'Cal Poly San Luis Obispo.md': 'Cal Poly San Luis Obispo',
            'University of Arkansas at Monticello .md': 'University of Arkansas at Monticello',
            'University of Maine .md': 'University of Maine',
            'Paul Smith\'s College of Arts and Sciences.md': 'Paul Smith\'s College of Arts and Sciences'
        }
        
        if filename in name_mapping:
            return name_mapping[filename]
        
        # Handle common patterns
        if name.startswith('University of '):
            return name
        elif name.endswith('University'):
            return name
        elif name.endswith('College'):
            return name
        elif name.endswith('Institute'):
            return name
        else:
            # Try to reconstruct university name
            name = name.replace('_', ' ')
            name = name.replace('-', ' ')
            return name
    
    def get_university_profiles(self) -> Dict[str, Path]:
        """Get all university profile files."""
        profiles = {}
        
        for file_path in self.profiles_dir.glob('*.md'):
            if file_path.name.startswith('University of ') or \
               file_path.name.endswith('University.md') or \
               file_path.name.endswith('College.md') or \
               file_path.name.endswith('Institute.md'):
                
                university_name = self.extract_university_name_from_filename(file_path.name)
                profiles[university_name] = file_path
        
        logger.info(f"Found {len(profiles)} university profile files")
        return profiles
    
    def get_graph_db_files(self) -> Dict[str, Path]:
        """Get all graph database files."""
        graph_files = {}
        
        for file_path in self.graph_db_dir.glob('extracted_kg_*.json'):
            # Extract university name from filename
            filename = file_path.name
            if filename.startswith('extracted_kg_') and filename.endswith('.json'):
                university_name = filename[13:-5]  # Remove 'extracted_kg_' and '.json'
                university_name = university_name.replace('_', ' ')
                graph_files[university_name] = file_path
        
        logger.info(f"Found {len(graph_files)} graph database files")
        return graph_files
    
    def analyze_hierarchy_issues(self) -> Dict[str, List[str]]:
        """Analyze hierarchy issues between profiles and graph DB."""
        logger.info("Analyzing hierarchy issues...")
        
        profiles = self.get_university_profiles()
        graph_files = self.get_graph_db_files()
        
        issues = {
            'missing_graph_files': [],
            'missing_profiles': [],
            'hierarchy_mismatches': [],
            'relationship_issues': []
        }
        
        # Check for missing graph files
        for profile_name in profiles.keys():
            if profile_name not in graph_files:
                issues['missing_graph_files'].append(profile_name)
        
        # Check for missing profiles
        for graph_name in graph_files.keys():
            if graph_name not in profiles:
                issues['missing_profiles'].append(graph_name)
        
        # Analyze hierarchy in graph files
        for university_name, graph_file in graph_files.items():
            try:
                with open(graph_file, 'r') as f:
                    graph_data = json.load(f)
                
                # Check if university entity exists
                university_entities = [e for e in graph_data['entities'] if e['type'] == 'University']
                if not university_entities:
                    issues['hierarchy_mismatches'].append(f"{university_name}: No University entity found")
                    continue
                
                # Check relationships
                relationships = graph_data.get('relationships', [])
                university_id = university_entities[0]['id']
                
                # Check for proper LOCATED_IN relationships
                located_in_rels = [r for r in relationships if r['source'] == university_id and r['type'] == 'LOCATED_IN']
                if not located_in_rels:
                    issues['relationship_issues'].append(f"{university_name}: No LOCATED_IN relationships found")
                
                # Check for OFFERS relationships
                offers_rels = [r for r in relationships if r['type'] == 'OFFERS']
                if not offers_rels:
                    issues['relationship_issues'].append(f"{university_name}: No OFFERS relationships found")
                
            except Exception as e:
                issues['hierarchy_mismatches'].append(f"{university_name}: Error reading graph file - {e}")
        
        return issues
    
    def fix_hierarchy_issues(self) -> Dict[str, Any]:
        """Fix hierarchy issues in graph database files."""
        logger.info("Fixing hierarchy issues...")
        
        fixes = {
            'files_updated': [],
            'relationships_added': [],
            'entities_created': [],
            'errors': []
        }
        
        graph_files = self.get_graph_db_files()
        
        for university_name, graph_file in graph_files.items():
            try:
                logger.info(f"Processing {university_name}...")
                
                with open(graph_file, 'r') as f:
                    graph_data = json.load(f)
                
                # Ensure university entity exists and is properly structured
                university_entities = [e for e in graph_data['entities'] if e['type'] == 'University']
                if not university_entities:
                    # Create university entity
                    university_entity = {
                        "id": university_name.replace(' ', '_').upper(),
                        "name": university_name,
                        "type": "University",
                        "properties": {
                            "description": f"University profile for {university_name}",
                            "source": "university_profile",
                            "year": "N/A",
                            "accreditation_status": "N/A"
                        }
                    }
                    graph_data['entities'].append(university_entity)
                    fixes['entities_created'].append(f"Created University entity for {university_name}")
                
                university_id = university_entities[0]['id'] if university_entities else university_name.replace(' ', '_').upper()
                
                # Fix relationships to ensure proper hierarchy
                relationships = graph_data.get('relationships', [])
                fixed_relationships = []
                
                # Track existing relationships to avoid duplicates
                existing_rels = set()
                
                for rel in relationships:
                    rel_key = f"{rel['source']}-{rel['type']}-{rel['target']}"
                    if rel_key not in existing_rels:
                        fixed_relationships.append(rel)
                        existing_rels.add(rel_key)
                
                # Ensure departments are properly connected to university
                department_entities = [e for e in graph_data['entities'] if e['type'] == 'Department']
                for dept in department_entities:
                    dept_id = dept['id']
                    rel_key = f"{university_id}-LOCATED_IN-{dept_id}"
                    
                    if rel_key not in existing_rels:
                        located_in_rel = {
                            "source": university_id,
                            "target": dept_id,
                            "type": "LOCATED_IN",
                            "properties": {
                                "description": f"{dept['name']} is located within {university_name}",
                                "year": "N/A",
                                "status": "active"
                            }
                        }
                        fixed_relationships.append(located_in_rel)
                        fixes['relationships_added'].append(f"Added LOCATED_IN relationship for {dept['name']}")
                
                # Ensure programs are properly connected to departments
                program_entities = [e for e in graph_data['entities'] if e['type'] == 'Program']
                for prog in program_entities:
                    prog_id = prog['id']
                    
                    # Find department that offers this program
                    offers_rels = [r for r in relationships if r['target'] == prog_id and r['type'] == 'OFFERS']
                    
                    if not offers_rels:
                        # Connect to first available department
                        if department_entities:
                            dept_id = department_entities[0]['id']
                            rel_key = f"{dept_id}-OFFERS-{prog_id}"
                            
                            if rel_key not in existing_rels:
                                offers_rel = {
                                    "source": dept_id,
                                    "target": prog_id,
                                    "type": "OFFERS",
                                    "properties": {
                                        "description": f"{department_entities[0]['name']} offers {prog['name']}",
                                        "year": "N/A",
                                        "status": "active"
                                    }
                                }
                                fixed_relationships.append(offers_rel)
                                fixes['relationships_added'].append(f"Added OFFERS relationship for {prog['name']}")
                
                # Update the graph data
                graph_data['relationships'] = fixed_relationships
                
                # Save updated file
                with open(graph_file, 'w') as f:
                    json.dump(graph_data, f, indent=2)
                
                fixes['files_updated'].append(university_name)
                
            except Exception as e:
                fixes['errors'].append(f"Error processing {university_name}: {e}")
        
        return fixes
    
    def validate_hierarchy(self) -> Dict[str, Any]:
        """Validate the hierarchy after fixes."""
        logger.info("Validating hierarchy...")
        
        validation_results = {
            'universities_with_proper_hierarchy': [],
            'universities_with_issues': [],
            'total_relationships': 0,
            'hierarchy_issues': []
        }
        
        graph_files = self.get_graph_db_files()
        
        for university_name, graph_file in graph_files.items():
            try:
                with open(graph_file, 'r') as f:
                    graph_data = json.load(f)
                
                entities = graph_data.get('entities', [])
                relationships = graph_data.get('relationships', [])
                
                # Check for university entity
                university_entities = [e for e in entities if e['type'] == 'University']
                if not university_entities:
                    validation_results['universities_with_issues'].append(university_name)
                    validation_results['hierarchy_issues'].append(f"{university_name}: No University entity")
                    continue
                
                university_id = university_entities[0]['id']
                
                # Check for departments
                department_entities = [e for e in entities if e['type'] == 'Department']
                
                # Check for programs
                program_entities = [e for e in entities if e['type'] == 'Program']
                
                # Validate relationships
                located_in_rels = [r for r in relationships if r['source'] == university_id and r['type'] == 'LOCATED_IN']
                offers_rels = [r for r in relationships if r['type'] == 'OFFERS']
                
                validation_results['total_relationships'] += len(relationships)
                
                # Check hierarchy completeness
                if department_entities and not located_in_rels:
                    validation_results['hierarchy_issues'].append(f"{university_name}: Departments not connected to university")
                
                if program_entities and not offers_rels:
                    validation_results['hierarchy_issues'].append(f"{university_name}: Programs not connected to departments")
                
                if not validation_results['hierarchy_issues']:
                    validation_results['universities_with_proper_hierarchy'].append(university_name)
                else:
                    validation_results['universities_with_issues'].append(university_name)
                
            except Exception as e:
                validation_results['universities_with_issues'].append(university_name)
                validation_results['hierarchy_issues'].append(f"{university_name}: Error - {e}")
        
        return validation_results
    
    def generate_fix_report(self, issues: Dict[str, List[str]], fixes: Dict[str, Any], validation: Dict[str, Any]) -> str:
        """Generate a comprehensive report of the fixes applied."""
        
        report_lines = [
            "# University Hierarchy Fix Report",
            "",
            "## Issues Found",
            f"- Missing Graph Files: {len(issues['missing_graph_files'])}",
            f"- Missing Profiles: {len(issues['missing_profiles'])}",
            f"- Hierarchy Mismatches: {len(issues['hierarchy_mismatches'])}",
            f"- Relationship Issues: {len(issues['relationship_issues'])}",
            "",
            "## Fixes Applied",
            f"- Files Updated: {len(fixes['files_updated'])}",
            f"- Relationships Added: {len(fixes['relationships_added'])}",
            f"- Entities Created: {len(fixes['entities_created'])}",
            f"- Errors: {len(fixes['errors'])}",
            "",
            "## Validation Results",
            f"- Universities with Proper Hierarchy: {len(validation['universities_with_proper_hierarchy'])}",
            f"- Universities with Issues: {len(validation['universities_with_issues'])}",
            f"- Total Relationships: {validation['total_relationships']}",
            f"- Hierarchy Issues: {len(validation['hierarchy_issues'])}",
            "",
            "## Detailed Issues"
        ]
        
        for category, items in issues.items():
            if items:
                report_lines.append(f"\n### {category.replace('_', ' ').title()}")
                for item in items:
                    report_lines.append(f"- {item}")
        
        if fixes['errors']:
            report_lines.append("\n### Errors During Fix")
            for error in fixes['errors']:
                report_lines.append(f"- {error}")
        
        if validation['hierarchy_issues']:
            report_lines.append("\n### Remaining Hierarchy Issues")
            for issue in validation['hierarchy_issues']:
                report_lines.append(f"- {issue}")
        
        return "\n".join(report_lines)
    
    def save_fix_report(self, report: str, output_dir: Path = None):
        """Save the fix report to file."""
        if output_dir is None:
            output_dir = Path('data/outputs')
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'university_hierarchy_fix_report.md', 'w') as f:
            f.write(report)
        
        logger.info(f"Fix report saved to {output_dir / 'university_hierarchy_fix_report.md'}")

def main():
    """Main execution function."""
    try:
        logger.info("Starting university hierarchy fix...")
        
        # Initialize fixer
        fixer = UniversityHierarchyFixer()
        
        # Analyze issues
        issues = fixer.analyze_hierarchy_issues()
        logger.info(f"Found {sum(len(v) for v in issues.values())} issues")
        
        # Apply fixes
        fixes = fixer.fix_hierarchy_issues()
        logger.info(f"Applied {len(fixes['files_updated'])} fixes")
        
        # Validate results
        validation = fixer.validate_hierarchy()
        logger.info(f"Validation complete: {len(validation['universities_with_proper_hierarchy'])} universities with proper hierarchy")
        
        # Generate and save report
        report = fixer.generate_fix_report(issues, fixes, validation)
        fixer.save_fix_report(report)
        
        # Print summary
        print("\n" + "="*80)
        print("UNIVERSITY HIERARCHY FIX SUMMARY")
        print("="*80)
        print(f"Files Updated: {len(fixes['files_updated'])}")
        print(f"Relationships Added: {len(fixes['relationships_added'])}")
        print(f"Entities Created: {len(fixes['entities_created'])}")
        print(f"Universities with Proper Hierarchy: {len(validation['universities_with_proper_hierarchy'])}")
        print(f"Remaining Issues: {len(validation['hierarchy_issues'])}")
        print("="*80)
        
        logger.info("University hierarchy fix completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"University hierarchy fix failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 