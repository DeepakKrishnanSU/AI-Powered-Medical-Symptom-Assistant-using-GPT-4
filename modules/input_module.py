"""
input_module.py - User Input Collection & Case Loader.
Collects patient demographics, health context, and symptoms interactively or from sample cases.
"""

import os
import pandas as pd
from typing import Optional, List, Dict, Any
from modules.profile_module import PatientProfile
from modules.utils import print_section, print_info, print_warning, print_success


def get_default_sample_case() -> PatientProfile:
    """Returns the default benchmark case from Lab Part A (Q1)."""
    return PatientProfile(
        age=22,
        sex="Female",
        symptoms_text="I have been having fever and cough for two days. My throat is also painful.",
        extracted_symptoms=["Fever", "Cough", "Sore throat"],
        duration="2 days",
        severity="Mild",
        medical_history="No known relevant condition",
        current_medications="None",
        allergies="None",
        additional_notes="None"
    )


def load_cases_from_csv(csv_path: str = "data/sample_cases.csv") -> List[Dict[str, Any]]:
    """Loads benchmark patient cases from the CSV dataset."""
    if not os.path.exists(csv_path):
        return []
    try:
        df = pd.read_csv(csv_path)
        return df.to_dict(orient="records")
    except Exception as e:
        print_warning(f"Could not load cases from {csv_path}: {e}")
        return []


def collect_patient_interactive() -> PatientProfile:
    """Interactively prompts the user for patient details from the terminal."""
    print_section("Patient Information Collection (Part A - Q1)")
    print_info("Press Enter without typing to accept default suggested values.")

    # Age collection
    while True:
        age_in = input("\n  Enter Age [Default: 22]: ").strip()
        if not age_in:
            age = 22
            break
        try:
            age = int(age_in)
            if 0 <= age <= 125:
                break
            print("  [!] Please enter a realistic age between 0 and 125.")
        except ValueError:
            print("  [!] Please enter a valid numerical age.")

    # Sex collection
    sex_in = input("  Enter Sex (Female/Male/Other/Not specified) [Default: Female]: ").strip()
    sex = sex_in if sex_in else "Female"

    # Duration collection
    duration_in = input("  Enter Duration (e.g., 2 days, 1 week) [Default: 2 days]: ").strip()
    duration = duration_in if duration_in else "2 days"

    # Severity collection
    while True:
        sev_in = input("  Enter Severity (Mild / Moderate / Severe) [Default: Mild]: ").strip().capitalize()
        if not sev_in:
            severity = "Mild"
            break
        if sev_in in ["Mild", "Moderate", "Severe"]:
            severity = sev_in
            break
        print("  [!] Invalid choice. Please enter Mild, Moderate, or Severe.")

    # Medical History
    hist_in = input("  Relevant Medical History [Default: No known relevant condition]: ").strip()
    medical_history = hist_in if hist_in else "No known relevant condition"

    # Medications
    med_in = input("  Current Medications [Default: None]: ").strip()
    current_medications = med_in if med_in else "None"

    # Allergies
    allg_in = input("  Known Allergies [Default: None]: ").strip()
    allergies = allg_in if allg_in else "None"

    profile = PatientProfile(
        age=age,
        sex=sex,
        symptoms_text="",
        duration=duration,
        severity=severity,
        medical_history=medical_history,
        current_medications=current_medications,
        allergies=allergies
    )

    print_success("Patient information collected successfully!")
    return profile


def collect_symptoms_interactive(existing_profile: Optional[PatientProfile] = None) -> PatientProfile:
    """Prompts for natural-language symptoms input."""
    print_section("Natural Language Symptom Input (Part B - Q2)")
    print_info("Describe symptoms in plain natural language (e.g., 'I have had a fever and cough for two days. My throat is also sore.')")

    default_text = "I have been having fever and cough for two days. My throat is also painful."
    print(f"\n  Default example: \"{default_text}\"")
    user_input = input("  Your symptoms description (Press Enter to use default): ").strip()

    symptoms_text = user_input if user_input else default_text

    if existing_profile is None:
        profile = get_default_sample_case()
        profile.symptoms_text = symptoms_text
        profile.extracted_symptoms = []
        return profile

    existing_profile.symptoms_text = symptoms_text
    print_success("Symptom narrative recorded!")
    return existing_profile
