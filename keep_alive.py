from flask import Flask
from threading import Thread
import logging

# Suppress Flask logging
logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask('')

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Couple Bot Status</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    background: linear-gradient(135deg, #ff69b4, #ff1493);
                    color: white;
                    margin: 0;
                    padding: 50px;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 30px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    max-width: 500px;
                    margin: 0 auto;
                }
                h1 { color: white; margin-bottom: 20px; }
                .heart { font-size: 2em; animation: pulse 1.5s infinite; }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                .status { 
                    background: rgba(0, 255, 0, 0.2);
                    padding: 10px;
                    border-radius: 10px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="heart">💕</div>
                <h1>Couple Bot is Running!</h1>
                <div class="status">
                    <strong>Status:</strong> Online and ready for love! 💖
                </div>
                <p>Your personal Discord bot for couples is active and monitoring for commands.</p>
                <p><em>Spreading love, one command at a time! 💌</em></p>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Bot is running! 💕'}

# Print routes
print("📡 Registered Flask routes:")
for rule in app.url_map.iter_rules():
    print(f"➡️  {rule.endpoint}: {rule.rule}")

def run():
    """Run Flask server"""
    app.run(host='0.0.0.0', port=5000, debug=False)

def keep_alive():
    """Start Flask server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("💕 Keep-alive server started on port 5000")
