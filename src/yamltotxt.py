import os
import yaml
from constants import SMARTBEANS_DIR


def convert_yaml_to_txt(source_folder):
    # Zielordner erstellen, falls er nicht existiert
    if not os.path.exists(source_folder):
        print(f"Fehler: Der Ordner '{source_folder}' wurde nicht gefunden.")
        return

    # Alle Dateien im Ordner durchlaufen
    for filename in os.listdir(source_folder):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            yaml_path = os.path.join(source_folder, filename)
            txt_path = os.path.join(source_folder, filename.rsplit('.', 1)[0] + ".txt")

            try:
                with open(yaml_path, 'r', encoding='utf-8') as yfile:
                    # YAML-Inhalt laden
                    data = yaml.safe_load(yfile)

                    with open(txt_path, 'w', encoding='utf-8') as tfile:
                        # Den Inhalt schön formatiert in die TXT schreiben
                        # Falls es ein Dictionary ist, gehen wir die Key-Value Paare durch
                        if isinstance(data, dict):
                            for key, value in data.items():
                                tfile.write(f"{key.upper()}:\n{value}\n\n")
                        else:
                            tfile.write(str(data))

                print(f"Konvertiert: {filename} -> {os.path.basename(txt_path)}")

            except Exception as e:
                print(f"Fehler beim Bearbeiten von {filename}: {e}")


if __name__ == "__main__":
    convert_yaml_to_txt(SMARTBEANS_DIR)