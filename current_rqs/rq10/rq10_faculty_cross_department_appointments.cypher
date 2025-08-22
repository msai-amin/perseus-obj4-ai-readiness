// RQ10: Faculty Cross-Department Appointments Analysis
// How many faculty members have appointments (joint or otherwise) with computer science, engineering, or data science departments?

// 1. Database Verification
MATCH (n) RETURN labels(n) as node_types, count(n) as count ORDER BY count DESC;

// 2. Faculty Count and Basic Information
MATCH (f:Faculty) 
RETURN count(f) as total_faculty;

// 3. Faculty with Department Appointments
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
RETURN f.name as faculty_name, d.name as department_name, d.category as department_category
ORDER BY faculty_name;

// 4. Computer Science Department Appointments
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
WHERE toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
      toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics'
RETURN f.name as faculty_name, d.name as department_name, d.category as department_category
ORDER BY faculty_name;

// 5. Engineering Department Appointments
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
WHERE toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
      toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
      toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
      toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental'
RETURN f.name as faculty_name, d.name as department_name, d.category as department_category
ORDER BY faculty_name;

// 6. Data Science Department Appointments
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
WHERE toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
      toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
      toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative'
RETURN f.name as faculty_name, d.name as department_name, d.category as department_category
ORDER BY faculty_name;

// 7. Cross-Department Appointments Summary
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
WITH f.name as faculty_name, 
     CASE 
         WHEN toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
              toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics' THEN 'Computer Science'
         WHEN toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
              toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
              toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
              toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental' THEN 'Engineering'
         WHEN toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
              toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
              toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative' THEN 'Data Science'
         ELSE 'Other'
     END as department_category
RETURN department_category, count(DISTINCT faculty_name) as faculty_count
ORDER BY faculty_count DESC;

// 8. Faculty with Multiple Department Appointments
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
WITH f.name as faculty_name, collect(d.name) as departments
WHERE size(departments) > 1
RETURN faculty_name, departments, size(departments) as appointment_count
ORDER BY appointment_count DESC, faculty_name;

// 9. University-Level Cross-Department Faculty Distribution
MATCH (u:University)-[:HAS]->(d:Department)<-[:APPOINTED_TO]-(f:Faculty)
WITH u.name as university_name, d.name as department_name, f.name as faculty_name,
     CASE 
         WHEN toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
              toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics' THEN 'Computer Science'
         WHEN toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
              toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
              toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
              toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental' THEN 'Engineering'
         WHEN toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
              toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
              toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative' THEN 'Data Science'
         ELSE 'Other'
     END as department_category
WHERE department_category IN ['Computer Science', 'Engineering', 'Data Science']
RETURN university_name, department_category, count(DISTINCT faculty_name) as faculty_count
ORDER BY university_name, department_category;

// 10. Faculty Technology Integration with Cross-Department Appointments
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'engineering' OR 
      toLower(d.name) CONTAINS 'data science'
RETURN f.name as faculty_name, d.name as department_name, t.name as technology_name, t.category as technology_category
ORDER BY faculty_name, technology_name;

// 11. Cross-Department Faculty by Research Area
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)-[:HAS_RESEARCH_AREA]->(ra:ResearchArea)
WHERE toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'engineering' OR 
      toLower(d.name) CONTAINS 'data science'
RETURN f.name as faculty_name, d.name as department_name, ra.name as research_area
ORDER BY faculty_name, research_area;

// 12. Summary Statistics for Cross-Department Faculty
MATCH (f:Faculty)-[:APPOINTED_TO]->(d:Department)
WITH f.name as faculty_name, 
     CASE 
         WHEN toLower(d.name) CONTAINS 'computer science' OR toLower(d.name) CONTAINS 'cs' OR 
              toLower(d.name) CONTAINS 'computing' OR toLower(d.name) CONTAINS 'informatics' THEN 'Computer Science'
         WHEN toLower(d.name) CONTAINS 'engineering' OR toLower(d.name) CONTAINS 'eng' OR
              toLower(d.name) CONTAINS 'mechanical' OR toLower(d.name) CONTAINS 'electrical' OR
              toLower(d.name) CONTAINS 'civil' OR toLower(d.name) CONTAINS 'chemical' OR
              toLower(d.name) CONTAINS 'biomedical' OR toLower(d.name) CONTAINS 'environmental' THEN 'Engineering'
         WHEN toLower(d.name) CONTAINS 'data science' OR toLower(d.name) CONTAINS 'data' OR
              toLower(d.name) CONTAINS 'analytics' OR toLower(d.name) CONTAINS 'statistics' OR
              toLower(d.name) CONTAINS 'biostatistics' OR toLower(d.name) CONTAINS 'quantitative' THEN 'Data Science'
         ELSE 'Other'
     END as department_category
WHERE department_category IN ['Computer Science', 'Engineering', 'Data Science']
RETURN department_category, 
       count(DISTINCT faculty_name) as faculty_count,
       round(count(DISTINCT faculty_name) * 100.0 / (MATCH (f2:Faculty) RETURN count(f2))[0], 2) as percentage_of_total_faculty
ORDER BY faculty_count DESC;
