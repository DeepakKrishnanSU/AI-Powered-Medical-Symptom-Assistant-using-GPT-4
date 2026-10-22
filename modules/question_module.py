"""
question_module.py - Clinical Follow-Up Question Generator.
Fulfills Part F (Q6) by generating targeted questions to clarify symptom trajectory and unstated clinical factors.
"""

from typing import List, Optional
from modules.profile_module import PatientProfile
from modules.utils import print_section, print_info


def generate_follow_up_questions(profile: PatientProfile, missing_info: Optional[List[str]] = None) -> List[str]:
    """
    Dynamically generates clinically relevant follow-up questions tailored to
    the patient's reported symptoms and detected missing context.
    """
    questions: List[str] = []
    symptoms = set([s.lower() for s in profile.extracted_symptoms])
    text_lower = profile.symptoms_text.lower()

    # Question 1: Measured Temperature
    if "fever" in symptoms or "chills" in symptoms or "fever" in text_lower:
        questions.append("What is your measured temperature (in °F or °C)?")

    # Question 2: Exact Onset & Timeline
    questions.append("When exactly did the symptoms begin, and did they start suddenly or develop gradually?")

    # Question 3: Respiratory / Breathing Status
    if any(s in symptoms for s in ["cough", "sore throat", "fever", "shortness of breath", "chest pain"]):
        questions.append("Are you experiencing any difficulty breathing, wheezing, or shortness of breath while resting or walking?")

    # Question 4: Cough Specifics
    if "cough" in symptoms or "cough" in text_lower:
        questions.append("Is the cough dry, or is it producing phlegm or mucus (and if so, what color)?")

    # Question 5: Sore Throat & Swallowing
    if "sore throat" in symptoms or "throat" in text_lower:
        questions.append("Is the throat pain affecting your ability to swallow liquids, foods, or saliva?")

    # Question 6: Severity Trajectory
    questions.append("Are the symptoms improving, worsening, or remaining about the same over the past 24 hours?")

    # Question 7: Gastrointestinal (if GI symptoms present)
    if any(s in symptoms for s in ["nausea", "vomiting", "diarrhea", "abdominal pain"]):
        questions.append("Are you able to keep down oral fluids, and have you noticed any blood in vomit or bowel movements?")

    # Question 8: Headache / Neurological (if headache present)
    if "headache" in symptoms or "dizziness" in symptoms:
        questions.append("Is the headache accompanied by extreme sensitivity to light or sound, stiff neck, or changes in vision?")

    # Deduplicate and prioritize to return the top 5 most relevant questions
    seen = set()
    unique_questions = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            unique_questions.append(q)

    # Ensure at least 5 standard high-yield clinical questions
    standard_defaults = [
        "What is your measured temperature?",
        "When exactly did the symptoms begin?",
        "Are you experiencing difficulty breathing?",
        "Is the cough dry or producing mucus?",
        "Are the symptoms improving or worsening?"
    ]

    for d in standard_defaults:
        if len(unique_questions) >= 5:
            break
        if d not in unique_questions:
            unique_questions.append(d)

    return unique_questions[:5]


def display_follow_up_questions(questions: List[str]):
    """Renders follow-up questions matching Part F (Q6) format."""
    print_section("Follow-Up Questions (Part F - Q6)")
    print_info("Recommended questions to clarify patient assessment:")
    print("\nFOLLOW-UP QUESTIONS")
    print("--------------------------------")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    print("--------------------------------")
