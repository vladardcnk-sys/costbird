from flask import Flask
from core.config import Config
from routes.site import site
from routes.api import api

app = Flask(__name__)
app.config.from_object(Config)

# Blueprints
app.register_blueprint(site)
app.register_blueprint(api)


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=5000)
