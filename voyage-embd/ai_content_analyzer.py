#!/usr/bin/env python3
"""
AI Content Analyzer using Voyage AI Embeddings
Specialized analysis for AI-related content in university profiles
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import pandas as pd
from voyage_extractor import VoyageAIExtractor, ContentSection

class AIContentAnalyzer:
    """Specialized analyzer for AI-related content"""
    
    def __init__(self, voyage_extractor: VoyageAIExtractor):
        """
        Initialize the AI content analyzer
        
        Args:
            voyage_extractor: Initialized VoyageAIExtractor instance
        """
        self.extractor = voyage_extractor
        self.ai_keywords = [
            "artificial intelligence", "AI", "machine learning", "ML", 
            "data science", "computational", "algorithm", "neural network",
            "deep learning", "automation", "robotics", "computer vision",
            "natural language processing", "NLP", "predictive modeling",
            "computer science", "engineering", "statistics", "informatics",
            "cyber systems", "digital transformation", "smart systems",
            "intelligent systems", "automated", "algorithmic", "computational thinking"
        ]
        
    def extract_ai_programs(self, sections: List[ContentSection]) -> List[Dict[str, Any]]:
        """
        Extract AI-related academic programs
        
        Args:
            sections: List of content sections
            
        Returns:
            List of AI program information
        """
        ai_programs = []
        
        for section in sections:
            if section.section_type == 'programs' and section.embedding:
                # Get embeddings for AI program keywords
                program_keywords = [
                    "AI program", "artificial intelligence degree", "machine learning major",
                    "data science program", "computer science AI", "AI concentration",
                    "AI minor", "AI certificate", "AI specialization"
                ]
                
                keyword_embeddings = self.extractor.get_embeddings(program_keywords)
                section_embedding = np.array(section.embedding)
                
                max_similarity = 0
                for keyword_emb in keyword_embeddings:
                    if keyword_emb and any(keyword_emb):
                        similarity = cosine_similarity([section_embedding], [keyword_emb])[0][0]
                        max_similarity = max(max_similarity, similarity)
                
                if max_similarity > 0.25:  # Lower threshold for programs
                    ai_programs.append({
                        'university': section.university,
                        'content': section.content,
                        'ai_relevance_score': float(max_similarity),
                        'metadata': section.metadata
                    })
        
        return sorted(ai_programs, key=lambda x: x['ai_relevance_score'], reverse=True)
    
    def extract_ai_faculty(self, sections: List[ContentSection]) -> List[Dict[str, Any]]:
        """
        Extract AI-related faculty expertise
        
        Args:
            sections: List of content sections
            
        Returns:
            List of AI faculty information
        """
        ai_faculty = []
        
        for section in sections:
            if section.section_type == 'faculty' and section.embedding:
                # Get embeddings for AI faculty keywords
                faculty_keywords = [
                    "AI researcher", "machine learning expert", "data scientist",
                    "computer scientist", "AI professor", "ML faculty",
                    "artificial intelligence faculty", "AI specialist", "computational researcher"
                ]
                
                keyword_embeddings = self.extractor.get_embeddings(faculty_keywords)
                section_embedding = np.array(section.embedding)
                
                max_similarity = 0
                for keyword_emb in keyword_embeddings:
                    if keyword_emb and any(keyword_emb):
                        similarity = cosine_similarity([section_embedding], [keyword_emb])[0][0]
                        max_similarity = max(max_similarity, similarity)
                
                if max_similarity > 0.25:
                    ai_faculty.append({
                        'university': section.university,
                        'content': section.content,
                        'ai_relevance_score': float(max_similarity),
                        'metadata': section.metadata
                    })
        
        return sorted(ai_faculty, key=lambda x: x['ai_relevance_score'], reverse=True)
    
    def extract_ai_research(self, sections: List[ContentSection]) -> List[Dict[str, Any]]:
        """
        Extract AI-related research centers and infrastructure
        
        Args:
            sections: List of content sections
            
        Returns:
            List of AI research information
        """
        ai_research = []
        
        for section in sections:
            if section.section_type == 'research' and section.embedding:
                # Get embeddings for AI research keywords
                research_keywords = [
                    "AI research center", "machine learning lab", "data science institute",
                    "AI laboratory", "computational research", "AI infrastructure",
                    "high performance computing", "AI computing cluster", "AI research facility"
                ]
                
                keyword_embeddings = self.extractor.get_embeddings(research_keywords)
                section_embedding = np.array(section.embedding)
                
                max_similarity = 0
                for keyword_emb in keyword_embeddings:
                    if keyword_emb and any(keyword_emb):
                        similarity = cosine_similarity([section_embedding], [keyword_emb])[0][0]
                        max_similarity = max(max_similarity, similarity)
                
                if max_similarity > 0.25:
                    ai_research.append({
                        'university': section.university,
                        'content': section.content,
                        'ai_relevance_score': float(max_similarity),
                        'metadata': section.metadata
                    })
        
        return sorted(ai_research, key=lambda x: x['ai_relevance_score'], reverse=True)
    
    def analyze_ai_readiness_patterns(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """
        Analyze patterns in AI readiness across universities
        
        Args:
            sections: List of content sections
            
        Returns:
            Dictionary containing AI readiness analysis
        """
        ai_readiness_sections = [s for s in sections if s.section_type == 'ai_readiness']
        
        if not ai_readiness_sections:
            return {"error": "No AI readiness sections found"}
        
        # Get embeddings for AI readiness keywords
        readiness_keywords = [
            "AI readiness", "artificial intelligence readiness", "AI adoption",
            "AI integration", "AI strategy", "AI implementation", "AI transformation",
            "digital readiness", "technology readiness", "AI maturity"
        ]
        
        keyword_embeddings = self.extractor.get_embeddings(readiness_keywords)
        
        readiness_scores = []
        for section in ai_readiness_sections:
            if section.embedding:
                section_embedding = np.array(section.embedding)
                max_similarity = 0
                
                for keyword_emb in keyword_embeddings:
                    if keyword_emb and any(keyword_emb):
                        similarity = cosine_similarity([section_embedding], [keyword_emb])[0][0]
                        max_similarity = max(max_similarity, similarity)
                
                readiness_scores.append({
                    'university': section.university,
                    'readiness_score': float(max_similarity),
                    'content_preview': section.content[:300] + "..."
                })
        
        # Sort by readiness score
        readiness_scores.sort(key=lambda x: x['readiness_score'], reverse=True)
        
        # Calculate statistics
        scores = [item['readiness_score'] for item in readiness_scores]
        
        return {
            'total_universities': len(readiness_scores),
            'readiness_scores': readiness_scores,
            'statistics': {
                'mean_score': float(np.mean(scores)),
                'median_score': float(np.median(scores)),
                'std_score': float(np.std(scores)),
                'min_score': float(np.min(scores)),
                'max_score': float(np.max(scores))
            },
            'top_performers': readiness_scores[:10],
            'bottom_performers': readiness_scores[-10:]
        }
    
    def cluster_universities_by_ai_focus(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """
        Cluster universities by their AI focus using DBSCAN
        
        Args:
            sections: List of content sections
            
        Returns:
            Dictionary containing clustering results
        """
        # Get all sections with embeddings
        sections_with_embeddings = [s for s in sections if s.embedding]
        
        if len(sections_with_embeddings) < 5:
            return {"error": "Insufficient sections with embeddings for clustering"}
        
        # Create embeddings matrix
        embeddings_matrix = np.array([s.embedding for s in sections_with_embeddings])
        
        # Use DBSCAN for clustering (handles varying cluster sizes)
        dbscan = DBSCAN(eps=0.3, min_samples=3)
        cluster_labels = dbscan.fit_predict(embeddings_matrix)
        
        # Group by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            
            clusters[label].append({
                'university': sections_with_embeddings[i].university,
                'section_type': sections_with_embeddings[i].section_type,
                'content_preview': sections_with_embeddings[i].content[:200] + "..."
            })
        
        # Analyze cluster characteristics
        cluster_analysis = {}
        for cluster_id, cluster_items in clusters.items():
            if cluster_id == -1:  # Noise points
                cluster_analysis['noise'] = {
                    'count': len(cluster_items),
                    'items': cluster_items
                }
            else:
                # Calculate cluster centroid
                cluster_embeddings = [sections_with_embeddings[i].embedding 
                                    for i, label in enumerate(cluster_labels) if label == cluster_id]
                centroid = np.mean(cluster_embeddings, axis=0)
                
                cluster_analysis[f'cluster_{cluster_id}'] = {
                    'count': len(cluster_items),
                    'centroid': centroid.tolist(),
                    'items': cluster_items,
                    'universities': list(set(item['university'] for item in cluster_items))
                }
        
        return {
            'total_clusters': len([k for k in clusters.keys() if k != -1]),
            'noise_points': len(clusters.get(-1, [])),
            'clusters': cluster_analysis,
            'total_sections': len(sections_with_embeddings)
        }
    
    def generate_ai_readiness_report(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """
        Generate comprehensive AI readiness report
        
        Args:
            sections: List of content sections
            
        Returns:
            Dictionary containing comprehensive AI readiness report
        """
        print("🔍 Analyzing AI programs...")
        ai_programs = self.extract_ai_programs(sections)
        
        print("🔍 Analyzing AI faculty...")
        ai_faculty = self.extract_ai_faculty(sections)
        
        print("🔍 Analyzing AI research...")
        ai_research = self.extract_ai_research(sections)
        
        print("🔍 Analyzing AI readiness patterns...")
        readiness_patterns = self.analyze_ai_readiness_patterns(sections)
        
        print("🔍 Clustering universities by AI focus...")
        ai_clusters = self.cluster_universities_by_ai_focus(sections)
        
        # Calculate overall AI readiness score for each university
        university_scores = {}
        for section in sections:
            if section.embedding:
                if section.university not in university_scores:
                    university_scores[section.university] = {
                        'sections': [],
                        'total_score': 0,
                        'section_count': 0
                    }
                
                # Calculate AI relevance for this section
                section_embedding = np.array(section.embedding)
                keyword_embeddings = self.extractor.get_embeddings(self.ai_keywords[:5])  # Use top 5 keywords
                
                max_similarity = 0
                for keyword_emb in keyword_embeddings:
                    if keyword_emb and any(keyword_emb):
                        similarity = cosine_similarity([section_embedding], [keyword_emb])[0][0]
                        max_similarity = max(max_similarity, similarity)
                
                university_scores[section.university]['sections'].append({
                    'type': section.section_type,
                    'ai_score': float(max_similarity)
                })
                university_scores[section.university]['total_score'] += max_similarity
                university_scores[section.university]['section_count'] += 1
        
        # Calculate average scores
        for university, data in university_scores.items():
            if data['section_count'] > 0:
                data['average_score'] = data['total_score'] / data['section_count']
            else:
                data['average_score'] = 0
        
        # Sort universities by average AI score
        sorted_universities = sorted(
            university_scores.items(), 
            key=lambda x: x[1]['average_score'], 
            reverse=True
        )
        
        return {
            'ai_programs': ai_programs,
            'ai_faculty': ai_faculty,
            'ai_research': ai_research,
            'readiness_patterns': readiness_patterns,
            'ai_clusters': ai_clusters,
            'university_ai_scores': dict(sorted_universities),
            'summary': {
                'total_universities': len(university_scores),
                'universities_with_ai_programs': len(ai_programs),
                'universities_with_ai_faculty': len(ai_faculty),
                'universities_with_ai_research': len(ai_research),
                'top_ai_universities': [u[0] for u in sorted_universities[:10]]
            }
        }

def main():
    """Main function to run AI content analysis"""
    
    # Get API key from environment variable
    api_key = os.getenv('VOYAGE_API_KEY')
    if not api_key:
        print("❌ Error: VOYAGE_API_KEY environment variable not set")
        print("Please set your Voyage AI API key:")
        print("export VOYAGE_API_KEY='your-api-key-here'")
        return
    
    # Initialize extractor and analyzer
    extractor = VoyageAIExtractor(api_key)
    analyzer = AIContentAnalyzer(extractor)
    
    # Get university profile files
    profiles_dir = Path("../docs/university-profiles")
    markdown_files = list(profiles_dir.glob("*.md"))
    
    print(f"🔍 Processing {len(markdown_files)} university profile files...")
    
    all_sections = []
    
    # Process each file
    for i, file_path in enumerate(markdown_files):
        print(f"\n📚 Processing {i+1}/{len(markdown_files)}: {file_path.stem}")
        
        try:
            sections = extractor.extract_sections(file_path)
            all_sections.extend(sections)
            print(f"  ✓ Extracted {len(sections)} content sections")
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
    
    if not all_sections:
        print("❌ No content sections extracted")
        return
    
    print(f"\n🎯 Total sections extracted: {len(all_sections)}")
    
    # Get embeddings for all sections
    print("\n🚀 Generating embeddings with Voyage AI...")
    texts = [section.content for section in all_sections]
    embeddings = extractor.get_embeddings(texts)
    
    # Assign embeddings to sections
    for section, embedding in zip(all_sections, embeddings):
        section.embedding = embedding
    
    print(f"✓ Generated embeddings for {len(all_sections)} sections")
    
    # Generate comprehensive AI readiness report
    print("\n🔬 Generating comprehensive AI readiness report...")
    ai_report = analyzer.generate_ai_readiness_report(all_sections)
    
    # Save results
    output_file = "ai_readiness_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ai_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ AI readiness report complete! Results saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("AI READINESS REPORT SUMMARY")
    print("="*60)
    summary = ai_report['summary']
    print(f"Total universities analyzed: {summary['total_universities']}")
    print(f"Universities with AI programs: {summary['universities_with_ai_programs']}")
    print(f"Universities with AI faculty: {summary['universities_with_ai_faculty']}")
    print(f"Universities with AI research: {summary['universities_with_ai_research']}")
    
    print(f"\nTop 10 AI-Ready Universities:")
    for i, university in enumerate(summary['top_ai_universities'][:10]):
        score = ai_report['university_ai_scores'][university]['average_score']
        print(f"{i+1}. {university} (Score: {score:.3f})")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
