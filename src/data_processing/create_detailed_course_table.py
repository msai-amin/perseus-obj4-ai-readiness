#!/usr/bin/env python3
"""
Create detailed APA table showing specific AI course examples
"""

import pandas as pd
import numpy as np

def create_detailed_course_table():
    """Create a detailed table showing specific AI course examples"""
    
    # Load the AI course data
    ai_courses = pd.read_csv('ai_course_analysis.csv')
    
    # Get unique courses by name and core/elective status
    unique_courses = ai_courses.groupby(['Course_Name', 'Core_Required', 'Matched_Keywords']).first().reset_index()
    
    # Categorize courses by technology area
    def categorize_course(row):
        keywords = str(row['Matched_Keywords']).lower()
        course_name = str(row['Course_Name']).lower()
        
        if 'artificial intelligence' in keywords or 'ai' in keywords or 'artificial intelligence' in course_name:
            return 'AI/ML'
        elif 'machine learning' in keywords or 'ml' in keywords or 'machine learning' in course_name:
            return 'AI/ML'
        elif 'data science' in keywords or 'data science' in course_name:
            return 'Data Science'
        elif 'gis' in keywords or 'geographic' in keywords or 'gis' in course_name:
            return 'GIS'
        elif 'remote sensing' in keywords or 'remote sensing' in course_name:
            return 'Remote Sensing'
        elif 'drone' in keywords or 'uav' in keywords or 'drone' in course_name:
            return 'Drone/UAV'
        elif 'programming' in keywords or 'coding' in keywords or 'programming' in course_name:
            return 'Programming'
        elif 'statistics' in keywords or 'statistical' in keywords or 'statistics' in course_name:
            return 'Statistics'
        else:
            return 'Other'
    
    unique_courses['Technology_Area'] = unique_courses.apply(categorize_course, axis=1)
    
    # Filter to only include relevant technology areas
    relevant_courses = unique_courses[unique_courses['Technology_Area'].isin(['AI/ML', 'Data Science', 'GIS', 'Remote Sensing', 'Programming', 'Statistics'])]
    
    # Create the detailed table
    table_data = []
    
    for tech_area in ['AI/ML', 'Data Science', 'GIS', 'Remote Sensing', 'Programming', 'Statistics']:
        tech_courses = relevant_courses[relevant_courses['Technology_Area'] == tech_area]
        
        # Get core courses
        core_courses = tech_courses[tech_courses['Core_Required'] == 'Core']
        elective_courses = tech_courses[tech_courses['Core_Required'] == 'Elective']
        
        # Add core course examples
        for _, course in core_courses.head(3).iterrows():
            table_data.append({
                'Technology Area': tech_area,
                'Course Type': 'Core/Required',
                'Course Name': course['Course_Name'],
                'Keywords': course['Matched_Keywords']
            })
        
        # Add elective course examples
        for _, course in elective_courses.head(3).iterrows():
            table_data.append({
                'Technology Area': tech_area,
                'Course Type': 'Elective',
                'Course Name': course['Course_Name'],
                'Keywords': course['Matched_Keywords']
            })
    
    # Create DataFrame and save
    detailed_table = pd.DataFrame(table_data)
    detailed_table.to_csv('ai_course_detailed_examples.csv', index=False)
    
    # Create APA formatted table
    apa_table = """
## Table 6
*Examples of AI-Related Courses by Technology Area and Course Type*

| Technology Area | Course Type | Course Name | Keywords |
|-----------------|-------------|-------------|----------|
"""
    
    for _, row in detailed_table.iterrows():
        apa_table += f"| {row['Technology Area']} | {row['Course Type']} | {row['Course Name']} | {row['Keywords']} |\n"
    
    apa_table += """
*Note.* This table shows representative examples of AI-related courses found in the analysis. Course names and keywords are as extracted from the database.
"""
    
    # Save APA table
    with open('ai_course_detailed_apa_table.md', 'w') as f:
        f.write(apa_table)
    
    print("Detailed course examples table created:")
    print("- ai_course_detailed_examples.csv")
    print("- ai_course_detailed_apa_table.md")
    
    return detailed_table

if __name__ == "__main__":
    create_detailed_course_table() 