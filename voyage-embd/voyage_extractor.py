#!/usr/bin/env python3
"""
Voyage AI Embeddings-Based University Profile Extractor
Uses Voyage AI embeddings for semantic analysis and content extraction
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

@dataclass
class ContentSection:
    """Represents a content section from a university profile"""
    university: str
    section_type: str
    content: str
    embedding: List[float] = None
    metadata: Dict[str, Any] = None

class VoyageAIExtractor:
    """Main class for Voyage AI-based content extraction"""
    
    def __init__(self, api_key: str, model_name: str = "voyage-large-2"):
        """
        Initialize the Voyage AI extractor
        
        Args:
            api_key: Voyage AI API key
            model_name: Model to use for embeddings
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.voyageai.com/v1/embeddings"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using Voyage AI
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            payload = {
                "model": self.model_name,
                "input": batch
            }
            
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                batch_embeddings = response.json()["data"]
                embeddings.extend([item["embedding"] for item in batch_embeddings])
                
                print(f"✓ Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                print(f"✗ Error processing batch {i//batch_size + 1}: {e}")
                # Return zero vectors for failed batches
                embeddings.extend([[0.0] * 1024] * len(batch))  # Assuming 1024-dim embeddings
        
        return embeddings
    
    def extract_sections(self, file_path: str) -> List[ContentSection]:
        """
        Extract content sections from a university profile markdown file
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of ContentSection objects
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        university_name = Path(file_path).stem.replace('_', ' ').title()
        sections = []
        
        # Define section patterns
        section_patterns = {
            'overview': r'## \*\*Overview\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'ai_readiness': r'## \*\*AI Readiness Assessment\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'programs': r'## \*\*Academic Programs\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'faculty': r'## \*\*Faculty Expertise\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'research': r'## \*\*Research Centers and Infrastructure\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'technology': r'## \*\*Technology Integration\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'strategic': r'## \*\*Strategic Recommendations\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
            'references': r'#### \*\*Works cited\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
        }
        
        for section_type, pattern in section_patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            if match:
                section_content = match.group(1).strip()
                if section_content and len(section_content) > 50:  # Filter out very short sections
                    sections.append(ContentSection(
                        university=university_name,
                        section_type=section_type,
                        content=section_content,
                        metadata={'file_path': str(file_path)}
                    ))
        
        return sections
    
    def analyze_semantic_similarity(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """
        Analyze semantic similarity between content sections
        
        Args:
            sections: List of ContentSection objects with embeddings
            
        Returns:
            Dictionary containing similarity analysis results
        """
        if not sections or not sections[0].embedding:
            return {"error": "No embeddings available for analysis"}
        
        # Convert embeddings to numpy array
        embeddings_matrix = np.array([s.embedding for s in sections])
        
        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(embeddings_matrix)
        
        # Find most similar sections
        most_similar = []
        for i in range(len(sections)):
            for j in range(i + 1, len(sections)):
                similarity = similarity_matrix[i][j]
                most_similar.append({
                    'section1': f"{sections[i].university} - {sections[i].section_type}",
                    'section2': f"{sections[j].university} - {sections[j].section_type}",
                    'similarity': float(similarity)
                })
        
        # Sort by similarity
        most_similar.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Cluster sections by similarity
        n_clusters = min(5, len(sections))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings_matrix)
        
        # Group sections by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({
                'university': sections[i].university,
                'section_type': sections[i].section_type,
                'similarity_score': float(similarity_matrix[i].mean())
            })
        
        return {
            'similarity_matrix': similarity_matrix.tolist(),
            'most_similar_sections': most_similar[:20],  # Top 20 most similar
            'clusters': clusters,
            'average_similarity': float(similarity_matrix.mean())
        }
    
    def extract_ai_related_content(self, sections: List[ContentSection], 
                                  ai_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Extract AI-related content using semantic similarity
        
        Args:
            sections: List of ContentSection objects
            ai_keywords: List of AI-related keywords to search for
            
        Returns:
            List of AI-related content items
        """
        if not ai_keywords:
            ai_keywords = [
                "artificial intelligence", "AI", "machine learning", "ML", 
                "data science", "computational", "algorithm", "neural network",
                "deep learning", "automation", "robotics", "computer vision",
                "natural language processing", "NLP", "predictive modeling"
            ]
        
        ai_content = []
        
        for section in sections:
            if section.embedding:
                # Create embedding for AI keywords
                keyword_embeddings = self.get_embeddings(ai_keywords)
                
                # Calculate similarity with section
                section_embedding = np.array(section.embedding)
                similarities = []
                
                for keyword_emb in keyword_embeddings:
                    if keyword_emb and any(keyword_emb):  # Check if embedding is valid
                        similarity = cosine_similarity(
                            [section_embedding], 
                            [keyword_emb]
                        )[0][0]
                        similarities.append(similarity)
                
                if similarities:
                    max_similarity = max(similarities)
                    if max_similarity > 0.3:  # Threshold for relevance
                        ai_content.append({
                            'university': section.university,
                            'section_type': section.section_type,
                            'content_preview': section.content[:200] + "...",
                            'ai_relevance_score': float(max_similarity),
                            'metadata': section.metadata
                        })
        
        # Sort by relevance score
        ai_content.sort(key=lambda x: x['ai_relevance_score'], reverse=True)
        return ai_content
    
    def generate_semantic_summary(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """
        Generate a semantic summary of all content
        
        Args:
            sections: List of ContentSection objects
            
        Returns:
            Dictionary containing semantic summary
        """
        if not sections:
            return {"error": "No sections to analyze"}
        
        # Group by section type
        by_type = {}
        for section in sections:
            if section.section_type not in by_type:
                by_type[section.section_type] = []
            by_type[section.section_type].append(section)
        
        summary = {
            'total_sections': len(sections),
            'universities_covered': len(set(s.university for s in sections)),
            'section_type_distribution': {k: len(v) for k, v in by_type.items()},
            'content_analysis': {}
        }
        
        # Analyze each section type
        for section_type, type_sections in by_type.items():
            if type_sections and type_sections[0].embedding:
                embeddings = np.array([s.embedding for s in type_sections])
                
                # Calculate diversity within section type
                avg_similarity = cosine_similarity(embeddings).mean()
                
                summary['content_analysis'][section_type] = {
                    'count': len(type_sections),
                    'diversity_score': 1 - float(avg_similarity),  # Higher = more diverse
                    'universities': list(set(s.university for s in type_sections))
                }
        
        return summary

def main():
    """Main function to demonstrate the Voyage AI extractor"""
    
    # Get API key from environment variable
    api_key = os.getenv('VOYAGE_API_KEY')
    if not api_key:
        print("❌ Error: VOYAGE_API_KEY environment variable not set")
        print("Please set your Voyage AI API key:")
        print("export VOYAGE_API_KEY='your-api-key-here'")
        return
    
    # Initialize extractor
    extractor = VoyageAIExtractor(api_key)
    
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
    
    # Perform semantic analysis
    print("\n🔬 Performing semantic analysis...")
    
    # Similarity analysis
    similarity_results = extractor.analyze_semantic_similarity(all_sections)
    
    # AI content extraction
    ai_content = extractor.extract_ai_related_content(all_sections)
    
    # Semantic summary
    summary = extractor.generate_semantic_summary(all_sections)
    
    # Save results
    results = {
        'similarity_analysis': similarity_results,
        'ai_content': ai_content,
        'semantic_summary': summary,
        'metadata': {
            'total_sections': len(all_sections),
            'universities_covered': len(set(s.university for s in all_sections)),
            'model_used': extractor.model_name
        }
    }
    
    output_file = "voyage_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analysis complete! Results saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("SEMANTIC ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total sections analyzed: {summary['total_sections']}")
    print(f"Universities covered: {summary['universities_covered']}")
    print(f"AI-relevant sections found: {len(ai_content)}")
    
    if ai_content:
        print(f"\nTop AI-relevant content:")
        for i, item in enumerate(ai_content[:5]):
            print(f"{i+1}. {item['university']} - {item['section_type']} (Score: {item['ai_relevance_score']:.3f})")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
