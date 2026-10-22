"""
profile_module.py - Patient Profile Model & Data Structures.
Fulfills Part A (Q1) and manages validated patient health context.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List


@dataclass
class PatientProfile:
    """Encapsulates patient demographics, clinical context, and input parameters."""
    age: int = 0
    sex: str = "Not specified"
    symptoms_text: str = ""
    extracted_symptoms: List[str] = field(default_factory=list)
    duration: str = "Not specified"
    severity: str = "Mild"  # 'Mild', 'Moderate', 'Severe'
    medical_history: str = "No known relevant condition"
    current_medications: str = "None"
    allergies: str = "None"
    additional_notes: str = "None"

    def validate(self) -> List[str]:
        """Validates patient profile parameters and returns list of validation warnings/errors."""
        errors = []
        if self.age < 0 or self.age > 125:
            errors.append(f"Age {self.age} is out of realistic clinical range (0-125).")
        if not self.symptoms_text.strip() and not self.extracted_symptoms:
            errors.append("No symptoms description provided.")
        valid_severities = {"mild", "moderate", "severe"}
        if self.severity.lower() not in valid_severities:
            errors.append(f"Invalid severity '{self.severity}'. Expected: Mild, Moderate, or Severe.")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serializes profile to a standard dictionary."""
        return asdict(self)

    def to_display_dict(self) -> Dict[str, Any]:
        """Returns clean dictionary formatted for console or UI display."""
        return {
            "Age": f"{self.age} years",
            "Sex": self.sex,
            "Reported Duration": self.duration,
            "Reported Severity": self.severity,
            "Relevant Medical History": self.medical_history,
            "Current Medications": self.current_medications,
            "Known Allergies": self.allergies,
            "Extracted Symptoms": ", ".join(self.extracted_symptoms) if self.extracted_symptoms else "Pending extraction",
        }

    def to_prompt_context(self) -> str:
        """Formats patient profile as structured context for LLM prompt generation."""
        symptoms_str = ", ".join(self.extracted_symptoms) if self.extracted_symptoms else self.symptoms_text
        return (
            f"Patient Age: {self.age}\n"
            f"Sex: {self.sex}\n"
            f"Reported Symptoms: {symptoms_str}\n"
            f"Duration: {self.duration}\n"
            f"Severity: {self.severity}\n"
            f"Relevant Medical History: {self.medical_history}\n"
            f"Current Medications: {self.current_medications}\n"
            f"Allergies: {self.allergies}"
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientProfile":
        """Instantiates PatientProfile from dictionary or CSV row."""
        extracted = data.get("extracted_symptoms", [])
        if isinstance(extracted, str):
            extracted = [s.strip() for s in extracted.split(";") if s.strip()]

        return cls(
            age=int(data.get("age", 0)),
            sex=str(data.get("sex", "Not specified")),
            symptoms_text=str(data.get("symptoms_text", "")),
            extracted_symptoms=extracted,
            duration=str(data.get("duration", "Not specified")),
            severity=str(data.get("severity", "Mild")),
            medical_history=str(data.get("medical_history", "No known relevant condition")),
            current_medications=str(data.get("current_medications", "None")),
            allergies=str(data.get("allergies", "None")),
            additional_notes=str(data.get("additional_notes", "None")),
        )
