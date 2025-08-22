#!/usr/bin/env python3
"""
Analysis of AI, ML, drones, and GIS technologies in mission statements and strategic materials
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

# Neo4j connection
uri = "bolt://localhost:7689"
username = "neo4j"
password = "perseus2025"

class MissionStatementAnalyzer:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.university_profiles_dir = "university-profiles"
        
    def close(self):
        self.driver.close()
        
    def run_query(self, query, parameters=None):
        """Run a Cypher query and return results"""
        with self.driver.session() as session:
            try:
                if parameters:
                    result = session.run(query, parameters)
                else:
                    result = session.run(query)
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error running query: {e}")
                return []

    def extract_mission_statements_from_profiles(self):
        """Extract mission statements and strategic materials from university profiles"""
        print("Extracting mission statements from university profiles...")
        
        mission_data = []
        
        # Keywords to identify mission statements and strategic content
        mission_keywords = [
            'mission', 'vision', 'strategic', 'goal', 'objective', 'purpose',
            'commitment', 'dedicated to', 'focused on', 'specializing in',
            'department of', 'school of', 'college of', 'program in',
            'research focus', 'research area', 'research emphasis',
            'teaching focus', 'educational focus', 'curriculum focus'
        ]
        
        # Technology keywords to search for
        tech_keywords = {
            'AI/ML': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural', 'deep learning', 'predictive modeling'],
            'GIS': ['geographic information system', 'GIS', 'geospatial', 'spatial analysis', 'mapping'],
            'Drones': ['drone', 'UAV', 'unmanned aerial vehicle', 'remote sensing', 'aerial survey'],
            'Data Science': ['data science', 'big data', 'analytics', 'statistical analysis', 'computational']
        }
        
        for filename in os.listdir(self.university_profiles_dir):
            if filename.endswith('.md'):
                university_name = filename.replace('.md', '')
                filepath = os.path.join(self.university_profiles_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split content into paragraphs
                    paragraphs = content.split('\n\n')
                    
                    mission_paragraphs = []
                    for para in paragraphs:
                        para_lower = para.lower()
                        # Check if paragraph contains mission-related keywords
                        if any(keyword in para_lower for keyword in mission_keywords):
                            mission_paragraphs.append(para)
                    
                    # Analyze each mission paragraph for technology mentions
                    for i, para in enumerate(mission_paragraphs):
                        para_lower = para.lower()
                        tech_mentions = {}
                        
                        for tech_category, keywords in tech_keywords.items():
                            mentions = []
                            for keyword in keywords:
                                if keyword.lower() in para_lower:
                                    mentions.append(keyword)
                            if mentions:
                                tech_mentions[tech_category] = mentions
                        
                        if tech_mentions:  # Only include paragraphs with technology mentions
                            mission_data.append({
                                'university': university_name,
                                'paragraph_index': i,
                                'content': para.strip(),
                                'technology_mentions': tech_mentions,
                                'tech_categories': list(tech_mentions.keys())
                            })
                
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        return pd.DataFrame(mission_data)

    def analyze_graph_mission_statements(self):
        """Analyze mission statements and strategic content in the Neo4j graph"""
        print("Analyzing mission statements in Neo4j graph...")
        
        # Query for programs with mission statements or descriptions
        mission_query = """
        MATCH (p:Program)
        WHERE p.description IS NOT NULL AND p.description <> ''
        RETURN p.name as program_name,
               p.university as university,
               p.description as description
        """
        
        programs = self.run_query(mission_query)
        
        # Query for departments with mission statements
        dept_query = """
        MATCH (d:Department)
        WHERE d.description IS NOT NULL AND d.description <> ''
        RETURN d.name as department_name,
               d.university as university,
               d.description as description
        """
        
        departments = self.run_query(dept_query)
        
        # Query for universities with mission statements
        univ_query = """
        MATCH (u:University)
        WHERE u.description IS NOT NULL AND u.description <> ''
        RETURN u.name as university_name,
               u.description as description
        """
        
        universities = self.run_query(univ_query)
        
        return programs, departments, universities

    def analyze_technology_prevalence(self, mission_df, programs, departments, universities):
        """Analyze technology prevalence across all sources"""
        print("Analyzing technology prevalence...")
        
        # Technology keywords
        tech_keywords = {
            'AI/ML': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural', 'deep learning', 'predictive modeling'],
            'GIS': ['geographic information system', 'GIS', 'geospatial', 'spatial analysis', 'mapping'],
            'Drones': ['drone', 'UAV', 'unmanned aerial vehicle', 'remote sensing', 'aerial survey'],
            'Data Science': ['data science', 'big data', 'analytics', 'statistical analysis', 'computational']
        }
        
        # Analyze university profiles data
        profile_analysis = self.analyze_profile_technology(mission_df, tech_keywords)
        
        # Analyze graph data
        graph_analysis = self.analyze_graph_technology(programs, departments, universities, tech_keywords)
        
        return profile_analysis, graph_analysis

    def analyze_profile_technology(self, mission_df, tech_keywords):
        """Analyze technology mentions in university profiles"""
        if mission_df.empty:
            return {}
        
        # Count technology mentions by category
        tech_counts = defaultdict(int)
        univ_tech_counts = defaultdict(lambda: defaultdict(int))
        
        for _, row in mission_df.iterrows():
            for tech_category in row['tech_categories']:
                tech_counts[tech_category] += 1
                univ_tech_counts[row['university']][tech_category] += 1
        
        # Calculate percentages
        total_mentions = sum(tech_counts.values())
        tech_percentages = {tech: (count/total_mentions*100) if total_mentions > 0 else 0 
                           for tech, count in tech_counts.items()}
        
        return {
            'tech_counts': dict(tech_counts),
            'tech_percentages': tech_percentages,
            'university_tech_counts': dict(univ_tech_counts),
            'total_mentions': total_mentions,
            'universities_with_tech': len([u for u, counts in univ_tech_counts.items() if sum(counts.values()) > 0])
        }

    def analyze_graph_technology(self, programs, departments, universities, tech_keywords):
        """Analyze technology mentions in graph data"""
        graph_tech_counts = defaultdict(int)
        graph_univ_tech_counts = defaultdict(lambda: defaultdict(int))
        
        # Analyze programs
        for program in programs:
            if program.get('description'):
                desc_lower = program['description'].lower()
                for tech_category, keywords in tech_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in desc_lower:
                            graph_tech_counts[tech_category] += 1
                            graph_univ_tech_counts[program['university']][tech_category] += 1
        
        # Analyze departments
        for dept in departments:
            if dept.get('description'):
                desc_lower = dept['description'].lower()
                for tech_category, keywords in tech_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in desc_lower:
                            graph_tech_counts[tech_category] += 1
                            graph_univ_tech_counts[dept['university']][tech_category] += 1
        
        # Analyze universities
        for univ in universities:
            if univ.get('description'):
                desc_lower = univ['description'].lower()
                for tech_category, keywords in tech_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in desc_lower:
                            graph_tech_counts[tech_category] += 1
                            graph_univ_tech_counts[univ['university_name']][tech_category] += 1
        
        # Calculate percentages
        total_graph_mentions = sum(graph_tech_counts.values())
        graph_tech_percentages = {tech: (count/total_graph_mentions*100) if total_graph_mentions > 0 else 0 
                                 for tech, count in graph_tech_counts.items()}
        
        return {
            'tech_counts': dict(graph_tech_counts),
            'tech_percentages': graph_tech_percentages,
            'university_tech_counts': dict(graph_univ_tech_counts),
            'total_mentions': total_graph_mentions,
            'universities_with_tech': len([u for u, counts in graph_univ_tech_counts.items() if sum(counts.values()) > 0])
        }

    def create_comprehensive_visualizations(self, profile_analysis, graph_analysis, mission_df):
        """Create comprehensive visualizations for technology prevalence analysis"""
        print("Creating visualizations...")
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Overall technology prevalence comparison
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Technology Prevalence in Mission Statements and Strategic Materials', fontsize=16, fontweight='bold')
        
        # 1. Technology distribution in university profiles
        if profile_analysis and profile_analysis['tech_counts']:
            tech_data = pd.DataFrame(list(profile_analysis['tech_counts'].items()), 
                                   columns=['Technology', 'Count'])
            tech_data = tech_data.sort_values('Count', ascending=True)
            
            bars = ax1.barh(tech_data['Technology'], tech_data['Count'], 
                           color=plt.cm.viridis(np.linspace(0, 1, len(tech_data))))
            ax1.set_xlabel('Number of Mentions')
            ax1.set_title('Technology Mentions in University Profiles')
            
            # Add count labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                        ha='left', va='center', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No technology mentions found', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Technology Mentions in University Profiles')
        
        # 2. Technology distribution in graph data
        if graph_analysis and graph_analysis['tech_counts']:
            graph_tech_data = pd.DataFrame(list(graph_analysis['tech_counts'].items()), 
                                         columns=['Technology', 'Count'])
            graph_tech_data = graph_tech_data.sort_values('Count', ascending=True)
            
            bars = ax2.barh(graph_tech_data['Technology'], graph_tech_data['Count'], 
                           color=plt.cm.plasma(np.linspace(0, 1, len(graph_tech_data))))
            ax2.set_xlabel('Number of Mentions')
            ax2.set_title('Technology Mentions in Graph Data')
            
            # Add count labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                        ha='left', va='center', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No technology mentions found', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Technology Mentions in Graph Data')
        
        # 3. University-level technology prevalence
        if profile_analysis and profile_analysis['university_tech_counts']:
            univ_tech_data = []
            for univ, tech_counts in profile_analysis['university_tech_counts'].items():
                total_mentions = sum(tech_counts.values())
                if total_mentions > 0:
                    univ_tech_data.append({
                        'University': univ,
                        'Total Mentions': total_mentions,
                        'AI/ML': tech_counts.get('AI/ML', 0),
                        'GIS': tech_counts.get('GIS', 0),
                        'Drones': tech_counts.get('Drones', 0),
                        'Data Science': tech_counts.get('Data Science', 0)
                    })
            
            if univ_tech_data:
                univ_df = pd.DataFrame(univ_tech_data)
                top_univ = univ_df.sort_values('Total Mentions', ascending=False).head(10)
                
                bars = ax3.barh(range(len(top_univ)), top_univ['Total Mentions'], 
                               color=plt.cm.magma(np.linspace(0, 1, len(top_univ))))
                ax3.set_xlabel('Total Technology Mentions')
                ax3.set_title('Top 10 Universities by Technology Mentions')
                ax3.set_yticks(range(len(top_univ)))
                ax3.set_yticklabels(top_univ['University'], fontsize=8)
                ax3.invert_yaxis()
            else:
                ax3.text(0.5, 0.5, 'No university data', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Top 10 Universities by Technology Mentions')
        else:
            ax3.text(0.5, 0.5, 'No university data', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Top 10 Universities by Technology Mentions')
        
        # 4. Summary statistics
        ax4.axis('off')
        summary_text = f"""
        TECHNOLOGY PREVALENCE SUMMARY:
        
        UNIVERSITY PROFILES ANALYSIS:
        • Universities with Technology Mentions: {profile_analysis.get('universities_with_tech', 0) if profile_analysis else 0}
        • Total Technology Mentions: {profile_analysis.get('total_mentions', 0) if profile_analysis else 0}
        • Mission Paragraphs Analyzed: {len(mission_df) if not mission_df.empty else 0}
        
        GRAPH DATA ANALYSIS:
        • Universities with Technology Mentions: {graph_analysis.get('universities_with_tech', 0) if graph_analysis else 0}
        • Total Technology Mentions: {graph_analysis.get('total_mentions', 0) if graph_analysis else 0}
        
        TOP TECHNOLOGY AREAS:
        {chr(10).join([f"• {tech}: {count} mentions" for tech, count in sorted(profile_analysis.get('tech_counts', {}).items(), key=lambda x: x[1], reverse=True)[:3]]) if profile_analysis and profile_analysis.get('tech_counts') else "None found"}
        """
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('visualizations/mission_statement_technology_prevalence.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Detailed technology breakdown
        if profile_analysis and profile_analysis['tech_counts']:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('Detailed Technology Prevalence Analysis', fontsize=16, fontweight='bold')
            
            # 1. Technology category breakdown
            tech_categories = list(profile_analysis['tech_counts'].keys())
            tech_counts = list(profile_analysis['tech_counts'].values())
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(tech_categories)))
            wedges, texts, autotexts = ax1.pie(tech_counts, labels=tech_categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax1.set_title('Technology Distribution in Mission Statements')
            
            # 2. University technology heatmap
            if profile_analysis['university_tech_counts']:
                univ_tech_matrix = []
                univ_names = []
                
                for univ, tech_counts in profile_analysis['university_tech_counts'].items():
                    if sum(tech_counts.values()) > 0:  # Only include universities with mentions
                        univ_names.append(univ)
                        row = [tech_counts.get(tech, 0) for tech in tech_categories]
                        univ_tech_matrix.append(row)
                
                if univ_tech_matrix:
                    # Limit to top 20 universities
                    top_20_univ = univ_names[:20]
                    top_20_matrix = univ_tech_matrix[:20]
                    
                    heatmap_df = pd.DataFrame(top_20_matrix, 
                                            index=top_20_univ,
                                            columns=tech_categories)
                    
                    sns.heatmap(heatmap_df, annot=True, fmt='d', cmap='YlOrRd', 
                               cbar_kws={'label': 'Number of Mentions'}, ax=ax2)
                    ax2.set_title('University Technology Mention Heatmap (Top 20)')
                    ax2.set_xlabel('Technology Categories')
                    ax2.set_ylabel('Universities')
                else:
                    ax2.text(0.5, 0.5, 'No university data', ha='center', va='center', transform=ax2.transAxes)
                    ax2.set_title('University Technology Mention Heatmap')
            else:
                ax2.text(0.5, 0.5, 'No university data', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('University Technology Mention Heatmap')
            
            plt.tight_layout()
            plt.savefig('visualizations/mission_statement_technology_breakdown.png', dpi=300, bbox_inches='tight')
            plt.close()

def main():
    """Main analysis function"""
    print("Starting Mission Statement Technology Prevalence Analysis...")
    
    # Initialize analyzer
    analyzer = MissionStatementAnalyzer(uri, username, password)
    
    try:
        # Extract mission statements from university profiles
        mission_df = analyzer.extract_mission_statements_from_profiles()
        print(f"Extracted {len(mission_df)} mission paragraphs with technology mentions")
        
        # Analyze graph data
        programs, departments, universities = analyzer.analyze_graph_mission_statements()
        print(f"Found {len(programs)} programs, {len(departments)} departments, {len(universities)} universities with descriptions")
        
        # Analyze technology prevalence
        profile_analysis, graph_analysis = analyzer.analyze_technology_prevalence(mission_df, programs, departments, universities)
        
        # Create visualizations
        analyzer.create_comprehensive_visualizations(profile_analysis, graph_analysis, mission_df)
        
        # Print summary
        print("\n" + "="*80)
        print("MISSION STATEMENT TECHNOLOGY PREVALENCE ANALYSIS")
        print("="*80)
        
        if profile_analysis:
            print(f"Universities with technology mentions in profiles: {profile_analysis['universities_with_tech']}")
            print(f"Total technology mentions in profiles: {profile_analysis['total_mentions']}")
            print("\nTechnology distribution in profiles:")
            for tech, count in profile_analysis['tech_counts'].items():
                percentage = profile_analysis['tech_percentages'][tech]
                print(f"  {tech}: {count} mentions ({percentage:.1f}%)")
        
        if graph_analysis:
            print(f"\nUniversities with technology mentions in graph: {graph_analysis['universities_with_tech']}")
            print(f"Total technology mentions in graph: {graph_analysis['total_mentions']}")
            print("\nTechnology distribution in graph:")
            for tech, count in graph_analysis['tech_counts'].items():
                percentage = graph_analysis['tech_percentages'][tech]
                print(f"  {tech}: {count} mentions ({percentage:.1f}%)")
        
        print("\nVisualizations saved to 'visualizations' folder:")
        print("- mission_statement_technology_prevalence.png")
        print("- mission_statement_technology_breakdown.png")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main() 