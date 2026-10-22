"""
analysis_module.py - Symptom Analysis Engine (Ollama / GPT-4).
Fulfills Part E (Q5) by interfacing with local Ollama or OpenAI GPT-4 to generate differential conditions and reasoning.
"""

import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from modules.profile_module import PatientProfile
from modules.prompt_module import build_gpt4_prompt
from modules.utils import print_section, print_info, print_warning, print_success, display_bullet_list


@dataclass
class SymptomAnalysisResult:
    """Encapsulates structured symptom analysis output."""
    reported_symptoms: List[str] = field(default_factory=list)
    possible_conditions: List[Dict[str, str]] = field(default_factory=list)
    general_reasoning: str = ""
    clinical_note: str = (
        "These symptoms can occur in multiple conditions. "
        "The information provided is not sufficient to establish a diagnosis."
    )
    raw_response: str = ""
    provider_used: str = "Ollama (Local)"


def call_ollama(system_prompt: str, user_prompt: str, model: str = "llama3.2:latest", host: str = "http://localhost:11434") -> Optional[str]:
    """Sends a chat request to the local Ollama API via standard HTTP."""
    url = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json.get("message", {}).get("content", "")
    except Exception as e:
        print_warning(f"Ollama local connection error: {e}")
        return None


def call_openai_gpt4(system_prompt: str, user_prompt: str, api_key: str, model: str = "gpt-4o") -> Optional[str]:
    """
    Sends a chat request to OpenAI GPT-4 API using standard library urllib.
    Requires no external 'openai' pip package.
    """
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    req = urllib.request.Request(url, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        print_warning(f"OpenAI GPT-4 API call failed: {e}")
        return None


def get_deterministic_fallback_analysis(profile: PatientProfile) -> SymptomAnalysisResult:
    """Clinical heuristic fallback when offline or LLM daemon is unavailable."""
    symptoms = [s.lower() for s in profile.extracted_symptoms]

    conditions = []
    if any(s in symptoms for s in ["fever", "cough", "sore throat"]):
        conditions = [
            {"name": "Common cold", "reasoning": "Frequent viral upper respiratory tract infection presenting with mild fever, cough, and throat irritation."},
            {"name": "Influenza", "reasoning": "Systemic viral illness characterized by acute fever, cough, sore throat, and muscle aches."},
            {"name": "Other respiratory infections", "reasoning": "Includes viral pharyngitis, acute laryngitis, or early bronchitis."}
        ]
        reasoning = "The reported symptoms can occur with several common respiratory conditions. Most are self-limiting viral etiologies."
    elif any(s in symptoms for s in ["nausea", "vomiting", "diarrhea", "abdominal pain"]):
        conditions = [
            {"name": "Viral gastroenteritis", "reasoning": "Acute intestinal infection causing watery diarrhea, cramps, and nausea."},
            {"name": "Foodborne illness", "reasoning": "Bacterial or viral contamination resulting in rapid onset of gastrointestinal symptoms."},
            {"name": "Gastritis / Peptic irritation", "reasoning": "Inflammation of the stomach lining producing pain and nausea."}
        ]
        reasoning = "Acute gastrointestinal symptoms frequently indicate self-limiting infection or dietary irritation."
    elif any(s in symptoms for s in ["headache"]):
        conditions = [
            {"name": "Tension-type headache", "reasoning": "Most common headache type, associated with stress or muscular contraction."},
            {"name": "Migraine", "reasoning": "Neurovascular headache often presenting with throbbing pain, sensory sensitivities, and nausea."},
            {"name": "Sinus headache", "reasoning": "Head pressure and facial pain related to sinus inflammation or congestion."}
        ]
        reasoning = "Headaches have diverse etiologies ranging from muscular tension to vascular migraines."
    else:
        conditions = [
            {"name": "Nonspecific viral syndrome", "reasoning": "Generalized presentation common in early or mild viral illnesses."},
            {"name": "Physiological fatigue or strain", "reasoning": "Physical exertion, stress, or inadequate recovery."},
            {"name": "Evaluation recommended", "reasoning": "Requires detailed medical examination to evaluate nonspecific presentation."}
        ]
        reasoning = "Symptoms require additional clinical context to narrow possible differentials."

    return SymptomAnalysisResult(
        reported_symptoms=profile.extracted_symptoms if profile.extracted_symptoms else ["Unspecified symptom"],
        possible_conditions=conditions,
        general_reasoning=reasoning,
        clinical_note="These symptoms can occur in multiple conditions. The information provided is not sufficient to establish a diagnosis.",
        raw_response="Deterministic Clinical Differential Fallback",
        provider_used="Clinical Knowledge Base (Offline Fallback)"
    )


def parse_llm_response(raw_text: str, profile: PatientProfile, provider: str) -> SymptomAnalysisResult:
    """Parses LLM response into structured SymptomAnalysisResult."""
    conditions: List[Dict[str, str]] = []
    lines = raw_text.splitlines()

    in_conditions = False
    for line in lines:
        line_clean = line.strip()
        if "POSSIBLE CONDITIONS" in line_clean.upper():
            in_conditions = True
            continue
        if in_conditions and (line_clean.startswith("3.") or "FOLLOW-UP" in line_clean.upper() or "MEDICAL ATTENTION" in line_clean.upper()):
            in_conditions = False
            break

        if in_conditions and line_clean:
            if line_clean.startswith(("-", "•", "*", "1.", "2.", "3.", "4.")):
                cond_text = line_clean.lstrip("-•* 0123456789.)").strip()
                if ":" in cond_text:
                    parts = cond_text.split(":", 1)
                    conditions.append({"name": parts[0].strip(), "reasoning": parts[1].strip()})
                elif "-" in cond_text:
                    parts = cond_text.split("-", 1)
                    conditions.append({"name": parts[0].strip(), "reasoning": parts[1].strip()})
                else:
                    conditions.append({"name": cond_text, "reasoning": "General association with reported symptom pattern."})

    if len(conditions) < 2:
        fallback = get_deterministic_fallback_analysis(profile)
        conditions = fallback.possible_conditions
        reasoning = fallback.general_reasoning
    else:
        reasoning = "The reported symptoms can occur across multiple distinct etiologies."

    return SymptomAnalysisResult(
        reported_symptoms=profile.extracted_symptoms if profile.extracted_symptoms else [profile.symptoms_text],
        possible_conditions=conditions[:4],
        general_reasoning=reasoning,
        clinical_note="These symptoms can occur in multiple conditions. The information provided is not sufficient to establish a diagnosis.",
        raw_response=raw_text,
        provider_used=provider
    )


def analyze_symptoms(profile: PatientProfile, missing_info: Optional[List[str]] = None) -> SymptomAnalysisResult:
    """
    Main entry point for Symptom Analysis (Part E - Q5).
    Selects provider (OpenAI GPT-4 if configured, else local Ollama, else heuristic fallback).
    """
    from dotenv import load_dotenv
    load_dotenv()

    system_prompt, user_prompt = build_gpt4_prompt(profile, missing_info)

    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest").strip()
    provider_pref = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    # 1. Try OpenAI if explicitly configured with valid key
    if provider_pref == "openai" and openai_key:
        print_info("Querying OpenAI GPT-4...")
        res = call_openai_gpt4(system_prompt, user_prompt, openai_key)
        if res:
            return parse_llm_response(res, profile, "OpenAI GPT-4")

    # 2. Try Ollama (Local LLM)
    print_info(f"Querying local Ollama model ({ollama_model})...")
    res = call_ollama(system_prompt, user_prompt, model=ollama_model, host=ollama_host)
    if res:
        return parse_llm_response(res, profile, f"Ollama ({ollama_model})")

    # 3. Fallback to clinical heuristic knowledge base
    print_warning("Local LLM not responding. Utilizing Clinical Knowledge Base fallback.")
    return get_deterministic_fallback_analysis(profile)


def display_symptom_analysis(result: SymptomAnalysisResult):
    """Renders preliminary symptom analysis matching Part E (Q5) sample output."""
    print_section("Symptom Analysis (Part E - Q5)")
    print_info(f"Analysis Engine: {result.provider_used}")
    print("\nSYMPTOM ANALYSIS")
    print("--------------------------------")
    print("Reported Symptoms:")
    for s in result.reported_symptoms:
        print(f"• {s}")

    print("\nPossible Conditions:")
    for cond in result.possible_conditions:
        name = cond.get("name", "")
        reasoning = cond.get("reasoning", "")
        print(f"• {name}")
        if reasoning:
            print(f"  Reasoning: {reasoning}")

    print("\nNote:")
    print(result.clinical_note)
    print("--------------------------------")
