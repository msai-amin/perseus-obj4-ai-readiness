-- RQ9 Cypher Queries for Research Centers and Labs Analysis
-- Neo4j Graph Database Queries for Research Question 9
-- How many programs are associated with research centers or labs devoted to GIS, AI, Remote Sensing?

-- ============================================================================
-- 1. DATABASE STRUCTURE VERIFICATION
-- ============================================================================

-- Query 1.1: Count Total Research Centers/Labs
MATCH (rc:ResearchCenter) 
RETURN count(rc) as total_research_centers;

-- Query 1.2: Count Total Labs
MATCH (l:Lab) 
RETURN count(l) as total_labs;

-- Query 1.3: Count Research Center-Program Relationships
MATCH (rc:ResearchCenter)-[:ASSOCIATED_WITH]->(p:Program) 
RETURN count(*) as total_research_center_program_relationships;

-- Query 1.4: Count Lab-Program Relationships
MATCH (l:Lab)-[:ASSOCIATED_WITH]->(p:Program) 
RETURN count(*) as total_lab_program_relationships;

-- ============================================================================
-- 2. RESEARCH CENTERS AND LABS CLASSIFICATION
-- ============================================================================

-- Query 2.1: Research Centers by Technology Focus
MATCH (rc:ResearchCenter)
WITH rc.name as center_name,
     CASE 
         WHEN toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
              toLower(rc.name) CONTAINS 'geographic' OR toLower(rc.name) CONTAINS 'spatial' OR
              toLower(rc.name) CONTAINS 'mapping' OR toLower(rc.name) CONTAINS 'cartography' THEN 'GIS'
         WHEN toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
              toLower(rc.name) CONTAINS 'machine learning' OR toLower(rc.name) CONTAINS 'ml' OR
              toLower(rc.name) CONTAINS 'computational' OR toLower(rc.name) CONTAINS 'data science' THEN 'AI'
         WHEN toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite' OR
              toLower(rc.name) CONTAINS 'aerial' OR toLower(rc.name) CONTAINS 'sensor' OR
              toLower(rc.name) CONTAINS 'earth observation' OR toLower(rc.name) CONTAINS 'spectral' THEN 'Remote Sensing'
         WHEN toLower(rc.name) CONTAINS 'drone' OR toLower(rc.name) CONTAINS 'uav' OR
              toLower(rc.name) CONTAINS 'unmanned aerial' OR toLower(rc.name) CONTAINS 'aerial photography' THEN 'Drones/UAV'
         WHEN toLower(rc.name) CONTAINS 'forestry' OR toLower(rc.name) CONTAINS 'forest' OR
              toLower(rc.name) CONTAINS 'natural resource' OR toLower(rc.name) CONTAINS 'environmental' THEN 'Forestry/Environmental'
         ELSE 'Other'
     END as technology_focus
RETURN technology_focus, count(center_name) as center_count
ORDER BY center_count DESC;

-- Query 2.2: Labs by Technology Focus
MATCH (l:Lab)
WITH l.name as lab_name,
     CASE 
         WHEN toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
              toLower(l.name) CONTAINS 'geographic' OR toLower(l.name) CONTAINS 'spatial' OR
              toLower(l.name) CONTAINS 'mapping' OR toLower(l.name) CONTAINS 'cartography' THEN 'GIS'
         WHEN toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
              toLower(l.name) CONTAINS 'machine learning' OR toLower(l.name) CONTAINS 'ml' OR
              toLower(l.name) CONTAINS 'computational' OR toLower(l.name) CONTAINS 'data science' THEN 'AI'
         WHEN toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite' OR
              toLower(l.name) CONTAINS 'aerial' OR toLower(l.name) CONTAINS 'sensor' OR
              toLower(l.name) CONTAINS 'earth observation' OR toLower(l.name) CONTAINS 'spectral' THEN 'Remote Sensing'
         WHEN toLower(l.name) CONTAINS 'drone' OR toLower(l.name) CONTAINS 'uav' OR
              toLower(l.name) CONTAINS 'unmanned aerial' OR toLower(l.name) CONTAINS 'aerial photography' THEN 'Drones/UAV'
         WHEN toLower(l.name) CONTAINS 'forestry' OR toLower(l.name) CONTAINS 'forest' OR
              toLower(l.name) CONTAINS 'natural resource' OR toLower(l.name) CONTAINS 'environmental' THEN 'Forestry/Environmental'
         ELSE 'Other'
     END as technology_focus
RETURN technology_focus, count(lab_name) as lab_count
ORDER BY lab_count DESC;

-- ============================================================================
-- 3. PROGRAM ASSOCIATIONS WITH RESEARCH CENTERS
-- ============================================================================

-- Query 3.1: Programs Associated with GIS Research Centers
MATCH (rc:ResearchCenter)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
      toLower(rc.name) CONTAINS 'geographic' OR toLower(rc.name) CONTAINS 'spatial' OR
      toLower(rc.name) CONTAINS 'mapping' OR toLower(rc.name) CONTAINS 'cartography'
RETURN rc.name as research_center, p.name as program_name, p.type as program_type
ORDER BY rc.name, p.name;

-- Query 3.2: Programs Associated with AI Research Centers
MATCH (rc:ResearchCenter)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
      toLower(rc.name) CONTAINS 'machine learning' OR toLower(rc.name) CONTAINS 'ml' OR
      toLower(rc.name) CONTAINS 'computational' OR toLower(rc.name) CONTAINS 'data science'
RETURN rc.name as research_center, p.name as program_name, p.type as program_type
ORDER BY rc.name, p.name;

-- Query 3.3: Programs Associated with Remote Sensing Research Centers
MATCH (rc:ResearchCenter)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite' OR
      toLower(rc.name) CONTAINS 'aerial' OR toLower(rc.name) CONTAINS 'sensor' OR
      toLower(rc.name) CONTAINS 'earth observation' OR toLower(rc.name) CONTAINS 'spectral'
RETURN rc.name as research_center, p.name as program_name, p.type as program_type
ORDER BY rc.name, p.name;

-- ============================================================================
-- 4. PROGRAM ASSOCIATIONS WITH LABS
-- ============================================================================

-- Query 4.1: Programs Associated with GIS Labs
MATCH (l:Lab)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
      toLower(l.name) CONTAINS 'geographic' OR toLower(l.name) CONTAINS 'spatial' OR
      toLower(l.name) CONTAINS 'mapping' OR toLower(l.name) CONTAINS 'cartography'
RETURN l.name as lab_name, p.name as program_name, p.type as program_type
ORDER BY l.name, p.name;

-- Query 4.2: Programs Associated with AI Labs
MATCH (l:Lab)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
      toLower(l.name) CONTAINS 'machine learning' OR toLower(l.name) CONTAINS 'ml' OR
      toLower(l.name) CONTAINS 'computational' OR toLower(l.name) CONTAINS 'data science'
RETURN l.name as lab_name, p.name as program_name, p.type as program_type
ORDER BY l.name, p.name;

-- Query 4.3: Programs Associated with Remote Sensing Labs
MATCH (l:Lab)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite' OR
      toLower(l.name) CONTAINS 'aerial' OR toLower(l.name) CONTAINS 'sensor' OR
      toLower(l.name) CONTAINS 'earth observation' OR toLower(l.name) CONTAINS 'spectral'
RETURN l.name as lab_name, p.name as program_name, p.type as program_type
ORDER BY l.name, p.name;

-- ============================================================================
-- 5. SUMMARY STATISTICS
-- ============================================================================

-- Query 5.1: Total Programs Associated with Technology Research Centers
MATCH (rc:ResearchCenter)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
      toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
      toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite'
RETURN count(DISTINCT p) as total_programs_with_tech_research_centers;

-- Query 5.2: Total Programs Associated with Technology Labs
MATCH (l:Lab)-[:ASSOCIATED_WITH]->(p:Program)
WHERE toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
      toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
      toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite'
RETURN count(DISTINCT p) as total_programs_with_tech_labs;

-- Query 5.3: Programs by Technology Focus Area (Research Centers)
MATCH (rc:ResearchCenter)-[:ASSOCIATED_WITH]->(p:Program)
WITH rc.name as center_name, p.name as program_name,
     CASE 
         WHEN toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
              toLower(rc.name) CONTAINS 'geographic' OR toLower(rc.name) CONTAINS 'spatial' THEN 'GIS'
         WHEN toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
              toLower(rc.name) CONTAINS 'machine learning' OR toLower(rc.name) CONTAINS 'ml' THEN 'AI'
         WHEN toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite' OR
              toLower(rc.name) CONTAINS 'aerial' OR toLower(rc.name) CONTAINS 'sensor' THEN 'Remote Sensing'
         ELSE 'Other'
     END as technology_focus
WHERE technology_focus IN ['GIS', 'AI', 'Remote Sensing']
RETURN technology_focus, count(DISTINCT program_name) as program_count
ORDER BY program_count DESC;

-- Query 5.4: Programs by Technology Focus Area (Labs)
MATCH (l:Lab)-[:ASSOCIATED_WITH]->(p:Program)
WITH l.name as lab_name, p.name as program_name,
     CASE 
         WHEN toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
              toLower(l.name) CONTAINS 'geographic' OR toLower(l.name) CONTAINS 'spatial' THEN 'GIS'
         WHEN toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
              toLower(l.name) CONTAINS 'machine learning' OR toLower(l.name) CONTAINS 'ml' THEN 'AI'
         WHEN toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite' OR
              toLower(l.name) CONTAINS 'aerial' OR toLower(l.name) CONTAINS 'sensor' THEN 'Remote Sensing'
         ELSE 'Other'
     END as technology_focus
WHERE technology_focus IN ['GIS', 'AI', 'Remote Sensing']
RETURN technology_focus, count(DISTINCT program_name) as program_count
ORDER BY program_count DESC;

-- ============================================================================
-- 6. UNIVERSITY-LEVEL ANALYSIS
-- ============================================================================

-- Query 6.1: Universities with Technology Research Centers
MATCH (u:University)-[:HAS]->(rc:ResearchCenter)
WHERE toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
      toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
      toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite'
RETURN u.name as university_name, count(rc) as technology_research_centers
ORDER BY technology_research_centers DESC;

-- Query 6.2: Universities with Technology Labs
MATCH (u:University)-[:HAS]->(l:Lab)
WHERE toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
      toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
      toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite'
RETURN u.name as university_name, count(l) as technology_labs
ORDER BY technology_labs DESC;

-- Query 6.3: Comprehensive University Technology Infrastructure
MATCH (u:University)
OPTIONAL MATCH (u)-[:HAS]->(rc:ResearchCenter)
WHERE toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
      toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
      toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite'
OPTIONAL MATCH (u)-[:HAS]->(l:Lab)
WHERE toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
      toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
      toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite'
WITH u.name as university_name, 
     count(DISTINCT rc) as tech_research_centers,
     count(DISTINCT l) as tech_labs
RETURN university_name, tech_research_centers, tech_labs, 
       (tech_research_centers + tech_labs) as total_tech_infrastructure
ORDER BY total_tech_infrastructure DESC;

-- ============================================================================
-- 7. DETAILED RESEARCH CENTER AND LAB ANALYSIS
-- ============================================================================

-- Query 7.1: All Technology Research Centers with Details
MATCH (rc:ResearchCenter)
WHERE toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' OR
      toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' OR
      toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite'
OPTIONAL MATCH (rc)-[:ASSOCIATED_WITH]->(p:Program)
OPTIONAL MATCH (u:University)-[:HAS]->(rc)
RETURN rc.name as research_center_name,
       u.name as university_name,
       count(p) as associated_programs,
       CASE 
           WHEN toLower(rc.name) CONTAINS 'gis' OR toLower(rc.name) CONTAINS 'geospatial' THEN 'GIS'
           WHEN toLower(rc.name) CONTAINS 'ai' OR toLower(rc.name) CONTAINS 'artificial intelligence' THEN 'AI'
           WHEN toLower(rc.name) CONTAINS 'remote sensing' OR toLower(rc.name) CONTAINS 'satellite' THEN 'Remote Sensing'
           ELSE 'Other'
       END as primary_focus
ORDER BY associated_programs DESC;

-- Query 7.2: All Technology Labs with Details
MATCH (l:Lab)
WHERE toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' OR
      toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' OR
      toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite'
OPTIONAL MATCH (l)-[:ASSOCIATED_WITH]->(p:Program)
OPTIONAL MATCH (u:University)-[:HAS]->(l)
RETURN l.name as lab_name,
       u.name as university_name,
       count(p) as associated_programs,
       CASE 
           WHEN toLower(l.name) CONTAINS 'gis' OR toLower(l.name) CONTAINS 'geospatial' THEN 'GIS'
           WHEN toLower(l.name) CONTAINS 'ai' OR toLower(l.name) CONTAINS 'artificial intelligence' THEN 'AI'
           WHEN toLower(l.name) CONTAINS 'remote sensing' OR toLower(l.name) CONTAINS 'satellite' THEN 'Remote Sensing'
           ELSE 'Other'
       END as primary_focus
ORDER BY associated_programs DESC;

