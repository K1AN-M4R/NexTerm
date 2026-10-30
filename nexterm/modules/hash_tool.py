
import hashlib
import os


ALGORITHMS = {
    "1": "md5",
    "2": "sha1",
    "3": "sha256",
    "4": "sha512",
}


def calculate_hash(file_path, algorithm="sha256"):
    if algorithm not in hashlib.algorithms_available:
        raise ValueError("Unsupported hash algorithm")

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File not found")

    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            hasher.update(chunk)

    return hasher.hexdigest()


def hash_menu():
    print("\n=== HASH CALCULATOR ===")
    print("[1] MD5")
    print("[2] SHA1")
    print("[3] SHA256")
    print("[4] SHA512")

    choice = input("\nAlgorithm > ").strip()

    algorithm = ALGORITHMS.get(choice)

    if not algorithm:
        print("Invalid algorithm!")
        return

    file_path = input("File path > ").strip().strip('"')

    try:
        result = calculate_hash(file_path, algorithm)

        print(f"\nAlgorithm : {algorithm.upper()}")
        print(f"File      : {os.path.basename(file_path)}")
        print(f"Hash      : {result}")

    except (OSError, ValueError) as error:
        print(f"\nError: {error}")
