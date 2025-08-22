# Database Setup Guide for KG-Perseus Project

This guide explains how to set up and use the Neo4j graph database for the KG-Perseus project.

## 🗄️ **What's Included in This Repository**

### **1. Extracted University Data (JSON Files)**
- **Location**: `extracted_university_data/` directory
- **Content**: 50+ universities with programs, courses, faculty, and research centers
- **Format**: Structured JSON with consistent schema
- **Size**: ~1.5MB total (perfect for GitHub)

### **2. Database Setup Scripts**
- **`database_setup.py`**: Python script to initialize Neo4j database
- **`docker-compose.yml`**: Docker configuration for local Neo4j instance
- **Cypher Queries**: Ready-to-use queries in `data/outputs/` directory

## 🚀 **Quick Start Options**

### **Option 1: Docker (Recommended for Beginners)**

1. **Install Docker and Docker Compose**
   ```bash
   # macOS (using Homebrew)
   brew install docker docker-compose
   
   # Ubuntu/Debian
   sudo apt-get install docker.io docker-compose
   ```

2. **Start Neo4j Database**
   ```bash
   cd /path/to/KG-perseus
   docker-compose up -d
   ```

3. **Access Neo4j Browser**
   - Open: http://localhost:7474
   - Username: `neo4j`
   - Password: `password`

4. **Initialize Database with Data**
   ```bash
   python database_setup.py --uri bolt://localhost:7687 --user neo4j --password password
   ```

### **Option 2: Local Neo4j Installation**

1. **Download Neo4j Desktop** from [neo4j.com](https://neo4j.com/download/)
2. **Create a new database** with username `neo4j` and password `password`
3. **Start the database** and note the connection details
4. **Run the setup script**:
   ```bash
   python database_setup.py --uri <your_neo4j_uri> --user neo4j --password password
   ```

### **Option 3: Cloud Neo4j (Neo4j AuraDB)**

1. **Sign up** for [Neo4j AuraDB](https://neo4j.com/cloud/platform/aura-graph-database/)
2. **Create a new database** and get connection details
3. **Update your `.env` file** with the cloud credentials
4. **Run the setup script** with cloud connection details

## 📊 **Database Schema**

### **Node Types**
- **University**: Educational institutions
- **Program**: Academic programs (undergraduate, master's, doctoral)
- **Course**: Individual courses with technology focus
- **Faculty**: Faculty members with research areas
- **Department**: Academic departments
- **ResearchCenter**: Research centers and labs

### **Relationship Types**
- **[:OFFERS]**: University → Program/Course
- **[:HAS]**: University → Faculty/ResearchCenter
- **[:APPOINTED_TO]**: Faculty → Department
- **[:USES_TECHNOLOGY]**: Program/Course → Technology
- **[:ASSOCIATED_WITH]**: Program → ResearchCenter

### **Key Properties**
- **Program Level**: Undergraduate, Master, Doctoral
- **Program Type**: Forestry/Environmental, Geography/Geospatial, Computer Science/Data Science
- **Technology Focus**: AI/ML, GIS, Remote Sensing, Drones/UAV

## 🔧 **Database Setup Script Details**

### **What the Script Does**
1. **Creates Constraints**: Ensures data integrity
2. **Creates Indexes**: Improves query performance
3. **Imports University Data**: Loads JSON files into Neo4j
4. **Classifies Data**: Automatically categorizes programs and technologies
5. **Verifies Import**: Confirms data was loaded correctly

### **Script Usage**
```bash
# Basic usage
python database_setup.py --uri bolt://localhost:7687 --user neo4j --password password

# Clear existing data first
python database_setup.py --uri bolt://localhost:7687 --user neo4j --password password --clear

# Use custom data directory
python database_setup.py --uri bolt://localhost:7687 --user neo4j --password password --data-dir my_data
```

## 📈 **Sample Queries**

### **Basic Data Exploration**
```cypher
// Count all nodes by type
MATCH (n)
RETURN labels(n)[0] as node_type, count(n) as count
ORDER BY count DESC;

// Count all relationships by type
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;
```

### **Program Analysis**
```cypher
// Programs by level and type
MATCH (p:Program)
RETURN p.level, p.type, count(p) as count
ORDER BY p.level, p.type;

// Technology integration by program level
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
RETURN p.level, t.category, count(t) as tech_count
ORDER BY p.level, tech_count DESC;
```

### **University Comparison**
```cypher
// Universities with most AI/ML programs
MATCH (u:University)-[:OFFERS]->(p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE t.category = 'AI/ML'
RETURN u.name, count(p) as ai_programs
ORDER BY ai_programs DESC
LIMIT 10;
```

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Connection Refused**
   - Ensure Neo4j is running
   - Check port numbers (7474 for HTTP, 7687 for Bolt)
   - Verify firewall settings

2. **Authentication Failed**
   - Default credentials: `neo4j` / `password`
   - Check if password was changed during setup
   - Reset password if needed

3. **Import Errors**
   - Check JSON file format
   - Ensure sufficient memory allocation
   - Check Neo4j logs for detailed error messages

4. **Performance Issues**
   - Increase memory allocation in docker-compose.yml
   - Create additional indexes for frequently queried properties
   - Use parameterized queries for better performance

### **Useful Commands**
```bash
# Check Neo4j container status
docker-compose ps

# View Neo4j logs
docker-compose logs neo4j

# Restart Neo4j
docker-compose restart neo4j

# Stop and remove everything
docker-compose down -v
```

## 📚 **Next Steps**

After setting up the database:

1. **Run Analysis Scripts**: Use the RQ analysis scripts in `src/analysis/`
2. **Explore Data**: Use Neo4j Browser to explore relationships
3. **Run Cypher Queries**: Execute queries from `data/outputs/` directory
4. **Create Visualizations**: Generate charts and tables from the data

## 🔗 **Additional Resources**

- [Neo4j Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Neo4j Browser Guide](https://neo4j.com/docs/browser-manual/current/)
- [Docker Documentation](https://docs.docker.com/)

## 📞 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Review Neo4j logs for error messages
3. Ensure all dependencies are installed
4. Verify database connection parameters

---

**Note**: This database contains real university data extracted from public sources. The data is for research purposes and should be used in accordance with appropriate academic and ethical guidelines.
