import os
import io
import zipfile
from flask import Flask, request, send_file, render_template_string
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator

# --- INITIALIZATION & DEBUGGING ---
app = Flask(__name__)
Image.MAX_IMAGE_PIXELS = None  # Debug: Fixes DecompressionBombWarning

# On Render/Linux, Tesseract is usually in the PATH. 
# If you run locally on Windows, you'll need the path line back.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Users\jackv\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

HTML_INTERFACE = '''
<!DOCTYPE html>
<html>
<head><title>Map Translator</title></head>
<body>
    <h2>Upload Images for Translation</h2>
    <p>Translation starts immediately. No previews will be shown.</p>
    <form method="post" enctype="multipart/form-data">
        <label>Target Language:</label>
        <select name="language">
            <option value="en">English</option>
            <option value="ru">Russian</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
        </select><br><br>
        <input type="file" name="files" multiple>
        <button type="submit">Translate & Download ZIP</button>
    </form>
</body>
</html>
'''

def get_text_color(bg_color):
    lum = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]) / 255
    return (0, 0, 0) if lum > 0.5 else (255, 255, 255)

def process_image(img_bytes, target_lang):
    original = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    width, height = original.size
    
    # Scale for OCR speed but preserve original for output
    ocr_img = original.copy()
    ocr_img.thumbnail((4000, 4000), Image.Resampling.LANCZOS)
    sx, sy = width / ocr_img.width, height / ocr_img.height

    # Debug: PSM 11 for sparse technical text
    data = pytesseract.image_to_data(ocr_img, output_type=pytesseract.Output.DICT, config='--psm 11')
    draw = ImageDraw.Draw(original)
    translator = GoogleTranslator(source='auto', target=target_lang)

    lines = {}
    for i in range(len(data['text'])):
        txt, conf, h = data['text'][i].strip(), int(data['conf'][i]), data['height'][i]
        # Debug: Filter out noise/table lines misidentified as huge letters
        if conf > 40 and len(txt) > 1 and (h * sy) < (height * 0.1):
            line_idx = data['line_num'][i]
            lines.setdefault(line_idx, []).append(i)

    for word_indices in lines.values():
        sentence = " ".join([data['text'][i] for i in word_indices]).strip()
        if not sentence: continue

        try:
            translated = translator.translate(sentence)
        except:
            translated = sentence

        l = min(data['left'][i] for i in word_indices) * sx
        t = min(data['top'][i] for i in word_indices) * sy
        h_orig = (max(data['top'][i] + data['height'][i] for i in word_indices) - min(data['top'][i] for i in word_indices)) * sy

        f_size = min(int(h_orig * 0.9), 60)
        try:
            font = ImageFont.truetype("arial.ttf", f_size)
        except:
            font = ImageFont.load_default()

        bg = original.getpixel((max(0, int(l)), max(0, int(t))))
        draw.text((l, t), translated, fill=get_text_color(bg), font=font)

    return original

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('files')
        target_lang = request.form.get('language', 'en')
        
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, 'w') as zf:
            for file in files:
                if file.filename == '': continue
                processed_img = process_image(file.read(), target_lang)
                img_io = io.BytesIO()
                processed_img.save(img_io, 'JPEG', quality=90)
                zf.writestr(f"translated_{file.filename}", img_io.getvalue())
        
        zip_io.seek(0)
        return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='translated_maps.zip')
    
    return render_template_string(HTML_INTERFACE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
