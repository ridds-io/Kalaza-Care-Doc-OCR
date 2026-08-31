from models.document import Document
from models.patient import Patient
from models.category import Category
from extensions import db


class DashboardService:

    @staticmethod
    def get_dashboard_stats():

        total_documents = Document.query.count()

        total_patients = Patient.query.count()

        medicine = (
            db.session.query(Document)
            .join(Category)
            .filter(Category.category_name == "Medicine")
            .count()
        )

        groceries = (
            db.session.query(Document)
            .join(Category)
            .filter(Category.category_name == "Groceries")
            .count()
        )

        office = (
            db.session.query(Document)
            .join(Category)
            .filter(Category.category_name == "Office")
            .count()
        )

        patient_details = (
            db.session.query(Document)
            .join(Category)
            .filter(Category.category_name == "Patient Details")
            .count()
        )

        misc = (
            db.session.query(Document)
            .join(Category)
            .filter(Category.category_name == "Misc")
            .count()
        )

        recent_uploads = (
            Document.query
            .order_by(Document.upload_date.desc())
            .limit(5)
            .all()
        )

        return {

            "total_documents": total_documents,

            "total_patients": total_patients,

            "medicine": medicine,

            "groceries": groceries,

            "office": office,

            "patient_details": patient_details,

            "misc": misc,

            "recent_uploads": recent_uploads
        }