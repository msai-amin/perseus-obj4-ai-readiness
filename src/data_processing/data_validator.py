#!/usr/bin/env python3
"""
KG-Perseus Data Validation Framework
Validates data quality and structure across the project.
"""

import logging
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation and quality checking framework."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path('data')
        self.validation_results = {}
    
    def validate_csv_structure(self, file_path: Path) -> Dict[str, Any]:
        """Validate CSV file structure and content."""
        logger.info(f"Validating CSV file: {file_path}")
        
        result = {
            'file_path': str(file_path),
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'row_count': 0,
            'column_count': 0,
            'empty_cells': 0,
            'duplicate_rows': 0
        }
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Basic structure validation
            result['row_count'] = len(df)
            result['column_count'] = len(df.columns)
            
            # Check for empty dataframe
            if df.empty:
                result['errors'].append("File is empty")
                return result
            
            # Check for minimum columns
            if len(df.columns) < 2:
                result['warnings'].append("File has very few columns")
            
            # Check for empty cells
            empty_cells = df.isnull().sum().sum()
            result['empty_cells'] = empty_cells
            
            if empty_cells > 0:
                result['warnings'].append(f"Found {empty_cells} empty cells")
            
            # Check for duplicate rows
            duplicate_rows = df.duplicated().sum()
            result['duplicate_rows'] = duplicate_rows
            
            if duplicate_rows > 0:
                result['warnings'].append(f"Found {duplicate_rows} duplicate rows")
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 100:
                result['warnings'].append(f"Large file size: {file_size_mb:.2f} MB")
            
            result['is_valid'] = True
            
        except Exception as e:
            result['errors'].append(f"Failed to read CSV file: {e}")
        
        return result
    
    def validate_json_structure(self, file_path: Path) -> Dict[str, Any]:
        """Validate JSON file structure and content."""
        logger.info(f"Validating JSON file: {file_path}")
        
        result = {
            'file_path': str(file_path),
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'entity_count': 0,
            'relationship_count': 0
        }
        
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if data is empty
            if not data:
                result['errors'].append("JSON file is empty")
                return result
            
            # Validate Graph DB structure
            if 'entities' in data:
                result['entity_count'] = len(data['entities'])
                if result['entity_count'] == 0:
                    result['warnings'].append("No entities found")
            
            if 'relationships' in data:
                result['relationship_count'] = len(data['relationships'])
                if result['relationship_count'] == 0:
                    result['warnings'].append("No relationships found")
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 50:
                result['warnings'].append(f"Large file size: {file_size_mb:.2f} MB")
            
            result['is_valid'] = True
            
        except json.JSONDecodeError as e:
            result['errors'].append(f"Invalid JSON format: {e}")
        except Exception as e:
            result['errors'].append(f"Failed to read JSON file: {e}")
        
        return result
    
    def check_data_consistency(self, data_dir: Path) -> List[str]:
        """Check data consistency across files."""
        logger.info("Checking data consistency across files")
        
        issues = []
        
        # Check for consistent column names in CSV files
        csv_files = list(data_dir.rglob('*.csv'))
        if len(csv_files) > 1:
            column_patterns = {}
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    columns = tuple(sorted(df.columns))
                    if columns not in column_patterns:
                        column_patterns[columns] = []
                    column_patterns[columns].append(csv_file.name)
                except Exception as e:
                    issues.append(f"Could not read {csv_file.name}: {e}")
            
            if len(column_patterns) > 3:
                issues.append("Multiple inconsistent column patterns found in CSV files")
        
        # Check for consistent JSON structure
        json_files = list(data_dir.rglob('*.json'))
        if json_files:
            json_structures = {}
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    structure = {
                        'has_entities': 'entities' in data,
                        'has_relationships': 'relationships' in data,
                        'entity_count': len(data.get('entities', [])),
                        'relationship_count': len(data.get('relationships', []))
                    }
                    
                    structure_key = tuple(sorted(structure.items()))
                    if structure_key not in json_structures:
                        json_structures[structure_key] = []
                    json_structures[structure_key].append(json_file.name)
                    
                except Exception as e:
                    issues.append(f"Could not read {json_file.name}: {e}")
            
            if len(json_structures) > 2:
                issues.append("Multiple inconsistent JSON structures found")
        
        return issues
    
    def generate_data_report(self, data_dir: Path) -> Dict[str, Any]:
        """Generate comprehensive data quality report."""
        logger.info("Generating data quality report")
        
        report = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'file_types': {},
            'validation_results': {},
            'consistency_issues': [],
            'recommendations': []
        }
        
        # Validate all files
        for file_path in data_dir.rglob('*'):
            if file_path.is_file():
                report['total_files'] += 1
                
                if file_path.suffix.lower() == '.csv':
                    result = self.validate_csv_structure(file_path)
                    report['file_types']['csv'] = report['file_types'].get('csv', 0) + 1
                elif file_path.suffix.lower() == '.json':
                    result = self.validate_json_structure(file_path)
                    report['file_types']['json'] = report['file_types'].get('json', 0) + 1
                else:
                    continue
                
                report['validation_results'][file_path.name] = result
                
                if result['is_valid']:
                    report['valid_files'] += 1
                else:
                    report['invalid_files'] += 1
        
        # Check consistency
        report['consistency_issues'] = self.check_data_consistency(data_dir)
        
        # Generate recommendations
        if report['invalid_files'] > 0:
            report['recommendations'].append(f"Fix {report['invalid_files']} invalid files")
        
        if report['consistency_issues']:
            report['recommendations'].append("Address data consistency issues")
        
        if report['total_files'] > 100:
            report['recommendations'].append("Consider data archiving for old files")
        
        return report
    
    def validate_all_data(self) -> Dict[str, Any]:
        """Validate all data in the project."""
        logger.info("Starting comprehensive data validation")
        
        validation_summary = {
            'raw_data': self.generate_data_report(self.data_dir / 'raw'),
            'processed_data': self.generate_data_report(self.data_dir / 'processed'),
            'outputs': self.generate_data_report(self.data_dir / 'outputs')
        }
        
        # Overall statistics
        total_files = sum(report['total_files'] for report in validation_summary.values())
        total_valid = sum(report['valid_files'] for report in validation_summary.values())
        total_invalid = sum(report['invalid_files'] for report in validation_summary.values())
        
        validation_summary['overall'] = {
            'total_files': total_files,
            'valid_files': total_valid,
            'invalid_files': total_invalid,
            'validity_rate': (total_valid / total_files * 100) if total_files > 0 else 0
        }
        
        return validation_summary
    
    def save_validation_report(self, report: Dict[str, Any], output_path: Path = None):
        """Save validation report to file."""
        if output_path is None:
            output_path = self.data_dir / 'outputs' / 'data_validation_report.json'
        
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Validation report saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")

def main():
    """Main validation function."""
    try:
        validator = DataValidator()
        report = validator.validate_all_data()
        validator.save_validation_report(report)
        
        # Print summary
        overall = report['overall']
        print(f"\nData Validation Summary:")
        print(f"Total Files: {overall['total_files']}")
        print(f"Valid Files: {overall['valid_files']}")
        print(f"Invalid Files: {overall['invalid_files']}")
        print(f"Validity Rate: {overall['validity_rate']:.1f}%")
        
        if overall['invalid_files'] > 0:
            print(f"\n⚠️  Found {overall['invalid_files']} invalid files that need attention")
            return 1
        else:
            print(f"\n✅ All data files are valid!")
            return 0
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 