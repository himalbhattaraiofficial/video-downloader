from flask import Flask, render_template_string, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Downloader</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
            font-size: 14px;
        }
        
        input[type="text"], input[type="url"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .radio-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .radio-option {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .radio-option input[type="radio"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .radio-option label {
            margin: 0;
            cursor: pointer;
            font-weight: normal;
        }
        
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .spinner {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .spinner-circle {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner-text {
            margin-top: 10px;
            color: #666;
            font-size: 14px;
        }
        
        .status-message {
            margin-top: 15px;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: 500;
            display: none;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .download-link {
            display: none;
            margin-top: 15px;
            text-align: center;
        }
        
        .download-link a {
            display: inline-block;
            padding: 12px 30px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .download-link a:hover {
            background: #218838;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 25px;
            }
            
            h1 {
                font-size: 24px;
            }
            
            .radio-group {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Video Downloader</h1>
        <p class="subtitle">Download videos from YouTube and other platforms</p>
        
        <form id="download-form">
            <div class="form-group">
                <label for="url">Video URL</label>
                <input type="url" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
            </div>
            
            <div class="form-group">
                <label>Quality</label>
                <div class="radio-group">
                    <div class="radio-option">
                        <input type="radio" id="best" name="quality" value="best" checked>
                        <label for="best">Best</label>
                    </div>
                    <div class="radio-option">
                        <input type="radio" id="720p" name="quality" value="720">
                        <label for="720p">720p</label>
                    </div>
                    <div class="radio-option">
                        <input type="radio" id="480p" name="quality" value="480">
                        <label for="480p">480p</label>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label>Format</label>
                <div class="radio-group">
                    <div class="radio-option">
                        <input type="radio" id="mp4" name="format" value="mp4" checked>
                        <label for="mp4">MP4 (Video)</label>
                    </div>
                    <div class="radio-option">
                        <input type="radio" id="webm" name="format" value="webm">
                        <label for="webm">WebM (Video)</label>
                    </div>
                    <div class="radio-option">
                        <input type="radio" id="audio" name="format" value="audio">
                        <label for="audio">Audio Only</label>
                    </div>
                </div>
            </div>
            
            <button type="submit" id="download-btn">Get Download Link</button>
        </form>
        
        <div class="spinner" id="spinner">
            <div class="spinner-circle"></div>
            <div class="spinner-text">Processing your request...</div>
        </div>
        
        <div class="status-message" id="status-message"></div>
        <div class="download-link" id="download-link"></div>
    </div>
    
    <script>
        document.getElementById('download-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('download-btn');
            const spinner = document.getElementById('spinner');
            const statusMessage = document.getElementById('status-message');
            const downloadLink = document.getElementById('download-link');
            
            btn.disabled = true;
            spinner.style.display = 'block';
            statusMessage.style.display = 'none';
            downloadLink.style.display = 'none';
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('Ready to download: ' + result.title, 'success');
                    showDownloadLink(result.download_url, result.title);
                } else {
                    showStatus('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
                spinner.style.display = 'none';
            }
        });
        
        function showStatus(message, type) {
            const statusMessage = document.getElementById('status-message');
            statusMessage.className = 'status-message status-' + type;
            statusMessage.textContent = message;
            statusMessage.style.display = 'block';
        }
        
        function showDownloadLink(url, title) {
            const downloadLink = document.getElementById('download-link');
            downloadLink.innerHTML = `<a href="${url}" download="${title}" target="_blank">⬇️ Download Video</a>`;
            downloadLink.style.display = 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/info', methods=['POST'])
def get_info():
    try:
        data = request.json
        url = data.get('url')
        quality = data.get('quality', 'best')
        format_type = data.get('format', 'mp4')
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'})
        
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs']
                }
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            formats = info.get('formats', [])
            
            if format_type == 'audio':
                valid_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]
            else:
                valid_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('url')]
                if quality != 'best':
                    valid_formats = [f for f in valid_formats if f.get('height', 0) <= int(quality)]
            
            if not valid_formats:
                valid_formats = [f for f in formats if f.get('url')]
            
            if not valid_formats:
                return jsonify({'success': False, 'error': 'No downloadable formats found'})
            
            if format_type == 'audio':
                best_format = max(valid_formats, key=lambda x: x.get('abr', 0))
            else:
                best_format = max(valid_formats, key=lambda x: x.get('height', 0))
            
            download_url = best_format.get('url')
            
            if not download_url:
                return jsonify({'success': False, 'error': 'Could not extract download URL'})
            
            return jsonify({
                'success': True,
                'title': title,
                'download_url': download_url
            })
            
    except Exception as e:
        error_msg = str(e)
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg:
            return jsonify({'success': False, 'error': 'YouTube bot check. Try again in a moment.'})
        return jsonify({'success': False, 'error': error_msg})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)