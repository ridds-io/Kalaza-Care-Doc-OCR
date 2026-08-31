from flask import (
    Flask,
    redirect,
    url_for,
    send_from_directory
)

import os

from config import Config

from extensions import db, login_manager
from utils.file_handler import get_upload_root

# Models
from models.user import User

# Blueprints
from routes.auth import auth
from routes.dashboard import dashboard
from routes.patients import patients
from routes.upload import upload
from routes.documents import documents
from routes.search import search
from routes.reports import reports
from routes.settings import settings


app = Flask(__name__)


# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

app.config.from_object(Config)


# ----------------------------------------------------
# Initialize Extensions
# ----------------------------------------------------

db.init_app(app)
login_manager.init_app(app)


# ----------------------------------------------------
# Flask Login
# ----------------------------------------------------

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# ----------------------------------------------------
# Register Blueprints
# ----------------------------------------------------

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(patients)
app.register_blueprint(upload)
app.register_blueprint(documents)
app.register_blueprint(search)
app.register_blueprint(reports)
app.register_blueprint(settings)


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.route("/")
def home():

    return redirect(
        url_for("auth.login")
    )


# ----------------------------------------------------
# Serve Uploaded Files
# ----------------------------------------------------

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    return send_from_directory(

        get_upload_root(),

        filename

    )


# ----------------------------------------------------
# Create Database Tables
# ----------------------------------------------------

with app.app_context():

    db.create_all()


# ----------------------------------------------------
# Run App
# ----------------------------------------------------

if __name__ == "__main__":

    debug_mode = os.getenv(
        "FLASK_DEBUG",
        "false"
    ).lower() == "true"

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=debug_mode

    )