from datetime import date

from flask import Blueprint
from flask import render_template

from flask_login import login_required

from sqlalchemy import func

from models.document import Document
from models.patient import Patient
from models.category import Category


dashboard = Blueprint(
    "dashboard",
    __name__
)


@dashboard.route("/dashboard")
@login_required
def home():

    total_documents = Document.query.count()

    total_patients = Patient.query.count()

    total_categories = Category.query.count()

    uploads_today = Document.query.filter(
        func.date(Document.upload_date) == date.today()
    ).count()

    return render_template(
        "dashboard/dashboard.html",
        total_documents=total_documents,
        total_patients=total_patients,
        total_categories=total_categories,
        uploads_today=uploads_today
    )