import os
import subprocess
from flask import *
from config import *
import logging

LIGHTS_HOME = get_home()
app = Flask(__name__)
app.config["DEBUG"] = True

bp = Blueprint('application_context', __name__, template_folder='templates')

logger = logging.getLogger('Lights')
p = None


@bp.route('/arrange/<section>', methods=['GET'])
def home(section):
    global p
    if p is not None:
        p.kill()
    p = subprocess.Popen("exec python " + LIGHTS_HOME + "child_process.py " + section, shell=True)
    return "<h1>Indoor Lights!</h1><p>" + str(section) + "</p>"


@bp.route('/custom', methods=['GET'])
def custom():
    try:
        colorValue = request.args.get('colorValue').lstrip("#")
        rgb = tuple(int(colorValue[i:i + 2], 16) for i in (0, 2, 4))
        logger.info('RGB =', rgb)
    except Exception:
        print("oops")
    return "200"


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@bp.route('/')
def render_home():
    return render_template('home.html', context=get_context())


app.register_blueprint(bp, url_prefix=get_context())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
