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
    p = subprocess.Popen("exec python3 " + LIGHTS_HOME + "child_process.py " + section, shell=True)
    return "<h1>"+get_context()+" Lights!</h1><p>" + str(section) + "</p>"


@bp.route('/status', methods=['GET'])
def status():
    global p
    if p is not None:
        state = f"running [{p.args}]." if p.poll() is None else "finished running."
        return f"Subprocess {state}"
    else:
        return "No subprocess initialized."


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
            "exec python3 " + LIGHTS_HOME + "child_process.py custom "
            + str(rgb[0]) + " " + str(rgb[1]) + " " + str(rgb[2]),
            shell=True)

    return render_template(FILE_NAME_CUSTOM, context=get_context())


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@bp.route('/')
def render_home():
    return render_template('home.html', context=get_context())


app.register_blueprint(bp, url_prefix=get_context())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
