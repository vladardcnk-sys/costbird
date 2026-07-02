from flask import Flask
from core.config import Config
from core.database import init_db
from routes.site import site
from routes.api import api
from routes.auth import auth
from routes.cabinet import cabinet

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

app.register_blueprint(site)
app.register_blueprint(api)
app.register_blueprint(auth)
app.register_blueprint(cabinet)

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=5000)
