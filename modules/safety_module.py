"""
safety_module.py - Risk Escalation Assessment & Medical Disclaimer.
Fulfills Part G (Q7) and Part I (Q9) with non-diagnostic triage escalation guidance and educational disclaimers.
"""

from typing import Tuple, List
from modules.profile_module import PatientProfile
from modules.utils import print_section, print_warning, print_info


# Emergency Red-Flag Keywords and Indicators
RED_FLAGS = [
    "crushing chest pain", "chest pressure", "radiating to left arm",
    "severe shortness of breath", "struggling to breathe", "bluish lips",
    "loss of consciousness", "fainting", "confusion", "slurred speech",
    "sudden weakness", "facial drooping", "coughing up blood",
    "anaphylaxis", "severe swelling around eyes", "inability to swallow liquids"
]

DISCLAIMER_TEXT = """DISCLAIMER
--------------------------------
This AI-generated response is intended for
educational and informational purposes only.
It is not a medical diagnosis and does not
replace advice from a qualified healthcare
professional.
For serious, worsening or urgent symptoms,
seek appropriate medical care."""


def assess_risk_and_guidance(profile: PatientProfile) -> Tuple[str, str]:
    """
    Evaluates patient symptoms, severity, and context to determine
    risk level and non-clinical medical attention escalation guidance.
    Returns: (risk_level, guidance_text)
    """
    text_lower = (profile.symptoms_text + " " + " ".join(profile.extracted_symptoms)).lower()
    severity_lower = profile.severity.lower()

    # 1. Check for emergency red flags
    detected_red_flags = [flag for flag in RED_FLAGS if flag in text_lower]

    if detected_red_flags or severity_lower == "severe" or "crushing chest pain" in text_lower:
        risk_level = "High / Urgent"
        guidance = (
            "URGENT ATTENTION RECOMMENDED:\n"
            "Reported symptoms may indicate an acute or severe condition requiring prompt\n"
            "evaluation. If you are experiencing difficulty breathing, chest tightness,\n"
            "severe pain, or rapid deterioration, please seek immediate emergency medical care\n"
            "or contact local emergency services immediately."
        )
    elif severity_lower == "moderate" or profile.duration.lower() in ["1 week", "2 weeks", "3 weeks"]:
        risk_level = "Moderate"
        guidance = (
            "PROFESSIONAL CONSULTATION RECOMMENDED:\n"
            "Symptoms have persisted or are causing moderate discomfort. It is recommended to\n"
            "schedule an appointment with a primary care physician or healthcare provider for an\n"
            "in-person evaluation and targeted guidance."
        )
    else:
        risk_level = "Low"
        guidance = (
            "MEDICAL ATTENTION\n"
            "--------------------------------\n"
            "If symptoms are severe, rapidly worsening,\n"
            "or concerning, seek appropriate professional\n"
            "medical care."
        )

    return risk_level, guidance


def get_disclaimer() -> str:
    """Returns the mandatory standardized disclaimer text for Part I (Q9)."""
    return DISCLAIMER_TEXT


def display_medical_attention(guidance: str, risk_level: str = "Low"):
    """Renders Medical Attention guidance matching Part G (Q7)."""
    print_section("Medical Attention Guidance (Part G - Q7)")
    print_info(f"Assessed Clinical Risk Level: {risk_level}")
    print("\n" + guidance)


def display_disclaimer_module():
    """Renders the required disclaimer matching Part I (Q9)."""
    print_section("Medical Disclaimer (Part I - Q9)")
    print(DISCLAIMER_TEXT)
