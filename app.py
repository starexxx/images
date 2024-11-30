import os
import requests
import json
from flask import Flask, jsonify
from threading import Thread

# Configurations
current_directory = os.path.dirname(os.path.abspath(__file__))
item_ids_file_path = os.path.join(current_directory, "Extracted_Item_IDs.json")
save_directory = os.path.join(current_directory, "Temp_Icons")
github_repo = "garenaa420/main_token_jwt"
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
            upload_to_github(file_path, f"{item_id}_rgb.astc")
        else:
            print(f"File not found for itemID: {item_id}")
    except Exception as e:
        print(f"Error downloading {item_id}: {e}")
    finally:
        progress["completed"] += 1

def download_all_icons():
    for item_id in item_ids:
        download_icon(item_id)

def upload_to_github(file_path, file_name):
    with open(file_path, 'rb') as file:
        content = file.read()
        encoded_content = content.encode("base64").decode("utf-8")  # Base64 encode the file content

        response = requests.put(
            f"https://api.github.com/repos/{github_repo}/contents/{file_name}",
            headers={
                "Authorization": f"token {github_token}",
                "Content-Type": "application/json",
            },
            json={
                "message": f"Add {file_name}",
                "content": encoded_content,
            }
        )

    if response.status_code in [200, 201]:
        print(f"Uploaded {file_name} to GitHub successfully.")
    else:
        print(f"Failed to upload {file_name} to GitHub: {response.content}")

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
