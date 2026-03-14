import yaml


def parse_smartbeans_exercise(yaml_string):
    # data = yaml.safe_load(yaml_string)
    # Falls das YAML als String reinkommt, nutzen wir safe_load:
    data = yaml.safe_load(yaml_string)

    # Basis-Infos sicher abrufen (Fallback auf leere Strings)
    title = data.get('title', 'Ohne Titel')
    shortname = data.get('shortname', '')
    task = data.get('task', '')
    raw_solution = data.get('solution', '')

    # ==========================================
    # 1. Struktureller Content (V2) - Dynamischer Aufbau
    # ==========================================
    content_parts = [f"Titel: {title}"]

    if shortname:
        content_parts.append(f"Thema (Kurz): {shortname}")

    content_parts.append(f"\nAufgabenstellung:\n{task}")

    # Lösung intelligent bereinigen und prüfen
    has_solution = False
    if raw_solution:
        clean_solution = raw_solution.strip()
        # Ignoriere leere Strings oder reine "TODO" Platzhalter
        if clean_solution and clean_solution.upper() != "TODO":
            content_parts.append(f"\nMusterlösung (C-Code):\n{clean_solution}")
            has_solution = True

    # Den finalen Textblock zusammensetzen
    content = "\n".join(content_parts)

    # ==========================================
    # 2. Metadaten-Anreicherung (V3)
    # ==========================================
    ckurs_info = data.get('courses', {}).get('ckurs', {})

    # Tags sicher extrahieren
    tags = []
    difficulty = "unbekannt"

    for t in ckurs_info.get('tags', []):
        if isinstance(t, dict) and 'name' in t:
            tags.append(t['name'])
        elif isinstance(t, dict):
            # z.B. {'schwierig': None}
            difficulty = list(t.keys())[0]
        elif isinstance(t, str):
            # z.B. "einfach"
            difficulty = t

    metadata = {
        "taskid": data.get("taskid", "unknown"),
        "title": title,
        "tags": ", ".join(tags),
        "difficulty": difficulty,
        "source_type": "smartbeans_yaml",
        "language": "c",
        "has_solution": has_solution
    }

    return content, metadata