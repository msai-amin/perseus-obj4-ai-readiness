#!/usr/bin/env python3
"""
Synchronize Neo4j graph with university profiles (Markdown) with verification.
- Parses files in `university-profiles/`
- Generates Cypher MERGE statements to enforce exact structure
- Optional live verification against Neo4j (if DB available)
- Emits mismatch report and Cypher script
"""

import re
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from neo4j import GraphDatabase  # optional if verify mode
except Exception:
    GraphDatabase = None  # type: ignore

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = ROOT / 'university-profiles'
OUTPUT_DIR = ROOT / 'data' / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------- Helpers ---------

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def clean_name(name: str) -> str:
    return normalize_whitespace(name.replace('\u2013', '-').replace('–', '-'))

def infer_program_level(program_name: str) -> str:
    name = program_name.lower()
    if any(k in name for k in ['bachelor', 'b.s', 'bs', 'b.a', 'ba', 'undergraduate']):
        return 'Undergraduate'
    if any(k in name for k in ['master', 'm.s', 'ms', 'm.a', 'ma', 'mba', 'graduate']):
        return 'Graduate'
    if any(k in name for k in ['phd', 'ph.d', 'doctorate', 'doctoral']):
        return 'Graduate'
    return 'Unknown'

# -------- Parsing ---------

def extract_university_name_from_filename(path: Path) -> str:
    # Filename sans extension is the university name in repo convention
    return clean_name(path.stem)

SECTION_HEADER_RE = re.compile(r"^#{1,6}\s+(.*)", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)")


def parse_profile_markdown(md_path: Path) -> Dict[str, Any]:
    """Parse a university profile to extract departments and programs.
    Assumptions:
      - University name comes from filename
      - Sections may include 'Departments', 'Programs', 'Undergraduate Programs', 'Graduate Programs'
      - Bulleted lists under these sections contain department/program names
    Returns a dict structure with departments and programs grouped.
    """
    university = extract_university_name_from_filename(md_path)
    content = md_path.read_text(encoding='utf-8', errors='ignore').splitlines()

    current_section: Optional[str] = None
    sections: Dict[str, List[str]] = {}

    for line in content:
        header = SECTION_HEADER_RE.match(line)
        if header:
            current_section = header.group(1).strip().lower()
            sections.setdefault(current_section, [])
            continue
        bullet = BULLET_RE.match(line)
        if bullet and current_section:
            item = clean_name(bullet.group(1))
            if item:
                sections[current_section].append(item)

    # Heuristics to map sections
    departments: List[str] = []
    programs: List[Tuple[str, Optional[str]]] = []  # (program_name, department)

    for section, items in sections.items():
        if any(k in section for k in ['department', 'school', 'college', 'division']):
            for it in items:
                if len(it) > 1:
                    departments.append(it)
        if any(k in section for k in ['program', 'degree', 'certificate', 'minor', 'major']):
            for it in items:
                if len(it) > 1:
                    programs.append((it, None))

    # Fallback: attempt to infer programs from inline patterns if no explicit program section
    if not programs:
        for section, items in sections.items():
            for it in items:
                if re.search(r"(bachelor|master|phd|ms|ma|bs|ba|certificate|minor|major)", it, re.I):
                    programs.append((it, None))

    parsed = {
        'university': university,
        'departments': sorted(list(dict.fromkeys(departments))),
        'programs': [{'name': p[0], 'department': p[1], 'level': infer_program_level(p[0])} for p in programs]
    }
    return parsed

# -------- Cypher generation ---------

def generate_cypher_for_university(parsed: Dict[str, Any]) -> str:
    u = parsed['university']
    departments: List[str] = parsed.get('departments', [])
    programs: List[Dict[str, Any]] = parsed.get('programs', [])

    lines: List[str] = []
    lines.append(f"MERGE (u:University {{name: $u_name}});")

    for d in departments:
        lines.append(
            "MERGE (d:Department {name: $d_name, university: $u_name})\n"  # scoped by university
            "WITH u, d\n"
            "MERGE (u)-[:LOCATED_IN]->(d);"
            .replace('$d_name', json.dumps(d))
            .replace('$u_name', json.dumps(u))
        )

    # Programs: attach to nearest matching department if specified; else attach to University default department bucket
    for p in programs:
        p_name = p['name']
        p_level = p.get('level', 'Unknown')
        d_name = p.get('department')
        if d_name:
            lines.append(
                "MATCH (u:University {name: $u_name})\n"
                "MERGE (d:Department {name: $d_name, university: $u_name})\n"
                "MERGE (p:Program {name: $p_name, university: $u_name})\n"
                "SET p.level = $p_level\n"
                "MERGE (d)-[:OFFERS]->(p);"
                .replace('$u_name', json.dumps(u))
                .replace('$d_name', json.dumps(d_name))
                .replace('$p_name', json.dumps(p_name))
                .replace('$p_level', json.dumps(p_level))
            )
        else:
            lines.append(
                "MATCH (u:University {name: $u_name})\n"
                "MERGE (d:Department {name: 'General Academic Unit', university: $u_name})\n"
                "MERGE (u)-[:LOCATED_IN]->(d)\n"
                "MERGE (p:Program {name: $p_name, university: $u_name})\n"
                "SET p.level = $p_level\n"
                "MERGE (d)-[:OFFERS]->(p);"
                .replace('$u_name', json.dumps(u))
                .replace('$p_name', json.dumps(p_name))
                .replace('$p_level', json.dumps(p_level))
            )

    return "\n".join(lines) + "\n"

# -------- Verification (live DB optional) ---------

def verify_against_db(uri: str, user: str, password: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    if GraphDatabase is None:
        return {'status': 'skipped', 'reason': 'neo4j driver not installed'}
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
    except Exception as e:
        return {'status': 'skipped', 'reason': f'connection_failed: {e}'}

    def run(q: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with driver.session() as s:
            return s.run(q, params or {}).data()

    u = expected['university']
    report = {'university': u, 'mismatches': []}

    # Verify University exists
    rows = run("MATCH (u:University {name:$u}) RETURN count(u) as c", {'u': u})
    if not rows or rows[0]['c'] == 0:
        report['mismatches'].append({'type': 'missing_university', 'name': u})

    # Verify Departments
    for d in expected.get('departments', []):
        rows = run("""
            MATCH (u:University {name:$u})-[:LOCATED_IN]->(d:Department {name:$d, university:$u})
            RETURN count(d) as c
        """, {'u': u, 'd': d})
        if not rows or rows[0]['c'] == 0:
            report['mismatches'].append({'type': 'missing_department', 'department': d})

    # Verify Programs
    for p in expected.get('programs', []):
        p_name = p['name']
        rows = run("""
            MATCH (u:University {name:$u})<-[:OFFERS]-(d:Department)-[:OFFERS]->(p:Program {name:$p, university:$u})
            RETURN count(p) as c
        """, {'u': u, 'p': p_name})
        if not rows or rows[0]['c'] == 0:
            report['mismatches'].append({'type': 'missing_program', 'program': p_name})

    driver.close()
    report['status'] = 'ok' if not report['mismatches'] else 'mismatch'
    return report

# -------- Main workflow ---------

def main():
    parser = argparse.ArgumentParser(description='Synchronize graph with university profiles and verify.')
    parser.add_argument('--profiles-dir', default=str(PROFILES_DIR), help='Directory with university profiles (.md)')
    parser.add_argument('--output-cypher', default=str(OUTPUT_DIR / 'profile_graph_sync.cypher'), help='Path to write Cypher upserts')
    parser.add_argument('--verify', action='store_true', help='Verify against live Neo4j')
    parser.add_argument('--uri', default='bolt://localhost:7689')
    parser.add_argument('--user', default='neo4j')
    parser.add_argument('--password', default='perseus2025')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of profiles processed (0 = all)')

    args = parser.parse_args()

    profiles_dir = Path(args.profiles_dir)
    if not profiles_dir.exists():
        logger.error(f"Profiles directory not found: {profiles_dir}")
        print("HINT: Ensure `university-profiles/` exists at project root with .md files.")
        return 1

    profile_files = sorted([p for p in profiles_dir.glob('*.md')])
    if args.limit > 0:
        profile_files = profile_files[: args.limit]

    if not profile_files:
        logger.error("No profile .md files found.")
        return 1

    all_cypher: List[str] = []
    verification_reports: List[Dict[str, Any]] = []

    for i, md_path in enumerate(profile_files, 1):
        logger.info(f"Processing [{i}/{len(profile_files)}]: {md_path.name}")
        parsed = parse_profile_markdown(md_path)
        cypher = generate_cypher_for_university(parsed)
        all_cypher.append(f"// === {parsed['university']} ===\n" + cypher)

        if args.verify:
            report = verify_against_db(args.uri, args.user, args.password, parsed)
            verification_reports.append(report)

    # Write outputs
    cypher_path = Path(args.output_cypher)
    cypher_path.write_text("\n".join(all_cypher), encoding='utf-8')
    logger.info(f"Cypher upsert written: {cypher_path}")

    if verification_reports:
        report_path = OUTPUT_DIR / 'profile_graph_verification_report.json'
        report_path.write_text(json.dumps(verification_reports, indent=2), encoding='utf-8')
        logger.info(f"Verification report written: {report_path}")

    # Also write a concise markdown summary
    md_lines = [
        "# Profile → Graph Synchronization Summary",
        "",
        f"Profiles processed: {len(profile_files)}",
        f"Cypher file: `{cypher_path.relative_to(ROOT)}`",
        "",
    ]
    if verification_reports:
        mismatches = sum(1 for r in verification_reports if r.get('status') == 'mismatch')
        md_lines += [
            f"Verification: {len(verification_reports)} universities checked",
            f"Mismatches found: {mismatches}",
        ]
    (OUTPUT_DIR / 'profile_graph_sync_summary.md').write_text("\n".join(md_lines), encoding='utf-8')

    logger.info("Done.")
    return 0

if __name__ == '__main__':
    sys.exit(main())



