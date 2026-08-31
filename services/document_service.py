from models.document import Document


class DocumentService:

    @staticmethod
    def get_all_documents():
        return (
            Document.query
            .order_by(Document.document_id.desc())
            .all()
        )

    @staticmethod
    def get_document(document_id):
        return Document.query.get_or_404(document_id)