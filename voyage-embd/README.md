# 🚀 Voyage AI Embeddings System

This folder contains a sophisticated embeddings-based analysis system for university profiles using **Voyage AI** embeddings. The system provides semantic analysis, content clustering, and AI readiness assessment.

## 🎯 **What This System Does**

### **Core Capabilities:**
- **Semantic Content Extraction**: Uses Voyage AI embeddings to understand content meaning
- **AI Readiness Analysis**: Identifies and scores universities based on AI-related content
- **Content Clustering**: Groups similar content using advanced clustering algorithms
- **Similarity Analysis**: Finds semantically similar sections across universities
- **Comprehensive Reporting**: Generates detailed analysis reports in JSON format

### **Analysis Types:**
1. **AI Programs**: Identifies AI-related academic programs
2. **AI Faculty**: Finds faculty with AI expertise
3. **AI Research**: Locates AI research centers and infrastructure
4. **AI Readiness**: Assesses overall AI readiness scores
5. **Content Clustering**: Groups universities by AI focus

## 🛠️ **Setup & Installation**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Voyage AI API Key**
```bash
export VOYAGE_API_KEY='your-api-key-here'
```

### **3. Verify Installation**
```bash
python voyage_extractor.py --help
```

## 📁 **File Structure**

```
voyage-embd/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.yaml                 # Configuration settings
├── voyage_extractor.py         # Main extraction and analysis engine
├── ai_content_analyzer.py      # Specialized AI content analyzer
└── results/                    # Output directory (created automatically)
```

## 🚀 **Quick Start**

### **Basic Analysis (All Content)**
```bash
cd voyage-embd
python voyage_extractor.py
```

### **AI-Focused Analysis**
```bash
cd voyage-embd
python ai_content_analyzer.py
```

## 🔧 **Configuration**

Edit `config.yaml` to customize:

- **Voyage AI Model**: Choose embedding model (`voyage-large-2`, etc.)
- **Batch Size**: Control API rate limiting
- **Analysis Thresholds**: Adjust similarity thresholds
- **AI Keywords**: Customize AI-related search terms
- **Output Settings**: Control what gets saved

## 📊 **Output Files**

### **1. General Analysis Results**
- **File**: `voyage_analysis_results.json`
- **Contains**: Similarity analysis, clustering, semantic summary

### **2. AI Readiness Report**
- **File**: `ai_readiness_report.json`
- **Contains**: AI programs, faculty, research, readiness scores

## 🎯 **Key Features**

### **Semantic Understanding**
- Uses **Voyage AI embeddings** for deep content understanding
- Processes text in semantic context, not just keyword matching
- Handles variations in terminology and language

### **Advanced Clustering**
- **K-means clustering** for general content grouping
- **DBSCAN clustering** for AI focus analysis
- Automatic cluster size optimization

### **Comprehensive Analysis**
- **8 content section types** analyzed per university
- **Multi-dimensional scoring** for AI readiness
- **Cross-university comparison** and ranking

## 🔍 **Content Section Types Analyzed**

1. **Overview**: General university information
2. **AI Readiness Assessment**: AI adoption status
3. **Academic Programs**: Degree programs and courses
4. **Faculty Expertise**: Faculty research and expertise
5. **Research Centers**: Research infrastructure
6. **Technology Integration**: Tech adoption and usage
7. **Strategic Recommendations**: Future plans and strategies
8. **References**: Source materials and citations

## 📈 **Analysis Metrics**

### **Similarity Scores**
- **Range**: 0.0 to 1.0 (higher = more similar)
- **Threshold**: 0.3 for AI relevance
- **Calculation**: Cosine similarity between embeddings

### **AI Readiness Scores**
- **Per Section**: Individual section AI relevance
- **Per University**: Average across all sections
- **Ranking**: Universities ranked by overall AI readiness

### **Clustering Results**
- **Cluster Count**: Automatic determination
- **Cluster Quality**: Based on similarity density
- **Noise Handling**: Outliers identified separately

## 🚨 **Rate Limiting & Best Practices**

### **API Usage**
- **Batch Size**: 10 texts per request (configurable)
- **Timeout**: 30 seconds per request
- **Error Handling**: Graceful fallback for failed requests

### **Performance Tips**
- Process universities in smaller batches for large datasets
- Monitor API usage and adjust batch sizes
- Use caching for repeated analyses

## 🔧 **Customization**

### **Adding New Section Types**
1. Add pattern to `section_patterns` in `extract_sections()`
2. Update analysis functions to handle new type
3. Modify clustering and similarity calculations

### **Custom AI Keywords**
1. Edit `ai_keywords` list in `AIContentAnalyzer`
2. Adjust similarity thresholds in `config.yaml`
3. Test with sample content

### **New Analysis Types**
1. Create new method in `AIContentAnalyzer`
2. Add to `generate_ai_readiness_report()`
3. Update output structure

## 📊 **Example Output Structure**

```json
{
  "ai_programs": [...],
  "ai_faculty": [...],
  "ai_research": [...],
  "readiness_patterns": {
    "total_universities": 50,
    "readiness_scores": [...],
    "statistics": {...},
    "top_performers": [...]
  },
  "ai_clusters": {
    "total_clusters": 5,
    "clusters": {...}
  },
  "university_ai_scores": {...},
  "summary": {...}
}
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **API Key Error**
   ```bash
   export VOYAGE_API_KEY='your-key-here'
   ```

2. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

3. **Memory Issues**
   - Reduce batch size in config
   - Process fewer universities at once

4. **Rate Limiting**
   - Increase batch size
   - Add delays between requests

## 📚 **Advanced Usage**

### **Custom Analysis Pipeline**
```python
from voyage_extractor import VoyageAIExtractor
from ai_content_analyzer import AIContentAnalyzer

# Initialize
extractor = VoyageAIExtractor(api_key)
analyzer = AIContentAnalyzer(extractor)

# Custom analysis
sections = extractor.extract_sections("university.md")
embeddings = extractor.get_embeddings([s.content for s in sections])
# ... custom processing
```

### **Integration with Other Systems**
- **Export to CSV**: Use pandas for data export
- **Database Storage**: Save embeddings to vector database
- **API Endpoints**: Create web service for analysis
- **Real-time Analysis**: Process new content as it arrives

## 🤝 **Contributing**

To extend the system:

1. **Add New Analysis Types**: Create new methods in analyzer classes
2. **Improve Embedding Quality**: Experiment with different Voyage AI models
3. **Optimize Performance**: Improve batching and caching
4. **Add Visualization**: Create charts and graphs from results

## 📄 **License & Attribution**

- **Voyage AI**: For embedding API and models
- **Scikit-learn**: For clustering and similarity algorithms
- **University Profiles**: Source data from Knowledge Graph Perseus project

## 🆘 **Support**

For issues or questions:

1. Check the troubleshooting section above
2. Review configuration settings
3. Verify API key and permissions
4. Check Voyage AI service status

---

**🚀 Ready to analyze university AI readiness with semantic intelligence!**
