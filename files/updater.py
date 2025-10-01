import requests
import zipfile
import os
import shutil
import sys
import tempfile
import time
import io

# --- CONFIG ---
latest_tool_url = "https://solal0.github.io/web/files/Skira's Blob Compiler.zip"
retry_download = 5
retry_delay = 5
info_file = os.path.join(tempfile.gettempdir(), "update_info.tmp")
max_info_retries = 5
info_retry_delay = 3

def wait_for_info():
    """Wait for compiler.py to send the directory of the outdated tool."""
    retries = 0
    target_dir = None
    print("Waiting for info from compiler.py...")
    while retries < max_info_retries and not target_dir:
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content and os.path.isdir(content):
                    target_dir = content
                    break
        except FileNotFoundError:
            pass

        retries += 1
        print(f"No info yet. Retrying ({retries}/{max_info_retries}) in {info_retry_delay}s...")
        time.sleep(info_retry_delay)

    if not target_dir:
        print("❌ No valid info received after maximum retries. Closing.")
        input("Press Enter to close...")
        sys.exit(1)

    print(f"✅ Info received: {target_dir}")
    return target_dir

def download_latest(url):
    for attempt in range(1, retry_download + 1):
        try:
            print(f"[{attempt}/{retry_download}] Downloading latest tool...")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            print("Download complete.")
            return io.BytesIO(r.content)
        except requests.RequestException as e:
            print(f"Error downloading: {e}")
            if attempt < retry_download:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to download the tool. Please check your internet connection.")
                input("Press Enter to close...")
                sys.exit(1)

def replace_tool_contents(target_dir, zip_bytesio):
    try:
        with zipfile.ZipFile(zip_bytesio) as z:
            for member in z.namelist():
                if member.endswith("/"):
                    continue  # skip directories
                dest_path = os.path.join(target_dir, os.path.basename(member))
                # Remove old file if exists
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                # Write new file
                with open(dest_path, "wb") as f_out:
                    f_out.write(z.read(member))
        print(f"✅ Tool updated successfully at: {target_dir}")
    except Exception as e:
        print(f"❌ Failed to replace tool contents: {e}")
        input("Press Enter to close...")
        sys.exit(1)

def main():
    print("Updater started...")
    target_dir = wait_for_info()

    zip_bytesio = download_latest(latest_tool_url)
    replace_tool_contents(target_dir, zip_bytesio)

    input("Press Enter to exit updater...")

if __name__ == "__main__":
    main()
