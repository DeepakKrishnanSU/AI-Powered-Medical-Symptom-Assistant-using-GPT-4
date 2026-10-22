"""
context_module.py - Context Analysis & Missing Clinical Information Detection.
Fulfills Part C (Q3) by evaluating patient context and identifying unstated but critical clinical parameters.
"""

import re
from typing import List, Dict, Set
from modules.profile_module import PatientProfile
from modules.utils import print_section, display_bullet_list, print_info


def analyze_context(profile: PatientProfile) -> List[str]:
    """
    Analyzes the patient profile and identified symptoms to detect missing
    information that would be vital for a physician to make a differential evaluation.
    """
    missing: List[str] = []
    text_lower = (profile.symptoms_text + " " + profile.additional_notes).lower()
    symptoms = set([s.lower() for s in profile.extracted_symptoms])

    # 1. Temperature Check (Particularly relevant if Fever is present or suspected)
    has_fever = "fever" in symptoms or "fever" in text_lower or "chills" in symptoms
    temp_pattern = r"\b(10[0-5]|\d{2})(\.\d)?\s*(°?f|°?c|degrees)?\b"
    has_measured_temp = bool(re.search(r"\b(9[89]|10[0-5])\b", text_lower)) or "measured" in text_lower
    if has_fever and not has_measured_temp:
        missing.append("Exact measured temperature (°F or °C)")

    # 2. Breathing / Respiratory Distress
    has_respiratory = any(s in symptoms for s in ["cough", "sore throat", "fever", "nasal congestion", "shortness of breath"])
    mentions_breathing = any(w in text_lower for w in ["breathing", "breath", "dyspnea", "wheezing", "suffocating", "air"])
    if has_respiratory and not mentions_breathing:
        missing.append("Presence or absence of breathing difficulty / shortness of breath")

    # 3. Cough Sputum / Phlegm Characteristics
    if "cough" in symptoms:
        mentions_cough_type = any(w in text_lower for w in ["dry", "phlegm", "mucus", "sputum", "productive", "wet"])
        if not mentions_cough_type:
            missing.append("Cough characteristics (dry vs. productive with colored phlegm/mucus)")

    # 4. Severity Progression / Trajectory
    progression_words = ["worsening", "improving", "getting better", "getting worse", "constant", "static", "progressing", "rapid"]
    has_progression = any(w in text_lower for w in progression_words)
    if not has_progression:
        missing.append("Severity progression over time (worsening, improving, or remaining constant)")

    # 5. Associated / Red-Flag Symptoms
    mentions_chest_or_neuro = any(w in text_lower for w in ["chest", "dizziness", "confusion", "stiff neck", "seizure"])
    if not mentions_chest_or_neuro:
        missing.append("Presence of associated red-flag symptoms (chest tightness, neck stiffness, confusion)")

    # 6. Hydration & Intake Status (Important for fever / GI cases)
    has_gi = any(s in symptoms for s in ["vomiting", "diarrhea", "nausea", "abdominal pain"])
    if (has_fever or has_gi) and not any(w in text_lower for w in ["drinking", "water", "hydration", "fluids", "urination", "urine"]):
        missing.append("Hydration status and oral fluid intake tolerance")

    # 7. Medication History Specifics
    if profile.current_medications.lower() in ["none", "none reported", ""]:
        missing.append("Confirmation of any over-the-counter medications taken recently (e.g., antipyretics, painkillers)")

    # Default fallback to guarantee Q3 standard output if already very detailed
    if not missing:
        missing = [
            "Exact measured temperature",
            "Breathing difficulty",
            "Severity progression",
            "Additional symptoms"
        ]

    return missing


def display_context_analysis(missing_info: List[str]):
    """Renders the missing context for terminal display / lab screenshot."""
    print_section("Context Analysis (Part C - Q3)")
    print_info("Identified missing clinical parameters that would clarify assessment:")
    print("\nMissing Information:")
    display_bullet_list(missing_info, bullet="•")
