import os

from flask import current_app


def get_upload_root():
	upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

	if os.path.isabs(upload_folder):
		return upload_folder

	return os.path.join(current_app.root_path, upload_folder)
