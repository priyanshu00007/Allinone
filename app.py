from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import pytesseract
from transformers import pipeline
import pyttsx3
import os
from elevenlabs import ElevenLabs  # Requires API key
from threading import Thread

app = Flask(__name__)
elevenlabs_client = ElevenLabs(api_key="YOUR_API_KEY")  # Replace with your key
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        file = request.files['file']
        file_path = f"uploads/{file.filename}"
        file.save(file_path)

        # Extract text
        text = extract_text_from_pdf(file_path)
        if not text:  # If text extraction fails, try OCR
            text = perform_ocr(file_path)

        # Summarize (optional)
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

        # Generate audio
        voice = request.form.get('voice', 'default')
        speed = int(request.form.get('speed', 150))
        audio_path = text_to_speech(text, voice, speed)

        return jsonify({
            'text': summary,  # or full text if preferred
            'audio': f"/audio/{os.path.basename(audio_path)}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(f"audio/{filename}")

@app.route('/get_voices')
def get_voices():
    # Example with ElevenLabs voices (replace with your logic)
    voices = elevenlabs_client.voices.get_all()
    return jsonify([{'id': v.voice_id, 'name': v.name} for v in voices])

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def perform_ocr(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += pytesseract.image_to_string(img)
    return text

def text_to_speech(text, voice, speed):
    output_path = f"audio/output_{os.getpid()}.mp3"
    if voice == 'default':  # Use pyttsx3 for offline
        engine = pyttsx3.init()
        engine.setProperty('rate', speed)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    else:  # Use ElevenLabs for premium voices
        audio = elevenlabs_client.generate(text=text, voice=voice)
        with open(output_path, "wb") as f:
            f.write(audio)
    return output_path

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('audio', exist_ok=True)
    app.run(debug=True)