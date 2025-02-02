from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# Path to the folder where item images are stored
ITEM_IMAGE_PATH = 'https://github.com/I-SHOW-AKIRU200/All_Icon/tree/main/icon'

@app.route('/akiru-free-fire-item-info', methods=['GET'])
def get_item_image():
    item_id = request.args.get('item_id')
    key = request.args.get('key')

    # Validate the API key
    if key != '1+2+3':
        return jsonify({"error": "Invalid API key"}), 401

    # Check if item ID is provided
    if not item_id:
        return jsonify({"error": "Item ID is required"}), 400

    # Path to the item image
    image_path = os.path.join(ITEM_IMAGE_PATH, f'{item_id}.png')

    # Check if the image exists
    if not os.path.exists(image_path):
        return jsonify({"error": "Item image not found"}), 404

    try:
        # Open the image
        image = Image.open(image_path).convert("RGBA")

        # Add text "AKIRU" in the middle of the image
        draw = ImageDraw.Draw(image)
        font_size = int(min(image.size) / 5)
        font = ImageFont.truetype("arial.ttf", font_size)

        text = "AKIRU"
        text_width, text_height = draw.textsize(text, font=font)
        text_position = ((image.width - text_width) // 2, (image.height - text_height) // 2)

        # Draw the text with a contrasting outline
        outline_color = "black"
        for offset in range(-2, 3):
            draw.text((text_position[0] + offset, text_position[1]), text, font=font, fill=outline_color)
            draw.text((text_position[0], text_position[1] + offset), text, font=font, fill=outline_color)

        draw.text(text_position, text, font=font, fill="white")

        # Save the modified image temporarily
        output_path = f'/tmp/{item_id}_modified.png'
        image.save(output_path)

        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
