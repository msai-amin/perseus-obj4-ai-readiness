import os
import re
import pandas as pd
from collections import defaultdict, Counter

# Directory containing university markdown profiles
PROFILE_DIR = 'university-profiles'

# Technology keywords for classification
TECH_KEYWORDS = {
    'AI/ML': [
        r'\bAI\b', r'\bArtificial Intelligence\b', r'\bMachine Learning\b', r'\bML\b',
        r'Deep Learning', r'Neural Network', r'Pattern Recognition', r'Computer Vision',
        r'Supervised Learning', r'Unsupervised Learning', r'Reinforcement Learning'
    ],
    'Data Science': [
        r'\bData Science\b', r'\bAnalytics\b', r'\bBig Data\b', r'\bData Analysis\b', r'\bAdvanced Data Science\b',
        r'Data Mining', r'Knowledge Discovery', r'Data Structures', r'Data Wrangling', r'Data Visualization'
    ],
    'GIS': [r'\bGIS\b', r'Geographic Information', r'Geospatial', r'Spatial Analysis'],
    'Remote Sensing': [r'Remote Sensing', r'Satellite', r'Photogrammetry'],
    'Drone/UAV': [r'\bDrone\b', r'\bUAV\b', r'Unmanned Aerial', r'Aerial Systems'],
    'Statistics': [
        r'\bStatistics\b', r'\bStatistical\b', r'\bRegression\b', r'\bModeling\b',
        r'Stats', r'Probability', r'Time Series', r'Multivariate', r'Biometry', r'Statistical Methods',
        r'Applied Statistics', r'Sampling', r'ANOVA', r'Inference', r'Quantitative Methods'
    ],
    'Programming': [
        r'\bPython\b', r'\bR\b', r'\bProgramming\b', r'\bComputational\b',
        r'Algorithms', r'Operating Systems', r'Software Design', r'Software Engineering',
        r'Object Oriented', r'OOP', r'Web Services'
    ],
    'Ethics': [
        r'Computer Ethics', r'Ethics in Computing', r'Responsible Conduct'
    ]
}

# Helper to classify a course by technology area
def classify_course(course_name):
    for tech, patterns in TECH_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, course_name, re.IGNORECASE):
                return tech
    return 'Other'

# Multiple patterns to match course lines
COURSE_PATTERNS = [
    # Pattern 1: Course code followed by colon and title (e.g., "ENV 755: Modeling Geographic Space")
    r'([A-Z]{2,4}\s+\d{3,4}[A-Z]?)\s*[:\-]\s*([^\.]+?)(?=\s*\(|\s*$|\s*\.)',
    # Pattern 2: Course code in parentheses or brackets - FIXED to properly capture content in parentheses
    r'([A-Z]{2,4}\s+\d{3,4}[A-Z]?)\s*\(([^\)]+)\)',
    # Pattern 3: Course title followed by course code
    r'([^\.]+?)\s*\(([A-Z]{2,4}\s+\d{3,4}[A-Z]?)\)',
    # Pattern 4: Course code with dash
    r'([A-Z]{2,4}\s+\d{3,4}[A-Z]?)\s*-\s*([^\.]+?)(?=\s*\(|\s*$|\s*\.)',
    # Pattern 5: Course code with slash
    r'([A-Z]{2,4}\s+\d{3,4}[A-Z]?)\s*/\s*([^\.]+?)(?=\s*\(|\s*$|\s*\.)',
]

def extract_courses_from_text(text, university_name):
    courses = []
    
    # Split text into lines and look for course patterns
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 10:  # Skip very short lines
            continue
            
        # Try each pattern
        for pattern in COURSE_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    course_code = match.group(1).strip()
                    course_name = match.group(2).strip()
                    
                    # Clean up course name
                    course_name = re.sub(r'^\s*[:\-]\s*', '', course_name)  # Remove leading colons/dashes
                    course_name = re.sub(r'\s+', ' ', course_name)  # Normalize whitespace
                    
                    # Skip if course name is too short or looks like a section header
                    if len(course_name) < 3 or course_name.upper() == course_name:
                        continue
                        
                    # Skip if it's clearly not a course (e.g., page numbers, references)
                    if re.search(r'^\d+$|^[A-Z\s]+$|^Chapter|^Section|^Table|^Figure', course_name):
                        continue
                    
                    tech_area = classify_course(course_name)
                    
                    courses.append({
                        'university': university_name,
                        'course_code': course_code,
                        'course_name': course_name,
                        'technology_area': tech_area,
                        'source_line': line[:100] + '...' if len(line) > 100 else line
                    })
    
    return courses

results = []
all_courses = []

print("Processing university markdown files...")
print("=" * 60)

for filename in os.listdir(PROFILE_DIR):
    if not filename.endswith('.md'):
        continue
        
    university = filename.replace('.md', '').replace('_', ' ').replace('-', ' ').strip()
    path = os.path.join(PROFILE_DIR, filename)
    
    print(f"Processing: {university}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract courses from this file
        courses = extract_courses_from_text(text, university)
        
        if courses:
            print(f"  Found {len(courses)} courses")
            all_courses.extend(courses)
        else:
            print(f"  No courses found")
            
    except Exception as e:
        print(f"  Error processing {filename}: {e}")

# Create DataFrame
df = pd.DataFrame(all_courses)

if len(df) > 0:
    # Save to CSV
    df.to_csv('all_courses_by_university_and_tech.csv', index=False)
    
    # Print summary statistics
    print(f"\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print(f"Total universities processed: {len(set(df['university']))}")
    print(f"Total courses found: {len(df)}")
    
    print(f"\nTop 10 universities by course count:")
    univ_counts = df['university'].value_counts().head(10)
    for univ, count in univ_counts.items():
        print(f"  {univ}: {count} courses")
    
    print(f"\nCourse count by technology area:")
    tech_counts = df['technology_area'].value_counts()
    for tech, count in tech_counts.items():
        print(f"  {tech}: {count} courses")
    
    print(f"\nSample extracted courses (first 20):")
    print("-" * 80)
    for i, row in df.head(20).iterrows():
        print(f"{i+1:2d}. {row['course_code']}: {row['course_name']} ({row['technology_area']})")
    
    if len(df) > 20:
        print(f"... and {len(df) - 20} more courses")
    
    print(f"\nResults saved to all_courses_by_university_and_tech.csv")
    
    # Show some examples of each technology area
    print(f"\nExamples by technology area:")
    for tech in tech_counts.index:
        if tech != 'Other':
            examples = df[df['technology_area'] == tech].head(3)
            print(f"\n{tech}:")
            for _, row in examples.iterrows():
                print(f"  {row['course_code']}: {row['course_name']}")
    
else:
    print("No courses found in any files. Check the extraction patterns.")

print(f"\nProcessing complete!") 