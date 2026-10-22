"""
modules - Medical Symptom Assistant Architecture Package.
Exposes all domain models, extraction engines, prompt builders, LLM connectors, and report generators.
"""

from modules.profile_module import PatientProfile
from modules.input_module import (
    collect_patient_interactive,
    collect_symptoms_interactive,
    load_cases_from_csv,
    get_default_sample_case
)
from modules.symptom_module import (
    extract_symptoms,
    display_extracted_symptoms
)
from modules.context_module import (
    analyze_context,
    display_context_analysis
)
from modules.prompt_module import (
    build_gpt4_prompt,
    get_full_prompt_text,
    display_prompt_generation
)
from modules.analysis_module import (
    analyze_symptoms,
    display_symptom_analysis,
    SymptomAnalysisResult
)
from modules.question_module import (
    generate_follow_up_questions,
    display_follow_up_questions
)
from modules.safety_module import (
    assess_risk_and_guidance,
    get_disclaimer,
    display_medical_attention,
    display_disclaimer_module
)
from modules.save_module import (
    build_structured_report,
    save_report_to_file,
    display_structured_report
)

__all__ = [
    "PatientProfile",
    "collect_patient_interactive",
    "collect_symptoms_interactive",
    "load_cases_from_csv",
    "get_default_sample_case",
    "extract_symptoms",
    "display_extracted_symptoms",
    "analyze_context",
    "display_context_analysis",
    "build_gpt4_prompt",
    "get_full_prompt_text",
    "display_prompt_generation",
    "analyze_symptoms",
    "display_symptom_analysis",
    "SymptomAnalysisResult",
    "generate_follow_up_questions",
    "display_follow_up_questions",
    "assess_risk_and_guidance",
    "get_disclaimer",
    "display_medical_attention",
    "display_disclaimer_module",
    "build_structured_report",
    "save_report_to_file",
    "display_structured_report"
]
