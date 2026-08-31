import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from extensions import db

from models.document import Document
from models.patient import Patient
from models.category import Category

from services.ocr_service import OCRService
from services.scanner_service import ScannerService
from utils.file_handler import get_upload_root


upload = Blueprint(
    "upload",
    __name__
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "pdf"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


CATEGORY_FOLDER = {

    "Medicine": "medicine",

    "Groceries": "groceries",

    "Office": "office",

    "Patient Details": "patients",

    "Misc": "misc"

}


# ============================================================
# NORMAL DOCUMENT UPLOAD
# ============================================================

@upload.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload_document():

    patients = Patient.query.order_by(
        Patient.patient_name
    ).all()

    categories = Category.query.order_by(
        Category.category_name
    ).all()

    if request.method == "POST":

        title = request.form.get("title")

        patient_id = request.form.get("patient_id")

        category_id = request.form.get("category_id")

        remarks = request.form.get("notes")

        file = request.files.get("document")

        if file is None or file.filename == "":

            flash(
                "Please choose a document.",
                "danger"
            )

            return redirect(request.url)

        if not allowed_file(file.filename):

            flash(
                "Only JPG, JPEG, PNG and PDF files are allowed.",
                "danger"
            )

            return redirect(request.url)

        category = Category.query.get(category_id)

        folder = CATEGORY_FOLDER.get(
            category.category_name,
            "misc"
        )

        upload_path = os.path.join(
            get_upload_root(),
            folder
        )

        os.makedirs(
            upload_path,
            exist_ok=True
        )

        extension = file.filename.rsplit(
            ".",
            1
        )[1].lower()

        stored_filename = secure_filename(
            f"{uuid.uuid4()}.{extension}"
        )

        filepath = os.path.join(
            upload_path,
            stored_filename
        )

        file.save(filepath)

        # ===================================================
        # DOCUMENT SCANNER
        # ===================================================

        if extension in ["jpg", "jpeg", "png"]:

            try:
                ScannerService.scan_document(filepath)
            except Exception as e:
                print("Scanner Error:", e)

        # ===================================================
        # OCR
        # ===================================================

        try:
            ocr_text = OCRService.extract_text(filepath)
        except Exception as e:
            print("OCR Error:", e)
            ocr_text = ""

        document = Document(

            title=title,

            patient_id=patient_id if patient_id else None,

            category_id=category_id,

            uploaded_by=current_user.user_id,

            original_filename=file.filename,

            stored_filename=stored_filename,

            file_path=os.path.join(
                folder,
                stored_filename
            ).replace("\\", "/"),

            file_type=extension,

            file_size=os.path.getsize(filepath),

            remarks=remarks,

            ocr_text=ocr_text,

            upload_date=datetime.now()

        )

        db.session.add(document)

        db.session.commit()

        flash(
            "Document uploaded successfully!",
            "success"
        )

        return redirect(
            url_for("documents.document_list")
        )

    return render_template(

        "upload/upload.html",

        patients=patients,

        categories=categories

    )


# ============================================================
# PHONE CAMERA PAGE
# ============================================================

@upload.route("/scan")
@login_required
def scan():

    return render_template(
        "upload/scan.html"
    )


# ============================================================
# CAMERA IMAGE UPLOAD
# ============================================================

@upload.route(
    "/upload-camera",
    methods=["POST"]
)
@login_required
def upload_camera():

    file = request.files.get("document")

    if file is None or file.filename == "":

        flash(
            "No image selected.",
            "danger"
        )

        return redirect(
            url_for("upload.scan")
        )

    upload_path = os.path.join(
        get_upload_root(),
        "camera"
    )

    os.makedirs(
        upload_path,
        exist_ok=True
    )

    extension = file.filename.rsplit(
        ".",
        1
    )[1].lower()

    filename = secure_filename(
        f"{uuid.uuid4()}.{extension}"
    )

    filepath = os.path.join(
        upload_path,
        filename
    )

    file.save(filepath)

    # ===================================================
    # DOCUMENT SCANNER
    # ===================================================

    try:
        ScannerService.scan_document(filepath)
    except Exception as e:
        print("Scanner Error:", e)

    # ===================================================
    # OCR
    # ===================================================

    try:
        ocr_text = OCRService.extract_text(filepath)
    except Exception as e:
        print("OCR Error:", e)
        ocr_text = ""

    document = Document(

        title="Camera Scan",

        patient_id=None,

        category_id=1,

        uploaded_by=current_user.user_id,

        original_filename=file.filename,

        stored_filename=filename,

        file_path=os.path.join(
            "camera",
            filename
        ).replace("\\", "/"),

        file_type=extension,

        file_size=os.path.getsize(filepath),

        remarks="Captured using phone camera",

        ocr_text=ocr_text,

        upload_date=datetime.now()

    )

    db.session.add(document)

    db.session.commit()

    flash(
        "Document scanned successfully!",
        "success"
    )

    return redirect(
        url_for("documents.document_list")
    )