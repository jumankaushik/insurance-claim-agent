export const demoScenarios = {
  diagnostic_success: {
    id: "diagnostic_success",
    name: "Complex Diagnostic (Approval)",
    payload: {
      member_id: "EMP001",
      policy_id: "PLUM_GHI_2024",
      claim_category: "DIAGNOSTIC",
      treatment_date: "2024-11-10",
      claimed_amount: 1350.0,
      hospital_name: "City Medical Centre",
      documents: [
        { file_id: "D1", file_name: "rx.jpg", content_path: "data/mock_prescription_v2.jpg" },
        { file_id: "D2", file_name: "lab.jpg", content_path: "data/mock_lab_report.jpg" },
        { file_id: "D3", file_name: "bill.jpg", content_path: "data/mock_hospital_bill_v2.jpg" }
      ]
    }
  },
  triage_failure: {
    id: "triage_failure",
    name: "Wrong Documents (Early Rejection)",
    payload: {
      member_id: "EMP010",
      policy_id: "PLUM_GHI_2024",
      claim_category: "CONSULTATION",
      treatment_date: "2024-11-03",
      claimed_amount: 4500.0,
      hospital_name: "Apollo Hospitals",
      documents: [
        { file_id: "D1", file_name: "bill_1.jpg", content_path: "data/mock_hospital_bill_v2.jpg" },
        { file_id: "D2", file_name: "bill_2.jpg", content_path: "data/mock_hospital_bill_v2.jpg" }
      ]
    }
  }
};

export type ScenarioKey = keyof typeof demoScenarios;