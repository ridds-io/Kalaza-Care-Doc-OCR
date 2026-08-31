from services.ocr_service import OCRService

image_path = r"C:\Users\Swayam\Documents\VScodePrograms\DocTrack_OCR\uploads\camera\3af585c9-e3d7-49ac-b552-703b98a8232f.jpg"

text = OCRService.extract_text(image_path)

print("\n===== OCR OUTPUT =====\n")
print(text)