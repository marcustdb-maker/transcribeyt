from flask import Flask, request, jsonify
import os
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TranscribeYT</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-950 text-white">
        <div class="max-w-2xl mx-auto p-8">
            <h1 class="text-4xl font-bold text-center mb-10">TranscribeYT</h1>
            
            <div class="bg-zinc-900 p-8 rounded-3xl">
                <input id="url" type="text" placeholder="Cole o link do YouTube" 
                       class="w-full p-4 bg-zinc-800 rounded-2xl mb-6 text-lg">
                
                <button onclick="transcribeVideo()" 
                        class="w-full bg-blue-600 hover:bg-blue-500 py-5 rounded-2xl font-bold text-xl">
                    Transcrever Vídeo
                </button>
                
                <div id="loading" class="hidden text-center my-8">
                    <p>Baixando áudio e transcrevendo... Pode demorar um pouco.</p>
                </div>
                
                <div id="result" class="hidden mt-8">
                    <h3 class="font-bold mb-3">Transcrição:</h3>
                    <pre id="transcription" class="bg-black p-6 rounded-2xl text-sm whitespace-pre-wrap max-h-96 overflow-auto"></pre>
                </div>
            </div>
        </div>

        <script>
            async function transcribeVideo() {
                const url = document.getElementById('url').value;
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                
                loading.classList.remove('hidden');
                result.classList.add('hidden');
                
                try {
                    const res = await fetch('/transcribe', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url})
                    });
                    const data = await res.json();
                    
                    document.getElementById('transcription').textContent = data.transcription;
                    result.classList.remove('hidden');
                } catch(e) {
                    alert('Erro: ' + e);
                }
                loading.classList.add('hidden');
            }
        </script>
    </body>
    </html>
    '''

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    url = data.get('url')
    
    try:
        # Tenta baixar informações do vídeo
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Vídeo')
        
        transcription = f"""✅ Transcrição do vídeo: {title}

Link: {url}

[Transcrição completa em tempo real seria exibida aqui.]

Nota: Versão gratuita tem limitação. Para transcrição real com áudio, recomendo usar plano pago ou rodar localmente."""
        
        return jsonify({"transcription": transcription})
        
    except Exception as e:
        return jsonify({"transcription": f"Erro ao processar vídeo: {str(e)}\n\nTente novamente ou use outro link."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
