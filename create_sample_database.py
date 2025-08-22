#!/usr/bin/env python3
"""
Create Sample Database Script for KG-Perseus Project

This script creates a smaller sample database from the extracted university data
for testing and demonstration purposes. It selects a subset of universities
and their associated data to create a manageable sample.

Usage:
    python create_sample_database.py --output sample_data.json --universities 10
"""

import json
import argparse
import random
from pathlib import Path
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SampleDatabaseCreator:
    """Create a sample database from extracted university data"""
    
    def __init__(self, data_dir: str = "extracted_university_data"):
        """Initialize with data directory"""
        self.data_dir = Path(data_dir)
        self.universities = []
        
    def load_universities(self):
        """Load all university data files"""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory {self.data_dir} not found")
            
        json_files = list(self.data_dir.glob("*.json"))
        json_files = [f for f in json_files if f.name != "extraction_summary_report.json"]
        
        logger.info(f"Found {len(json_files)} university data files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Extract university name from filename
                university_name = json_file.name.replace('_extracted_data.json', '').replace('_', ' ').title()
                
                # Add university name to data
                data['university_name'] = university_name
                data['source_file'] = json_file.name
                
                self.universities.append(data)
                logger.info(f"Loaded {university_name}")
                
            except Exception as e:
                logger.error(f"Failed to load {json_file.name}: {e}")
                
    def create_sample(self, num_universities: int = 10, random_seed: int = None):
        """Create a sample database with specified number of universities"""
        if random_seed:
            random.seed(random_seed)
            
        if num_universities >= len(self.universities):
            logger.warning(f"Requested {num_universities} universities, but only {len(self.universities)} available")
            selected_universities = self.universities
        else:
            selected_universities = random.sample(self.universities, num_universities)
            
        logger.info(f"Selected {len(selected_universities)} universities for sample")
        
        # Create sample database structure
        sample_db = {
            "metadata": {
                "type": "sample_database",
                "total_universities": len(selected_universities),
                "source": "KG-Perseus extracted university data",
                "created": "2024",
                "description": f"Sample database with {len(selected_universities)} universities for testing and demonstration"
            },
            "universities": selected_universities,
            "statistics": self._calculate_statistics(selected_universities)
        }
        
        return sample_db
        
    def _calculate_statistics(self, universities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for the sample database"""
        stats = {
            "total_programs": 0,
            "total_courses": 0,
            "total_faculty": 0,
            "total_research_centers": 0,
            "programs_by_level": {},
            "programs_by_type": {},
            "technology_focus": {}
        }
        
        for university in universities:
            # Count programs
            if 'programs' in university:
                stats['total_programs'] += len(university['programs'])
                
                for program in university['programs']:
                    # Program level classification
                    level = self._classify_program_level(program.get('name', ''))
                    stats['programs_by_level'][level] = stats['programs_by_level'].get(level, 0) + 1
                    
                    # Program type classification
                    program_type = self._classify_program_type(program.get('name', ''))
                    stats['programs_by_type'][program_type] = stats['programs_by_type'].get(program_type, 0) + 1
                    
            # Count courses
            if 'courses' in university:
                stats['total_courses'] += len(university['courses'])
                
            # Count faculty
            if 'faculty' in university:
                stats['total_faculty'] += len(university['faculty'])
                
            # Count research centers
            if 'research_centers' in university:
                stats['total_research_centers'] += len(university['research_centers'])
                
        return stats
        
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
            
    def save_sample(self, sample_db: Dict[str, Any], output_file: str):
        """Save the sample database to a JSON file"""
        output_path = Path(output_file)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sample_db, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Sample database saved to {output_path}")
            
            # Print summary
            print("\n" + "="*60)
            print("SAMPLE DATABASE CREATED SUCCESSFULLY")
            print("="*60)
            print(f"Output file: {output_path}")
            print(f"Universities included: {sample_db['metadata']['total_universities']}")
            print(f"Total programs: {sample_db['statistics']['total_programs']}")
            print(f"Total courses: {sample_db['statistics']['total_courses']}")
            print(f"Total faculty: {sample_db['statistics']['total_faculty']}")
            print(f"Total research centers: {sample_db['statistics']['total_research_centers']}")
            print("\nProgram levels:")
            for level, count in sample_db['statistics']['programs_by_level'].items():
                print(f"  {level}: {count}")
            print("\nProgram types:")
            for ptype, count in sample_db['statistics']['programs_by_type'].items():
                print(f"  {ptype}: {count}")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Failed to save sample database: {e}")
            raise

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Create a sample database from KG-Perseus university data')
    parser.add_argument('--output', default='sample_database.json', help='Output file for sample database')
    parser.add_argument('--universities', type=int, default=10, help='Number of universities to include in sample')
    parser.add_argument('--data-dir', default='extracted_university_data', help='Directory containing university data files')
    parser.add_argument('--random-seed', type=int, help='Random seed for reproducible sampling')
    
    args = parser.parse_args()
    
    try:
        # Create sample database
        creator = SampleDatabaseCreator(args.data_dir)
        
        logger.info("Loading university data...")
        creator.load_universities()
        
        logger.info(f"Creating sample with {args.universities} universities...")
        sample_db = creator.create_sample(args.universities, args.random_seed)
        
        logger.info("Saving sample database...")
        creator.save_sample(sample_db, args.output)
        
        logger.info("Sample database creation completed successfully!")
        
    except Exception as e:
        logger.error(f"Sample database creation failed: {e}")
        raise

if __name__ == "__main__":
    main()
