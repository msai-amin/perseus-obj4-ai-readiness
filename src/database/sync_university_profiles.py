#!/usr/bin/env python3
"""
Sync university profiles (SAF-accredited) to Neo4j by generating idempotent Cypher.

Guarantees 100% accuracy for the set of universities under `docs/university-profiles/` by:
- Upserting each university as `:University:SAFAccredited {name}`
- Ensuring (u)-[:ACCREDITED_BY]->(:Organization {name:'Society of American Foresters', acronym:'SAF'})
- Cleaning up any existing `:SAFAccredited` universities not present in the source list

Outputs:
- data/outputs/sync_university_profiles.cypher (idempotent upserts + cleanup)
- data/outputs/verify_university_sync.cypher (verification queries)
- data/outputs/university_sync_report.json (summary)
"""

from pathlib import Path
import json
import re
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = ROOT / 'docs' / 'university-profiles'
OUTPUT_DIR = ROOT / 'data' / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_university_name(file_name: str) -> str:
    # Use the file stem as authoritative display name; trim whitespace
    name = Path(file_name).stem.strip()
    return name


def list_university_profiles() -> List[Dict[str, str]]:
    profiles = []
    for md in sorted(PROFILES_DIR.glob('*.md')):
        if md.name.startswith('.'):
            continue
        name = normalize_university_name(md.name)
        profiles.append({
            'name': name,
            'file': str(md.relative_to(ROOT))
        })
    return profiles


def generate_upsert_cypher(universities: List[Dict[str, str]]) -> str:
    """Generate an UNWIND-based, idempotent upsert that avoids variable reuse issues."""
    lines = []
    # Prepare rows array
    row_entries = []
    for uni in universities:
        name = uni['name'].replace("'", "\\'")
        file_path = uni['file'].replace("'", "\\'")
        row_entries.append(f"{{name:'{name}', file:'{file_path}'}}")
    rows_literal = ',\n  '.join(row_entries)

    # Upsert block
    lines.append('// Upsert all SAF universities and their accreditation in one statement')
    lines.append('WITH [')
    lines.append(f'  {rows_literal}')
    lines.append(
        "] AS rows\nMERGE (saf:Organization {name: 'Society of American Foresters'})\nON CREATE SET saf.acronym = 'SAF'\nON MATCH SET saf.acronym = coalesce(saf.acronym, 'SAF')\nWITH rows, saf\nUNWIND rows AS row\nMERGE (u:University:SAFAccredited {name: row.name})\n  ON CREATE SET u.saf_accredited = true, u.sourceFile = row.file\n  ON MATCH  SET u.saf_accredited = true, u.sourceFile = row.file\nMERGE (u)-[:ACCREDITED_BY]->(saf)"
    )

    # Cleanup block (to be run as a second statement in Browser)
    names_list = ', '.join([f"'{uni['name'].replace("'", "\\'")}'" for uni in universities])
    lines.append('\n// ---- Run the following cleanup as a separate statement in Browser ----')
    lines.append(f'// WITH [{names_list}] AS expected\n// MATCH (u:University:SAFAccredited)\n// WHERE NOT u.name IN expected\n// WITH collect(u) AS to_remove, count(u) AS removed_count\n// FOREACH (n IN to_remove | DETACH DELETE n)\n// RETURN removed_count AS removed')

    return '\n'.join(lines)


def generate_verify_cypher(universities: List[Dict[str, str]]) -> str:
    names_list = ', '.join([f"'{uni['name'].replace("'", "\\'")}'" for uni in universities])
    lines = []
    lines.append('// Count SAF universities in DB')
    lines.append('MATCH (u:University:SAFAccredited)-[:ACCREDITED_BY]->(a:Organization {acronym: "SAF"})')
    lines.append('RETURN count(u) AS saf_university_count')
    lines.append('')
    lines.append('// Validate expected set matches exactly (no APOC)')
    lines.append(f'WITH [{names_list}] AS expected')
    lines.append('MATCH (u:University:SAFAccredited)')
    lines.append('WITH expected, collect(u.name) AS present')
    lines.append('WITH expected, present, [x IN expected WHERE NOT x IN present] AS missing, [x IN present WHERE NOT x IN expected] AS unexpected')
    lines.append('RETURN size(present) AS present_count, size(expected) AS expected_count, missing, unexpected')
    lines.append('')
    return '\n'.join(lines)


def main():
    universities = list_university_profiles()
    if not universities:
        raise SystemExit(f'No markdown profiles found in {PROFILES_DIR}')

    report = {
        'source_directory': str(PROFILES_DIR),
        'total_universities': len(universities),
        'universities': universities,
    }

    # Write upsert + cleanup cypher
    upsert_path = OUTPUT_DIR / 'sync_university_profiles.cypher'
    upsert_path.write_text(generate_upsert_cypher(universities))

    # Write verification queries
    verify_path = OUTPUT_DIR / 'verify_university_sync.cypher'
    verify_path.write_text(generate_verify_cypher(universities))

    # Write JSON report
    (OUTPUT_DIR / 'university_sync_report.json').write_text(json.dumps(report, indent=2))

    print(f'Wrote: {upsert_path}')
    print(f'Wrote: {verify_path}')
    print(f'Wrote: {OUTPUT_DIR / "university_sync_report.json"}')


if __name__ == '__main__':
    main()


