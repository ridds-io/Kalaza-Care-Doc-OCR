import os
from datetime import datetime
from werkzeug.utils import secure_filename

from extensions import db
from models.document import Document


class UploadService:

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "pdf"
    }

    @staticmethod
    def allowed_file(filename):

        return (
            "." in filename and
            filename.rsplit(".", 1)[1].lower()
            in UploadService.ALLOWED_EXTENSIONS
        )

    @staticmethod
    def save_document(file,
                      title,
                      patient_id,
                      category_id,
                      notes):

        extension = file.filename.rsplit(".", 1)[1].lower()

        filename = (
            datetime.now().strftime("%Y%m%d_%H%M%S")
            + "."
            + extension
        )

        filename = secure_filename(filename)

        upload_folder = os.path.join(
            "uploads",
            str(category_id)
        )

        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(
            upload_folder,
            filename
        )

        file.save(filepath)

        document = Document(

            title=title,

            filename=filename,

            filepath=filepath,

            patient_id=patient_id if patient_id else None,

            category_id=category_id,

            notes=notes

        )

        db.session.add(document)
        db.session.commit()

        return document