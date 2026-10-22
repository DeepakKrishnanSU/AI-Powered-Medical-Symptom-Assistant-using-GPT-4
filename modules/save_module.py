"""
save_module.py - Structured Report Assembly & Persistence.
Fulfills Part H (Q8) and Part J (Q10) by compiling the complete 8-section report and saving to outputs/medical_analysis.txt.
"""

import os
from datetime import datetime
from typing import List, Optional
from modules.profile_module import PatientProfile
from modules.analysis_module import SymptomAnalysisResult
from modules.safety_module import get_disclaimer
from modules.utils import print_section, print_success, print_info


def build_structured_report(
    profile: PatientProfile,
    analysis: SymptomAnalysisResult,
    missing_info: List[str],
    follow_up_questions: List[str],
    guidance: str,
    risk_level: str = "Low"
) -> str:
    """
    Constructs the complete 8-part structured medical symptom report
    as specified in Part H (Q8).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format 1. Reported Symptoms
    symptoms_list = profile.extracted_symptoms if profile.extracted_symptoms else [profile.symptoms_text]
    symptoms_str = "\n".join([f"• {s}" for s in symptoms_list])

    # Format 2. Patient Information
    patient_info_str = (
        f"Age       : {profile.age}\n"
        f"Sex       : {profile.sex}\n"
        f"Duration  : {profile.duration}\n"
        f"Severity  : {profile.severity}\n"
        f"History   : {profile.medical_history}\n"
        f"Medication: {profile.current_medications}\n"
        f"Allergies : {profile.allergies}"
    )

    # Format 3. Possible Conditions
    conditions_str = "\n".join([f"• {c['name']}" for c in analysis.possible_conditions])

    # Format 4. Explanation
    explanations = []
    for c in analysis.possible_conditions:
        if c.get("reasoning"):
            explanations.append(f"• {c['name']}: {c['reasoning']}")
    if not explanations:
        explanations.append(analysis.general_reasoning)
    explanation_str = "\n".join(explanations)

    # Format 5. Missing Information
    missing_str = "\n".join([f"• {m}" for m in missing_info])

    # Format 6. Follow-up Questions
    questions_str = "\n".join([f"{i}. {q}" for i, q in enumerate(follow_up_questions, 1)])

    # Format 7. Medical Attention Guidance
    attention_str = guidance.strip()

    # Format 8. Disclaimer
    disclaimer_str = get_disclaimer().strip()

    report = f"""======================================================================
AI-POWERED MEDICAL SYMPTOM ASSISTANT - STRUCTURED REPORT
Generated on: {timestamp} | Engine: {analysis.provider_used}
======================================================================

1. REPORTED SYMPTOMS
--------------------------------
{symptoms_str}

2. PATIENT INFORMATION
--------------------------------
{patient_info_str}

3. POSSIBLE CONDITIONS
--------------------------------
{conditions_str}

4. EXPLANATION
--------------------------------
{explanation_str}

5. MISSING INFORMATION
--------------------------------
{missing_str}

6. FOLLOW-UP QUESTIONS
--------------------------------
{questions_str}

7. MEDICAL ATTENTION GUIDANCE
--------------------------------
{attention_str}

8. DISCLAIMER
--------------------------------
{disclaimer_str}
======================================================================
"""
    return report


def save_report_to_file(report_text: str, output_path: str = "outputs/medical_analysis.txt") -> str:
    """
    Saves the structured analysis report to outputs/medical_analysis.txt (Part J - Q10).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return os.path.abspath(output_path)


def display_structured_report(report_text: str):
    """Renders the entire structured report on terminal for lab screenshot."""
    print_section("Complete Structured Analysis (Part H - Q8)")
    print(report_text)
