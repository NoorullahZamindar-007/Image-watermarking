from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PIL import Image
import cv2
import numpy as np
import os
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/results'

# Ensure upload and result directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

def add_watermark(image_path, text, output_path):
    # Load the image
    image = Image.open(image_path)
    image_textw = image.resize((500, 300))
    image_text = np.array(image_textw.convert('RGB'))

    # Get image dimensions
    h_image, w_image = image_text.shape[:2]

    # Add watermark text using OpenCV
    cv2.putText(image_text, text=text, org=(w_image - 150, h_image - 20), 
                fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, 
                color=(0, 0, 255), thickness=2, lineType=cv2.LINE_4)

    # Save the watermarked image
    cv2.imwrite(output_path, cv2.cvtColor(image_text, cv2.COLOR_RGB2BGR))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file part"
        file = request.files['image']
        text = request.form.get('watermark', 'Pianalytix')
        
        if file.filename == '':
            return "No selected file"
        
        # Save the uploaded image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)

        # Watermark output path
        output_path = os.path.join(app.config['RESULT_FOLDER'], 'watermarked_' + file.filename)
        
        # Add watermark
        add_watermark(image_path, text, output_path)

        return redirect(url_for('show_image', filename='watermarked_' + file.filename))
    
    return render_template('index.html')

@app.route('/static/results/<filename>')
def show_image(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
