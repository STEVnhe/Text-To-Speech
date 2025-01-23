from flask import Flask, request, render_template, url_for
import os
from PyPDF2 import PdfReader
from gtts import gTTS

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/audio'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return "No file part in the request."
    file = request.files['pdf']
    if file.filename == '':
        return "No file selected."
    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            return "The uploaded PDF contains no readable text."

        audio_filename = convert_text_to_audio(text, file.filename)
        audio_url = url_for('static', filename=f'audio/{audio_filename}', _external=False)

        return render_template('index.html', audio_url=audio_url, download_url=audio_url)
    else:
        return "Invalid file format. Please upload a PDF file."

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def convert_text_to_audio(text, original_filename):
    audio_filename = os.path.splitext(original_filename)[0] + '.mp3'
    audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
    tts = gTTS(text)
    tts.save(audio_path)
    return audio_filename

if __name__ == '__main__':
    app.run(debug=True, port=8000)