from flask import Flask, render_template, request, jsonify
import os
from googletrans import Translator  # For text translation
from PIL import Image  # For image processing
import pytesseract  # For OCR
from werkzeug.utils import secure_filename

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
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return str(e)

# Function to translate text
def translate_text(text, target_language='en', source_language='auto'):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language, src=source_language)
        return translated.text
    except Exception as e:
        return str(e)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads and translation
@app.route('/translate_files', methods=['POST'])
def translate_files():
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
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                extracted_text = extract_text_from_image(filepath)
            elif filename.lower().endswith('.pdf'):
                # You'll need a PDF library like PyPDF2 to extract text from PDFs
                extracted_text = "PDF support not yet implemented."
            else:
                extracted_text = "Unsupported file type."

            translated_text = translate_text(extracted_text, target_language)
            translations[filename] = translated_text

            os.remove(filepath)  # Remove the file after processing

    return jsonify(translations)

# Route to handle text translation
@app.route('/translate_text', methods=['POST'])
def translate_text_route():
    text = request.form['text']
    source_language = request.form['sourceLanguage']
    target_language = request.form['targetLanguage']

    translated_text = translate_text(text, target_language, source_language)
    return jsonify({'translated_text': translated_text})

if __name__ == '__main__':
    app.run(debug=True)
