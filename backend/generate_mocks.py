import os
from PIL import Image, ImageDraw, ImageFont

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

def create_mock_document(filename, content):
    # Create a white background image
    img = Image.new('RGB', (600, 600), color='white')
    draw = ImageDraw.Draw(img)

    # Try to load a standard font, fallback to default if not found
    try:
        # Windows usually has arial, Mac has Arial
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    # Draw the text onto the image
    draw.text((30, 30), content, fill='black', font=font)

    # Save it to the data folder
    filepath = os.path.join("data", filename)
    img.save(filepath)
    print(f"✅ Generated mock document: {filepath}")

# 1. Create the Prescription
prescription_text = """
┌─────────────────────────────────────────────────────┐
│  Dr. S. Iyer, MBBS, MD (Internal Medicine)          │
│  Reg. No: TN/56789/2013                             │
│  Apollo Hospitals, Bengaluru                        │
│  Ph: +91-80-XXXXXXXX                                │
├─────────────────────────────────────────────────────┤
│  Patient: Deepak Shah           Date: 03-Nov-2024   │
│  Age: 44 years   Gender: M                          │
├─────────────────────────────────────────────────────┤
│  Diagnosis: Acute Bronchitis                        │
│                                                     │
│  Rx:                                                │
│  1. Tab Amoxicillin 500mg — 1-1-1 x 5 days          │
│  2. Salbutamol Inhaler — As needed                  │
│                                                     │
│                            [Doctor's Signature]     │
│                            [Registration Stamp]     │
└─────────────────────────────────────────────────────┘
"""

# 2. Create the Hospital Bill
bill_text = """
┌─────────────────────────────────────────────────────┐
│  APOLLO HOSPITALS                                   │
│  Bengaluru – 560001                                 │
│  GSTIN: 29XXXXX1234X1ZX                             │
│  Ph: 080-XXXXXXXX                                   │
├─────────────────────────────────────────────────────┤
│  BILL / RECEIPT                                     │
│  Bill No: AH/2024/08321     Date: 03-Nov-2024       │
├─────────────────────────────────────────────────────┤
│  Patient Name: Deepak Shah                          │
│  Referring Doctor: Dr. S. Iyer                      │
├─────────────────────────────────────────────────────┤
│  DESCRIPTION                  QTY    RATE    AMOUNT │
│  Consultation Fee (OPD)        1    1500.00  1500.00│
│  Pharmacy / Medicines          1    3000.00  3000.00│
│                                                     │
│  Subtotal:                               4500.00    │
│  Total Amount:                           4500.00    │
├─────────────────────────────────────────────────────┤
│  Received by: Cashier           [Cashier Stamp]     │
└─────────────────────────────────────────────────────┘
"""

if __name__ == "__main__":
    print("Generating mock medical documents...")
    create_mock_document("mock_prescription.jpg", prescription_text)
    create_mock_document("mock_hospital_bill.jpg", bill_text)