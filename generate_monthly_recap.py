import argparse
import csv
import os
from datetime import date

from app import app
from services.report_service import ReportService


def resolve_month(target_month):
    if target_month:
        year, month = map(int, target_month.split("-"))
        return year, month

    today = date.today()
    return today.year, today.month


def write_csv(recap, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    filename = f"monthly_recap_{recap['year']:04d}_{recap['month']:02d}.csv"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

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

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate monthly recap CSV report")
    parser.add_argument(
        "--month",
        help="Month in YYYY-MM format. Defaults to current month.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Generate even if today is not in the last 5 days of the month.",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join("exports", "csv"),
        help="Directory where the report CSV will be saved.",
    )

    args = parser.parse_args()

    with app.app_context():
        if not args.force and not ReportService.is_last_five_days_of_month():
            print("Skipped: today is not in the last 5 days of the month.")
            return

        year, month = resolve_month(args.month)
        recap = ReportService.get_monthly_recap(year, month)

        output_path = write_csv(recap, args.output_dir)
        print(f"Monthly recap generated: {output_path}")


if __name__ == "__main__":
    main()
