from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_required

from services.patient_service import PatientService


patients = Blueprint(
    "patients",
    __name__
)


@patients.route("/patients")
@login_required
def patient_list():

    patient_list = PatientService.get_all_patients()

    return render_template(
        "patients/patients.html",
        patients=patient_list
    )


@patients.route("/patients/add", methods=["GET", "POST"])
@login_required
def add_patient():

    if request.method == "POST":

        PatientService.add_patient(request.form)

        flash(
            "Patient Added Successfully",
            "success"
        )

        return redirect(
            url_for("patients.patient_list")
        )

    return render_template(
        "patients/add_patient.html"
    )


@patients.route("/patients/<int:patient_id>")
@login_required
def view_patient(patient_id):

    patient = PatientService.get_patient(patient_id)

    return render_template(
        "patients/patient_profile.html",
        patient=patient
    )


@patients.route("/patients/edit/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):

    patient = PatientService.get_patient(patient_id)

    if request.method == "POST":

        PatientService.update_patient(
            patient_id,
            request.form
        )

        flash(
            "Patient Updated Successfully",
            "success"
        )

        return redirect(
            url_for("patients.patient_list")
        )

    return render_template(
        "patients/edit_patient.html",
        patient=patient
    )


@patients.route("/patients/delete/<int:patient_id>")
@login_required
def delete_patient(patient_id):

    success = PatientService.delete_patient(patient_id)

    if success:

        flash(
            "Patient Deleted Successfully",
            "success"
        )

    else:

        flash(
            "Cannot delete patient because documents are linked.",
            "danger"
        )

    return redirect(
        url_for("patients.patient_list")
    )