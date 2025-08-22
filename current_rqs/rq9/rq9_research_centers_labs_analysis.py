#!/usr/bin/env python3
"""
RQ9: Research Centers and Labs Analysis
How many programs are associated with research centers or labs devoted to GIS, AI, Remote Sensing?

This analysis follows the established RQ procedure to examine the relationship between academic programs
and technology-focused research infrastructure across universities.
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

class RQ9ResearchCentersLabsAnalyzer:
    def __init__(self, uri, user, password):
        """Initialize the RQ9 Research Centers and Labs Analyzer"""
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
    
    def get_research_centers_data(self):
        """Extract research centers data from the graph database"""
        print("🔍 Extracting research centers data from Neo4j...")
        
        # Query for research centers with technology focus
        research_centers_query = """
        MATCH (rc:ResearchCenter)
        OPTIONAL MATCH (rc)-[:ASSOCIATED_WITH]->(p:Program)
        OPTIONAL MATCH (u:University)-[:HAS]->(rc)
        RETURN DISTINCT
               rc.name as research_center_name,
               u.name as university_name,
               collect(DISTINCT p.name) as associated_programs,
               count(DISTINCT p) as program_count
        ORDER BY u.name, rc.name
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(research_centers_query)
                research_centers_data = [record.data() for record in result]
                print(f"📊 Found {len(research_centers_data)} research centers")
                return research_centers_data
        except Exception as e:
            print(f"❌ Error extracting research centers data: {e}")
            return []
    
    def get_labs_data(self):
        """Extract labs data from the graph database"""
        print("🔍 Extracting labs data from Neo4j...")
        
        # Query for labs with technology focus
        labs_query = """
        MATCH (l:Lab)
        OPTIONAL MATCH (l)-[:ASSOCIATED_WITH]->(p:Program)
        OPTIONAL MATCH (u:University)-[:HAS]->(l)
        RETURN DISTINCT
               l.name as lab_name,
               u.name as university_name,
               collect(DISTINCT p.name) as associated_programs,
               count(DISTINCT p) as program_count
        ORDER BY u.name, l.name
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(labs_query)
                labs_data = [record.data() for record in result]
                print(f"📊 Found {len(labs_data)} labs")
                return labs_data
        except Exception as e:
            print(f"❌ Error extracting labs data: {e}")
            return []
    
    def classify_technology_focus(self, name):
        """Classify research center or lab by technology focus"""
        if not name:
            return 'Other'
        
        name_lower = str(name).lower()
        
        # GIS/Geospatial focus
        if any(term in name_lower for term in [
            'gis', 'geospatial', 'geographic', 'spatial', 'mapping', 'cartography'
        ]):
            return 'GIS'
        
        # AI/Machine Learning focus
        elif any(term in name_lower for term in [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'computational', 'data science'
        ]):
            return 'AI'
        
        # Remote Sensing focus
        elif any(term in name_lower for term in [
            'remote sensing', 'satellite', 'aerial', 'sensor', 'earth observation', 'spectral'
        ]):
            return 'Remote Sensing'
        
        # Drones/UAV focus
        elif any(term in name_lower for term in [
            'drone', 'uav', 'unmanned aerial', 'aerial photography'
        ]):
            return 'Drones/UAV'
        
        # Forestry/Environmental focus
        elif any(term in name_lower for term in [
            'forestry', 'forest', 'natural resource', 'environmental'
        ]):
            return 'Forestry/Environmental'
        
        else:
            return 'Other'
    
    def analyze_research_centers(self, research_centers_data):
        """Analyze research centers by technology focus and program associations"""
        print("🔬 Analyzing research centers...")
        
        # Convert to DataFrame
        df = pd.DataFrame(research_centers_data)
        
        # Add technology focus classification
        df['technology_focus'] = df['research_center_name'].apply(self.classify_technology_focus)
        
        # Filter for technology-focused research centers
        tech_centers = df[df['technology_focus'].isin(['GIS', 'AI', 'Remote Sensing'])].copy()
        
        # Group by technology focus
        focus_summary = tech_centers.groupby('technology_focus').agg({
            'research_center_name': 'count',
            'program_count': 'sum'
        }).rename(columns={
            'research_center_name': 'center_count',
            'program_count': 'total_programs'
        })
        
        # Calculate average programs per center
        focus_summary['avg_programs_per_center'] = (focus_summary['total_programs'] / focus_summary['center_count']).round(1)
        
        # University-level analysis
        university_summary = tech_centers.groupby('university_name').agg({
            'research_center_name': 'count',
            'program_count': 'sum'
        }).rename(columns={
            'research_center_name': 'tech_centers',
            'program_count': 'total_programs'
        })
        
        return {
            'focus_summary': focus_summary,
            'university_summary': university_summary,
            'tech_centers': tech_centers,
            'all_centers': df
        }
    
    def analyze_labs(self, labs_data):
        """Analyze labs by technology focus and program associations"""
        print("🔬 Analyzing labs...")
        
        # Convert to DataFrame
        df = pd.DataFrame(labs_data)
        
        # Add technology focus classification
        df['technology_focus'] = df['lab_name'].apply(self.classify_technology_focus)
        
        # Filter for technology-focused labs
        tech_labs = df[df['technology_focus'].isin(['GIS', 'AI', 'Remote Sensing'])].copy()
        
        # Group by technology focus
        focus_summary = tech_labs.groupby('technology_focus').agg({
            'lab_name': 'count',
            'program_count': 'sum'
        }).rename(columns={
            'lab_name': 'lab_count',
            'program_count': 'total_programs'
        })
        
        # Calculate average programs per lab
        focus_summary['avg_programs_per_lab'] = (focus_summary['total_programs'] / focus_summary['lab_count']).round(1)
        
        # University-level analysis
        university_summary = tech_labs.groupby('university_name').agg({
            'lab_name': 'count',
            'program_count': 'sum'
        }).rename(columns={
            'lab_name': 'tech_labs',
            'program_count': 'total_programs'
        })
        
        return {
            'focus_summary': focus_summary,
            'university_summary': university_summary,
            'tech_labs': tech_labs,
            'all_labs': df
        }
    
    def analyze_combined_infrastructure(self, research_centers_analysis, labs_analysis):
        """Analyze combined research infrastructure across universities"""
        print("🔬 Analyzing combined research infrastructure...")
        
        # Combine university summaries
        centers_summary = research_centers_analysis['university_summary'].reset_index()
        labs_summary = labs_analysis['university_summary'].reset_index()
        
        # Merge on university name
        combined_summary = pd.merge(
            centers_summary, 
            labs_summary, 
            on='university_name', 
            how='outer'
        ).fillna(0)
        
        # Calculate total technology infrastructure
        combined_summary['total_tech_infrastructure'] = (
            combined_summary['tech_centers'] + combined_summary['tech_labs']
        )
        
        # Calculate total programs
        combined_summary['total_programs'] = (
            combined_summary['total_programs_x'] + combined_summary['total_programs_y']
        )
        
        # Clean up column names
        combined_summary = combined_summary.rename(columns={
            'total_programs_x': 'center_programs',
            'total_programs_y': 'lab_programs'
        })
        
        # Sort by total infrastructure
        combined_summary = combined_summary.sort_values('total_tech_infrastructure', ascending=False)
        
        return combined_summary
    
    def analyze_program_associations(self, research_centers_data, labs_data):
        """Analyze program associations with research centers and labs"""
        print("🔬 Analyzing program associations...")
        
        # Research centers associations
        centers_df = pd.DataFrame(research_centers_data)
        centers_df['technology_focus'] = centers_df['research_center_name'].apply(self.classify_technology_focus)
        tech_centers = centers_df[centers_df['technology_focus'].isin(['GIS', 'AI', 'Remote Sensing'])]
        
        # Labs associations
        labs_df = pd.DataFrame(labs_data)
        labs_df['technology_focus'] = labs_df['lab_name'].apply(self.classify_technology_focus)
        tech_labs = labs_df[labs_df['technology_focus'].isin(['GIS', 'AI', 'Remote Sensing'])]
        
        # Count programs by technology focus
        centers_programs = tech_centers.groupby('technology_focus')['program_count'].sum()
        labs_programs = tech_labs.groupby('technology_focus')['program_count'].sum()
        
        # Combine results
        combined_programs = pd.DataFrame({
            'Research_Centers': centers_programs,
            'Labs': labs_programs
        }).fillna(0)
        
        combined_programs['Total_Programs'] = combined_programs['Research_Centers'] + combined_programs['Labs']
        
        return {
            'centers_programs': centers_programs,
            'labs_programs': labs_programs,
            'combined_programs': combined_programs
        }
    
    def create_visualizations(self, research_centers_analysis, labs_analysis, combined_infrastructure, program_associations):
        """Create comprehensive visualizations for RQ9"""
        print("📊 Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Technology Focus Distribution - Research Centers
        plt.subplot(3, 3, 1)
        centers_focus = research_centers_analysis['focus_summary']
        if not centers_focus.empty:
            centers_focus['center_count'].plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title('Research Centers by Technology Focus', fontsize=12, fontweight='bold')
            plt.xlabel('Technology Focus')
            plt.ylabel('Number of Centers')
            plt.xticks(rotation=45)
        
        # 2. Technology Focus Distribution - Labs
        plt.subplot(3, 3, 2)
        labs_focus = labs_analysis['focus_summary']
        if not labs_focus.empty:
            labs_focus['lab_count'].plot(kind='bar', color='lightgreen', edgecolor='black')
            plt.title('Labs by Technology Focus', fontsize=12, fontweight='bold')
            plt.xlabel('Technology Focus')
            plt.ylabel('Number of Labs')
            plt.xticks(rotation=45)
        
        # 3. Programs per Technology Focus - Combined
        plt.subplot(3, 3, 3)
        combined_programs = program_associations['combined_programs']
        if not combined_programs.empty:
            combined_programs[['Research_Centers', 'Labs']].plot(kind='bar', ax=plt.gca())
            plt.title('Programs by Technology Focus and Infrastructure Type', fontsize=12, fontweight='bold')
            plt.xlabel('Technology Focus')
            plt.ylabel('Number of Programs')
            plt.xticks(rotation=45)
            plt.legend()
        
        # 4. University Technology Infrastructure Ranking
        plt.subplot(3, 3, 4)
        top_universities = combined_infrastructure.head(15)
        if not top_universities.empty:
            plt.barh(range(len(top_universities)), top_universities['total_tech_infrastructure'], 
                    color='orange', edgecolor='black')
            plt.yticks(range(len(top_universities)), top_universities['university_name'])
            plt.title('Top 15 Universities by Technology Infrastructure', fontsize=12, fontweight='bold')
            plt.xlabel('Total Technology Infrastructure')
        
        # 5. Research Centers vs Labs Comparison
        plt.subplot(3, 3, 5)
        if not combined_infrastructure.empty:
            plt.scatter(combined_infrastructure['tech_centers'], combined_infrastructure['tech_labs'], 
                       alpha=0.7, s=100, color='purple')
            plt.xlabel('Technology Research Centers')
            plt.ylabel('Technology Labs')
            plt.title('Research Centers vs Labs Distribution', fontsize=12, fontweight='bold')
            
            # Add trend line
            z = np.polyfit(combined_infrastructure['tech_centers'], combined_infrastructure['tech_labs'], 1)
            p = np.poly1d(z)
            plt.plot(combined_infrastructure['tech_centers'], p(combined_infrastructure['tech_centers']), 
                    "r--", alpha=0.8)
        
        # 6. Programs per Infrastructure Unit
        plt.subplot(3, 3, 6)
        if not centers_focus.empty and not labs_focus.empty:
            centers_avg = centers_focus['avg_programs_per_center']
            labs_avg = labs_focus['avg_programs_per_lab']
            
            x = np.arange(len(centers_avg))
            width = 0.35
            
            plt.bar(x - width/2, centers_avg, width, label='Research Centers', color='skyblue', alpha=0.8)
            plt.bar(x + width/2, labs_avg, width, label='Labs', color='lightgreen', alpha=0.8)
            
            plt.xlabel('Technology Focus')
            plt.ylabel('Average Programs per Unit')
            plt.title('Program Density by Infrastructure Type', fontsize=12, fontweight='bold')
            plt.xticks(x, centers_avg.index, rotation=45)
            plt.legend()
        
        # 7. Technology Focus Heatmap
        plt.subplot(3, 3, 7)
        if not combined_programs.empty:
            heatmap_data = combined_programs[['Research_Centers', 'Labs']].T
            sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=plt.gca())
            plt.title('Technology Focus Infrastructure Heatmap', fontsize=12, fontweight='bold')
            plt.xlabel('Technology Focus')
            plt.ylabel('Infrastructure Type')
        
        # 8. University Infrastructure Distribution
        plt.subplot(3, 3, 8)
        if not combined_infrastructure.empty:
            plt.hist(combined_infrastructure['total_tech_infrastructure'], bins=15, 
                    color='lightcoral', edgecolor='black', alpha=0.7)
            plt.xlabel('Total Technology Infrastructure')
            plt.ylabel('Number of Universities')
            plt.title('Distribution of Technology Infrastructure Across Universities', fontsize=12, fontweight='bold')
        
        # 9. Summary Statistics
        plt.subplot(3, 3, 9)
        plt.axis('off')
        
        # Calculate summary statistics
        total_centers = len(research_centers_analysis['tech_centers'])
        total_labs = len(labs_analysis['tech_labs'])
        total_programs = program_associations['combined_programs']['Total_Programs'].sum()
        
        # Get focus counts safely
        gis_centers = len(centers_focus.get('GIS', pd.Series([0]))) if 'GIS' in centers_focus.index else 0
        gis_labs = len(labs_focus.get('GIS', pd.Series([0]))) if 'GIS' in labs_focus.index else 0
        ai_centers = len(centers_focus.get('AI', pd.Series([0]))) if 'AI' in centers_focus.index else 0
        ai_labs = len(labs_focus.get('AI', pd.Series([0]))) if 'AI' in labs_focus.index else 0
        rs_centers = len(centers_focus.get('Remote Sensing', pd.Series([0]))) if 'Remote Sensing' in centers_focus.index else 0
        rs_labs = len(labs_focus.get('Remote Sensing', pd.Series([0]))) if 'Remote Sensing' in labs_focus.index else 0
        
        summary_text = f"""
        RQ9 Analysis Summary
        
        Technology Research Centers: {total_centers}
        Technology Labs: {total_labs}
        Total Technology Infrastructure: {total_centers + total_labs}
        Associated Programs: {total_programs}
        
        Key Findings:
        • GIS Focus: {gis_centers + gis_labs} units
        • AI Focus: {ai_centers + ai_labs} units
        • Remote Sensing Focus: {rs_centers + rs_labs} units
        
        Universities Analyzed: {len(combined_infrastructure)}
        """
        
        plt.text(0.1, 0.9, summary_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save the visualization
        output_path = 'visualizations/rq9_research_centers_labs_analysis.png'
        os.makedirs('visualizations', exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved to {output_path}")
        
        plt.show()
        
        return output_path
    
    def print_detailed_results(self, research_centers_analysis, labs_analysis, combined_infrastructure, program_associations):
        """Print detailed analysis results"""
        print("\n" + "="*80)
        print("RQ9: RESEARCH CENTERS AND LABS ANALYSIS RESULTS")
        print("="*80)
        
        # Research Centers Analysis
        print("\n📊 RESEARCH CENTERS ANALYSIS")
        print("-" * 50)
        centers_focus = research_centers_analysis['focus_summary']
        if not centers_focus.empty:
            print("Technology Focus Summary:")
            print(centers_focus.to_string())
        else:
            print("No technology-focused research centers found")
        
        # Labs Analysis
        print("\n📊 LABS ANALYSIS")
        print("-" * 50)
        labs_focus = labs_analysis['focus_summary']
        if not labs_focus.empty:
            print("Technology Focus Summary:")
            print(labs_focus.to_string())
        else:
            print("No technology-focused labs found")
        
        # Combined Infrastructure Analysis
        print("\n📊 COMBINED INFRASTRUCTURE ANALYSIS")
        print("-" * 50)
        if not combined_infrastructure.empty:
            print("Top 10 Universities by Technology Infrastructure:")
            print(combined_infrastructure.head(10).to_string())
        else:
            print("No combined infrastructure data available")
        
        # Program Associations Analysis
        print("\n📊 PROGRAM ASSOCIATIONS ANALYSIS")
        print("-" * 50)
        combined_programs = program_associations['combined_programs']
        if not combined_programs.empty:
            print("Programs by Technology Focus and Infrastructure Type:")
            print(combined_programs.to_string())
        else:
            print("No program association data available")
        
        print("\n" + "="*80)
    
    def save_results(self, research_centers_analysis, labs_analysis, combined_infrastructure, program_associations):
        """Save analysis results to CSV files"""
        print("💾 Saving results to CSV files...")
        
        # Create outputs directory
        os.makedirs('data/outputs', exist_ok=True)
        
        # Save research centers analysis
        if not research_centers_analysis['focus_summary'].empty:
            research_centers_analysis['focus_summary'].to_csv('data/outputs/rq9_research_centers_focus_summary.csv')
            print("✅ Research centers focus summary saved")
        
        if not research_centers_analysis['university_summary'].empty:
            research_centers_analysis['university_summary'].to_csv('data/outputs/rq9_research_centers_university_summary.csv')
            print("✅ Research centers university summary saved")
        
        # Save labs analysis
        if not labs_analysis['focus_summary'].empty:
            labs_analysis['focus_summary'].to_csv('data/outputs/rq9_labs_focus_summary.csv')
            print("✅ Labs focus summary saved")
        
        if not labs_analysis['university_summary'].empty:
            labs_analysis['university_summary'].to_csv('data/outputs/rq9_labs_university_summary.csv')
            print("✅ Labs university summary saved")
        
        # Save combined infrastructure analysis
        if not combined_infrastructure.empty:
            combined_infrastructure.to_csv('data/outputs/rq9_combined_infrastructure_summary.csv')
            print("✅ Combined infrastructure summary saved")
        
        # Save program associations analysis
        if not program_associations['combined_programs'].empty:
            program_associations['combined_programs'].to_csv('data/outputs/rq9_program_associations_summary.csv')
            print("✅ Program associations summary saved")
        
        # Save detailed data
        if not research_centers_analysis['tech_centers'].empty:
            research_centers_analysis['tech_centers'].to_csv('data/outputs/rq9_technology_research_centers_detailed.csv')
            print("✅ Technology research centers detailed data saved")
        
        if not labs_analysis['tech_labs'].empty:
            labs_analysis['tech_labs'].to_csv('data/outputs/rq9_technology_labs_detailed.csv')
            print("✅ Technology labs detailed data saved")
        
        print("✅ All results saved successfully")
    
    def run_complete_analysis(self):
        """Run the complete RQ9 analysis"""
        print("🚀 Starting RQ9: Research Centers and Labs Analysis")
        print("="*80)
        
        # Test connection
        if not self.connect():
            print("❌ Cannot proceed without database connection")
            return
        
        try:
            # Extract data
            research_centers_data = self.get_research_centers_data()
            labs_data = self.get_labs_data()
            
            if not research_centers_data and not labs_data:
                print("❌ No research centers or labs data found")
                return
            
            # Run analyses
            research_centers_analysis = self.analyze_research_centers(research_centers_data)
            labs_analysis = self.analyze_labs(labs_data)
            combined_infrastructure = self.analyze_combined_infrastructure(research_centers_analysis, labs_analysis)
            program_associations = self.analyze_program_associations(research_centers_data, labs_data)
            
            # Create visualizations
            viz_path = self.create_visualizations(research_centers_analysis, labs_analysis, combined_infrastructure, program_associations)
            
            # Print results
            self.print_detailed_results(research_centers_analysis, labs_analysis, combined_infrastructure, program_associations)
            
            # Save results
            self.save_results(research_centers_analysis, labs_analysis, combined_infrastructure, program_associations)
            
            print(f"\n🎉 RQ9 analysis completed successfully!")
            print(f"📊 Visualization saved to: {viz_path}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close()

def main():
    """Main function to run RQ9 analysis"""
    # Database connection parameters
    uri = "bolt://localhost:7689"
    username = "neo4j"
    password = "perseus2025"
    
    # Create analyzer and run analysis
    analyzer = RQ9ResearchCentersLabsAnalyzer(uri, username, password)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
