"""
prompt_module.py - Prompt Construction for GPT-4 / Ollama.
Fulfills Part D (Q4) by building guardrailed, non-diagnostic prompts.
"""

from typing import List, Dict, Optional, Tuple
from modules.profile_module import PatientProfile
from modules.utils import print_section, print_info


SYSTEM_INSTRUCTION = """You are an AI-powered Medical Symptom Assistant designed to provide informational and educational insights based on user-reported health details.

CRITICAL CLINICAL & SAFETY CONSTRAINTS:
1. You are NOT a doctor and CANNOT provide a definitive medical diagnosis.
2. Communicate uncertainty clearly. Use cautious language such as "Possible explanations may include...", "These symptoms can occur with several conditions...", "This is not sufficient to establish a diagnosis."
3. Never invent symptoms, medications, or lab values not provided.
4. Identify when professional medical care or immediate emergency attention may be appropriate.
5. Provide reasoning at a general, educational level.
6. Generate practical, non-judgmental follow-up questions to clarify unstated clinical context.
"""


def build_gpt4_prompt(profile: PatientProfile, missing_info: Optional[List[str]] = None) -> Tuple[str, str]:
    """
    Constructs the system prompt and user prompt for GPT-4 / Ollama.
    Returns: (system_prompt, user_prompt)
    """
    symptoms_str = ", ".join(profile.extracted_symptoms) if profile.extracted_symptoms else profile.symptoms_text
    missing_str = "\n".join([f"- {m}" for m in missing_info]) if missing_info else "- None identified"

    user_prompt = f"""PATIENT CONTEXT:
--------------------------------
Age: {profile.age}
Sex: {profile.sex}
Reported Symptoms: {symptoms_str}
Duration: {profile.duration}
Reported Severity: {profile.severity}
Medical History: {profile.medical_history}
Current Medications: {profile.current_medications}
Known Allergies: {profile.allergies}

NATURAL LANGUAGE DESCRIPTION:
"{profile.symptoms_text}"

DETECTED MISSING CLINICAL CONTEXT:
{missing_str}

TASK:
Analyze the reported symptoms and patient profile. Provide your response strictly in the following structured format:

1. REPORTED SYMPTOMS:
List the primary identified symptoms.

2. POSSIBLE CONDITIONS:
List 3 to 4 possible conditions or explanations that may be associated with these symptoms. For each condition, provide a brief, general explanation of why it was considered.

3. FOLLOW-UP QUESTIONS:
Generate 4 to 5 relevant follow-up questions to help clarify the situation.

4. MEDICAL ATTENTION GUIDANCE:
Explain clearly when and under what circumstances the user should seek professional or emergency medical attention.

5. CLINICAL NOTE & UNCERTAINTY:
Explicitly communicate that these symptoms alone cannot confirm a diagnosis.
"""
    return SYSTEM_INSTRUCTION.strip(), user_prompt.strip()


def get_full_prompt_text(profile: PatientProfile, missing_info: Optional[List[str]] = None) -> str:
    """Returns the complete combined prompt text for display and single-prompt LLM execution."""
    system_p, user_p = build_gpt4_prompt(profile, missing_info)
    return f"=== SYSTEM INSTRUCTION ===\n{system_p}\n\n=== USER PROMPT ===\n{user_p}"


def display_prompt_generation(system_prompt: str, user_prompt: str):
    """Renders generated prompt for terminal display / lab screenshot."""
    print_section("Prompt Generation (Part D - Q4)")
    print_info("Constructed guardrailed prompt for GPT-4 / Ollama:")
    print("\n--- System Prompt ---")
    print(system_prompt)
    print("\n--- User Prompt ---")
    print(user_prompt)
