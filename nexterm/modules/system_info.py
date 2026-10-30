
import os
import platform
import shutil
import socket
import subprocess
import time


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except (OSError, UnicodeError):
        return None


def format_bytes(size):
    if size is None:
        return "Unknown"

    size = float(size)

    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} EB"


def get_linux_cpu_info():
    data = {}

    content = read_file("/proc/cpuinfo")
    if not content:
        return data

    for line in content.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip().lower()

        if key in ("model name", "hardware", "cpu implementer"):
            data.setdefault("model", value.strip())

        elif key in ("vendor_id", "cpu implementer"):
            data.setdefault("vendor", value.strip())

        elif key == "cpu family":
            data["family"] = value.strip()

        elif key == "model":
            data["model_id"] = value.strip()

        elif key == "stepping":
            data["stepping"] = value.strip()

        elif key == "microcode":
            data["microcode"] = value.strip()

        elif key == "cpu mhz":
            data.setdefault("frequency", value.strip() + " MHz")

        elif key == "cache size":
            data["cache"] = value.strip()

    return data


def get_cpu_info():
    cpu_data = get_linux_cpu_info()

    model = (
        cpu_data.get("model")
        or platform.processor()
        or "Unknown"
    )

    logical_cores = os.cpu_count() or "Unknown"

    physical_cores = "Unknown"
    if os.path.exists("/proc/cpuinfo"):
        physical_ids = set()
        core_ids = set()

        content = read_file("/proc/cpuinfo") or ""

        for line in content.splitlines():
            if line.startswith("physical id"):
                physical_ids.add(line.split(":", 1)[1].strip())

            elif line.startswith("core id"):
                core_ids.add(line.split(":", 1)[1].strip())

        if physical_ids and core_ids:
            physical_cores = len({
                (physical, core)
                for physical in physical_ids
                for core in core_ids
            })

    frequency = cpu_data.get("frequency", "Unknown")

    current_frequency = read_file(
        "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    )

    if current_frequency:
        try:
            frequency = f"{int(current_frequency) / 1000:.0f} MHz"
        except ValueError:
            pass

    return {
        "Model": model,
        "Vendor": cpu_data.get("vendor", "Unknown"),
        "Logical Cores": logical_cores,
        "Physical Cores": physical_cores,
        "Frequency": frequency,
        "Cache": cpu_data.get("cache", "Unknown"),
        "CPU Family": cpu_data.get("family", "Unknown"),
        "Model ID": cpu_data.get("model_id", "Unknown"),
        "Stepping": cpu_data.get("stepping", "Unknown"),
        "Microcode": cpu_data.get("microcode", "Unknown"),
    }


def get_ram_info():
    if os.path.exists("/proc/meminfo"):
        try:
            memory = {}

            content = read_file("/proc/meminfo") or ""

            for line in content.splitlines():
                key, value = line.split(":", 1)
                memory[key] = int(value.strip().split()[0]) * 1024

            total = memory["MemTotal"]
            available = memory.get("MemAvailable")

            if available is None:
                available = memory.get("MemFree", 0)

            used = total - available

            return {
                "Total": format_bytes(total),
                "Used": format_bytes(used),
                "Available": format_bytes(available),
                "Usage": f"{used / total * 100:.1f}%" if total else "Unknown",
                "Free": format_bytes(memory.get("MemFree")),
                "Buffers": format_bytes(memory.get("Buffers")),
                "Cached": format_bytes(memory.get("Cached")),
                "Swap Total": format_bytes(memory.get("SwapTotal", 0)),
                "Swap Free": format_bytes(memory.get("SwapFree", 0)),
            }

        except (KeyError, ValueError):
            pass

    if os.name == "nt":
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)

        if ctypes.windll.kernel32.GlobalMemoryStatusEx(
            ctypes.byref(status)
        ):
            total = status.ullTotalPhys
            available = status.ullAvailPhys
            used = total - available

            return {
                "Total": format_bytes(total),
                "Used": format_bytes(used),
                "Available": format_bytes(available),
                "Usage": f"{used / total * 100:.1f}%" if total else "Unknown",
                "Free": "Unknown",
                "Buffers": "Unknown",
                "Cached": "Unknown",
                "Swap Total": "Unknown",
                "Swap Free": "Unknown",
            }

    return {"Status": "Memory information unavailable"}


def get_disk_info():
    disks = []

    if os.name == "nt":
        import ctypes

        drives = ctypes.windll.kernel32.GetLogicalDrives()

        for index in range(26):
            if drives & (1 << index):
                drive = f"{chr(65 + index)}:\\"

                try:
                    usage = shutil.disk_usage(drive)
                    disks.append({
                        "Mount": drive,
                        "Total": format_bytes(usage.total),
                        "Used": format_bytes(usage.used),
                        "Free": format_bytes(usage.free),
                        "Usage": f"{usage.used / usage.total * 100:.1f}%"
                        if usage.total else "Unknown",
                    })
                except OSError:
                    continue

    else:
        mounts = set()

        content = read_file("/proc/mounts") or ""

        for line in content.splitlines():
            parts = line.split()

            if len(parts) < 3:
                continue

            device, mount, filesystem = parts[:3]

            if not device.startswith("/dev/"):
                continue

            if filesystem in ("squashfs", "tmpfs"):
                continue

            mounts.add(mount)

        if not mounts:
            mounts.add(os.path.expanduser("~"))

        for mount in sorted(mounts):
            try:
                usage = shutil.disk_usage(mount)

                disks.append({
                    "Mount": mount,
                    "Total": format_bytes(usage.total),
                    "Used": format_bytes(usage.used),
                    "Free": format_bytes(usage.free),
                    "Usage": f"{usage.used / usage.total * 100:.1f}%"
                    if usage.total else "Unknown",
                })
            except OSError:
                continue

    return disks


def get_network_info():
    hostname = socket.gethostname()

    try:
        addresses = sorted({
            result[4][0]
            for result in socket.getaddrinfo(hostname, None)
            if result[0] == socket.AF_INET
        })

        ip_address = ", ".join(addresses) if addresses else "Unknown"

    except OSError:
        ip_address = "Unknown"

    interfaces = []

    try:
        interfaces = [
            name for _, name in socket.if_nameindex()
        ]
    except OSError:
        pass

    return {
        "Hostname": hostname,
        "IPv4 Addresses": ip_address,
        "Interfaces": ", ".join(interfaces) or "Unknown",
    }


def get_os_info():
    distro = "Unknown"

    if os.path.exists("/etc/os-release"):
        content = read_file("/etc/os-release") or ""

        for line in content.splitlines():
            if line.startswith("PRETTY_NAME="):
                distro = line.split("=", 1)[1].strip().strip('"')
                break

    return {
        "System": platform.system(),
        "Distribution": distro,
        "Release": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.machine(),
        "Platform": platform.platform(),
        "Hostname": socket.gethostname(),
        "Python Version": platform.python_version(),
        "Python Implementation": platform.python_implementation(),
    }


def get_uptime():
    uptime = read_file("/proc/uptime")

    if uptime:
        try:
            seconds = int(float(uptime.split()[0]))
        except (ValueError, IndexError):
            return "Unknown"

    elif os.name == "nt":
        import ctypes
        seconds = ctypes.windll.kernel32.GetTickCount64() // 1000

    else:
        return "Unknown"

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return f"{days}d {hours}h {minutes}m {seconds}s"


def get_virtualization_info():
    if "microsoft" in platform.release().lower():
        return "WSL"

    if os.path.exists("/.dockerenv"):
        return "Docker"

    if os.path.exists("/proc/1/cgroup"):
        content = read_file("/proc/1/cgroup") or ""

        if any(word in content.lower() for word in (
            "docker", "containerd", "kubepods"
        )):
            return "Container"

    return "Unknown / Physical"


def get_system_info():
    return {
        "OPERATING SYSTEM": get_os_info(),
        "PROCESSOR": get_cpu_info(),
        "MEMORY": get_ram_info(),
        "STORAGE": {
            f"Disk {index}": disk
            for index, disk in enumerate(get_disk_info(), start=1)
        },
        "NETWORK": get_network_info(),
        "SYSTEM STATUS": {
            "Uptime": get_uptime(),
            "Virtualization": get_virtualization_info(),
            "Current User": os.environ.get("USER")
            or os.environ.get("USERNAME")
            or "Unknown",
        },
    }
