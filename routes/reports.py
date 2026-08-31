from datetime import date
import csv
import io

from flask import Blueprint, render_template, request, make_response
from flask_login import login_required

from models.document import Document
from models.patient import Patient
from models.category import Category
from services.report_service import ReportService


reports = Blueprint(
    "reports",
    __name__
)


@reports.route("/reports")
@login_required
def reports_page():

    total_documents = Document.query.count()

    total_patients = Patient.query.count()

    total_categories = Category.query.count()

    recent_documents = Document.query.order_by(
        Document.upload_date.desc()
    ).limit(10).all()

    month_param = request.args.get("month", "").strip()

    today = date.today()
    selected_year = today.year
    selected_month = today.month

    if month_param:
        try:
            selected_year, selected_month = map(int, month_param.split("-"))
        except ValueError:
            selected_year = today.year
            selected_month = today.month

    monthly_recap = ReportService.get_monthly_recap(
        selected_year,
        selected_month
    )

    recap_window_open = ReportService.is_last_five_days_of_month(today)

    if recap_window_open:
        recap_hint = "You are in the last 5 days of this month. This recap will continue to update until month-end."
    else:
        recap_hint = "Monthly recap can be finalized in the last 5 days of the month. You can still preview any month here."

    return render_template(
        "reports/reports.html",
        total_documents=total_documents,
        total_patients=total_patients,
        total_categories=total_categories,
        recent_documents=recent_documents,
        monthly_recap=monthly_recap,
        selected_month=f"{selected_year:04d}-{selected_month:02d}",
        recap_window_open=recap_window_open,
        recap_hint=recap_hint
    )


@reports.route("/reports/monthly-csv")
@login_required
def export_monthly_csv():
    month_param = request.args.get("month", "").strip()

    today = date.today()
    year = today.year
    month = today.month

    if month_param:
        try:
            year, month = map(int, month_param.split("-"))
        except ValueError:
            year = today.year
            month = today.month

    recap = ReportService.get_monthly_recap(year, month)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Monthly Recap", recap["month_label"]])
    writer.writerow(["Total Documents", recap["total_documents"]])
    writer.writerow(["Documents With Amount", recap["documents_with_amount"]])
    writer.writerow(["Total Amount", f"{recap['total_amount']:.2f}"])
    writer.writerow(["Linked To Patients", recap["linked_to_patient"]])
    writer.writerow(["Without Patient", recap["without_patient"]])
    writer.writerow([])

    writer.writerow(["Category", "Count"])
    for category in recap["category_stats"]:
        writer.writerow([category["category_name"], category["count"]])

    writer.writerow([])
    writer.writerow(["Document ID", "Title", "Category", "Uploaded", "Extracted Amount", "Original Filename"])

    for item in recap["items"]:
        doc = item["document"]
        writer.writerow([
            doc.document_id,
            doc.title,
            doc.category.category_name if doc.category else "",
            doc.upload_date,
            f"{item['amount']:.2f}" if item["amount"] is not None else "",
            doc.original_filename,
        ])

    csv_data = output.getvalue()
    output.close()

    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=monthly_recap_{year:04d}_{month:02d}.csv"
    )

    return response