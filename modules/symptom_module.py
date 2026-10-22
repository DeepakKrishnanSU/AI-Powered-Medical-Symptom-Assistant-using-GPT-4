"""
symptom_module.py - Natural-Language Symptom Extraction.
Fulfills Part B (Q2) using high-precision clinical NLP pattern matching and phrase parsing.
"""

import re
from typing import List, Dict, Set, Optional
from modules.utils import print_section, print_info, display_bullet_list

# Clinical patterns mapping flexible natural language to canonical symptoms
CLINICAL_PATTERNS: Dict[str, List[str]] = {
    "Fever": [
        r"\bfever\b", r"\bhigh\s+temperature\b", r"\bfebrile\b", r"\bfeverish\b",
        r"\bhot\s+feeling\b", r"\bpyrexia\b"
    ],
    "Cough": [
        r"\bcough(ing)?\b", r"\bhacking\b", r"\bdry\s+cough\b", r"\bproductive\s+cough\b",
        r"\bphlegm\b", r"\bmucus\b"
    ],
    "Sore throat": [
        r"\bsore\s+throat\b",
        r"\bthroat\b(?:\s+\w+){0,3}\s+(?:painful|sore|hurts?|tender|irritated|burning|inflamed)\b",
        r"\bpain(?:\s+\w+){0,2}\s+(?:in\s+)?(?:my\s+)?throat\b",
        r"\bpharyngitis\b",
        r"\bpain\s+swallowing\b"
    ],
    "Shortness of breath": [
        r"\bshortness\s+of\s+breath\b", r"\bdifficulty\s+breathing\b", r"\bbreathless(ness)?\b",
        r"\bcan'?t\s+breathe\b", r"\bdyspnea\b", r"\bwheezing\b", r"\bstruggling\s+to\s+breathe\b"
    ],
    "Headache": [
        r"\bheadache(s)?\b", r"\bhead\s+pain\b", r"\bmigraine(s)?\b", r"\bpounding\s+head\b",
        r"\bthrobbing\s+head\b"
    ],
    "Chest pain": [
        r"\bchest\s+pain\b", r"\btightness\s+in\s+chest\b", r"\bchest\s+tightness\b",
        r"\bchest\s+pressure\b", r"\bcrushing\s+chest\s+pain\b", r"\bchest\s+discomfort\b"
    ],
    "Fatigue": [
        r"\bfatigue(d)?\b", r"\btired(ness)?\b", r"\bexhaustion\b", r"\bletharg(y|ic)\b",
        r"\bfeeling\s+drained\b", r"\bweakness\b"
    ],
    "Nausea": [
        r"\bnausea\b", r"\bnauseous\b", r"\bsick\s+to\s+my\s+stomach\b", r"\bqueasy\b"
    ],
    "Vomiting": [
        r"\bvomit(ing)?\b", r"\bthrowing\s+up\b", r"\bpuking\b", r"\bemesis\b"
    ],
    "Diarrhea": [
        r"\bdiarrhea\b", r"\bloose\s+stools?\b", r"\bwatery\s+diarrhea\b", r"\bwatery\s+stools?\b"
    ],
    "Abdominal pain": [
        r"\babdominal\s+pain\b", r"\bstomach\s+(ache|pain|cramps?)\b", r"\bbelly\s+pain\b",
        r"\babdominal\s+cramps?\b"
    ],
    "Runny nose": [
        r"\brunny\s+nose\b", r"\brhinorrhea\b", r"\bnasal\s+discharge\b"
    ],
    "Nasal congestion": [
        r"\bnasal\s+congestion\b", r"\bstuffy\s+nose\b", r"\bblocked\s+nose\b", r"\bcongested\b"
    ],
    "Sneezing": [
        r"\bsneez(e|ing)\b"
    ],
    "Body aches": [
        r"\bbody\s+aches?\b", r"\bmuscle\s+pain\b", r"\bmyalgia\b", r"\bjoint\s+pain\b",
        r"\bwhole\s+body\s+aches?\b"
    ],
    "Chills": [
        r"\bchills?\b", r"\bshivering\b", r"\brigors\b"
    ],
    "Dizziness": [
        r"\bdizz(y|iness)\b", r"\blightheaded(ness)?\b", r"\bvertigo\b"
    ],
    "Loss of appetite": [
        r"\bloss\s+of\s+appetite\b", r"\bnot\s+hungry\b", r"\breduced\s+appetite\b"
    ],
    "Skin rash": [
        r"\b(skin\s+)?rash\b", r"\bhives\b", r"\bwelts\b", r"\burticaria\b", r"\bitchy\s+skin\b"
    ],
    "Burning urination": [
        r"\bburning\s+(while\s+)?urination\b", r"\bpainful\s+urination\b", r"\bdysuria\b",
        r"\bburning\s+sensation\s+while\s+urinat(e|ing)\b"
    ],
    "Acid reflux": [
        r"\bacid\s+reflux\b", r"\bheartburn\b", r"\bindigestion\b", r"\bsour\s+taste\b"
    ],
    "Back pain": [
        r"\bback\s+pain\b", r"\blower\s+back\s+pain\b", r"\blumbar\s+pain\b"
    ],
    "Joint stiffness": [
        r"\bjoint\s+stiffness\b", r"\bstiffness\s+in\s+morning\b"
    ]
}


def extract_symptoms(text: str) -> List[str]:
    """
    Extracts clinical symptoms from free-form natural language input.
    Matches variations such as 'throat is also painful' -> 'Sore throat'.
    """
    if not text or not text.strip():
        return []

    normalized_text = text.lower()
    extracted: Set[str] = set()

    for canonical, patterns in CLINICAL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, normalized_text):
                extracted.add(canonical)
                break

    # If nothing matched directly, extract plausible phrase fragments
    if not extracted:
        phrases = [p.strip().capitalize() for p in re.split(r"[,.;]+|and", text) if len(p.strip()) > 3]
        extracted = set(phrases[:3] if phrases else ["Unspecified symptom"])

    return sorted(list(extracted))


def display_extracted_symptoms(symptoms: List[str], raw_text: Optional[str] = None):
    """Prints extracted symptoms nicely for terminal display / lab screenshot."""
    print_section("Symptom Extraction (Part B - Q2)")
    if raw_text:
        print_info(f"Natural Language Input: \"{raw_text}\"")
    print("\nExtracted Symptoms:")
    display_bullet_list(symptoms, bullet="•")
