-- RQ8 Cypher Queries for Program Level and Type Technology Correlation Analysis
-- Neo4j Graph Database Queries for Research Question 8
-- To what extent are drone/GIS/AI topics correlated with the level (undergraduate, master's, or doctoral) 
-- and type of academic programs?

-- ============================================================================
-- 1. DATABASE STRUCTURE VERIFICATION
-- ============================================================================

-- Query 1.1: Count Total Programs
MATCH (p:Program) 
RETURN count(p) as total_programs;

-- Query 1.2: Count Technology Relationships
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology) 
RETURN count(*) as total_technology_relationships;

-- Query 1.3: Count Program-University Relationships
MATCH (u:University)-[:OFFERS]->(p:Program) 
RETURN count(*) as total_program_university_relationships;

-- ============================================================================
-- 2. PROGRAM LEVEL CLASSIFICATION
-- ============================================================================

-- Query 2.1: Programs by Level (Undergraduate, Master's, Doctoral)
MATCH (p:Program)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level
RETURN program_level, count(program_name) as program_count
ORDER BY program_level;

-- Query 2.2: Programs by Type (Forestry, Natural Resources, etc.)
MATCH (p:Program)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type
RETURN program_type, count(program_name) as program_count
ORDER BY program_count DESC;

-- ============================================================================
-- 3. TECHNOLOGY INTEGRATION BY PROGRAM LEVEL
-- ============================================================================

-- Query 3.1: Technology Integration by Program Level
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     t.category as technology_category
RETURN program_level, technology_category, count(*) as technology_count
ORDER BY program_level, technology_count DESC;

-- Query 3.2: Specific Technology Areas by Program Level
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE t.category IN ['AI/ML', 'GIS', 'Drones/UAV', 'Remote Sensing', 'Data Analytics']
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     t.category as technology_category
RETURN program_level, technology_category, count(*) as technology_count
ORDER BY program_level, technology_count DESC;

-- Query 3.3: Programs with Any Technology by Level
MATCH (p:Program)
OPTIONAL MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     CASE WHEN t IS NOT NULL THEN 'Has Technology' ELSE 'No Technology' END as technology_status
RETURN program_level, technology_status, count(*) as program_count
ORDER BY program_level, technology_status;

-- ============================================================================
-- 4. TECHNOLOGY INTEGRATION BY PROGRAM TYPE
-- ============================================================================

-- Query 4.1: Technology Integration by Program Type
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type,
     t.category as technology_category
RETURN program_type, technology_category, count(*) as technology_count
ORDER BY program_type, technology_count DESC;

-- Query 4.2: Programs with Any Technology by Type
MATCH (p:Program)
OPTIONAL MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type,
     CASE WHEN t IS NOT NULL THEN 'Has Technology' ELSE 'No Technology' END as technology_status
RETURN program_type, technology_status, count(*) as program_count
ORDER BY program_type, technology_status;

-- ============================================================================
-- 5. CROSS-ANALYSIS: PROGRAM LEVEL AND TYPE COMBINED
-- ============================================================================

-- Query 5.1: Technology Integration by Program Level AND Type
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type,
     t.category as technology_category
RETURN program_level, program_type, technology_category, count(*) as technology_count
ORDER BY program_level, program_type, technology_count DESC;

-- Query 5.2: Summary Statistics by Level and Type
MATCH (p:Program)
OPTIONAL MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type,
     CASE WHEN t IS NOT NULL THEN 'Has Technology' ELSE 'No Technology' END as technology_status
RETURN program_level, program_type, technology_status, count(*) as program_count
ORDER BY program_level, program_type, technology_status;

-- ============================================================================
-- 6. DETAILED TECHNOLOGY ANALYSIS
-- ============================================================================

-- Query 6.1: AI/ML Technology by Program Level and Type
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE t.category = 'AI/ML'
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type
RETURN program_level, program_type, count(*) as ai_ml_count
ORDER BY program_level, program_type;

-- Query 6.2: GIS Technology by Program Level and Type
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE t.category = 'GIS'
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type
RETURN program_level, program_type, count(*) as gis_count
ORDER BY program_level, program_type;

-- Query 6.3: Drone/UAV Technology by Program Level and Type
MATCH (p:Program)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE t.category = 'Drones/UAV'
WITH p.name as program_name,
     CASE 
         WHEN toLower(p.name) CONTAINS 'bachelor' OR toLower(p.name) CONTAINS 'bs' OR 
              toLower(p.name) CONTAINS 'ba' OR toLower(p.name) CONTAINS 'undergraduate' OR
              toLower(p.name) CONTAINS 'associate' OR toLower(p.name) CONTAINS 'a.s.' OR
              toLower(p.name) CONTAINS 'a.a.' THEN 'Undergraduate'
         WHEN toLower(p.name) CONTAINS 'master' OR toLower(p.name) CONTAINS 'ms' OR 
              toLower(p.name) CONTAINS 'ma' OR toLower(p.name) CONTAINS 'mba' OR
              toLower(p.name) CONTAINS 'graduate' OR toLower(p.name) CONTAINS 'post-baccalaureate' THEN 'Master'
         WHEN toLower(p.name) CONTAINS 'phd' OR toLower(p.name) CONTAINS 'ph.d.' OR 
              toLower(p.name) CONTAINS 'doctorate' OR toLower(p.name) CONTAINS 'doctoral' OR
              toLower(p.name) CONTAINS 'd.phil' THEN 'Doctoral'
         ELSE 'Unknown'
     END as program_level,
     CASE 
         WHEN toLower(p.name) CONTAINS 'forestry' OR toLower(p.name) CONTAINS 'forest' OR
              toLower(p.name) CONTAINS 'silviculture' THEN 'Forestry'
         WHEN toLower(p.name) CONTAINS 'natural resource' OR toLower(p.name) CONTAINS 'environmental' OR
              toLower(p.name) CONTAINS 'ecology' OR toLower(p.name) CONTAINS 'conservation' THEN 'Natural Resources'
         WHEN toLower(p.name) CONTAINS 'gis' OR toLower(p.name) CONTAINS 'geospatial' OR
              toLower(p.name) CONTAINS 'geographic' OR toLower(p.name) CONTAINS 'spatial' THEN 'Geospatial'
         WHEN toLower(p.name) CONTAINS 'data science' OR toLower(p.name) CONTAINS 'analytics' OR
              toLower(p.name) CONTAINS 'informatics' OR toLower(p.name) CONTAINS 'computational' THEN 'Data Science'
         WHEN toLower(p.name) CONTAINS 'engineering' OR toLower(p.name) CONTAINS 'technology' OR
              toLower(p.name) CONTAINS 'technical' THEN 'Engineering'
         WHEN toLower(p.name) CONTAINS 'business' OR toLower(p.name) CONTAINS 'management' OR
              toLower(p.name) CONTAINS 'administration' OR toLower(p.name) CONTAINS 'policy' THEN 'Business/Management'
         WHEN toLower(p.name) CONTAINS 'science' OR toLower(p.name) CONTAINS 'scientific' OR
              toLower(p.name) CONTAINS 'research' THEN 'Science'
         WHEN toLower(p.name) CONTAINS 'computer science' OR toLower(p.name) CONTAINS 'computing' OR
              toLower(p.name) CONTAINS 'software' OR toLower(p.name) CONTAINS 'programming' THEN 'Computer Science'
         ELSE 'Other'
     END as program_type
RETURN program_level, program_type, count(*) as drone_count
ORDER BY program_level, program_type;
