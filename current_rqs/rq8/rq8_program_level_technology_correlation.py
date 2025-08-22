#!/usr/bin/env python3
"""
RQ8: Program Level and Type Technology Correlation Analysis
To what extent are drone/GIS/AI topics correlated with the level (undergraduate, master's, or doctoral) 
and type of academic programs?

This analysis follows the established RQ procedure to examine technology integration patterns
across different program levels and types in forestry and related academic programs.
"""

from neo4j import GraphDatabase
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class RQ8ProgramLevelTechnologyCorrelationAnalyzer:
    def __init__(self, uri, user, password):
        """Initialize the RQ8 Program Level Technology Correlation Analyzer"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user
        self.password = password
        
    def connect(self):
        """Test database connection"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                print("✅ Successfully connected to Neo4j database")
                return True
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        self.driver.close()
        print("Database connection closed")
    
    def get_program_data(self):
        """Extract program data from the graph database"""
        print("🔍 Extracting program data from Neo4j...")
        
        # Query for programs with technology relationships
        program_query = """
        MATCH (p:Program)
        OPTIONAL MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
        OPTIONAL MATCH (u:University)-[:OFFERS]->(p)
        RETURN DISTINCT
               p.name as program_name,
               t.category as technology_category,
               u.name as university_name
        ORDER BY u.name, p.name
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(program_query)
                program_data = [record.data() for record in result]
                print(f"📊 Found {len(program_data)} program-technology relationships")
                return program_data
        except Exception as e:
            print(f"❌ Error extracting program data: {e}")
            return []
    
    def classify_program_level(self, program_name):
        """Classify program by level (Undergraduate, Master, Doctoral)"""
        if not program_name:
            return 'Unknown'
        
        program_lower = str(program_name).lower()
        
        # Undergraduate keywords
        if any(term in program_lower for term in [
            'bachelor', 'bs', 'ba', 'undergraduate', 'associate', 'a.s.', 'a.a.'
        ]):
            return 'Undergraduate'
        
        # Master's keywords
        elif any(term in program_lower for term in [
            'master', 'ms', 'ma', 'mba', 'graduate', 'post-baccalaureate'
        ]):
            return 'Master'
        
        # Doctoral keywords
        elif any(term in program_lower for term in [
            'phd', 'ph.d.', 'doctorate', 'doctoral', 'd.phil'
        ]):
            return 'Doctoral'
        
        else:
            return 'Unknown'
    
    def classify_program_type(self, program_name):
        """Classify program by type (Forestry, Natural Resources, etc.)"""
        if not program_name:
            return 'Other'
        
        program_lower = str(program_name).lower()
        
        # Forestry programs
        if any(term in program_lower for term in [
            'forestry', 'forest', 'silviculture'
        ]):
            return 'Forestry'
        
        # Natural Resources programs
        elif any(term in program_lower for term in [
            'natural resource', 'environmental', 'ecology', 'conservation'
        ]):
            return 'Natural Resources'
        
        # Geospatial programs
        elif any(term in program_lower for term in [
            'gis', 'geospatial', 'geographic', 'spatial'
        ]):
            return 'Geospatial'
        
        # Data Science programs
        elif any(term in program_lower for term in [
            'data science', 'analytics', 'informatics', 'computational'
        ]):
            return 'Data Science'
        
        # Engineering programs
        elif any(term in program_lower for term in [
            'engineering', 'technology', 'technical'
        ]):
            return 'Engineering'
        
        # Business/Management programs
        elif any(term in program_lower for term in [
            'business', 'management', 'administration', 'policy'
        ]):
            return 'Business/Management'
        
        # Science programs
        elif any(term in program_lower for term in [
            'science', 'scientific', 'research'
        ]):
            return 'Science'
        
        # Computer Science programs
        elif any(term in program_lower for term in [
            'computer science', 'computing', 'software', 'programming'
        ]):
            return 'Computer Science'
        
        else:
            return 'Other'
    
    def analyze_program_level_technology_correlation(self, program_data):
        """Analyze technology integration by program level"""
        print("🔬 Analyzing technology integration by program level...")
        
        # Convert to DataFrame
        df = pd.DataFrame(program_data)
        
        # Add program level classification
        df['program_level'] = df['program_name'].apply(self.classify_program_level)
        
        # Filter for programs with technology
        tech_programs = df[df['technology_category'].notna()].copy()
        
        # Group by program level and technology category
        level_tech_counts = tech_programs.groupby(['program_level', 'technology_category']).size().reset_index(name='count')
        
        # Calculate summary statistics by level
        level_summary = tech_programs.groupby('program_level').agg({
            'program_name': 'nunique',
            'technology_category': 'count'
        }).rename(columns={
            'program_name': 'unique_programs',
            'technology_category': 'total_technology_mentions'
        })
        
        # Calculate technology adoption rate by level
        total_programs_by_level = df.groupby('program_level')['program_name'].nunique()
        tech_programs_by_level = tech_programs.groupby('program_level')['program_name'].nunique()
        
        level_summary['total_programs'] = total_programs_by_level
        level_summary['tech_programs'] = tech_programs_by_level
        level_summary['adoption_rate'] = (level_summary['tech_programs'] / level_summary['total_programs'] * 100).round(1)
        
        return {
            'level_tech_counts': level_tech_counts,
            'level_summary': level_summary,
            'tech_programs': tech_programs
        }
    
    def analyze_program_type_technology_correlation(self, program_data):
        """Analyze technology integration by program type"""
        print("🔬 Analyzing technology integration by program type...")
        
        # Convert to DataFrame
        df = pd.DataFrame(program_data)
        
        # Add program type classification
        df['program_type'] = df['program_name'].apply(self.classify_program_type)
        
        # Filter for programs with technology
        tech_programs = df[df['technology_category'].notna()].copy()
        
        # Group by program type and technology category
        type_tech_counts = tech_programs.groupby(['program_type', 'technology_category']).size().reset_index(name='count')
        
        # Calculate summary statistics by type
        type_summary = tech_programs.groupby('program_type').agg({
            'program_name': 'nunique',
            'technology_category': 'count'
        }).rename(columns={
            'program_name': 'unique_programs',
            'technology_category': 'total_technology_mentions'
        })
        
        # Calculate technology adoption rate by type
        total_programs_by_type = df.groupby('program_type')['program_name'].nunique()
        tech_programs_by_type = tech_programs.groupby('program_type')['program_name'].nunique()
        
        type_summary['total_programs'] = total_programs_by_type
        type_summary['tech_programs'] = tech_programs_by_type
        type_summary['adoption_rate'] = (type_summary['tech_programs'] / type_summary['total_programs'] * 100).round(1)
        
        return {
            'type_tech_counts': type_tech_counts,
            'type_summary': type_summary,
            'tech_programs': tech_programs
        }
    
    def analyze_cross_correlation(self, program_data):
        """Analyze technology integration by both program level AND type"""
        print("🔬 Analyzing cross-correlation between program level and type...")
        
        # Convert to DataFrame
        df = pd.DataFrame(program_data)
        
        # Add classifications
        df['program_level'] = df['program_name'].apply(self.classify_program_level)
        df['program_type'] = df['program_name'].apply(self.classify_program_type)
        
        # Filter for programs with technology
        tech_programs = df[df['technology_category'].notna()].copy()
        
        # Cross-tabulation: Level x Type x Technology
        cross_analysis = tech_programs.groupby(['program_level', 'program_type', 'technology_category']).size().reset_index(name='count')
        
        # Summary by level and type
        level_type_summary = tech_programs.groupby(['program_level', 'program_type']).agg({
            'program_name': 'nunique',
            'technology_category': 'count'
        }).reset_index()
        
        level_type_summary = level_type_summary.rename(columns={
            'program_name': 'unique_programs',
            'technology_category': 'total_technology_mentions'
        })
        
        return {
            'cross_analysis': cross_analysis,
            'level_type_summary': level_type_summary
        }
    
    def analyze_specific_technologies(self, program_data):
        """Analyze specific technology areas (AI/ML, GIS, Drones/UAV) by level and type"""
        print("🔬 Analyzing specific technology areas...")
        
        # Convert to DataFrame
        df = pd.DataFrame(program_data)
        
        # Add classifications
        df['program_level'] = df['program_name'].apply(self.classify_program_level)
        df['program_type'] = df['program_name'].apply(self.classify_program_type)
        
        # Filter for specific technologies
        target_technologies = ['AI/ML', 'GIS', 'Drones/UAV']
        
        results = {}
        for tech in target_technologies:
            tech_programs = df[df['technology_category'] == tech].copy()
            
            if not tech_programs.empty:
                # By program level
                level_counts = tech_programs.groupby('program_level').size().reset_index(name=f'{tech}_count')
                
                # By program type
                type_counts = tech_programs.groupby('program_type').size().reset_index(name=f'{tech}_count')
                
                # Cross-tabulation
                cross_counts = tech_programs.groupby(['program_level', 'program_type']).size().reset_index(name=f'{tech}_count')
                
                results[tech] = {
                    'level_counts': level_counts,
                    'type_counts': type_counts,
                    'cross_counts': cross_counts,
                    'total_programs': len(tech_programs)
                }
            else:
                results[tech] = {
                    'level_counts': pd.DataFrame(),
                    'type_counts': pd.DataFrame(),
                    'cross_counts': pd.DataFrame(),
                    'total_programs': 0
                }
        
        return results
    
    def create_visualizations(self, level_analysis, type_analysis, cross_analysis, specific_tech_analysis):
        """Create comprehensive visualizations for RQ8"""
        print("📊 Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Technology Integration by Program Level
        plt.subplot(3, 3, 1)
        level_summary = level_analysis['level_summary']
        if not level_summary.empty:
            level_summary['adoption_rate'].plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title('Technology Adoption Rate by Program Level', fontsize=12, fontweight='bold')
            plt.xlabel('Program Level')
            plt.ylabel('Adoption Rate (%)')
            plt.xticks(rotation=45)
            plt.ylim(0, 100)
        
        # 2. Technology Integration by Program Type
        plt.subplot(3, 3, 2)
        type_summary = type_analysis['type_summary']
        if not type_summary.empty:
            type_summary['adoption_rate'].plot(kind='bar', color='lightgreen', edgecolor='black')
            plt.title('Technology Adoption Rate by Program Type', fontsize=12, fontweight='bold')
            plt.xlabel('Program Type')
            plt.ylabel('Adoption Rate (%)')
            plt.xticks(rotation=45)
            plt.ylim(0, 100)
        
        # 3. Technology Distribution by Program Level
        plt.subplot(3, 3, 3)
        level_tech_counts = level_analysis['level_tech_counts']
        if not level_tech_counts.empty:
            pivot_level = level_tech_counts.pivot(index='program_level', columns='technology_category', values='count').fillna(0)
            pivot_level.plot(kind='bar', stacked=True, ax=plt.gca())
            plt.title('Technology Distribution by Program Level', fontsize=12, fontweight='bold')
            plt.xlabel('Program Level')
            plt.ylabel('Technology Count')
            plt.xticks(rotation=45)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 4. Technology Distribution by Program Type
        plt.subplot(3, 3, 4)
        type_tech_counts = type_analysis['type_tech_counts']
        if not type_tech_counts.empty:
            pivot_type = type_tech_counts.pivot(index='program_type', columns='technology_category', values='count').fillna(0)
            pivot_type.plot(kind='bar', stacked=True, ax=plt.gca())
            plt.title('Technology Distribution by Program Type', fontsize=12, fontweight='bold')
            plt.xlabel('Program Type')
            plt.ylabel('Technology Count')
            plt.xticks(rotation=45)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 5. AI/ML Technology by Program Level
        plt.subplot(3, 3, 5)
        if 'AI/ML' in specific_tech_analysis and specific_tech_analysis['AI/ML']['total_programs'] > 0:
            ai_ml_level = specific_tech_analysis['AI/ML']['level_counts']
            if not ai_ml_level.empty:
                plt.bar(ai_ml_level['program_level'], ai_ml_level['AI/ML_count'], color='orange', edgecolor='black')
                plt.title('AI/ML Technology by Program Level', fontsize=12, fontweight='bold')
                plt.xlabel('Program Level')
                plt.ylabel('Program Count')
                plt.xticks(rotation=45)
        
        # 6. GIS Technology by Program Level
        plt.subplot(3, 3, 6)
        if 'GIS' in specific_tech_analysis and specific_tech_analysis['GIS']['total_programs'] > 0:
            gis_level = specific_tech_analysis['GIS']['level_counts']
            if not gis_level.empty:
                plt.bar(gis_level['program_level'], gis_level['GIS_count'], color='green', edgecolor='black')
                plt.title('GIS Technology by Program Level', fontsize=12, fontweight='bold')
                plt.xlabel('Program Level')
                plt.ylabel('Program Count')
                plt.xticks(rotation=45)
        
        # 7. Drone/UAV Technology by Program Level
        plt.subplot(3, 3, 7)
        if 'Drones/UAV' in specific_tech_analysis and specific_tech_analysis['Drones/UAV']['total_programs'] > 0:
            drone_level = specific_tech_analysis['Drones/UAV']['level_counts']
            if not drone_level.empty:
                plt.bar(drone_level['program_level'], drone_level['Drones/UAV_count'], color='red', edgecolor='black')
                plt.title('Drone/UAV Technology by Program Level', fontsize=12, fontweight='bold')
                plt.xlabel('Program Level')
                plt.ylabel('Program Count')
                plt.xticks(rotation=45)
        
        # 8. Heatmap: Technology by Level and Type
        plt.subplot(3, 3, 8)
        cross_summary = cross_analysis['level_type_summary']
        if not cross_summary.empty:
            # Create pivot table for heatmap
            heatmap_data = cross_summary.pivot(index='program_level', columns='program_type', values='total_technology_mentions').fillna(0)
            sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=plt.gca())
            plt.title('Technology Integration Heatmap\n(Level × Type)', fontsize=12, fontweight='bold')
            plt.xlabel('Program Type')
            plt.ylabel('Program Level')
        
        # 9. Summary Statistics
        plt.subplot(3, 3, 9)
        plt.axis('off')
        
        # Calculate summary statistics
        total_programs = len(pd.DataFrame(level_analysis['tech_programs']['program_name'].unique()))
        total_tech_mentions = len(level_analysis['tech_programs'])
        
        summary_text = f"""
        RQ8 Analysis Summary
        
        Total Programs Analyzed: {total_programs}
        Total Technology Mentions: {total_tech_mentions}
        
        Key Findings:
        • Program Level Analysis: {len(level_analysis['level_summary'])} levels
        • Program Type Analysis: {len(type_analysis['type_summary'])} types
        • Cross-Correlation: {len(cross_analysis['cross_analysis'])} combinations
        
        Technology Focus:
        • AI/ML: {specific_tech_analysis.get('AI/ML', {}).get('total_programs', 0)} programs
        • GIS: {specific_tech_analysis.get('GIS', {}).get('total_programs', 0)} programs
        • Drones/UAV: {specific_tech_analysis.get('Drones/UAV', {}).get('total_programs', 0)} programs
        """
        
        plt.text(0.1, 0.9, summary_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save the visualization
        output_path = 'visualizations/rq8_program_level_technology_correlation.png'
        os.makedirs('visualizations', exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved to {output_path}")
        
        plt.show()
        
        return output_path
    
    def print_detailed_results(self, level_analysis, type_analysis, cross_analysis, specific_tech_analysis):
        """Print detailed analysis results"""
        print("\n" + "="*80)
        print("RQ8: PROGRAM LEVEL AND TYPE TECHNOLOGY CORRELATION ANALYSIS RESULTS")
        print("="*80)
        
        # Program Level Analysis
        print("\n📊 TECHNOLOGY INTEGRATION BY PROGRAM LEVEL")
        print("-" * 50)
        level_summary = level_analysis['level_summary']
        if not level_summary.empty:
            print(level_summary.to_string())
        else:
            print("No program level data available")
        
        # Program Type Analysis
        print("\n📊 TECHNOLOGY INTEGRATION BY PROGRAM TYPE")
        print("-" * 50)
        type_summary = type_analysis['type_summary']
        if not type_summary.empty:
            print(type_summary.to_string())
        else:
            print("No program type data available")
        
        # Cross-Correlation Analysis
        print("\n📊 CROSS-CORRELATION: PROGRAM LEVEL × PROGRAM TYPE")
        print("-" * 50)
        cross_summary = cross_analysis['level_type_summary']
        if not cross_summary.empty:
            print(cross_summary.to_string())
        else:
            print("No cross-correlation data available")
        
        # Specific Technology Analysis
        print("\n📊 SPECIFIC TECHNOLOGY AREAS ANALYSIS")
        print("-" * 50)
        for tech, data in specific_tech_analysis.items():
            print(f"\n{tech} Technology:")
            if data['total_programs'] > 0:
                print(f"  Total Programs: {data['total_programs']}")
                if not data['level_counts'].empty:
                    print("  By Program Level:")
                    print(data['level_counts'].to_string(index=False))
                if not data['type_counts'].empty:
                    print("  By Program Type:")
                    print(data['type_counts'].to_string(index=False))
            else:
                print(f"  No programs found with {tech} technology")
        
        print("\n" + "="*80)
    
    def save_results(self, level_analysis, type_analysis, cross_analysis, specific_tech_analysis):
        """Save analysis results to CSV files"""
        print("💾 Saving results to CSV files...")
        
        # Create outputs directory
        os.makedirs('data/outputs', exist_ok=True)
        
        # Save program level analysis
        if not level_analysis['level_summary'].empty:
            level_analysis['level_summary'].to_csv('data/outputs/rq8_program_level_analysis.csv')
            print("✅ Program level analysis saved")
        
        if not level_analysis['level_tech_counts'].empty:
            level_analysis['level_tech_counts'].to_csv('data/outputs/rq8_program_level_tech_counts.csv')
            print("✅ Program level technology counts saved")
        
        # Save program type analysis
        if not type_analysis['type_summary'].empty:
            type_analysis['type_summary'].to_csv('data/outputs/rq8_program_type_analysis.csv')
            print("✅ Program type analysis saved")
        
        if not type_analysis['type_tech_counts'].empty:
            type_analysis['type_tech_counts'].to_csv('data/outputs/rq8_program_type_tech_counts.csv')
            print("✅ Program type technology counts saved")
        
        # Save cross-correlation analysis
        if not cross_analysis['cross_analysis'].empty:
            cross_analysis['cross_analysis'].to_csv('data/outputs/rq8_cross_correlation_analysis.csv')
            print("✅ Cross-correlation analysis saved")
        
        if not cross_analysis['level_type_summary'].empty:
            cross_analysis['level_type_summary'].to_csv('data/outputs/rq8_level_type_summary.csv')
            print("✅ Level-type summary saved")
        
        # Save specific technology analysis
        for tech, data in specific_tech_analysis.items():
            if data['total_programs'] > 0:
                if not data['level_counts'].empty:
                    data['level_counts'].to_csv(f'data/outputs/rq8_{tech.lower().replace("/", "_")}_by_level.csv')
                if not data['type_counts'].empty:
                    data['type_counts'].to_csv(f'data/outputs/rq8_{tech.lower().replace("/", "_")}_by_type.csv')
                if not data['cross_counts'].empty:
                    data['cross_counts'].to_csv(f'data/outputs/rq8_{tech.lower().replace("/", "_")}_cross_analysis.csv')
        
        print("✅ All results saved successfully")
    
    def run_complete_analysis(self):
        """Run the complete RQ8 analysis"""
        print("🚀 Starting RQ8: Program Level and Type Technology Correlation Analysis")
        print("="*80)
        
        # Test connection
        if not self.connect():
            print("❌ Cannot proceed without database connection")
            return
        
        try:
            # Extract data
            program_data = self.get_program_data()
            if not program_data:
                print("❌ No program data found")
                return
            
            # Run analyses
            level_analysis = self.analyze_program_level_technology_correlation(program_data)
            type_analysis = self.analyze_program_type_technology_correlation(program_data)
            cross_analysis = self.analyze_cross_correlation(program_data)
            specific_tech_analysis = self.analyze_specific_technologies(program_data)
            
            # Create visualizations
            viz_path = self.create_visualizations(level_analysis, type_analysis, cross_analysis, specific_tech_analysis)
            
            # Print results
            self.print_detailed_results(level_analysis, type_analysis, cross_analysis, specific_tech_analysis)
            
            # Save results
            self.save_results(level_analysis, type_analysis, cross_analysis, specific_tech_analysis)
            
            print(f"\n🎉 RQ8 analysis completed successfully!")
            print(f"📊 Visualization saved to: {viz_path}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()

def main():
    """Main function to run RQ8 analysis"""
    # Database connection parameters
    uri = "bolt://localhost:7689"
    username = "neo4j"
    password = "perseus2025"
    
    # Create analyzer and run analysis
    analyzer = RQ8ProgramLevelTechnologyCorrelationAnalyzer(uri, username, password)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
