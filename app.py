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
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
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
        
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            font-size: 13px;
            color: #1565c0;
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
        
        <div class="info-box">
            💡 <strong>Tip:</strong> If YouTube videos don't work, try videos from other platforms like Vimeo, Dailymotion, Twitter, or TikTok!
        </div>
        
        <form id="download-form">
            <div class="form-group">
                <label for="url">Video URL</label>
                <input type="url" id="url" name="url" placeholder="Paste video URL here..." required>
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
        
        # Enhanced yt-dlp options to bypass bot detection
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                    'player_skip': ['webpage', 'js'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            formats = info.get('formats', [])
            
            # Filter formats based on user selection
            if format_type == 'audio':
                valid_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]
            else:
                valid_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('url')]
                if format_type != 'webm':
                    valid_formats = [f for f in valid_formats if f.get('ext') in ['mp4', 'm4a']]
                
                if quality != 'best':
                    target_height = int(quality)
                    valid_formats = [f for f in valid_formats if f.get('height', 0) <= target_height]
            
            # Fallback to any available format
            if not valid_formats:
                valid_formats = [f for f in formats if f.get('url')]
            
            if not valid_formats:
                return jsonify({'success': False, 'error': 'No downloadable formats found for this video'})
            
            # Select best format
            if format_type == 'audio':
                best_format = max(valid_formats, key=lambda x: x.get('abr', 0) or 0)
            else:
                best_format = max(valid_formats, key=lambda x: (x.get('height', 0) or 0, x.get('tbr', 0) or 0))
            
            download_url = best_format.get('url')
            
            if not download_url:
                return jsonify({'success': False, 'error': 'Could not extract download URL'})
            
            return jsonify({
                'success': True,
                'title': title,
                'download_url': download_url
            })
            
    except yt_dlp.utils.DownloadError as e:
        error_str = str(e)
        if 'Sign in to confirm' in error_str or 'bot' in error_str.lower():
            return jsonify({
                'success': False, 
                'error': 'YouTube is blocking this request. Try: 1) A different video 2) Videos from other platforms (Vimeo, Twitter, TikTok, etc.)'
            })
        return jsonify({'success': False, 'error': f'Download error: {error_str}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)