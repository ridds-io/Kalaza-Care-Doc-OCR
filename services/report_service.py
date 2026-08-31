import calendar
import re
from datetime import date, datetime

from sqlalchemy import func

from extensions import db
from models.category import Category
from models.document import Document


class ReportService:

    AMOUNT_PATTERNS = [
        r"(?:total|grand\s*total|amount\s*paid|amt)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
        r"(?:mrp)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
        r"(?:rs\.?|inr|₹)\s*([0-9,]+(?:\.[0-9]{1,2})?)",
    ]

    @staticmethod
    def is_last_five_days_of_month(today=None):
        today = today or date.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        return today.day >= (last_day - 4)

    @staticmethod
    def _month_bounds(year, month):
        start_date = datetime(year, month, 1)

        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return start_date, end_date

    @staticmethod
    def _extract_amount(text):
        if not text:
            return None

        normalized = " ".join(text.split())

        for pattern in ReportService.AMOUNT_PATTERNS:
            match = re.search(pattern, normalized, flags=re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", "")
                try:
                    return float(value)
                except ValueError:
                    return None

        return None

    @staticmethod
    def get_monthly_recap(year, month):
        start_date, end_date = ReportService._month_bounds(year, month)

        documents = (
            Document.query
            .filter(Document.upload_date >= start_date)
            .filter(Document.upload_date < end_date)
            .order_by(Document.upload_date.desc())
            .all()
        )

        category_stats_raw = (
            db.session.query(
                Category.category_name,
                func.count(Document.document_id)
            )
            .join(Document, Document.category_id == Category.category_id)
            .filter(Document.upload_date >= start_date)
            .filter(Document.upload_date < end_date)
            .group_by(Category.category_name)
            .order_by(func.count(Document.document_id).desc())
            .all()
        )

        category_stats = [
            {
                "category_name": category_name,
                "count": count,
            }
            for category_name, count in category_stats_raw
        ]

        total_amount = 0.0
        docs_with_amount = 0
        monthly_items = []

        for doc in documents:
            amount = ReportService._extract_amount(doc.ocr_text)

            if amount is not None:
                total_amount += amount
                docs_with_amount += 1

            monthly_items.append(
                {
                    "document": doc,
                    "amount": amount,
                }
            )

        linked_to_patient = sum(1 for d in documents if d.patient_id is not None)

        return {
            "year": year,
            "month": month,
            "month_label": start_date.strftime("%B %Y"),
            "total_documents": len(documents),
            "linked_to_patient": linked_to_patient,
            "without_patient": len(documents) - linked_to_patient,
            "total_amount": round(total_amount, 2),
            "documents_with_amount": docs_with_amount,
            "category_stats": category_stats,
            "items": monthly_items,
            "period_start": start_date,
            "period_end": end_date,
        }
