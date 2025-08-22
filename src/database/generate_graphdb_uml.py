#!/usr/bin/env python3
"""
Graph Database UML Diagram Generator
Generates UML diagrams specifically for Neo4j Graph Database entities and relationships
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import os

def create_graphdb_uml_diagram():
    """Create UML diagram showing Graph Database entities and relationships."""
    fig, ax = plt.subplots(1, 1, figsize=(20, 16))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define colors for Graph DB entities
    colors = {
        'node': '#E8F4FD',
        'relationship': '#FFE6E6',
        'border': '#2E86AB',
        'text': '#2C3E50',
        'arrow': '#34495E',
        'neo4j': '#018BFF'  # Neo4j blue
    }
    
    # Graph Database entities with Neo4j-specific properties
    entities = {
        'University': {
            'pos': (1, 10),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'type: String', 'location: String', 'land_grant: Boolean', 'description: String'],
            'color': colors['node'],
            'label': '(:University)'
        },
        'Department': {
            'pos': (5, 10),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'university: String', 'focus_area: String', 'faculty_count: Integer'],
            'color': colors['node'],
            'label': '(:Department)'
        },
        'Program': {
            'pos': (9, 10),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'level: String', 'type: String', 'technology_integration: Float'],
            'color': colors['node'],
            'label': '(:Program)'
        },
        'Course': {
            'pos': (1, 7.5),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'code: String', 'level: String', 'technology_focus: String'],
            'color': colors['node'],
            'label': '(:Course)'
        },
        'Faculty': {
            'pos': (5, 7.5),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'title: String', 'expertise: String', 'research_interests: String'],
            'color': colors['node'],
            'label': '(:Faculty)'
        },
        'Technology': {
            'pos': (9, 7.5),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'category: String', 'adoption_level: String', 'applications: String'],
            'color': colors['node'],
            'label': '(:Technology)'
        },
        'ResearchCenter': {
            'pos': (1, 5),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'name: String', 'focus_area: String', 'funding_level: String'],
            'color': colors['node'],
            'label': '(:ResearchCenter)'
        },
        'Funding': {
            'pos': (5, 5),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'source: String', 'amount: Float', 'purpose: String'],
            'color': colors['node'],
            'label': '(:Funding)'
        },
        'Partnership': {
            'pos': (9, 5),
            'width': 2.8,
            'height': 2,
            'attributes': ['id: String', 'type: String', 'description: String', 'status: String'],
            'color': colors['node'],
            'label': '(:Partnership)'
        }
    }
    
    # Draw entities
    for name, info in entities.items():
        x, y = info['pos']
        width, height = info['width'], info['height']
        color = info['color']
        label = info['label']
        
        # Draw entity box
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=color,
                            edgecolor=colors['border'],
                            linewidth=2)
        ax.add_patch(box)
        
        # Add Neo4j label
        ax.text(x + width/2, y + height - 0.1, label,
                ha='center', va='top', fontsize=10, fontweight='bold',
                color=colors['neo4j'])
        
        # Add entity name
        ax.text(x + width/2, y + height - 0.3, name,
                ha='center', va='top', fontsize=11, fontweight='bold',
                color=colors['text'])
        
        # Add attributes
        for i, attr in enumerate(info['attributes']):
            ax.text(x + 0.1, y + height - 0.5 - i*0.12, attr,
                   ha='left', va='top', fontsize=8, color=colors['text'])
    
    # Graph Database relationships with Neo4j syntax
    relationships = [
        ((1.4, 9.5), (5.4, 9.5), '[:OFFERS]'),
        ((5.4, 9.5), (9.4, 9.5), '[:OFFERS]'),
        ((1.4, 9.5), (1.4, 7.5), '[:OFFERS]'),
        ((5.4, 9.5), (5.4, 7.5), '[:EMPLOYS]'),
        ((9.4, 9.5), (9.4, 7.5), '[:SPECIALIZES_IN]'),
        ((1.4, 7.5), (5.4, 7.5), '[:COVERS]'),
        ((5.4, 7.5), (9.4, 7.5), '[:RESEARCHES]'),
        ((1.4, 7.5), (1.4, 5), '[:HAS]'),
        ((5.4, 7.5), (5.4, 5), '[:RECEIVES]'),
        ((9.4, 7.5), (9.4, 5), '[:HAS]'),
        ((1.4, 5), (5.4, 5), '[:FOCUSES_ON]'),
        ((5.4, 5), (9.4, 5), '[:WORKS_IN]')
    ]
    
    for start, end, label in relationships:
        # Draw relationship arrow
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc=colors['arrow'])
        ax.add_patch(arrow)
        
        # Add relationship label
        mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2
        ax.text(mid_x, mid_y + 0.1, label, ha='center', va='bottom',
               fontsize=7, color=colors['arrow'], fontweight='bold')
    
    # Add Graph Database specific elements
    ax.text(6, 2, 'Neo4j Graph Database Schema', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            color=colors['neo4j'])
    
    ax.text(6, 1.5, 'Nodes: (:Label) | Relationships: [:TYPE]', 
            ha='center', va='center', fontsize=10,
            color=colors['text'])
    
    plt.title('Knowledge Graph Database UML Model (Neo4j)', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_graphdb_query_diagram():
    """Create UML diagram showing Graph Database query patterns."""
    fig, ax = plt.subplots(1, 1, figsize=(18, 14))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define colors
    colors = {
        'query': '#FFE6E6',
        'result': '#E6F3FF',
        'border': '#2E86AB',
        'text': '#2C3E50',
        'arrow': '#34495E',
        'cypher': '#018BFF'
    }
    
    # Query patterns and their visual representation
    queries = {
        'Technology_Adoption': {
            'pos': (1, 10),
            'width': 3,
            'height': 1.5,
            'query': 'MATCH (u:University)-[:OFFERS]->(d:Department)-[:OFFERS]->(p:Program)-[:SPECIALIZES_IN]->(t:Technology)',
            'result': 'Technology adoption by universities',
            'color': colors['query']
        },
        'Faculty_Expertise': {
            'pos': (6, 10),
            'width': 3,
            'height': 1.5,
            'query': 'MATCH (f:Faculty)-[:RESEARCHES]->(t:Technology)',
            'result': 'Faculty research expertise',
            'color': colors['query']
        },
        'Course_Technology': {
            'pos': (1, 8),
            'width': 3,
            'height': 1.5,
            'query': 'MATCH (c:Course)-[:COVERS]->(t:Technology)',
            'result': 'Technology coverage in courses',
            'color': colors['query']
        },
        'Research_Centers': {
            'pos': (6, 8),
            'width': 3,
            'height': 1.5,
            'query': 'MATCH (rc:ResearchCenter)-[:FOCUSES_ON]->(t:Technology)',
            'result': 'Research center technology focus',
            'color': colors['query']
        },
        'Funding_Analysis': {
            'pos': (1, 6),
            'width': 3,
            'height': 1.5,
            'query': 'MATCH (u:University)-[:RECEIVES]->(f:Funding)',
            'result': 'University funding analysis',
            'color': colors['query']
        },
        'Partnership_Network': {
            'pos': (6, 6),
            'width': 3,
            'height': 1.5,
            'query': 'MATCH (u:University)-[:HAS]->(p:Partnership)',
            'result': 'University partnership networks',
            'color': colors['query']
        }
    }
    
    # Draw query patterns
    for name, info in queries.items():
        x, y = info['pos']
        width, height = info['width'], info['height']
        color = info['color']
        
        # Draw query box
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=color,
                            edgecolor=colors['border'],
                            linewidth=2)
        ax.add_patch(box)
        
        # Add query name
        ax.text(x + width/2, y + height - 0.1, name.replace('_', ' '),
                ha='center', va='top', fontsize=10, fontweight='bold',
                color=colors['text'])
        
        # Add Cypher query
        ax.text(x + 0.1, y + height - 0.3, info['query'],
               ha='left', va='top', fontsize=7, color=colors['cypher'],
               fontfamily='monospace')
        
        # Add result description
        ax.text(x + 0.1, y + height - 0.5, info['result'],
               ha='left', va='top', fontsize=8, color=colors['text'])
    
    # Add relationship arrows between queries
    arrows = [
        ((2.5, 9.5), (6, 9.5), 'Data Flow'),
        ((2.5, 7.5), (6, 7.5), 'Cross Analysis'),
        ((2.5, 5.5), (6, 5.5), 'Network Analysis')
    ]
    
    for start, end, label in arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=15, fc=colors['arrow'])
        ax.add_patch(arrow)
        
        mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2
        ax.text(mid_x, mid_y + 0.1, label, ha='center', va='bottom',
               fontsize=8, color=colors['arrow'], fontweight='bold')
    
    # Add Graph Database query information
    ax.text(6, 3, 'Neo4j Cypher Query Patterns', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            color=colors['cypher'])
    
    ax.text(6, 2.5, 'Complex relationship traversal and pattern matching', 
            ha='center', va='center', fontsize=10,
            color=colors['text'])
    
    plt.title('Graph Database Query Patterns UML', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_graphdb_architecture_diagram():
    """Create UML diagram showing Graph Database architecture."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    colors = {
        'layer': '#E8F4FD',
        'component': '#FFE6E6',
        'border': '#2E86AB',
        'text': '#2C3E50',
        'arrow': '#34495E',
        'neo4j': '#018BFF'
    }
    
    # Architecture components
    components = {
        'Application_Layer': {
            'pos': (1, 9),
            'width': 8,
            'height': 0.8,
            'components': ['Python Scripts', 'Analysis Tools', 'Visualization'],
            'color': colors['layer']
        },
        'API_Layer': {
            'pos': (1, 8),
            'width': 8,
            'height': 0.8,
            'components': ['Neo4j Python Driver', 'Cypher Queries', 'Graph Algorithms'],
            'color': colors['layer']
        },
        'Database_Layer': {
            'pos': (1, 7),
            'width': 8,
            'height': 0.8,
            'components': ['Neo4j Database', 'Nodes & Relationships', 'Indexes'],
            'color': colors['layer']
        },
        'Data_Sources': {
            'pos': (1, 6),
            'width': 3.5,
            'height': 1.5,
            'components': ['University Profiles', 'Gemini Research', 'OpenAI Extraction'],
            'color': colors['component']
        },
        'Knowledge_Graph': {
            'pos': (5.5, 6),
            'width': 3.5,
            'height': 1.5,
            'components': ['Entities', 'Relationships', 'Properties'],
            'color': colors['component']
        },
        'Analysis_Results': {
            'pos': (1, 4),
            'width': 8,
            'height': 1.5,
            'components': ['Technology Adoption', 'Faculty Expertise', 'Program Analysis'],
            'color': colors['component']
        },
        'Neo4j_Features': {
            'pos': (1, 2),
            'width': 8,
            'height': 1,
            'components': ['Graph Traversal', 'Pattern Matching', 'Cypher Queries', 'Graph Algorithms'],
            'color': colors['neo4j']
        }
    }
    
    # Draw components
    for name, info in components.items():
        x, y = info['pos']
        width, height = info['width'], info['height']
        color = info['color']
        
        # Draw component box
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=color,
                            edgecolor=colors['border'],
                            linewidth=2)
        ax.add_patch(box)
        
        # Add component name
        ax.text(x + width/2, y + height - 0.1, name.replace('_', ' '),
                ha='center', va='top', fontsize=10, fontweight='bold',
                color=colors['text'])
        
        # Add sub-components
        for i, comp in enumerate(info['components']):
            ax.text(x + 0.1, y + height - 0.3 - i*0.15, comp,
                   ha='left', va='top', fontsize=8, color=colors['text'])
    
    # Draw connections
    connections = [
        ((5, 8.5), (5, 7.5), 'Data Flow'),
        ((2.75, 6.5), (5, 6.5), 'ETL Process'),
        ((5, 6.5), (7.25, 6.5), 'Graph Construction'),
        ((5, 5.5), (5, 4.5), 'Analysis Pipeline'),
        ((5, 3.5), (5, 2.5), 'Results Generation')
    ]
    
    for start, end, label in connections:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=15, fc=colors['arrow'])
        ax.add_patch(arrow)
        
        mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2
        ax.text(mid_x, mid_y + 0.1, label, ha='center', va='bottom',
               fontsize=8, color=colors['arrow'], fontweight='bold')
    
    plt.title('Graph Database Architecture UML', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def main():
    """Generate all Graph Database UML diagrams."""
    print("Generating Graph Database UML diagrams...")
    
    # Create output directory
    os.makedirs('uml_images', exist_ok=True)
    
    # Generate Graph Database schema diagram
    print("Generating Graph Database schema diagram...")
    fig1 = create_graphdb_uml_diagram()
    fig1.savefig('uml_images/graphdb_schema_uml.png', dpi=300, bbox_inches='tight')
    fig1.savefig('uml_images/graphdb_schema_uml.pdf', bbox_inches='tight')
    plt.close(fig1)
    
    # Generate Graph Database query patterns diagram
    print("Generating Graph Database query patterns diagram...")
    fig2 = create_graphdb_query_diagram()
    fig2.savefig('uml_images/graphdb_queries_uml.png', dpi=300, bbox_inches='tight')
    fig2.savefig('uml_images/graphdb_queries_uml.pdf', bbox_inches='tight')
    plt.close(fig2)
    
    # Generate Graph Database architecture diagram
    print("Generating Graph Database architecture diagram...")
    fig3 = create_graphdb_architecture_diagram()
    fig3.savefig('uml_images/graphdb_architecture_uml.png', dpi=300, bbox_inches='tight')
    fig3.savefig('uml_images/graphdb_architecture_uml.pdf', bbox_inches='tight')
    plt.close(fig3)
    
    print("✓ All Graph Database UML diagrams generated successfully!")
    print("\nGenerated files:")
    print("- uml_images/graphdb_schema_uml.png")
    print("- uml_images/graphdb_schema_uml.pdf")
    print("- uml_images/graphdb_queries_uml.png")
    print("- uml_images/graphdb_queries_uml.pdf")
    print("- uml_images/graphdb_architecture_uml.png")
    print("- uml_images/graphdb_architecture_uml.pdf")

if __name__ == "__main__":
    main() 