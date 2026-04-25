"""
Utility script: batch-convert SmartBeans YAML exercise files to plain text.

Each YAML file in the source folder is read and its top-level key-value pairs
are written to a companion .txt file with UPPERCASE keys as section headers.
"""

import os
import yaml
from constants import SMARTBEANS_DIR


def convert_yaml_to_txt(source_folder: str) -> None:
    """
    Convert all YAML files in a folder to plain-text .txt files.

    For each .yaml / .yml file, a sibling .txt file is created where every
    top-level key is written as an UPPERCASE header followed by its value.

    Args:
        source_folder: Path to the directory containing YAML exercise files.
    """
    if not os.path.exists(source_folder):
        print(f"Error: folder '{source_folder}' not found.")
        return

    for filename in os.listdir(source_folder):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            yaml_path = os.path.join(source_folder, filename)
            txt_path  = os.path.join(source_folder, filename.rsplit('.', 1)[0] + ".txt")

            try:
                with open(yaml_path, 'r', encoding='utf-8') as yfile:
                    data = yaml.safe_load(yfile)

                    with open(txt_path, 'w', encoding='utf-8') as tfile:
                        if isinstance(data, dict):
                            for key, value in data.items():
                                tfile.write(f"{key.upper()}:\n{value}\n\n")
                        else:
                            tfile.write(str(data))

                print(f"Converted: {filename} -> {os.path.basename(txt_path)}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    convert_yaml_to_txt(SMARTBEANS_DIR)
