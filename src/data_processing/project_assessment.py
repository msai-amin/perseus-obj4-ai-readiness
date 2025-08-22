#!/usr/bin/env python3
"""
KG-Perseus Project Assessment Script
Identifies critical issues and provides recommendations for cleanup.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any
import json
import pandas as pd
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectAssessment:
    """Assess project state and identify critical issues."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.assessment_results = {}
    
    def assess_file_organization(self) -> Dict[str, Any]:
        """Assess file organization and structure."""
        logger.info("Assessing file organization...")
        
        results = {
            'total_files': 0,
            'file_types': defaultdict(int),
            'directories': [],
            'duplicate_files': [],
            'orphaned_files': [],
            'large_files': [],
            'issues': []
        }
        
        # Analyze all files
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                results['total_files'] += 1
                
                # Count file types
                ext = file_path.suffix.lower()
                results['file_types'][ext] += 1
                
                # Check for large files (>1MB)
                if file_path.stat().st_size > 1024 * 1024:
                    results['large_files'].append({
                        'path': str(file_path.relative_to(self.project_root)),
                        'size_mb': file_path.stat().st_size / (1024 * 1024)
                    })
        
        # Check for potential issues
        if results['file_types']['.py'] > 50:
            results['issues'].append("Too many Python scripts - needs organization")
        
        if results['file_types']['.csv'] > 30:
            results['issues'].append("Too many CSV files - needs data management")
        
        if len(results['large_files']) > 10:
            results['issues'].append("Too many large files - consider compression or cleanup")
        
        return results
    
    def assess_code_quality(self) -> Dict[str, Any]:
        """Assess code quality and structure."""
        logger.info("Assessing code quality...")
        
        results = {
            'python_files': 0,
            'files_with_docstrings': 0,
            'files_with_imports': 0,
            'files_with_main': 0,
            'files_with_logging': 0,
            'files_with_error_handling': 0,
            'issues': []
        }
        
        for file_path in self.project_root.rglob('*.py'):
            results['python_files'] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for various code quality indicators
                if '"""' in content or "'''" in content:
                    results['files_with_docstrings'] += 1
                
                if 'import ' in content:
                    results['files_with_imports'] += 1
                
                if '__main__' in content:
                    results['files_with_main'] += 1
                
                if 'logging' in content:
                    results['files_with_logging'] += 1
                
                if 'try:' in content and 'except' in content:
                    results['files_with_error_handling'] += 1
                
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        # Calculate quality metrics
        if results['python_files'] > 0:
            docstring_rate = results['files_with_docstrings'] / results['python_files']
            logging_rate = results['files_with_logging'] / results['python_files']
            error_handling_rate = results['files_with_error_handling'] / results['python_files']
            
            if docstring_rate < 0.5:
                results['issues'].append("Low documentation rate - needs more docstrings")
            
            if logging_rate < 0.3:
                results['issues'].append("Low logging rate - needs better error tracking")
            
            if error_handling_rate < 0.4:
                results['issues'].append("Low error handling rate - needs better exception handling")
        
        return results
    
    def assess_data_quality(self) -> Dict[str, Any]:
        """Assess data quality and organization."""
        logger.info("Assessing data quality...")
        
        results = {
            'csv_files': 0,
            'json_files': 0,
            'data_files': 0,
            'empty_files': [],
            'corrupted_files': [],
            'duplicate_data': [],
            'issues': []
        }
        
        # Check CSV files
        for csv_file in self.project_root.rglob('*.csv'):
            results['csv_files'] += 1
            results['data_files'] += 1
            
            try:
                # Check if file is empty or corrupted
                df = pd.read_csv(csv_file)
                if df.empty:
                    results['empty_files'].append(str(csv_file.relative_to(self.project_root)))
                elif len(df.columns) < 2:
                    results['issues'].append(f"CSV file with few columns: {csv_file.name}")
            except Exception as e:
                results['corrupted_files'].append(str(csv_file.relative_to(self.project_root)))
        
        # Check JSON files
        for json_file in self.project_root.rglob('*.json'):
            results['json_files'] += 1
            results['data_files'] += 1
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                if not data:
                    results['empty_files'].append(str(json_file.relative_to(self.project_root)))
            except Exception as e:
                results['corrupted_files'].append(str(json_file.relative_to(self.project_root)))
        
        if len(results['empty_files']) > 0:
            results['issues'].append(f"Found {len(results['empty_files'])} empty files")
        
        if len(results['corrupted_files']) > 0:
            results['issues'].append(f"Found {len(results['corrupted_files'])} corrupted files")
        
        return results
    
    def assess_dependencies(self) -> Dict[str, Any]:
        """Assess dependency management."""
        logger.info("Assessing dependencies...")
        
        results = {
            'has_requirements': False,
            'has_setup_py': False,
            'has_env_file': False,
            'imports_found': set(),
            'issues': []
        }
        
        # Check for dependency files
        if (self.project_root / 'requirements.txt').exists():
            results['has_requirements'] = True
        
        if (self.project_root / 'setup.py').exists():
            results['has_setup_py'] = True
        
        if (self.project_root / '.env').exists() or (self.project_root / '.env.example').exists():
            results['has_env_file'] = True
        
        # Find all imports in Python files
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import statements
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_statement = line.strip()
                        if ' as ' in import_statement:
                            module = import_statement.split(' as ')[0]
                        else:
                            module = import_statement.split()[1]
                        results['imports_found'].add(module)
            
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        # Convert set to list for JSON serialization
        results['imports_found'] = list(results['imports_found'])
        
        # Check for common issues
        if not results['has_requirements']:
            results['issues'].append("No requirements.txt found - needs dependency management")
        
        if not results['has_env_file']:
            results['issues'].append("No environment configuration - needs .env setup")
        
        # Check for problematic imports
        problematic_imports = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'neo4j']
        missing_imports = [imp for imp in problematic_imports if imp not in results['imports_found']]
        if missing_imports:
            results['issues'].append(f"Missing common imports: {missing_imports}")
        
        return results
    
    def assess_documentation(self) -> Dict[str, Any]:
        """Assess documentation quality."""
        logger.info("Assessing documentation...")
        
        results = {
            'readme_files': 0,
            'doc_files': 0,
            'comment_lines': 0,
            'total_lines': 0,
            'issues': []
        }
        
        # Count documentation files
        for file_path in self.project_root.rglob('*.md'):
            results['doc_files'] += 1
            if 'readme' in file_path.name.lower():
                results['readme_files'] += 1
        
        # Analyze Python files for comments
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                results['total_lines'] += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                        results['comment_lines'] += 1
            
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        # Calculate documentation metrics
        if results['total_lines'] > 0:
            comment_rate = results['comment_lines'] / results['total_lines']
            if comment_rate < 0.1:
                results['issues'].append("Low comment rate - needs more documentation")
        
        if results['readme_files'] == 0:
            results['issues'].append("No README file found - needs project documentation")
        
        return results
    
    def generate_recommendations(self) -> List[str]:
        """Generate specific recommendations based on assessment."""
        recommendations = []
        
        # File organization recommendations
        if self.assessment_results.get('file_organization', {}).get('total_files', 0) > 100:
            recommendations.append("🔴 CRITICAL: Implement structured directory organization")
        
        if self.assessment_results.get('file_organization', {}).get('file_types', {}).get('.py', 0) > 30:
            recommendations.append("🔴 CRITICAL: Organize Python scripts into functional modules")
        
        # Code quality recommendations
        code_quality = self.assessment_results.get('code_quality', {})
        if code_quality.get('files_with_logging', 0) / max(code_quality.get('python_files', 1), 1) < 0.3:
            recommendations.append("🔴 CRITICAL: Implement comprehensive logging across all scripts")
        
        if code_quality.get('files_with_error_handling', 0) / max(code_quality.get('python_files', 1), 1) < 0.4:
            recommendations.append("🔴 CRITICAL: Add error handling to all scripts")
        
        # Data quality recommendations
        data_quality = self.assessment_results.get('data_quality', {})
        if data_quality.get('empty_files'):
            recommendations.append("🟡 WARNING: Remove or fix empty data files")
        
        if data_quality.get('corrupted_files'):
            recommendations.append("🔴 CRITICAL: Fix corrupted data files")
        
        # Dependency recommendations
        dependencies = self.assessment_results.get('dependencies', {})
        if not dependencies.get('has_requirements'):
            recommendations.append("🔴 CRITICAL: Create requirements.txt for dependency management")
        
        if not dependencies.get('has_env_file'):
            recommendations.append("🟡 WARNING: Create .env.example for environment configuration")
        
        # Documentation recommendations
        documentation = self.assessment_results.get('documentation', {})
        if documentation.get('readme_files', 0) == 0:
            recommendations.append("🔴 CRITICAL: Create comprehensive README.md")
        
        if documentation.get('comment_lines', 0) / max(documentation.get('total_lines', 1), 1) < 0.1:
            recommendations.append("🟡 WARNING: Add more code comments and documentation")
        
        return recommendations
    
    def run_assessment(self) -> Dict[str, Any]:
        """Run complete project assessment."""
        logger.info("Starting comprehensive project assessment...")
        
        self.assessment_results = {
            'file_organization': self.assess_file_organization(),
            'code_quality': self.assess_code_quality(),
            'data_quality': self.assess_data_quality(),
            'dependencies': self.assess_dependencies(),
            'documentation': self.assess_documentation()
        }
        
        # Generate recommendations
        self.assessment_results['recommendations'] = self.generate_recommendations()
        
        # Calculate overall health score
        total_issues = sum(len(results.get('issues', [])) for results in self.assessment_results.values() if isinstance(results, dict))
        self.assessment_results['health_score'] = max(0, 100 - (total_issues * 10))
        
        return self.assessment_results
    
    def print_summary(self):
        """Print assessment summary."""
        print("\n" + "="*80)
        print("KG-PERSEUS PROJECT ASSESSMENT SUMMARY")
        print("="*80)
        
        # Overall health
        health_score = self.assessment_results.get('health_score', 0)
        print(f"\n🏥 Overall Project Health: {health_score}/100")
        
        if health_score >= 80:
            print("✅ Project is in good condition")
        elif health_score >= 60:
            print("⚠️  Project needs some improvements")
        else:
            print("🔴 Project needs significant cleanup")
        
        # Key metrics
        print(f"\n📊 Key Metrics:")
        print(f"   • Total Files: {self.assessment_results['file_organization']['total_files']}")
        print(f"   • Python Scripts: {self.assessment_results['code_quality']['python_files']}")
        print(f"   • Data Files: {self.assessment_results['data_quality']['data_files']}")
        print(f"   • Documentation Files: {self.assessment_results['documentation']['doc_files']}")
        
        # Critical issues
        print(f"\n🔴 Critical Issues Found:")
        critical_issues = [rec for rec in self.assessment_results['recommendations'] if 'CRITICAL' in rec]
        for issue in critical_issues:
            print(f"   • {issue}")
        
        # Warnings
        warnings = [rec for rec in self.assessment_results['recommendations'] if 'WARNING' in rec]
        if warnings:
            print(f"\n🟡 Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        
        # Next steps
        print(f"\n📋 Recommended Next Steps:")
        print("   1. Run the cleanup implementation script")
        print("   2. Review and fix critical issues")
        print("   3. Implement proper dependency management")
        print("   4. Add comprehensive documentation")
        print("   5. Set up testing framework")
        
        print("\n" + "="*80)

def main():
    """Main execution function."""
    project_root = Path.cwd()
    
    logger.info(f"Assessing project at: {project_root}")
    
    # Create assessment instance
    assessment = ProjectAssessment(project_root)
    
    # Run assessment
    results = assessment.run_assessment()
    
    # Print summary
    assessment.print_summary()
    
    # Save detailed results
    results_file = project_root / 'project_assessment_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Detailed assessment results saved to: {results_file}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 