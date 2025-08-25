#!/usr/bin/env python3
"""
Extract References from University Profile Markdown Files
Creates a comprehensive LaTeX document with all references from university profiles
"""

import os
import re
import glob
from pathlib import Path

def extract_references_from_file(file_path):
    """Extract references section from a single markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for references section - different patterns used in different files
    references_patterns = [
        r'#### \*\*Works cited\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
        r'#### \*\*References\*\*\s*\n(.*?)(?=\n##|\n#|\Z)',
        r'^References\s*\n(.*?)(?=\n##|\n#|\Z)',
        r'^Works cited\s*\n(.*?)(?=\n##|\n#|\Z)',
        r'#### References\s*\n(.*?)(?=\n##|\n#|\Z)',
        r'#### Works cited\s*\n(.*?)(?=\n##|\n#|\Z)',
    ]
    
    references = ""
    for pattern in references_patterns:
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            references = match.group(1).strip()
            break
    
    return references

def clean_references(references_text):
    """Clean and format references text for LaTeX"""
    if not references_text:
        return ""
    
    # Remove markdown formatting
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', references_text)
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)
    
    # Convert markdown links to LaTeX format
    cleaned = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 \\url{\2}', cleaned)
    
    # Clean up numbered lists
    cleaned = re.sub(r'^(\d+)\.\s*', r'\\item ', cleaned, flags=re.MULTILINE)
    
    # Handle special characters for LaTeX
    cleaned = cleaned.replace('&', '\\&')
    cleaned = cleaned.replace('%', '\\%')
    cleaned = cleaned.replace('$', '\\$')
    cleaned = cleaned.replace('_', '\\_')
    cleaned = cleaned.replace('{', '\\{')
    cleaned = cleaned.replace('}', '\\}')
    
    return cleaned

def create_latex_document(university_references):
    """Create the complete LaTeX document"""
    latex_content = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{url}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{titlesec}

% Page setup
\geometry{margin=1in}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}

% Header and footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{University Profiles References}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Title formatting
\titleformat{\section}{\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}

% URL formatting
\urlstyle{same}

\begin{document}

\title{\Huge\textbf{Comprehensive References from University Profiles}\\
\large Knowledge Graph Perseus Project\\
\large AI Readiness Analysis}
\author{Generated from University Profile Analysis}
\date{\today}

\maketitle

\tableofcontents
\newpage

"""

    # Add each university's references
    for university_name, references in university_references.items():
        if references.strip():
            latex_content += f"\\section{{{university_name}}}\n\n"
            latex_content += "\\begin{enumerate}\n"
            latex_content += references
            latex_content += "\n\\end{enumerate}\n\n"
            latex_content += "\\newpage\n\n"
    
    latex_content += r"""
\end{document}
"""
    
    return latex_content

def main():
    """Main function to extract references and create LaTeX document"""
    # Get all university profile markdown files
    profiles_dir = Path("docs/university-profiles")
    markdown_files = glob.glob(str(profiles_dir / "*.md"))
    
    university_references = {}
    
    print(f"Processing {len(markdown_files)} university profile files...")
    
    for file_path in sorted(markdown_files):
        university_name = Path(file_path).stem.replace('_', ' ').title()
        print(f"Processing: {university_name}")
        
        # Extract references
        references = extract_references_from_file(file_path)
        
        if references:
            # Clean and format references
            cleaned_references = clean_references(references)
            university_references[university_name] = cleaned_references
            print(f"  ✓ Found {len(references.split('.'))} references")
        else:
            print(f"  ✗ No references found")
    
    # Create LaTeX document
    print("\nCreating LaTeX document...")
    latex_content = create_latex_document(university_references)
    
    # Save LaTeX file
    output_file = "university_profiles_references.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"\n✓ LaTeX document created: {output_file}")
    print(f"✓ Total universities with references: {len([r for r in university_references.values() if r.strip()])}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for university, refs in university_references.items():
        if refs.strip():
            ref_count = len([line for line in refs.split('\n') if line.strip() and line.startswith('\\item')])
            print(f"{university}: {ref_count} references")
    
    print("\n" + "="*60)
    print("LaTeX document is ready for compilation!")
    print("="*60)

if __name__ == "__main__":
    main()
