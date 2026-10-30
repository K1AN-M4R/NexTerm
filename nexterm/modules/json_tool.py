
import json
from pathlib import Path


def format_json_file(file_path):
    path = Path(file_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError("JSON file not found")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    )


def json_menu():
    print("\n=== JSON FORMATTER ===")
    print("[1] Format JSON file")
    print("[2] Validate JSON file")

    choice = input("\nJSON > ").strip()

    if choice not in ("1", "2"):
        print("Invalid option!")
        return

    file_path = input("File path > ").strip().strip('"')

    try:
        formatted = format_json_file(file_path)

        if choice == "1":
            print("\n" + formatted)

            save = input("\nSave formatted file? (y/n) > ").lower()

            if save == "y":
                output_path = input("Output path > ").strip().strip('"')

                if not output_path:
                    print("Output path cannot be empty.")
                    return

                Path(output_path).expanduser().write_text(
                    formatted + "\n",
                    encoding="utf-8"
                )

                print("File saved successfully!")

        else:
            print("\nJSON is valid!")

    except json.JSONDecodeError as error:
        print(f"\nInvalid JSON: {error}")

    except (OSError, UnicodeError, ValueError) as error:
        print(f"\nError: {error}")
