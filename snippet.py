from flask import Flask, render_template, jsonify, request
import subprocess
import threading
import os
import time

app = Flask(__name__)

def run_process():
    output = []
    try:
        # Schritt 1: Git Clone (wenn nicht vorhanden)
        if not os.path.exists('Kitty-Tools'):
            proc = subprocess.Popen(['git', 'clone', 'https://github.com/CPScript/Kitty-Tools'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                    text=True, bufsize=1)
            for line in proc.stdout:
                output.append(line.strip())
                time.sleep(0.1) # Verzögerung zum Streamen
            proc.wait()
        
        # Schritt 2: In Verzeichnis wechseln und starten
        os.chdir('Kitty-Tools')
        proc = subprocess.Popen(['python', 'main.py'], 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                text=True, bufsize=1)
        for line in proc.stdout:
            output.append(line.strip())
            time.sleep(0.1)
        proc.wait()
        
        output.append("Fertigstellung.")
    except Exception as e:
        output.append(f"Fehler: {str(e)}")
    finally:
        return output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_script():
    # Startet den Prozess in einem Thread, damit der Server nicht blockiert
    def background_task():
        global last_output
        last_output = run_process()
    
    thread = threading.Thread(target=background_task)
    thread.start()
    return jsonify({"status": "gestartet"})

@app.route('/status')
def get_status():
    return jsonify({"output": getattr(globals().get('last_output'), '__dict__', []) or []})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
