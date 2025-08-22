#!/usr/bin/env python3
"""
SAF-Accredited Forestry Programs: Proportion offering AI/GIS/Remote Sensing/Drone courses
and how many of those courses are core/required.

This script:
- Builds robust Cypher queries that work across plausible schema variations
- Executes them (if Neo4j is reachable)
- Writes results to JSON/MD and emits a .cypher file for reproducibility
"""

from neo4j import GraphDatabase
from neo4j.exceptions import AuthError
from pathlib import Path
import json
import logging
from typing import Dict, Any
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/outputs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORD_PREDICATE = """
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'artificial intelligence' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'machine learning' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'deep learning' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'data mining' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'computer vision' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'nlp' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'natural language processing' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'gis' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'geographic information' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'geospatial' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'remote sensing' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'drone' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'uav' OR
  toLower(coalesce(c.name,'') + ' ' + coalesce(c.description,'')) CONTAINS 'unmanned aerial'
""".strip()

ACCRED_PREDICATE = """
  toLower(a.name) CONTAINS 'society of american foresters' OR
  toLower(coalesce(a.abbreviation,'')) = 'saf' OR
  toLower(coalesce(a.acronym,'')) = 'saf'
""".strip()

REL_TYPES = ":OFFERS|:INCLUDES_COURSE|:HAS_COURSE"

CYPHER_TOTAL_SAF_PROGRAMS = f"""
MATCH (p:Program)-[:ACCREDITED_BY]->(a)
WHERE {ACCRED_PREDICATE}
RETURN count(DISTINCT p) AS total_saf_programs
""".strip()

CYPHER_QUALIFIED_PROGRAMS = f"""
MATCH (p:Program)-[:ACCREDITED_BY]->(a)
WHERE {ACCRED_PREDICATE}
MATCH p-[{REL_TYPES}]->(c:Course)
WHERE {KEYWORD_PREDICATE}
RETURN count(DISTINCT p) AS saf_programs_with_qualifying_course
""".strip()

CYPHER_TOTAL_AND_PROPORTION = f"""
CALL {{
  MATCH (p:Program)-[:ACCREDITED_BY]->(a)
  WHERE {ACCRED_PREDICATE}
  RETURN count(DISTINCT p) AS total
}}
CALL {{
  MATCH (p:Program)-[:ACCREDITED_BY]->(a)
  WHERE {ACCRED_PREDICATE}
  MATCH p-[{REL_TYPES}]->(c:Course)
  WHERE {KEYWORD_PREDICATE}
  RETURN count(DISTINCT p) AS qualified
}}
RETURN total, qualified, CASE WHEN total>0 THEN 1.0*qualified/total ELSE 0 END AS proportion
""".strip()

CYPHER_COURSE_COUNTS = f"""
MATCH (p:Program)-[:ACCREDITED_BY]->(a)
WHERE {ACCRED_PREDICATE}
MATCH p-[{REL_TYPES}]->(c:Course)
WHERE {KEYWORD_PREDICATE}
WITH c,
  (
    CASE WHEN
      toLower(coalesce(c.type,'')) IN ['core','required'] OR
      toLower(coalesce(c.requirement,'')) IN ['core','required'] OR
      toLower(coalesce(c.core_required,'')) IN ['core','required'] OR
      c.core = true OR c.isRequired = true
    THEN 1 ELSE 0 END
  ) AS is_core_required
RETURN count(c) AS total_qualifying_courses,
       sum(is_core_required) AS core_or_required_courses
""".strip()

CYPHER_PROGRAMS_WITH_CORE_REQUIRED = f"""
MATCH (p:Program)-[:ACCREDITED_BY]->(a)
WHERE {ACCRED_PREDICATE}
MATCH p-[{REL_TYPES}]->(c:Course)
WHERE {KEYWORD_PREDICATE}
WITH p,
  (
    CASE WHEN
      toLower(coalesce(c.type,'')) IN ['core','required'] OR
      toLower(coalesce(c.requirement,'')) IN ['core','required'] OR
      toLower(coalesce(c.core_required,'')) IN ['core','required'] OR
      c.core = true OR c.isRequired = true
    THEN 1 ELSE 0 END
  ) AS is_core_required
WITH p, max(is_core_required) AS has_core_required
RETURN count(DISTINCT p) AS programs_with_core_or_required_qualifying_course
""".strip()

ALL_QUERIES = {
    'total_saf_programs': CYPHER_TOTAL_SAF_PROGRAMS,
    'qualified_programs': CYPHER_QUALIFIED_PROGRAMS,
    'proportion': CYPHER_TOTAL_AND_PROPORTION,
    'course_counts': CYPHER_COURSE_COUNTS,
    'programs_with_core_or_required': CYPHER_PROGRAMS_WITH_CORE_REQUIRED,
}


def write_cypher_file() -> Path:
    path = OUTPUT_DIR / 'saf_program_course_proportion.cypher'
    with open(path, 'w') as f:
        f.write("-- SAF-accredited Program Course Proportion Queries\n\n")
        for name, q in ALL_QUERIES.items():
            f.write(f"-- {name}\n{q}\n\n")
    logger.info(f"Cypher queries written to: {path}")
    return path


def _create_driver(uri: str, user: str, password: str):
    """Create a Neo4j driver, trying basic auth first (or none) and
    gracefully falling back to no-auth if the server has auth disabled.

    Respects env flag `NEO4J_AUTH_DISABLED` (truthy to force no-auth first).
    """
    auth_disabled_env = os.getenv('NEO4J_AUTH_DISABLED', '').lower() in {"1", "true", "yes", "on"}

    try_order = []
    # If user/pass absent or auth disabled is requested, try no-auth first
    if auth_disabled_env or not user or not password or str(user).lower() == 'none':
        try_order = [None, (user, password)]
    else:
        try_order = [(user, password), None]

    last_error = None
    for auth in try_order:
        try:
            return GraphDatabase.driver(uri, auth=auth)
        except AuthError as e:
            # Unsupported auth scheme or wrong creds; try next mode
            last_error = e
            continue
        except Exception as e:
            # Connection or other errors; keep last error but try next auth mode
            last_error = e
            continue

    # If all attempts failed, raise the last error
    if last_error is not None:
        raise last_error
    raise RuntimeError("Failed to create Neo4j driver for unknown reasons")


def run_queries(uri: str, user: str, password: str) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    try:
        driver = _create_driver(uri, user, password)
        # Proactively verify connectivity to surface auth errors early and allow fallback
        try:
            driver.verify_connectivity()
        except AuthError as e:
            # Retry with no-auth in case server has auth disabled
            try:
                driver.close()
            except Exception:
                pass
            driver = _create_driver(uri, user=None, password=None)
            driver.verify_connectivity()
    except AuthError as e:
        logger.error(f"Neo4j authentication failed: {e}")
        results['error'] = f"authentication_failed: {e}"
        return results
    except Exception as e:
        logger.error(f"Neo4j connection failed: {e}")
        results['error'] = f"connection_failed: {e}"
        return results

    def run(q: str):
        with driver.session() as s:
            return s.run(q).data()

    try:
        for name, q in ALL_QUERIES.items():
            rows = run(q)
            results[name] = rows
            logger.info(f"Executed {name}: {rows}")
    finally:
        driver.close()

    # Compose a compact summary if possible
    try:
        total = results.get('proportion', [{}])[0].get('total', 0)
        qualified = results.get('proportion', [{}])[0].get('qualified', 0)
        proportion = results.get('proportion', [{}])[0].get('proportion', 0.0)
        course_counts = results.get('course_counts', [{}])[0]
        core_required_courses = course_counts.get('core_or_required_courses', 0)
        total_qualifying_courses = course_counts.get('total_qualifying_courses', 0)
        programs_with_core_req = results.get('programs_with_core_or_required', [{}])[0].get('programs_with_core_or_required_qualifying_course', 0)

        results['summary'] = {
            'total_saf_programs': int(total),
            'qualified_programs': int(qualified),
            'proportion_qualified': float(proportion),
            'total_qualifying_courses': int(total_qualifying_courses),
            'core_or_required_courses': int(core_required_courses),
            'programs_with_core_or_required_qualifying_course': int(programs_with_core_req),
        }
    except Exception:
        pass

    return results


def write_results(results: Dict[str, Any]):
    json_path = OUTPUT_DIR / 'saf_program_course_proportion_results.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results written to: {json_path}")

    # Markdown summary if summary present
    if 'summary' in results:
        s = results['summary']
        md = []
        md.append("# SAF-Accredited Programs: AI/GIS/RS/Drone Course Adoption")
        md.append("")
        md.append(f"- **Total SAF Programs**: {s['total_saf_programs']}")
        md.append(f"- **Programs with ≥1 qualifying course**: {s['qualified_programs']} ({s['proportion_qualified']*100:.1f}%)")
        md.append(f"- **Qualifying Courses (total)**: {s['total_qualifying_courses']}")
        md.append(f"- **Core/Required Qualifying Courses**: {s['core_or_required_courses']}")
        md.append(f"- **Programs with a Core/Required Qualifying Course**: {s['programs_with_core_or_required_qualifying_course']}")
        (OUTPUT_DIR / 'saf_program_course_proportion_summary.md').write_text("\n".join(md))
        logger.info("Markdown summary written.")


def main():
    # Always write the cypher for reproducibility
    write_cypher_file()

    # Allow configuration via environment variables
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7693')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'perseus2025')

    results = run_queries(uri, user, password)
    write_results(results)

    if 'error' in results:
        logger.warning("Query execution was skipped or failed. Use the .cypher file to run directly in Neo4j once the DB is up.")


if __name__ == '__main__':
    main()
