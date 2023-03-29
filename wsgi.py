"""Serves the app"""


from os import getenv
from os.path import join as join_path
from app.index import app as flask_app
from flask_assets import Environment, Bundle

# allows run-time compilation of scss to css
assets = Environment(flask_app)
assets.url = flask_app.static_url_path
scss = Bundle(join_path("scss", "_custom_bootstrap.scss"), filters="pyscss", output="all.css")
assets.register("scss_all", scss)


if __name__ == "__main__":
    port = int(getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
