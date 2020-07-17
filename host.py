import os
import subprocess
from flask import *
from config import *
import logging
import rpyc
from strip_functions import *


LIGHTS_HOME = SOURCE_PATH
app = Flask(__name__)
app.config["DEBUG"] = True

bp = Blueprint('application_context', __name__, template_folder='templates')

logger = logging.getLogger('Lights')
p = None
c = rpyc.connect("localhost", REMOTE_PORT)


@bp.route('/arrange/<section>', methods=['GET'])
def home(section):
    arrangement(c.root.exposed_strip, section)
    return "<h1>Indoor Lights!</h1><p>" + str(section) + "</p>"


@bp.route('/custom/', methods=['GET'])
def custom():
    if request.args.get('colorValue'):
        color_value = request.args.get('colorValue').lstrip("#")
        print(color_value)
        rgb = tuple(int(color_value[i:i + 2], 16) for i in (0, 2, 4))
        print(rgb)
        global p
        if p is not None:
            p.kill()
        p = subprocess.Popen(
            "exec python " + LIGHTS_HOME + "child_process.py custom "
            + str(rgb[1]) + " " + str(rgb[0]) + " " + str(rgb[2]),
            shell=True)

    return render_template(FILE_NAME_CUSTOM, context=CONTEXT_PATH)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@bp.route('/')
def render_home():
    return render_template('home.html', context=CONTEXT_PATH)


app.register_blueprint(bp, url_prefix=CONTEXT_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=WEBSERVER_PORT)
