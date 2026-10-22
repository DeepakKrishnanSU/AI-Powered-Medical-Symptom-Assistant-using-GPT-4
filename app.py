"""
app.py - Web Server Entry Point for AuraHealth Clinical AI Assistant.
Connects the modern HTML/CSS/JS frontend to the core modular Python backend.
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

from modules.profile_module import PatientProfile
from modules.input_module import load_cases_from_csv, get_default_sample_case
from modules.symptom_module import extract_symptoms
from modules.context_module import analyze_context
from modules.prompt_module import build_gpt4_prompt, get_full_prompt_text
from modules.analysis_module import analyze_symptoms
from modules.question_module import generate_follow_up_questions
from modules.safety_module import assess_risk_and_guidance, get_disclaimer
from modules.save_module import build_structured_report, save_report_to_file
from modules.utils import print_banner, print_info, print_success

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


@app.route("/")
def index():
    """Serves the main clinical dashboard frontend."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/css/<path:filename>")
def serve_css(filename):
    """Serves CSS stylesheets."""
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    """Serves JavaScript application files."""
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health probe verifying Ollama model configuration and engine availability."""
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    provider = os.getenv("LLM_PROVIDER", "ollama")

    return jsonify({
        "status": "online",
        "provider": provider,
        "model": ollama_model,
        "host": ollama_host
    })


@app.route("/api/cases", methods=["GET"])
def get_benchmark_cases():
    """Returns clinical benchmark cases loaded from data/sample_cases.csv."""
    csv_path = os.path.join(BASE_DIR, "data", "sample_cases.csv")
    cases = load_cases_from_csv(csv_path)
    return jsonify({
        "total": len(cases),
        "cases": cases
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_patient_symptoms():
    """
    Main API endpoint: Executes the full clinical AI pipeline:
    Extraction -> Context Analysis -> LLM Analysis -> Questions -> Safety -> Report
    """
    data = request.get_json() or {}

    profile = PatientProfile(
        age=int(data.get("age", 22)),
        sex=str(data.get("sex", "Female")),
        symptoms_text=str(data.get("symptoms_text", "")),
        duration=str(data.get("duration", "2 days")),
        severity=str(data.get("severity", "Mild")),
        medical_history=str(data.get("medical_history", "No known relevant condition")),
        current_medications=str(data.get("current_medications", "None")),
        allergies=str(data.get("allergies", "None"))
    )

    # 1. Symptom Extraction (Part B - Q2)
    extracted = extract_symptoms(profile.symptoms_text)
    profile.extracted_symptoms = extracted

    # 2. Context Analysis (Part C - Q3)
    missing_info = analyze_context(profile)

    # 3. Prompt Construction (Part D - Q4)
    system_prompt, user_prompt = build_gpt4_prompt(profile, missing_info)

    # 4. LLM Differential Analysis (Part E - Q5)
    analysis = analyze_symptoms(profile, missing_info)

    # 5. Follow-Up Questions (Part F - Q6)
    questions = generate_follow_up_questions(profile, missing_info)

    # 6. Safety & Escalation Guidance (Part G - Q7 & Part I - Q9)
    risk_level, guidance = assess_risk_and_guidance(profile)

    # 7. Structured Report Assembly (Part H - Q8)
    report_text = build_structured_report(
        profile=profile,
        analysis=analysis,
        missing_info=missing_info,
        follow_up_questions=questions,
        guidance=guidance,
        risk_level=risk_level
    )

    # 8. Persist to outputs/medical_analysis.txt (Part J - Q10)
    output_path = os.path.join(BASE_DIR, "outputs", "medical_analysis.txt")
    save_report_to_file(report_text, output_path)

    return jsonify({
        "patient": profile.to_dict(),
        "extracted_symptoms": extracted,
        "missing_information": missing_info,
        "possible_conditions": analysis.possible_conditions,
        "general_reasoning": analysis.general_reasoning,
        "follow_up_questions": questions,
        "risk_level": risk_level,
        "guidance": guidance,
        "disclaimer": get_disclaimer(),
        "structured_report": report_text,
        "saved_to": output_path
    })


@app.route("/api/save-report", methods=["POST"])
def save_report():
    """Explicitly saves report text to outputs/medical_analysis.txt."""
    data = request.get_json() or {}
    report_text = data.get("report_text", "")
    if not report_text:
        return jsonify({"error": "No report content provided"}), 400

    output_path = os.path.join(BASE_DIR, "outputs", "medical_analysis.txt")
    saved_path = save_report_to_file(report_text, output_path)
    return jsonify({
        "status": "saved",
        "file_path": saved_path
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print_banner(
        "AURAHEALTH WEB SERVER STARTED",
        f"Access Dashboard at: http://localhost:{port}"
    )
    print_info(f"Serving web application from: {FRONTEND_DIR}")
    print_success("Connected to local Ollama and modules.")
    app.run(host="0.0.0.0", port=port, debug=False)
