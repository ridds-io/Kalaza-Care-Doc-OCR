import os
import tempfile

import cv2
import numpy as np
import pypdfium2 as pdfium
from google.cloud import vision
from paddleocr import PaddleOCR

from utils.image_processing import preprocess_image


class OCRService:

    _paddle_ocr = None
    _vision_client = None

    @classmethod
    def _get_provider(cls):
        return os.getenv("OCR_PROVIDER", "paddle").strip().lower()

    @classmethod
    def _fallback_enabled(cls):
        return os.getenv("OCR_ENABLE_FALLBACK", "true").strip().lower() == "true"

    @classmethod
    def _pdf_max_pages(cls):
        return int(os.getenv("OCR_PDF_MAX_PAGES", "10"))

    @classmethod
    def _get_paddle_ocr(cls):
        if cls._paddle_ocr is None:
            cls._paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en"
            )
        return cls._paddle_ocr

    @classmethod
    def _get_vision_client(cls):
        if cls._vision_client is None:
            cls._vision_client = vision.ImageAnnotatorClient()
        return cls._vision_client

    @staticmethod
    def _extract_text_from_paddle_image(image_path):
        image = preprocess_image(image_path)

        if image is None:
            return ""

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            cv2.imwrite(temp_path, image)

            result = OCRService._get_paddle_ocr().ocr(temp_path)

            text = []

            if result:
                for page in result:
                    if page is None:
                        continue
                    for line in page:
                        text.append(line[1][0])

            return "\n".join(text)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @staticmethod
    def _extract_text_from_google_image(image_path):
        with open(image_path, "rb") as f:
            image_content = f.read()

        response = OCRService._get_vision_client().document_text_detection(
            image=vision.Image(content=image_content)
        )

        if response.error.message:
            raise RuntimeError(response.error.message)

        if response.full_text_annotation and response.full_text_annotation.text:
            return response.full_text_annotation.text.strip()

        return ""

    @staticmethod
    def _extract_text_from_google_bytes(image_bytes):
        response = OCRService._get_vision_client().document_text_detection(
            image=vision.Image(content=image_bytes)
        )

        if response.error.message:
            raise RuntimeError(response.error.message)

        if response.full_text_annotation and response.full_text_annotation.text:
            return response.full_text_annotation.text.strip()

        return ""

    @staticmethod
    def _pdf_page_text_with_paddle(pdf_path):
        page_texts = []
        pdf_document = pdfium.PdfDocument(pdf_path)

        try:
            page_count = min(len(pdf_document), OCRService._pdf_max_pages())

            for page_index in range(page_count):
                page = pdf_document[page_index]
                pil_image = page.render(scale=2).to_pil()

                bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    cv2.imwrite(temp_path, bgr)
                    text = OCRService._extract_text_from_paddle_image(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                if text:
                    page_texts.append(f"[Page {page_index + 1}]\n{text}")
        finally:
            pdf_document.close()

        return "\n\n".join(page_texts)

    @staticmethod
    def _pdf_page_text_with_google(pdf_path):
        page_texts = []
        pdf_document = pdfium.PdfDocument(pdf_path)

        try:
            page_count = min(len(pdf_document), OCRService._pdf_max_pages())

            for page_index in range(page_count):
                page = pdf_document[page_index]
                pil_image = page.render(scale=2).to_pil()

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    pil_image.save(temp_path, format="JPEG")
                    with open(temp_path, "rb") as f:
                        image_bytes = f.read()
                    text = OCRService._extract_text_from_google_bytes(image_bytes)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                if text:
                    page_texts.append(f"[Page {page_index + 1}]\n{text}")
        finally:
            pdf_document.close()

        return "\n\n".join(page_texts)

    @staticmethod
    def _run_primary_then_fallback(primary_func, fallback_func):
        text = ""

        try:
            text = primary_func()
        except Exception:
            text = ""

        if text:
            return text

        if OCRService._fallback_enabled():
            return fallback_func()

        return ""

    @staticmethod
    def extract_text(file_path):
        extension = os.path.splitext(file_path)[1].lower()
        provider = OCRService._get_provider()

        is_google = provider in {"google", "gcv", "cloud_vision"}

        if extension == ".pdf":
            if is_google:
                return OCRService._run_primary_then_fallback(
                    lambda: OCRService._pdf_page_text_with_google(file_path),
                    lambda: OCRService._pdf_page_text_with_paddle(file_path)
                )

            return OCRService._run_primary_then_fallback(
                lambda: OCRService._pdf_page_text_with_paddle(file_path),
                lambda: OCRService._pdf_page_text_with_google(file_path)
            )

        if is_google:
            return OCRService._run_primary_then_fallback(
                lambda: OCRService._extract_text_from_google_image(file_path),
                lambda: OCRService._extract_text_from_paddle_image(file_path)
            )

        return OCRService._run_primary_then_fallback(
            lambda: OCRService._extract_text_from_paddle_image(file_path),
            lambda: OCRService._extract_text_from_google_image(file_path)
        )