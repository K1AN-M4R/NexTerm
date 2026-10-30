
import os
import shutil
import textwrap


GREEN = "\033[92m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"


def terminal_width():
    return max(50, min(shutil.get_terminal_size((90, 25)).columns, 90))


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def line(char="═"):
    width = terminal_width()
    print(f"{PURPLE}{char * width}{RESET}")


def center(text, width=None):
    width = width or terminal_width()
    print(text.center(width))


def show_banner():
    clear_screen()

    width = terminal_width()

    logo = [
        "███╗   ██╗███████╗██╗  ██╗",
        "████╗  ██║██╔════╝╚██╗██╔╝",
        "██╔██╗ ██║█████╗   ╚███╔╝",
        "██║╚██╗██║██╔══╝   ██╔██╗",
        "██║ ╚████║███████╗██╔╝ ██╗",
        "╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝",
    ]

    print()

    for row in logo:
        center(f"{GREEN}{BOLD}{row}{RESET}", width)

    print()
    center(f"{CYAN}{BOLD}N E X T E R M   S Y S T E M   T O O L K I T{RESET}", width)
    center(f"{GRAY}Version 1.0 | Python Standard Library{RESET}", width)

    print()
    line()


def show_menu():
    width = terminal_width()

    title = " MAIN MENU "
    print(f"\n{PURPLE}{BOLD}{title.center(width, '═')}{RESET}\n")

    options = [
        ("1", "System Information"),
        ("2", "Hash Calculator"),
        ("3", "JSON Formatter"),
        ("4", "File Explorer"),
        ("5", "Network Diagnostics"),
    ]

    for number, label in options:
        print(
            f"  {GREEN}{BOLD}[{number}]{RESET}"
            f"  {WHITE}{label}{RESET}"
        )

    print(f"\n  {RED}{BOLD}[0]{RESET}  Exit\n")

    line()


def show_system_info(info):
    width = terminal_width()
    content_width = width - 6

    print()
    print(f"{GREEN}{BOLD}{' SYSTEM REPORT '.center(width, '═')}{RESET}")

    for section, items in info.items():

        print(f"\n{PURPLE}{BOLD}  ┌── {section}{RESET}")

        if not isinstance(items, dict):
            print(f"  {CYAN}{items}{RESET}")
            continue

        for name, value in items.items():

            if isinstance(value, dict):
                print(f"\n  {CYAN}{BOLD}  {name}{RESET}")

                for sub_name, sub_value in value.items():
                    label = f"    {sub_name}: "
                    available = max(15, content_width - len(label))

                    wrapped = textwrap.wrap(
                        str(sub_value),
                        width=available
                    ) or [""]

                    print(f"  {GREEN}{label}{wrapped[0]}{RESET}")

                    for part in wrapped[1:]:
                        print(f"  {GREEN}{' ' * len(label)}{part}{RESET}")

            else:
                label = f"  {name}: "
                available = max(15, content_width - len(label))

                wrapped = textwrap.wrap(
                    str(value),
                    width=available
                ) or [""]

                print(f"{CYAN}{label}{wrapped[0]}{RESET}")

                for part in wrapped[1:]:
                    print(f"{CYAN}{' ' * len(label)}{part}{RESET}")

        print(f"{PURPLE}  └{'─' * (width - 4)}{RESET}")

    print()
    print(f"{GREEN}{BOLD}{' END OF REPORT '.center(width, '═')}{RESET}")


def get_choice():
    return input(f"\n{CYAN}{BOLD}NexTerm {GREEN}» {RESET}").strip()


def pause():
    input(f"\n{GRAY}Press Enter to continue...{RESET}")


def success(message):
    print(f"\n{GREEN}[+] {message}{RESET}")


def error(message):
    print(f"\n{RED}[-] {message}{RESET}")


def warning(message):
    print(f"\n{YELLOW}[!] {message}{RESET}")


def info(message):
    print(f"\n{CYAN}[*] {message}{RESET}")
