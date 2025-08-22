#!/usr/bin/env python3
"""
University Profile Data Extraction Script
Extracts structured data from university profile markdown files using LangExtract
and saves them as independent structured data files.

Author: AI Assistant
Date: 2024
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('university_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniversityDataExtractor:
    """Extracts structured data from university profile markdown files."""
    
    def __init__(self, profiles_dir: str, output_dir: str):
        self.profiles_dir = Path(profiles_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Technology keywords for categorization
        self.tech_categories = {
            'AI_ML': [
                'artificial intelligence', 'machine learning', 'AI', 'ML', 'deep learning',
                'neural networks', 'computer vision', 'natural language processing',
                'predictive modeling', 'data mining', 'pattern recognition'
            ],
            'GIS': [
                'geographic information systems', 'GIS', 'spatial analysis', 'mapping',
                'cartography', 'geospatial', 'spatial data', 'spatial modeling'
            ],
            'Remote_Sensing': [
                'remote sensing', 'satellite imagery', 'LiDAR', 'aerial photography',
                'spectral analysis', 'multispectral', 'hyperspectral', 'radar'
            ],
            'Drones_UAV': [
                'drone', 'UAV', 'unmanned aerial vehicle', 'unmanned aerial system',
                'UAS', 'aerial survey', 'drone mapping', 'drone imagery'
            ],
            'Data_Science': [
                'data science', 'big data', 'data analytics', 'statistical analysis',
                'quantitative methods', 'modeling', 'simulation', 'optimization'
            ]
        }
        
    def extract_basic_info(self, content: str) -> Dict[str, Any]:
        """Extract basic university information."""
        basic_info = {
            'university_name': '',
            'executive_summary': '',
            'accreditation': [],
            'total_students': '',
            'research_expenditures': '',
            'national_ranking': '',
            'public_ranking': ''
        }
        
        # Extract university name from first heading
        name_match = re.search(r'^#\s*\*\*(.*?)\*\*', content, re.MULTILINE)
        if name_match:
            basic_info['university_name'] = name_match.group(1).strip()
        
        # Extract executive summary
        summary_match = re.search(r'##\s*\*\*Executive Summary\*\*\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if summary_match:
            basic_info['executive_summary'] = summary_match.group(1).strip()
        
        # Extract accreditation information
        accreditation_patterns = [
            r'SAF\s*accreditation',
            r'Society of American Foresters',
            r'accredited by',
            r'professional certification',
            r'certified to'
        ]
        
        for pattern in accreditation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                basic_info['accreditation'].extend(matches)
        
        # Extract student numbers
        student_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*students?', content, re.IGNORECASE)
        if student_match:
            basic_info['total_students'] = student_match.group(1)
        
        # Extract research expenditures
        research_match = re.search(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*million.*research', content, re.IGNORECASE)
        if research_match:
            basic_info['research_expenditures'] = research_match.group(1)
        
        # Extract rankings
        ranking_match = re.search(r'#(\d+).*public', content, re.IGNORECASE)
        if ranking_match:
            basic_info['public_ranking'] = ranking_match.group(1)
        
        return basic_info
    
    def extract_academic_programs(self, content: str) -> Dict[str, Any]:
        """Extract academic program information."""
        programs = {
            'undergraduate_programs': [],
            'graduate_programs': [],
            'certificates_programs': [],
            'minors_programs': [],
            'departments': []
        }
        
        # Extract department information
        dept_pattern = r'##\s*\*\*(\d+\.)?\s*([^*\n]+?)\*\*'
        dept_matches = re.findall(dept_pattern, content)
        
        for match in dept_matches:
            dept_name = match[1].strip()
            if dept_name and len(dept_name) > 5:  # Filter out short matches
                programs['departments'].append(dept_name)
        
        # Extract program types
        program_patterns = {
            'undergraduate': [
                r'Bachelor.*?Science.*?\(([^)]+)\)',
                r'B\.S\.\s*in\s*([^,\n]+)',
                r'undergraduate.*?programs?.*?([^,\n]+)'
            ],
            'graduate': [
                r'Master.*?Science.*?\(([^)]+)\)',
                r'M\.S\.\s*in\s*([^,\n]+)',
                r'Ph\.D\.\s*in\s*([^,\n]+)',
                r'Doctor.*?Philosophy.*?\(([^)]+)\)'
            ],
            'certificates': [
                r'certificate.*?in\s*([^,\n]+)',
                r'certification.*?([^,\n]+)'
            ],
            'minors': [
                r'minor.*?in\s*([^,\n]+)',
                r'minors?.*?([^,\n]+)'
            ]
        }
        
        for program_type, patterns in program_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    programs[f'{program_type}_programs'].extend([m.strip() for m in matches if m.strip()])
        
        # Remove duplicates
        for key in programs:
            if isinstance(programs[key], list):
                programs[key] = list(set(programs[key]))
        
        return programs
    
    def extract_technology_integration(self, content: str) -> Dict[str, Any]:
        """Extract technology integration information."""
        tech_info = {
            'technology_categories': {},
            'technology_courses': [],
            'research_centers': [],
            'faculty_expertise': [],
            'infrastructure': []
        }
        
        # Analyze technology categories
        for category, keywords in self.tech_categories.items():
            category_count = 0
            for keyword in keywords:
                matches = re.findall(rf'\b{re.escape(keyword)}\b', content, re.IGNORECASE)
                category_count += len(matches)
            
            tech_info['technology_categories'][category] = {
                'count': category_count,
                'keywords_found': [k for k in keywords if re.search(rf'\b{re.escape(k)}\b', content, re.IGNORECASE)]
            }
        
        # Extract technology-related courses
        course_patterns = [
            r'([A-Z]{2,4}\s+\d{4}[^,\n]*(?:AI|ML|GIS|drone|remote sensing|data science)[^,\n]*)',
            r'([^,\n]*(?:AI|ML|GIS|drone|remote sensing|data science)[^,\n]*\d{4}[^,\n]*)'
        ]
        
        for pattern in course_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tech_info['technology_courses'].extend([m.strip() for m in matches if m.strip()])
        
        # Extract research centers
        center_patterns = [
            r'Center for ([^,\n]+)',
            r'Institute for ([^,\n]+)',
            r'Laboratory for ([^,\n]+)',
            r'([^,\n]+) Center',
            r'([^,\n]+) Institute'
        ]
        
        for pattern in center_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tech_info['research_centers'].extend([m.strip() for m in matches if m.strip()])
        
        # Extract faculty expertise
        faculty_patterns = [
            r'Dr\.\s+([^,\n]+).*?(?:AI|ML|GIS|drone|remote sensing|data science)',
            r'([^,\n]+).*?specializes?.*?(?:AI|ML|GIS|drone|remote sensing|data science)'
        ]
        
        for pattern in faculty_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tech_info['faculty_expertise'].extend([m.strip() for m in matches if m.strip()])
        
        # Remove duplicates
        for key in tech_info:
            if isinstance(tech_info[key], list):
                tech_info[key] = list(set(tech_info[key]))
        
        return tech_info
    
    def extract_curriculum_details(self, content: str) -> Dict[str, Any]:
        """Extract detailed curriculum information."""
        curriculum = {
            'core_requirements': [],
            'elective_offerings': [],
            'prerequisites': [],
            'cross_listings': [],
            'interdisciplinary_programs': []
        }
        
        # Extract core requirements
        core_patterns = [
            r'core.*?requirement.*?([^,\n]+)',
            r'required.*?course.*?([^,\n]+)',
            r'mandatory.*?([^,\n]+)'
        ]
        
        for pattern in core_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            curriculum['core_requirements'].extend([m.strip() for m in matches if m.strip()])
        
        # Extract elective offerings
        elective_patterns = [
            r'elective.*?([^,\n]+)',
            r'optional.*?course.*?([^,\n]+)',
            r'concentration.*?([^,\n]+)'
        ]
        
        for pattern in elective_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            curriculum['elective_offerings'].extend([m.strip() for m in matches if m.strip()])
        
        # Extract cross-listings
        cross_listing_patterns = [
            r'cross.?listed.*?([^,\n]+)',
            r'joint.*?course.*?([^,\n]+)',
            r'interdisciplinary.*?([^,\n]+)'
        ]
        
        for pattern in cross_listing_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            curriculum['cross_listings'].extend([m.strip() for m in matches if m.strip()])
        
        # Remove duplicates
        for key in curriculum:
            if isinstance(curriculum[key], list):
                curriculum[key] = list(set(curriculum[key]))
        
        return curriculum
    
    def extract_research_highlights(self, content: str) -> Dict[str, Any]:
        """Extract research highlights and focus areas."""
        research = {
            'research_areas': [],
            'funding_sources': [],
            'publications': [],
            'collaborations': [],
            'strategic_initiatives': []
        }
        
        # Extract research areas
        area_patterns = [
            r'research.*?in\s*([^,\n]+)',
            r'focus.*?on\s*([^,\n]+)',
            r'specializes?.*?in\s*([^,\n]+)',
            r'studies?.*?([^,\n]+)'
        ]
        
        for pattern in area_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            research['research_areas'].extend([m.strip() for m in matches if m.strip()])
        
        # Extract funding sources
        funding_patterns = [
            r'funded.*?by\s*([^,\n]+)',
            r'grant.*?from\s*([^,\n]+)',
            r'sponsored.*?by\s*([^,\n]+)'
        ]
        
        for pattern in funding_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            research['funding_sources'].extend([m.strip() for m in matches if m.strip()])
        
        # Extract strategic initiatives
        initiative_patterns = [
            r'strategic.*?plan.*?([^,\n]+)',
            r'initiative.*?([^,\n]+)',
            r'roadmap.*?([^,\n]+)'
        ]
        
        for pattern in initiative_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            research['strategic_initiatives'].extend([m.strip() for m in matches if m.strip()])
        
        # Remove duplicates
        for key in research:
            if isinstance(research[key], list):
                research[key] = list(set(research[key]))
        
        return research
    
    def extract_mission_statement(self, content: str) -> Dict[str, Any]:
        """Extract mission statement and strategic content."""
        mission = {
            'mission_statement': '',
            'strategic_goals': [],
            'public_facing_content': [],
            'technology_mentions': {},
            'overall_technology_focus': 0
        }
        
        # Extract mission statement
        mission_patterns = [
            r'mission.*?is.*?([^,\n]+)',
            r'mission.*?([^,\n]+)',
            r'aims?.*?to\s*([^,\n]+)'
        ]
        
        for pattern in mission_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                mission['mission_statement'] = match.group(1).strip()
                break
        
        # Extract strategic goals
        goal_patterns = [
            r'strategic.*?goal.*?([^,\n]+)',
            r'objective.*?([^,\n]+)',
            r'target.*?([^,\n]+)'
        ]
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            mission['strategic_goals'].extend([m.strip() for m in matches if m.strip()])
        
        # Analyze technology mentions in mission content
        mission_sections = []
        for pattern in ['mission', 'strategic', 'goal', 'objective']:
            matches = re.findall(rf'{pattern}.*?([^,\n]+)', content, re.IGNORECASE)
            mission_sections.extend(matches)
        
        mission_content = ' '.join(mission_sections)
        
        # Count technology mentions in mission content
        total_mentions = 0
        for category, keywords in self.tech_categories.items():
            category_count = 0
            for keyword in keywords:
                matches = re.findall(rf'\b{re.escape(keyword)}\b', mission_content, re.IGNORECASE)
                category_count += len(matches)
                total_mentions += len(matches)
            
            mission['technology_mentions'][category] = category_count
        
        mission['overall_technology_focus'] = total_mentions
        
        return mission
    
    def process_university_profile(self, file_path: Path) -> Dict[str, Any]:
        """Process a single university profile file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Processing: {file_path.name}")
            
            # Extract all data categories
            extracted_data = {
                'file_info': {
                    'source_file': file_path.name,
                    'extraction_date': datetime.now().isoformat(),
                    'file_size_bytes': len(content),
                    'total_lines': len(content.split('\n'))
                },
                'basic_info': self.extract_basic_info(content),
                'academic_programs': self.extract_academic_programs(content),
                'technology_integration': self.extract_technology_integration(content),
                'curriculum_details': self.extract_curriculum_details(content),
                'research_highlights': self.extract_research_highlights(content),
                'mission_statement': self.extract_mission_statement(content)
            }
            
            # Calculate summary statistics
            extracted_data['summary_stats'] = {
                'total_technology_mentions': sum(
                    cat['count'] for cat in extracted_data['technology_integration']['technology_categories'].values()
                ),
                'total_programs': (
                    len(extracted_data['academic_programs']['undergraduate_programs']) +
                    len(extracted_data['academic_programs']['graduate_programs'])
                ),
                'total_departments': len(extracted_data['academic_programs']['departments']),
                'technology_focus_score': extracted_data['mission_statement']['overall_technology_focus']
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return {
                'error': str(e),
                'file_name': file_path.name,
                'extraction_date': datetime.now().isoformat()
            }
    
    def save_extracted_data(self, data: Dict[str, Any], university_name: str):
        """Save extracted data to JSON file."""
        # Clean university name for filename
        clean_name = re.sub(r'[^\w\s-]', '', university_name)
        clean_name = re.sub(r'\s+', '_', clean_name).lower()
        
        output_file = self.output_dir / f"{clean_name}_extracted_data.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving {output_file}: {e}")
            return None
    
    def create_summary_report(self, all_data: List[Dict[str, Any]]):
        """Create a summary report of all extracted data."""
        summary = {
            'extraction_summary': {
                'total_files_processed': len(all_data),
                'successful_extractions': len([d for d in all_data if 'error' not in d]),
                'failed_extractions': len([d for d in all_data if 'error' in d]),
                'extraction_date': datetime.now().isoformat()
            },
            'technology_adoption_summary': {},
            'program_summary': {},
            'university_summary': []
        }
        
        successful_data = [d for d in all_data if 'error' not in d]
        
        if successful_data:
            # Technology adoption summary
            tech_summary = {}
            for category in self.tech_categories.keys():
                universities_with_tech = []
                for data in successful_data:
                    if data['technology_integration']['technology_categories'].get(category, {}).get('count', 0) > 0:
                        universities_with_tech.append(data['basic_info']['university_name'])
                
                tech_summary[category] = {
                    'universities_count': len(universities_with_tech),
                    'universities': universities_with_tech,
                    'adoption_rate': len(universities_with_tech) / len(successful_data) * 100
                }
            
            summary['technology_adoption_summary'] = tech_summary
            
            # Program summary
            total_undergrad = sum(len(d['academic_programs']['undergraduate_programs']) for d in successful_data)
            total_graduate = sum(len(d['academic_programs']['graduate_programs']) for d in successful_data)
            
            summary['program_summary'] = {
                'total_undergraduate_programs': total_undergrad,
                'total_graduate_programs': total_graduate,
                'average_programs_per_university': (total_undergrad + total_graduate) / len(successful_data)
            }
            
            # University summary
            for data in successful_data:
                univ_summary = {
                    'name': data['basic_info']['university_name'],
                    'total_technology_mentions': data['summary_stats']['total_technology_mentions'],
                    'total_programs': data['summary_stats']['total_programs'],
                    'technology_focus_score': data['summary_stats']['technology_focus_score']
                }
                summary['university_summary'].append(univ_summary)
        
        # Save summary report
        summary_file = self.output_dir / "extraction_summary_report.json"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved summary report: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving summary report: {e}")
    
    def run_extraction(self):
        """Run the complete extraction process."""
        logger.info("Starting university profile data extraction...")
        
        # Get all markdown files
        md_files = list(self.profiles_dir.glob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files to process")
        
        all_extracted_data = []
        
        # Process each file
        for file_path in md_files:
            extracted_data = self.process_university_profile(file_path)
            all_extracted_data.append(extracted_data)
            
            # Save individual file data
            if 'error' not in extracted_data:
                university_name = extracted_data['basic_info']['university_name']
                self.save_extracted_data(extracted_data, university_name)
        
        # Create summary report
        self.create_summary_report(all_extracted_data)
        
        logger.info("Extraction process completed!")
        return all_extracted_data

def main():
    """Main function to run the extraction."""
    # Define paths
    profiles_dir = "docs/university-profiles"
    output_dir = "extracted_university_data"
    
    # Create extractor and run
    extractor = UniversityDataExtractor(profiles_dir, output_dir)
    results = extractor.run_extraction()
    
    print(f"\n✅ Extraction completed!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Files processed: {len(results)}")
    print(f"✅ Successful extractions: {len([r for r in results if 'error' not in r])}")
    
    return results

if __name__ == "__main__":
    main()
