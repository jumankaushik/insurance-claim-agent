import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("data", exist_ok=True)

def create_mock_document(filename, content):
    # Make the canvas slightly larger to fit the complex documents
    img = Image.new('RGB', (700, 800), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    draw.text((30, 30), content, fill='black', font=font)
    filepath = os.path.join("data", filename)
    img.save(filepath)
    print(f"✅ Generated: {filepath}")

# 1. Prescription (Includes State Reg No and T2DM shorthand)
rx_text = """
┌─────────────────────────────────────────────────────────┐
│  Dr. Meena Reddy, MBBS, MD (Endocrinology)              │
│  Reg. No: KA/89012/2018                                 │
│  City Medical Centre, Bengaluru                         │
├─────────────────────────────────────────────────────────┤
│  Patient: Rajesh Kumar          Date: 10-Nov-2024       │
│  Age: 55 years   Gender: M                              │
├─────────────────────────────────────────────────────────┤
│  Diagnosis: T2DM, HTN                                   │
│                                                         │
│  Rx:                                                    │
│  1. Tab Metformin 500mg — 1-0-1 x 30 days               │
│  2. Tab Telmisartan 40mg — 1-0-0 x 30 days              │
│                                                         │
│  Investigations: HbA1c, Lipid Profile                   │
│                                                         │
│                            [Signature & Stamp]          │
└─────────────────────────────────────────────────────────┘
"""

# 2. Hospital Bill (Includes GSTIN)
hospital_bill_text = """
┌─────────────────────────────────────────────────────────┐
│  CITY MEDICAL CENTRE                                    │
│  Bengaluru – 560001                                     │
│  GSTIN: 29XXXXX1234X1ZX                                 │
├─────────────────────────────────────────────────────────┤
│  BILL / RECEIPT                                         │
│  Bill No: CMC/2024/09988    Date: 10-Nov-2024           │
│  Patient Name: Rajesh Kumar                             │
├─────────────────────────────────────────────────────────┤
│  DESCRIPTION                  QTY    RATE    AMOUNT     │
│  Consultation Fee (OPD)        1    1200.00  1200.00    │
│  Registration Charges          1     150.00   150.00    │
│                                                         │
│  Total Amount:                               1350.00    │
├─────────────────────────────────────────────────────────┤
│  Received by: Cashier           [PAID STAMP]            │
└─────────────────────────────────────────────────────────┘
"""

# 3. Lab Report (Includes NABL ID and specific test results)
lab_report_text = """
┌─────────────────────────────────────────────────────────┐
│  PRECISION DIAGNOSTICS PVT LTD                          │
│  NABL Accredited Lab   |   Lab ID: KA-NABL-1234         │
├─────────────────────────────────────────────────────────┤
│  Patient: Rajesh Kumar      Ref Dr: Dr. Meena Reddy     │
│  Sample Date: 11-Nov-2024   Report Date: 11-Nov-2024    │
├─────────────────────────────────────────────────────────┤
│  TEST NAME          RESULT    UNIT    NORMAL RANGE      │
│  DIABETES SCREENING:                                    │
│  HbA1c              7.8       %       4.0 – 5.6         │
│  Fasting Blood Sug  145       mg/dL   70 – 100          │
│                                                         │
│  LIPID PROFILE:                                         │
│  Total Cholesterol  220       mg/dL   < 200             │
│                                                         │
│  Remarks: HbA1c indicative of poor glycemic control.    │
└─────────────────────────────────────────────────────────┘
"""

# 4. Pharmacy Bill (Includes Drug License Number and Batches)
pharmacy_bill_text = """
┌─────────────────────────────────────────────────────────┐
│  HEALTH FIRST PHARMACY                                  │
│  Drug Lic. No: KA-BLR-887766                            │
├─────────────────────────────────────────────────────────┤
│  Bill No: HFP-24-11002    Date: 11-Nov-2024             │
│  Patient: Rajesh Kumar    Dr: Dr. Meena Reddy           │
├─────────────────────────────────────────────────────────┤
│  MEDICINE           BATCH    QTY  MRP    AMT            │
│  Metformin 500mg    A1122     30  5.00   150.00         │
│  Telmisartan 40mg   B3344     30  8.00   240.00         │
│                                                         │
│  Net Amount:                             390.00         │
├─────────────────────────────────────────────────────────┤
│  Pharmacist: S. Gupta    [DUPLICATE STAMP]              │
└─────────────────────────────────────────────────────────┘
"""

if __name__ == "__main__":
    print("Generating comprehensive mock documents...")
    create_mock_document("mock_prescription_v2.jpg", rx_text)
    create_mock_document("mock_hospital_bill_v2.jpg", hospital_bill_text)
    create_mock_document("mock_lab_report.jpg", lab_report_text)
    create_mock_document("mock_pharmacy_bill.jpg", pharmacy_bill_text)