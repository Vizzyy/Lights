import subprocess
from flask import *

app = Flask(__name__)
app.config["DEBUG"] = True
p = None

@app.route('/arrange/<section>', methods=['GET'])
def home(section):
    global p
    if section == "clear":
        print("Killing child process!")
        p.kill()
    else:
        p = subprocess.Popen("exec python child_process.py " + section, shell=True)
    return "<h1>Indoor Lights!</h1><p>"+str(section)+"</p>"

@app.route('/custom', methods=['GET'])
def custom():
    colorValue = request.args.get('colorValue').lstrip("#")
    rgb = tuple(int(colorValue[i:i+2], 16) for i in (0, 2, 4))
    print('RGB =', rgb)

    return "200"

@app.route('/static/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')