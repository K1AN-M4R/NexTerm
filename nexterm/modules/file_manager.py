
import os
from pathlib import Path


def list_directory(directory):
    path = Path(directory).expanduser()

    if not path.is_dir():
        raise NotADirectoryError("Directory not found")

    items = sorted(
        path.iterdir(),
        key=lambda item: (not item.is_dir(), item.name.lower())
    )

    for index, item in enumerate(items, start=1):
        if item.is_dir():
            kind = "[DIR]"
            size = "-"
        else:
            kind = "[FILE]"

            try:
                size = format_size(item.stat().st_size)
            except OSError:
                size = "Unknown"

        print(f"{index:>3}. {kind:<7} {item.name:<35} {size}")


def format_size(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def file_menu():
    current_path = Path.cwd()

    while True:
        print("\n=== FILE EXPLORER ===")
        print(f"Current directory: {current_path}")
        print("[1] List files")
        print("[2] Change directory")
        print("[3] Show file information")
        print("[0] Back")

        choice = input("\nFile Explorer > ").strip()

        if choice == "1":
            try:
                list_directory(current_path)
            except OSError as error:
                print(f"Error: {error}")

        elif choice == "2":
            new_path = input("Directory > ").strip().strip('"')

            target = Path(new_path).expanduser()

            if not target.is_absolute():
                target = current_path / target

            try:
                target = target.resolve(strict=True)

                if target.is_dir():
                    current_path = target
                else:
                    print("Not a directory!")

            except OSError as error:
                print(f"Error: {error}")

        elif choice == "3":
            name = input("File name > ").strip()

            target = current_path / name

            try:
                if target.is_file():
                    stat = target.stat()

                    print(f"\nName: {target.name}")
                    print(f"Size: {format_size(stat.st_size)}")
                    print(f"Modified: {stat.st_mtime}")
                else:
                    print("File not found!")

            except OSError as error:
                print(f"Error: {error}")

        elif choice == "0":
            break

        else:
            print("Invalid option!")
