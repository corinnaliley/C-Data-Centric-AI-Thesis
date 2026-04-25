"""
Parser for SmartBeans YAML exercise files.

Extracts structured fields (title, task, solution, tags, difficulty) and
returns them as separate text chunks ready for embedding.
"""

import yaml


def parse_smartbeans_exercise(yaml_string: str) -> list[tuple[str, dict]]:
    """
    Parse a SmartBeans YAML exercise into embeddable text chunks.

    Produces up to two chunks per exercise:
    1. Task chunk — title, topic, tags, and the full task description.
    2. Solution chunk — same header plus the model solution (omitted if absent or TODO).

    The text labels injected into chunk content are intentionally kept in
    German because the exercise corpus and benchmark queries are in German,
    and changing them would shift embedding semantics.

    Args:
        yaml_string: Raw YAML content of one SmartBeans exercise file.

    Returns:
        List of (text, metadata) tuples, one per produced chunk.
        metadata contains: taskid, title, tags, difficulty, source_type, language, chunk_type.
    """
    data = yaml.safe_load(yaml_string)

    title     = data.get('title', 'Untitled')
    shortname = data.get('shortname', '')
    task      = data.get('task', '')
    raw_solution = data.get('solution', '')

    ckurs_info = data.get('courses', {}).get('ckurs', {})

    # German difficulty names must match the values used in the YAML files
    DIFFICULTY_NAMES = {"einfach", "mittel", "schwer", "leicht"}
    tags = []
    difficulty = "unknown"

    for t in ckurs_info.get('tags', []):
        if isinstance(t, dict) and 'name' in t:
            name = t['name']
            if name.lower() in DIFFICULTY_NAMES:
                difficulty = name
            else:
                tags.append(name)
        elif isinstance(t, dict):
            difficulty = list(t.keys())[0]
        elif isinstance(t, str):
            if t.lower() in DIFFICULTY_NAMES:
                difficulty = t
            else:
                tags.append(t)

    base_metadata = {
        "taskid":      data.get("taskid", "unknown"),
        "title":       title,
        "tags":        ", ".join(tags),
        "difficulty":  difficulty,
        "source_type": "smartbeans_yaml",
        "language":    "c",
    }

    chunks = []

    # Chunk 1: task description
    task_parts = [f"Titel: {title}"]
    if shortname:
        task_parts.append(f"Thema (Kurz): {shortname}")
    if tags:
        task_parts.append(f"Themen: {', '.join(tags)}")
    task_parts.append(f"\nAufgabenstellung:\n{task}")
    chunks.append(("\n".join(task_parts), {**base_metadata, "chunk_type": "task"}))

    # Chunk 2: model solution (only if present and non-empty)
    if raw_solution:
        clean_solution = raw_solution.strip()
        if clean_solution and clean_solution.upper() != "TODO":
            solution_parts = [f"Titel: {title}"]
            if shortname:
                solution_parts.append(f"Thema (Kurz): {shortname}")
            if tags:
                solution_parts.append(f"Themen: {', '.join(tags)}")
            solution_parts.append(f"\nMusterlösung (C-Code):\n{clean_solution}")
            chunks.append(("\n".join(solution_parts), {**base_metadata, "chunk_type": "solution"}))

    return chunks
