from flask import Flask, render_template, request, jsonify
import os
from googletrans import Translator  # For text translation - REMAINING LIMITATION
from PIL import Image, ImageOps  # For image processing
import pytesseract  # For OCR
from werkzeug.utils import secure_filename
import PyPDF2 # Pdf reader
import time
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}  # Allowed file extensions

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from image using OCR
def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)

        # **Image Pre-processing (Optimization)**
        img = ImageOps.grayscale(img)
        img = img.point(lambda x: 0 if x < 128 else 255, '1') #Threshold
        width, height = img.size
        if width < 300 or height < 300:
            img = img.resize((width * 2, height * 2), Image.LANCZOS)
        elif width > 1000 or height > 1000:
            img = img.resize((width // 2, height // 2), Image.LANCZOS)

        # **Tesseract Configuration**
        text = pytesseract.image_to_string(img, config='--psm 6 --oem 3')
        return text
    except Exception as e:
        print(f"OCR Error: {e} - Image: {image_path}")  # Log the error
        return f"OCR Error: {e}"

    # Function to translate text (with retry)
def translate_text(text, target_language='en', source_language='auto'):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language, src=source_language)
        return translated.text
    except Exception as e:
        print(f"Translation Error: {e}") # Log the error
        return f"Translation Error: {e}"

# Function to extract text from PDF files
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"PDF Error: {e}")
        return f"PDF Error: {e}"

def translate_with_retry(text, target_language='en', source_language='auto', max_retries=3):
    for i in range(max_retries):
        try:
            return translate_text(text, target_language, source_language)
        except Exception as e:
            print(f"Translation attempt {i+1} failed: {e}")
            if i < max_retries - 1:
                wait_time = (2 ** i) + random.random()  # Exponential backoff with jitter
                print(f"Waiting {wait_time:.2f} seconds before retrying...")
                time.sleep(wait_time)
            else:
                return f"Translation failed after {max_retries} attempts: {e}" # Return the error


# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads and translation
@app.route('/translate_files', methods=['POST'])
def translate_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files part'})

        files = request.files.getlist('files')
        target_language = request.form['targetLanguage']
        translations = {}

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)  # Save the file

                # Extract text and translate based on file type
                extracted_text = ""
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    extracted_text = extract_text_from_image(filepath)
                elif filename.lower().endswith('.pdf'):
                    extracted_text = extract_text_from_pdf(filepath)
                else:
                    extracted_text = "Unsupported file type."

                translated_text = translate_with_retry(extracted_text, target_language)
                translations[filename] = translated_text

                os.remove(filepath)  # Remove the file after processing

        return jsonify(translations)

    except Exception as e:
        print(f"File Translation Route Error: {e}")
        return jsonify({'error': str(e)})

# Route to handle text translation
@app.route('/translate_text', methods=['POST'])
def translate_text_route():
    try:
        text = request.form['text']
        source_language = request.form['sourceLanguage']
        target_language = request.form['targetLanguage']

        translated_text = translate_with_retry(text, target_language, source_language)
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        print(f"Text Translation Route Error: {e}")
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
