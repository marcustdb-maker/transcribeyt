from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    url = data.get('url', '')
    return jsonify({
        "transcription": f"✅ Transcrição simulada do vídeo:\n\n{url}\n\n[Transcrição completa seria exibida aqui. Versão de teste funcionando!]",
        "success": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
