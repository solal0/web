import requests
import zipfile
import os
import shutil
import sys
import tempfile
import time

# --- CONFIG ---
latest_tool_url = "https://solal0.github.io/web/files/Skira's Blob Compiler.zip"
tool_folder_name = "Skira's Blob Compiler"
retry_download = 5
retry_delay = 5
info_file = os.path.join(tempfile.gettempdir(), "update_info.tmp")
max_info_retries = 5
info_retry_delay = 3

def wait_for_info():
    """Wait for compiler.py to send info via a temporary file."""
    retries = 0
    info_received = None
    print("Waiting for info from compiler.py...")
    while retries < max_info_retries and not info_received:
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                target_dir = f.read().strip()
                info = f.read().strip()
                
                if not os.path.isdir(target_dir):
                    print(f"❌ The target folder from info file does not exist: {target_dir}")
                    input("Press Enter to close...")
                    sys.exit(1)
                    
                if info:
                    info_received = info
                    break
        except FileNotFoundError:
            pass

        retries += 1
        print(f"No info yet. Retrying ({retries}/{max_info_retries}) in {info_retry_delay}s...")
        time.sleep(info_retry_delay)

    if info_received:
        print(f"✅ Info received: {info_received}")
        return info_received
    else:
        print("❌ No info received after maximum retries. Closing.")
        input("Press Enter to close...")
        sys.exit(1)

def download_latest(url, dest_path):
    for attempt in range(1, retry_download + 1):
        try:
            print(f"[{attempt}/{retry_download}] Downloading latest tool...")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print("Download complete.")
            return
        except requests.RequestException as e:
            print(f"Error downloading: {e}")
            if attempt < retry_download:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to download the tool. Please check your internet connection.")
                input("Press Enter to close...")
                sys.exit(1)

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extraction completed to: {extract_to}")
    except Exception as e:
        print(f"Failed to extract zip file: {e}")
        input("Press Enter to close...")
        sys.exit(1)

def replace_old_tool(target_dir):
    if os.path.exists(target_dir):
        backup_dir = target_dir + "_old_" + str(int(time.time()))
        print(f"Existing tool folder detected. Renaming old folder to: {backup_dir}")
        try:
            shutil.move(target_dir, backup_dir)
        except Exception as e:
            print(f"Failed to move old folder: {e}")
            input("Press Enter to close...")
            sys.exit(1)

if not os.path.isdir(target_dir):
    print(f"❌ The target folder from info file does not exist: {target_dir}")
    input("Press Enter to close...")
    sys.exit(1)

def main():
    print("Updater started...")
    info = wait_for_info()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    target_dir = os.path.join(parent_dir, tool_folder_name)

    tmp_zip = os.path.join(tempfile.gettempdir(), "latest_tool.zip")
    download_latest(latest_tool_url, tmp_zip)

    replace_old_tool(target_dir)
    extract_zip(tmp_zip, os.path.dirname(target_dir))

    print("\n✅ Tool has been updated successfully!")
    print(f"You can now run the tool at: {target_dir}")
    input("Press Enter to exit updater...")

if __name__ == "__main__":
    main()


