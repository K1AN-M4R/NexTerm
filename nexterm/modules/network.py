
import socket
import subprocess
import platform
import time


def get_local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]

    except OSError:
        return "Unknown"

    finally:
        sock.close()


def dns_lookup(hostname):
    try:
        results = socket.getaddrinfo(hostname, None)

        addresses = sorted({
            result[4][0] for result in results
        })

        return addresses

    except socket.gaierror:
        return []


def ping_host(host):
    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "3", "-w", "2000", host]
    else:
        command = ["ping", "-c", "3", "-W", "2", host]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        return result.returncode == 0, result.stdout

    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error)


def network_menu():
    while True:
        print("\n=== NETWORK DIAGNOSTICS ===")
        print("[1] Show local IP")
        print("[2] DNS Lookup")
        print("[3] Ping Host")
        print("[0] Back")

        choice = input("\nNetwork > ").strip()

        if choice == "1":
            print(f"\nLocal IP: {get_local_ip()}")

        elif choice == "2":
            hostname = input("Hostname > ").strip()

            if not hostname or any(c.isspace() for c in hostname):
                print("Invalid hostname!")
                continue

            addresses = dns_lookup(hostname)

            if addresses:
                print("\nDNS Results:")

                for address in addresses:
                    print(f"  {address}")
            else:
                print("DNS lookup failed!")

        elif choice == "3":
            host = input("Host > ").strip()

            if not host or any(c.isspace() for c in host):
                print("Invalid host!")
                continue

            success, output = ping_host(host)

            print("\n" + output)

            print(
                "Ping successful!"
                if success
                else "Ping failed!"
            )

        elif choice == "0":
            break

        else:
            print("Invalid option!")
