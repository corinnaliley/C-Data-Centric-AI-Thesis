import yaml


def parse_smartbeans_exercise(yaml_string):
    data = yaml.safe_load(yaml_string)

    title = data.get('title', 'Ohne Titel')
    shortname = data.get('shortname', '')
    task = data.get('task', '')
    raw_solution = data.get('solution', '')

    ckurs_info = data.get('courses', {}).get('ckurs', {})
    DIFFICULTY_NAMES = {"einfach", "mittel", "schwer", "leicht"}
    tags = []
    difficulty = "unbekannt"

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
        "taskid": data.get("taskid", "unknown"),
        "title": title,
        "tags": ", ".join(tags),
        "difficulty": difficulty,
        "source_type": "smartbeans_yaml",
        "language": "c",
    }

    chunks = []

    # Chunk 1: Aufgabenstellung
    task_parts = [f"Titel: {title}"]
    if shortname:
        task_parts.append(f"Thema (Kurz): {shortname}")
    if tags:
        task_parts.append(f"Themen: {', '.join(tags)}")
    task_parts.append(f"\nAufgabenstellung:\n{task}")
    chunks.append(("\n".join(task_parts), {**base_metadata, "chunk_type": "task"}))

    # Chunk 2: Musterlösung (nur wenn vorhanden und nicht leer/TODO)
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