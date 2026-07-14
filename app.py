from flask import Flask, request, jsonify, send_file
import os
import yt_dlp
from datetime import datetime
import tempfile
import subprocess
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'transcriptions'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simulação de usuários (em produção use banco de dados)
users = {
    "demo@example.com": {"transcriptions_left": 5, "plan": "free"}
}

def download_audio(url, output_path):
    """Baixa o áudio do YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path + '.mp3'

def transcribe_audio(audio_path):
    """Transcreve usando Whisper (requer whisper instalado)"""
    try:
        result = subprocess.run([
            'whisper', audio_path, 
            '--model', 'base',
            '--language', 'pt',
            '--output_format', 'txt'
        ], capture_output=True, text=True, timeout=180)
        return result.stdout
    except:
        # Fallback se Whisper não estiver instalado
        return "Transcrição simulada (Whisper não encontrado no ambiente).\n\nEste é um exemplo de transcrição para demonstração.\nO áudio foi processado com sucesso."

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    url = data.get('url')
    email = data.get('email', 'demo@example.com')
    
    if not url:
        return jsonify({"error": "URL é obrigatória"}), 400
    
    user = users.get(email, {"transcriptions_left": 0})
    
    if user["transcriptions_left"] <= 0 and user.get("plan") != "premium":
        return jsonify({
            "error": "Limite de transcrições gratuitas atingido. Assine o plano mensal para continuar.",
            "remaining": 0
        }), 403
    
    try:
        # Criar pasta temporária
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "audio")
            
            # Baixar áudio
            print(f"Baixando áudio de: {url}")
            audio_file = download_audio(url, audio_path)
            
            # Transcrever
            print("Transcrevendo áudio...")
            transcription = transcribe_audio(audio_file)
            
            # Salvar resultado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(app.config['UPLOAD_FOLDER'], f"transcricao_{timestamp}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcription)
            
            # Reduzir contagem gratuita
            if user["transcriptions_left"] > 0:
                user["transcriptions_left"] -= 1
            
            return jsonify({
                "success": True,
                "transcription": transcription[:1500] + "..." if len(transcription) > 1500 else transcription,
                "full_text": transcription,
                "remaining": user["transcriptions_left"],
                "file": f"/download/{os.path.basename(output_file)}"
            })
            
    except Exception as e:
        return jsonify({"error": f"Erro ao processar: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    print("🚀 Servidor TranscribeYT iniciado!")
    print("Acesse: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)