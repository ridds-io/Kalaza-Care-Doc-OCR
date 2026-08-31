from extensions import db
from models.patient import Patient


class PatientService:

    @staticmethod
    def get_all_patients():
        return Patient.query.order_by(Patient.patient_name).all()

    @staticmethod
    def add_patient(data):

        patient = Patient(
            patient_name=data["patient_name"],
            age=data["age"] or None,
            gender=data["gender"],
            phone=data["phone"],
            address=data["address"],
            notes=data["notes"]
        )

        db.session.add(patient)
        db.session.commit()

        return patient

    @staticmethod
    def get_patient(patient_id):
        return Patient.query.get_or_404(patient_id)

    @staticmethod
    def update_patient(patient_id, data):

        patient = Patient.query.get_or_404(patient_id)

        patient.patient_name = data["patient_name"]
        patient.age = data["age"] or None
        patient.gender = data["gender"]
        patient.phone = data["phone"]
        patient.address = data["address"]
        patient.notes = data["notes"]

        db.session.commit()

        return patient

    @staticmethod
    def delete_patient(patient_id):

        patient = Patient.query.get_or_404(patient_id)

        if patient.documents:
            return False

        db.session.delete(patient)
        db.session.commit()

        return True