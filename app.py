import os
import subprocess
from flask import *
from config import *
# from systemd import journal
import logging

LIGHTS_HOME = get_home()
app = Flask(__name__)
app.config["DEBUG"] = True
logger = logging.getLogger('Lights')
# journald_handler = journal.JournalHandler()
# logger.addHandler(journald_handler)
p = None


@app.route('/arrange/<section>', methods=['GET'])
def home(section):
    global p
    if p is not None:
        p.kill()
    p = subprocess.Popen("exec python " + LIGHTS_HOME + "child_process.py " + section, shell=True)
    return "<h1>Indoor Lights!</h1><p>" + str(section) + "</p>"


@app.route('/custom', methods=['GET'])
def custom():
    colorValue = request.args.get('colorValue').lstrip("#")
    rgb = tuple(int(colorValue[i:i + 2], 16) for i in (0, 2, 4))
    logger.info('RGB =', rgb)

    return "200"


@app.route('/static/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
