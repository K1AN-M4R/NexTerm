
from nexterm.ui import (
    clear_screen,
    show_banner,
    show_menu,
    show_system_info,
    get_choice,
    pause,
    GREEN,
    RESET,
)

from nexterm.modules.system_info import get_system_info
from nexterm.modules.hash_tool import hash_menu
from nexterm.modules.json_tool import json_menu
from nexterm.modules.file_manager import file_menu
from nexterm.modules.network import network_menu


def run_tool(tool):
    clear_screen()

    try:
        tool()

    except Exception as error:
        print(f"\nError: {error}")

    pause()


def show_hash():
    hash_menu()


def show_json():
    json_menu()


def show_files():
    file_menu()


def show_network():
    network_menu()


def main():
    while True:
        clear_screen()
        show_banner()
        show_menu()

        choice = get_choice()

        if choice == "1":
            def system_report():
                info = get_system_info()
                show_system_info(info)

            run_tool(system_report)

        elif choice == "2":
            run_tool(show_hash)

        elif choice == "3":
            run_tool(show_json)

        elif choice == "4":
            run_tool(show_files)

        elif choice == "5":
            run_tool(show_network)

        elif choice == "0":
            clear_screen()
            print(f"\n{GREEN}Shutting down NexTerm...{RESET}")
            break

        else:
            print("\nInvalid option!")
            pause()


if __name__ == "__main__":
    main()
