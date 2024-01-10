from flask import Flask, redirect, url_for, current_app
from app.config import config
from flask_login import LoginManager
from json import JSONEncoder
from enum import Enum
# Importa tus Blueprints y sesiones
from routes.auth import auth_blueprint
from routes.home import home_blueprint
from routes.compras import compras_blueprint
from routes.reportes import reportes_blueprint
from routes.api_routes import api_blueprint, api_actualizacion
from routes.configuraciones import configuraciones_blueprint

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value # or obj.value, depending on what you want to serialize
        return super().default(self, obj)

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_object(config['development_postgres'])
app.json_encoder = CustomJSONEncoder()
login_manager = LoginManager(app)

# Registra tus Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(compras_blueprint)
app.register_blueprint(configuraciones_blueprint)
app.register_blueprint(reportes_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(api_actualizacion)

app.make_default_options_response

@login_manager.user_loader
def load_user(id):
    from models.model_user import ModelUser
    user = ModelUser.get_by_id(id)  
    return user

def status_401(error):
    return redirect(url_for('auth.login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>"

if __name__ == '__main__':
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(port=8000)  # Cambia el número "8000" al puerto que desees.
