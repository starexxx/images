import os
import requests
import json
import zipfile
import base64
from flask import Flask, jsonify
from threading import Thread

# Configurations
current_directory = os.path.dirname(os.path.abspath(__file__))
item_ids_file_path = os.path.join(current_directory, "Extracted_Item_IDs.json")
save_directory = os.path.join(current_directory, "Temp_Icons")
zip_file_path = os.path.join(current_directory, "All_Icons.zip")
github_repo = "garena420/main_jwt_token"
github_token = "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"

# Flask App
app = Flask(__name__)
progress = {"completed": 0, "total": 0}

os.makedirs(save_directory, exist_ok=True)
base_url = "https://dl.cdn.freefiremobile.com/live/ABHotUpdates/IconCDN/android/{number}_rgb.astc"

# Load item IDs
with open(item_ids_file_path, 'r') as file:
    item_ids = json.load(file)
progress["total"] = len(item_ids)


def download_icon(item_id):
    url = base_url.format(number=item_id)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_path = os.path.join(save_directory, f"{item_id}_rgb.astc")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded: {item_id}")
        else:
            print(f"File not found for itemID: {item_id}")
    except Exception as e:
        print(f"Error downloading {item_id}: {e}")
    finally:
        progress["completed"] += 1


def download_all_icons():
    for item_id in item_ids:
        download_icon(item_id)
    create_zip()
    upload_to_github()


def create_zip():
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(save_directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, save_directory))
    print(f"Created ZIP file at: {zip_file_path}")


def upload_to_github():
    with open(zip_file_path, 'rb') as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode('utf-8')

        # Construct the API URL
        url = f"https://api.github.com/repos/{github_repo}/contents/{os.path.basename(zip_file_path)}"

        # Debugging: Log the URL and payload
        print(f"Uploading to URL: {url}")

        response = requests.put(
            url,
            headers={
                "Authorization": f"token {github_token}",
                "Content-Type": "application/json",
            },
            json={
                "message": "Add All_Icons.zip",
                "content": encoded_content,
            }
        )

    if response.status_code in [200, 201]:
        print("Uploaded ZIP to GitHub successfully.")
    else:
        print(f"Failed to upload ZIP to GitHub: {response.status_code}, {response.content.decode()}")


@app.route('/progress', methods=['GET'])
def check_progress():
    return jsonify({
        "completed": progress["completed"],
        "total": progress["total"],
        "percentage": (progress["completed"] / progress["total"]) * 100 if progress["total"] > 0 else 0
    })


if __name__ == '__main__':
    # Start the download process in a separate thread
    download_thread = Thread(target=download_all_icons)
    download_thread.start()

    # Run Flask app
    app.run(debug=True, port=5000)
