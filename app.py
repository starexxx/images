from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

# Define the directory containing your images
ICON_DIRECTORY = os.path.join(os.getcwd(), "icon")

@app.route('/get-image', methods=['GET'])
def get_image():
    # Get the filename from the request arguments
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"error": "Filename parameter is missing"}), 400

    # Construct the full path to the image
    file_path = os.path.join(ICON_DIRECTORY, f"{filename}.png")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": f"Image '{filename}' not found"}), 404

    # Return the image
    return send_file(file_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
