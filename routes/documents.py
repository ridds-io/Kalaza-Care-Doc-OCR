import os

from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    redirect,
    url_for,
    flash
)

from flask_login import login_required

from extensions import db

from models.document import Document
from utils.file_handler import get_upload_root


documents = Blueprint(
    "documents",
    __name__
)


# ----------------------------------------------------
# DOCUMENT LIST
# ----------------------------------------------------

@documents.route("/documents")
@login_required
def document_list():

    docs = Document.query.order_by(
        Document.document_id.desc()
    ).all()

    return render_template(
        "documents/documents.html",
        documents=docs
    )


# ----------------------------------------------------
# VIEW DOCUMENT
# ----------------------------------------------------

@documents.route("/documents/view/<int:document_id>")
@login_required
def view_document(document_id):

    document = Document.query.get_or_404(document_id)

    from services.summary_service import SummaryService

    summary = SummaryService.extract_summary(
        document.ocr_text
    )

    return render_template(
        "documents/view_document.html",
        document=document,
        summary=summary
    )


# ----------------------------------------------------
# DOWNLOAD DOCUMENT
# ----------------------------------------------------

@documents.route("/documents/download/<int:document_id>")
@login_required
def download_document(document_id):

    document = Document.query.get_or_404(document_id)

    upload_folder = os.path.join(
        get_upload_root()
    )

    return send_from_directory(
        upload_folder,
        document.file_path,
        as_attachment=True,
        download_name=document.original_filename
    )


# ----------------------------------------------------
# DELETE DOCUMENT
# ----------------------------------------------------

@documents.route("/documents/delete/<int:document_id>")
@login_required
def delete_document(document_id):

    document = Document.query.get_or_404(document_id)

    full_path = os.path.join(
        get_upload_root(),
        document.file_path
    )

    # Delete physical file
    if os.path.exists(full_path):
        os.remove(full_path)

    # Delete database record
    db.session.delete(document)
    db.session.commit()

    flash(
        "Document deleted successfully.",
        "success"
    )

    return redirect(
        url_for("documents.document_list")
    )