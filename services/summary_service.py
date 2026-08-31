import re


class SummaryService:

    @staticmethod
    def extract_summary(ocr_text):

        if not ocr_text:
            return {
                "date": None,
                "price": None
            }

        text = ocr_text.replace("\n", " ")

        # =====================================================
        # DATE EXTRACTION
        # =====================================================

        date = None

        date_patterns = [

            # 09/2025 or 09-2025
            r"\b\d{1,2}[/-]\d{4}\b",

            # 09/02/2025 or 09-02-2025
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

            # 09/2025 with spaces
            r"\b\d{1,2}\s*[/-]\s*\d{4}\b"

        ]

        for pattern in date_patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                date = match.group(0)

                break


        # =====================================================
        # PRICE / MRP EXTRACTION
        # =====================================================

        price = None

        # First try to find MRP because that is normally
        # the main price we want from a document.

        mrp_patterns = [

            # MRP ₹80.00
            r"MRP\s*[:\-]?\s*₹?\s*([0-9,]+(?:\.[0-9]{1,2})?)",

            # MRP Rs. 80.00
            r"MRP\s*[:\-]?\s*(?:Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)",

            # MRP 80.00
            r"MRP\s*[:\-]?\s*([0-9,]+(?:\.[0-9]{1,2})?)"

        ]

        for pattern in mrp_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                price = match.group(1)

                price = price.replace(",", "")

                price = f"₹{price}"

                break


        # =====================================================
        # FALLBACK PRICE SEARCH
        # =====================================================

        if price is None:

            price_patterns = [

                r"₹\s*([0-9,]+(?:\.[0-9]{1,2})?)",

                r"(?:Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)"

            ]

            for pattern in price_patterns:

                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                if match:

                    price = match.group(1)

                    price = price.replace(",", "")

                    price = f"₹{price}"

                    break


        return {
            "date": date,
            "price": price
        }