"""
======================================================================
main.py - Master Application Orchestrator for Medical Symptom Assistant.
Course: 24CS2506 – Building Applications using GPT-4
Experiment 6 – AI-Powered Medical Symptom Assistant using GPT-4 / Ollama
======================================================================
Integrates all 10 core modules into a unified, interactive application
fulfilling Part K (Q11) and all 13 lab output screenshot requirements.
"""

import sys
import os
from typing import Optional, List, Dict, Any

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
    display_medical_attention,
    display_disclaimer_module
)
from modules.save_module import (
    build_structured_report,
    save_report_to_file,
    display_structured_report
)
from modules.utils import (
    print_banner,
    print_section,
    print_info,
    print_success,
    print_warning,
    display_key_value
)


class MedicalAssistantApp:
    """Master controller managing application state and the 9-option workflow."""

    def __init__(self):
        # Active session state
        self.profile: PatientProfile = get_default_sample_case()
        self.missing_info: List[str] = []
        self.system_prompt: str = ""
        self.user_prompt: str = ""
        self.analysis_result: Optional[SymptomAnalysisResult] = None
        self.follow_up_questions: List[str] = []
        self.risk_level: str = "Low"
        self.guidance: str = ""
        self.structured_report: str = ""
        self.saved_file_path: Optional[str] = None

    def display_home_screen(self):
        """Displays Home Screen banner and active status (Screenshot 1)."""
        print_banner(
            "AI-POWERED MEDICAL SYMPTOM ASSISTANT",
            "Experiment 6 | 24CS2506 - Building Applications using GPT-4"
        )
        status_info = {
            "Active Patient": f"{self.profile.age} y/o {self.profile.sex}",
            "Reported Severity": self.profile.severity,
            "Duration": self.profile.duration,
            "Symptoms Recorded": "Yes" if self.profile.symptoms_text else "Pending",
            "Symptoms Extracted": f"{len(self.profile.extracted_symptoms)} identified" if self.profile.extracted_symptoms else "Pending",
            "Analysis Status": "Completed" if self.analysis_result else "Pending"
        }
        display_key_value(status_info, title="Current Assistant Session State")

    def print_menu(self):
        """Prints the mandatory 9-option interactive menu matching Q11."""
        print("\n=============================================================")
        print("                   APPLICATION MAIN MENU                     ")
        print("=============================================================")
        print("  1. Enter Patient Information")
        print("  2. Enter Symptoms (Natural Language)")
        print("  3. Analyze Symptoms (Run GPT-4 / Ollama)")
        print("  4. Generate Follow-up Questions")
        print("  5. Display Possible Conditions")
        print("  6. Display Medical Attention Guidance")
        print("  7. Display Disclaimer")
        print("  8. Save Report (outputs/medical_analysis.txt)")
        print("  9. Exit")
        print("-------------------------------------------------------------")
        print("  L. Load Benchmark Case from CSV (Case 1 / Presets)")
        print("  D. Run Complete Automated Workflow Demo (All Steps)")
        print("  W. Launch Visual Web Dashboard (Browser GUI)")
        print("=============================================================")

    # -------------------------------------------------------------
    # Option Handlers
    # -------------------------------------------------------------
    def option_1_patient_info(self):
        """Option 1: Collects patient demographics and history (Part A - Q1)."""
        print_section("Option 1: Patient Information Input")
        choice = input("  Use interactive entry (I) or reload Lab Benchmark Case (B)? [Default: I]: ").strip().upper()
        if choice == "B":
            self.profile = get_default_sample_case()
            print_success("Benchmark reference patient loaded (22-yr Female, Mild, 2 days).")
        else:
            self.profile = collect_patient_interactive()

        display_key_value(self.profile.to_display_dict(), title="Verified Patient Profile")

    def option_2_enter_symptoms(self):
        """Option 2: Symptom entry and automated extraction & context analysis (Part B - Q2 & Part C - Q3)."""
        print_section("Option 2: Symptom Input & Extraction")
        self.profile = collect_symptoms_interactive(self.profile)

        # Run extraction
        self.profile.extracted_symptoms = extract_symptoms(self.profile.symptoms_text)
        display_extracted_symptoms(self.profile.extracted_symptoms, raw_text=self.profile.symptoms_text)

        # Run context analysis
        self.missing_info = analyze_context(self.profile)
        display_context_analysis(self.missing_info)

    def option_3_analyze_symptoms(self):
        """Option 3: Prompt generation and LLM differential analysis (Part D - Q4 & Part E - Q5)."""
        print_section("Option 3: Symptom Analysis (GPT-4 / Ollama)")

        if not self.profile.symptoms_text and not self.profile.extracted_symptoms:
            print_warning("No symptoms found. Loading default benchmark symptoms first.")
            self.profile = get_default_sample_case()

        if not self.profile.extracted_symptoms:
            self.profile.extracted_symptoms = extract_symptoms(self.profile.symptoms_text)

        if not self.missing_info:
            self.missing_info = analyze_context(self.profile)

        # Build and display prompt (Part D - Q4)
        self.system_prompt, self.user_prompt = build_gpt4_prompt(self.profile, self.missing_info)
        display_prompt_generation(self.system_prompt, self.user_prompt)

        # Execute LLM analysis (Part E - Q5)
        print_info("Connecting to AI engine to generate clinical possibilities...")
        self.analysis_result = analyze_symptoms(self.profile, self.missing_info)
        display_symptom_analysis(self.analysis_result)

        # Automatically compute risk assessment
        self.risk_level, self.guidance = assess_risk_and_guidance(self.profile)

    def option_4_generate_questions(self):
        """Option 4: Generate targeted follow-up questions (Part F - Q6)."""
        print_section("Option 4: Follow-up Questions")
        if not self.missing_info:
            self.missing_info = analyze_context(self.profile)
        self.follow_up_questions = generate_follow_up_questions(self.profile, self.missing_info)
        display_follow_up_questions(self.follow_up_questions)

    def option_5_display_conditions(self):
        """Option 5: Display possible conditions and reasoning (Part E - Q5)."""
        print_section("Option 5: Possible Conditions Display")
        if self.analysis_result is None:
            print_info("No analysis has been run yet. Running analysis now...")
            self.option_3_analyze_symptoms()
        else:
            display_symptom_analysis(self.analysis_result)

    def option_6_display_guidance(self):
        """Option 6: Display medical attention and escalation guidance (Part G - Q7)."""
        print_section("Option 6: Medical Attention Guidance")
        self.risk_level, self.guidance = assess_risk_and_guidance(self.profile)
        display_medical_attention(self.guidance, self.risk_level)

    def option_7_display_disclaimer(self):
        """Option 7: Display the mandatory non-diagnostic disclaimer (Part I - Q9)."""
        display_disclaimer_module()

    def option_8_save_report(self):
        """Option 8: Compile structured report and save to outputs/medical_analysis.txt (Part H - Q8 & Part J - Q10)."""
        print_section("Option 8: Save Structured Report")

        # Ensure all components exist
        if not self.profile.extracted_symptoms:
            self.profile.extracted_symptoms = extract_symptoms(self.profile.symptoms_text or "Fever, cough and sore throat")
        if not self.missing_info:
            self.missing_info = analyze_context(self.profile)
        if self.analysis_result is None:
            self.analysis_result = analyze_symptoms(self.profile, self.missing_info)
        if not self.follow_up_questions:
            self.follow_up_questions = generate_follow_up_questions(self.profile, self.missing_info)
        if not self.guidance:
            self.risk_level, self.guidance = assess_risk_and_guidance(self.profile)

        # Build report
        self.structured_report = build_structured_report(
            profile=self.profile,
            analysis=self.analysis_result,
            missing_info=self.missing_info,
            follow_up_questions=self.follow_up_questions,
            guidance=self.guidance,
            risk_level=self.risk_level
        )

        display_structured_report(self.structured_report)

        output_path = "outputs/medical_analysis.txt"
        self.saved_file_path = save_report_to_file(self.structured_report, output_path)
        print_success(f"Report successfully saved to: {self.saved_file_path}")

    def option_load_case(self):
        """Helper to inspect and load from sample_cases.csv."""
        print_section("Load Clinical Benchmark Case from CSV")
        cases = load_cases_from_csv("data/sample_cases.csv")
        if not cases:
            print_warning("No cases found in data/sample_cases.csv. Loading default benchmark case.")
            self.profile = get_default_sample_case()
            return

        print_info(f"Loaded {len(cases)} cases from data/sample_cases.csv.")
        print("  Available Quick Selections:")
        print("  1. CASE_001 (Benchmark: 22yo Female - Fever, cough, sore throat - Mild)")
        print("  2. CASE_002 (Acute Respiratory / High Risk)")
        print("  3. Pick by Case Number (1 - 250)")

        choice = input("\n  Enter selection [Default: 1]: ").strip()
        idx = 0
        if choice.isdigit() and 1 <= int(choice) <= len(cases):
            idx = int(choice) - 1

        selected = cases[idx]
        self.profile = PatientProfile.from_dict(selected)
        self.analysis_result = None  # Reset analysis for fresh case
        print_success(f"Loaded {selected.get('case_id', f'Case #{idx+1}')} successfully!")
        display_key_value(self.profile.to_display_dict(), title="Active Loaded Patient Profile")

    def run_automated_demo(self):
        """Runs the complete end-to-end pipeline automatically for quick review and screenshotting."""
        print_banner("RUNNING COMPLETE AUTOMATED LAB DEMONSTRATION")
        print_info("Executing all 8 pipeline phases sequentially...")

        # Step 1: Patient Profile
        self.profile = get_default_sample_case()
        display_key_value(self.profile.to_display_dict(), title="Phase 1: Patient Information (Q1)")

        # Step 2: Extraction
        self.profile.extracted_symptoms = extract_symptoms(self.profile.symptoms_text)
        display_extracted_symptoms(self.profile.extracted_symptoms, self.profile.symptoms_text)

        # Step 3: Context Analysis
        self.missing_info = analyze_context(self.profile)
        display_context_analysis(self.missing_info)

        # Step 4: Prompt Generation
        self.system_prompt, self.user_prompt = build_gpt4_prompt(self.profile, self.missing_info)
        display_prompt_generation(self.system_prompt, self.user_prompt)

        # Step 5: Symptom Analysis
        self.analysis_result = analyze_symptoms(self.profile, self.missing_info)
        display_symptom_analysis(self.analysis_result)

        # Step 6: Follow-up Questions
        self.follow_up_questions = generate_follow_up_questions(self.profile, self.missing_info)
        display_follow_up_questions(self.follow_up_questions)

        # Step 7: Medical Attention Guidance
        self.risk_level, self.guidance = assess_risk_and_guidance(self.profile)
        display_medical_attention(self.guidance, self.risk_level)

        # Step 8: Disclaimer
        display_disclaimer_module()

        # Step 9: Save Report
        self.option_8_save_report()

        print_banner("DEMO COMPLETED SUCCESSFULLY", "All lab requirements fulfilled & outputs/medical_analysis.txt saved")

    def run(self):
        """Main application interactive loop."""
        self.display_home_screen()

        while True:
            self.print_menu()
            choice = input("\n  Select an option (1-9, L, D): ").strip().upper()

            if choice == "1":
                self.option_1_patient_info()
            elif choice == "2":
                self.option_2_enter_symptoms()
            elif choice == "3":
                self.option_3_analyze_symptoms()
            elif choice == "4":
                self.option_4_generate_questions()
            elif choice == "5":
                self.option_5_display_conditions()
            elif choice == "6":
                self.option_6_display_guidance()
            elif choice == "7":
                self.option_7_display_disclaimer()
            elif choice == "8":
                self.option_8_save_report()
            elif choice == "9":
                print_info("Exiting Medical Symptom Assistant. Stay healthy!")
                break
            elif choice == "L":
                self.option_load_case()
            elif choice == "D":
                self.run_automated_demo()
            elif choice == "W":
                print_info("Starting visual web dashboard...")
                import app as web_app
                port = int(os.environ.get("PORT", 5000))
                web_app.app.run(host="0.0.0.0", port=port, debug=False)
                break
            else:
                print_warning(f"Invalid option '{choice}'. Please select between 1 and 9.")


if __name__ == "__main__":
    cli_args = [a.lower() for a in sys.argv[1:]]

    # Mode 1: Web Dashboard Server
    if any(arg in cli_args for arg in ["--web", "-w", "--server", "-s"]):
        import app as web_app
        port = int(os.environ.get("PORT", 5000))
        print_banner(
            "AURAHEALTH WEB SERVER STARTED",
            f"Access Dashboard at: http://localhost:{port}"
        )
        web_app.app.run(host="0.0.0.0", port=port, debug=False)

    # Mode 2: Automated Demo Pipeline
    elif any(arg in cli_args for arg in ["--demo", "--auto", "-d"]):
        cli_app = MedicalAssistantApp()
        cli_app.run_automated_demo()

    # Mode 3: Interactive CLI
    else:
        cli_app = MedicalAssistantApp()
        cli_app.run()

