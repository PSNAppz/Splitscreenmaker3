

from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import *
from flask import Flask
import subprocess
from flask import Flask
import subprocess

app = Flask(__name__)








@app.route('/')
def index():
    with open('index.html') as f:
        return f.read()

@app.route('/run_script', methods=['POST'])
def run_script():
    subprocess.run(['python', 'script.py'])
    return 'Script executed successfully'

if __name__ == '__main__':
    app.run()




