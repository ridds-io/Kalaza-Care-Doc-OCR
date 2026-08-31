from flask import Blueprint, render_template, request
from flask_login import login_required

from extensions import db
from models.document import Document


search = Blueprint(
    "search",
    __name__
)


@search.route("/search", methods=["GET",])
@login_required
def search_documents():

    query = request.args.get("q", "").strip()

    documents = []

    if query:

        search_term = f"%{query}%"

        documents = Document.query.filter(
            db.or_(
                Document.title.ilike(search_term),
                Document.ocr_text.ilike(search_term),
                Document.original_filename.ilike(search_term)
            )
        ).order_by(
            Document.upload_date.desc()
        ).all()

    return render_template(
        "search/search.html",
        documents=documents,
        query=query
    )