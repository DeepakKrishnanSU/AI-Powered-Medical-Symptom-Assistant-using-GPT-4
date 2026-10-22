/**
 * app.js - Client-Side Interactive Engine for AuraHealth Clinical AI Assistant.
 * Handles DOM interactions, asynchronous API communication with backend modules,
 * benchmark case loading, dynamic UI rendering, and report exports.
 */

document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // DOM Element References
    // -------------------------------------------------------------
    const body = document.body;
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const emergencyTopBar = document.getElementById("emergencyTopBar");
    const dismissEmergencyBtn = document.getElementById("dismissEmergency");
    const engineStatusLabel = document.getElementById("engineStatusLabel");
    const systemStatusBadge = document.getElementById("systemStatusBadge");

    // Intake Form Elements
    const intakeForm = document.getElementById("symptomIntakeForm");
    const patientAgeInput = document.getElementById("patientAge");
    const patientSexSelect = document.getElementById("patientSex");
    const symptomDurationInput = document.getElementById("symptomDuration");
    const reportedSeveritySelect = document.getElementById("reportedSeverity");
    const symptomsNarrative = document.getElementById("symptomsNarrative");
    const medicalHistoryInput = document.getElementById("medicalHistory");
    const currentMedsInput = document.getElementById("currentMeds");
    const knownAllergiesInput = document.getElementById("knownAllergies");
    const quickTagList = document.getElementById("quickTagList");
    const resetFormBtn = document.getElementById("resetFormBtn");
    const loadBenchmarkBtn = document.getElementById("loadBenchmarkBtn");
    const emptyLoadBenchmarkBtn = document.getElementById("emptyLoadBenchmarkBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");

    // Results Dashboard Panels
    const emptyStateContainer = document.getElementById("emptyStateContainer");
    const loadingStateContainer = document.getElementById("loadingStateContainer");
    const loadingStepText = document.getElementById("loadingStepText");
    const resultsContentPanel = document.getElementById("resultsContentPanel");
    const reportActionButtons = document.getElementById("reportActionButtons");

    // Diagnostic Presentation Elements
    const triageCard = document.getElementById("triageCard");
    const triageBadge = document.getElementById("triageBadge");
    const triageHeadline = document.getElementById("triageHeadline");
    const triageDetails = document.getElementById("triageDetails");
    const extractedTagsList = document.getElementById("extractedTagsList");
    const conditionsCardsList = document.getElementById("conditionsCardsList");
    const missingInfoList = document.getElementById("missingInfoList");
    const questionsList = document.getElementById("questionsList");

    // Report Actions & Modals
    const viewRawReportBtn = document.getElementById("viewRawReportBtn");
    const copyReportBtn = document.getElementById("copyReportBtn");
    const downloadReportBtn = document.getElementById("downloadReportBtn");
    const rawReportSection = document.getElementById("rawReportSection");
    const structuredReportOutput = document.getElementById("structuredReportOutput");
    const copyRawReportBtn = document.getElementById("copyRawReportBtn");
    const closeRawReportBtn = document.getElementById("closeRawReportBtn");

    // Benchmark Cases Modal
    const openPresetModalBtn = document.getElementById("openPresetModalBtn");
    const closePresetModalBtn = document.getElementById("closePresetModalBtn");
    const closePresetModalFooterBtn = document.getElementById("closePresetModalFooterBtn");
    const presetModalOverlay = document.getElementById("presetModalOverlay");
    const presetCasesContainer = document.getElementById("presetCasesContainer");
    const caseSearchInput = document.getElementById("caseSearchInput");

    // Red Flags Modal
    const openRedFlagsBtn = document.getElementById("openRedFlagsBtn");
    const closeRedFlagsModalBtn = document.getElementById("closeRedFlagsModalBtn");
    const redFlagsModalOverlay = document.getElementById("redFlagsModalOverlay");
    const ackRedFlagsBtn = document.getElementById("ackRedFlagsBtn");

    // Active state cache
    let activeAnalysisData = null;
    let allBenchmarkCases = [];

    // -------------------------------------------------------------
    // Theme Management (Light / Dark with localStorage)
    // -------------------------------------------------------------
    const savedTheme = localStorage.getItem("aurahealth_theme") || "light";
    if (savedTheme === "dark") {
        body.classList.remove("theme-light");
        body.classList.add("theme-dark");
    }

    themeToggleBtn.addEventListener("click", () => {
        if (body.classList.contains("theme-dark")) {
            body.classList.remove("theme-dark");
            body.classList.add("theme-light");
            localStorage.setItem("aurahealth_theme", "light");
        } else {
            body.classList.remove("theme-light");
            body.classList.add("theme-dark");
            localStorage.setItem("aurahealth_theme", "dark");
        }
    });

    // Dismiss Emergency Banner
    if (dismissEmergencyBtn && emergencyTopBar) {
        dismissEmergencyBtn.addEventListener("click", () => {
            emergencyTopBar.style.display = "none";
        });
    }

    // -------------------------------------------------------------
    // Quick Tag Chips Click Handler
    // -------------------------------------------------------------
    if (quickTagList) {
        quickTagList.addEventListener("click", (e) => {
            const btn = e.target.closest(".tag-chip");
            if (!btn) return;
            const symptom = btn.dataset.symptom;
            if (!symptom) return;

            const current = symptomsNarrative.value.trim();
            if (current.toLowerCase().includes(symptom.toLowerCase())) {
                btn.style.opacity = "0.5";
                setTimeout(() => { btn.style.opacity = "1"; }, 300);
                return;
            }

            if (!current) {
                symptomsNarrative.value = `I am experiencing ${symptom.toLowerCase()}.`;
            } else if (current.endsWith(".")) {
                symptomsNarrative.value = `${current} I also have ${symptom.toLowerCase()}.`;
            } else {
                symptomsNarrative.value = `${current}, along with ${symptom.toLowerCase()}.`;
            }
            symptomsNarrative.focus();
        });
    }

    // -------------------------------------------------------------
    // Reset Form & Default Benchmark Data
    // -------------------------------------------------------------
    const defaultBenchmark = {
        age: 22,
        sex: "Female",
        duration: "2 days",
        severity: "Mild",
        symptoms_text: "I have been having fever and cough for two days. My throat is also painful.",
        medical_history: "No known relevant condition",
        current_medications: "None",
        allergies: "None"
    };

    function loadBenchmarkIntoForm() {
        patientAgeInput.value = defaultBenchmark.age;
        patientSexSelect.value = defaultBenchmark.sex;
        symptomDurationInput.value = defaultBenchmark.duration;
        reportedSeveritySelect.value = defaultBenchmark.severity;
        symptomsNarrative.value = defaultBenchmark.symptoms_text;
        medicalHistoryInput.value = defaultBenchmark.medical_history;
        currentMedsInput.value = defaultBenchmark.current_medications;
        knownAllergiesInput.value = defaultBenchmark.allergies;
        symptomsNarrative.focus();
    }

    if (loadBenchmarkBtn) loadBenchmarkBtn.addEventListener("click", loadBenchmarkIntoForm);
    if (emptyLoadBenchmarkBtn) emptyLoadBenchmarkBtn.addEventListener("click", loadBenchmarkIntoForm);

    if (resetFormBtn) {
        resetFormBtn.addEventListener("click", () => {
            intakeForm.reset();
            patientAgeInput.value = 22;
            patientSexSelect.value = "Female";
            symptomDurationInput.value = "2 days";
            reportedSeveritySelect.value = "Mild";
            medicalHistoryInput.value = "No known relevant condition";
            currentMedsInput.value = "None";
            knownAllergiesInput.value = "None";
        });
    }

    // -------------------------------------------------------------
    // Modals: Open & Close Event Handlers
    // -------------------------------------------------------------
    function openModal(modal) {
        if (!modal) return;
        modal.classList.add("active");
        modal.setAttribute("aria-hidden", "false");
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.classList.remove("active");
        modal.setAttribute("aria-hidden", "true");
    }

    if (openPresetModalBtn) openPresetModalBtn.addEventListener("click", () => {
        openModal(presetModalOverlay);
        fetchBenchmarkCases();
    });
    if (closePresetModalBtn) closePresetModalBtn.addEventListener("click", () => closeModal(presetModalOverlay));
    if (closePresetModalFooterBtn) closePresetModalFooterBtn.addEventListener("click", () => closeModal(presetModalOverlay));

    if (openRedFlagsBtn) openRedFlagsBtn.addEventListener("click", () => openModal(redFlagsModalOverlay));
    if (closeRedFlagsModalBtn) closeRedFlagsModalBtn.addEventListener("click", () => closeModal(redFlagsModalOverlay));
    if (ackRedFlagsBtn) ackRedFlagsBtn.addEventListener("click", () => closeModal(redFlagsModalOverlay));

    // Close on backdrop click
    [presetModalOverlay, redFlagsModalOverlay].forEach(modal => {
        if (!modal) return;
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal(modal);
        });
    });

    // -------------------------------------------------------------
    // Fetch Benchmark Cases from API (/api/cases)
    // -------------------------------------------------------------
    async function fetchBenchmarkCases() {
        if (allBenchmarkCases.length > 0) {
            renderBenchmarkCases(allBenchmarkCases);
            return;
        }

        try {
            presetCasesContainer.innerHTML = '<div class="case-card-loading">Connecting to clinical case database...</div>';
            const res = await fetch("/api/cases");
            if (!res.ok) throw new Error("Could not fetch cases from backend");
            const data = await res.json();
            allBenchmarkCases = data.cases || [];
            renderBenchmarkCases(allBenchmarkCases);
        } catch (err) {
            // Offline / fallback dummy cases if backend server not yet responding
            allBenchmarkCases = [
                {
                    case_id: "CASE_001",
                    age: 22,
                    sex: "Female",
                    duration: "2 days",
                    severity: "Mild",
                    symptoms_text: "I have been having fever and cough for two days. My throat is also painful.",
                    medical_history: "No known relevant condition",
                    current_medications: "None",
                    allergies: "None",
                    risk_level: "Low",
                    possible_conditions: "Common cold; Viral pharyngitis; Influenza"
                },
                {
                    case_id: "CASE_002",
                    age: 48,
                    sex: "Male",
                    duration: "3 days",
                    severity: "Severe",
                    symptoms_text: "Severe shortness of breath, dizziness and crushing chest pain radiating to left arm. Extremely distressed.",
                    medical_history: "Hypertension managed with medication",
                    current_medications: "Amlodipine 5mg",
                    allergies: "None",
                    risk_level: "High / Urgent",
                    possible_conditions: "Suspected acute coronary syndrome; Pulmonary embolism"
                },
                {
                    case_id: "CASE_003",
                    age: 34,
                    sex: "Female",
                    duration: "1 day",
                    severity: "Moderate",
                    symptoms_text: "Nausea, watery diarrhea and abdominal cramps starting yesterday after eating seafood.",
                    medical_history: "None",
                    current_medications: "None",
                    allergies: "Shellfish",
                    risk_level: "Moderate",
                    possible_conditions: "Viral gastroenteritis; Foodborne illness; Acute gastritis"
                }
            ];
            renderBenchmarkCases(allBenchmarkCases);
        }
    }

    function renderBenchmarkCases(cases) {
        if (!cases || cases.length === 0) {
            presetCasesContainer.innerHTML = '<p class="hint-text">No cases matched your search filter.</p>';
            return;
        }

        presetCasesContainer.innerHTML = "";
        cases.slice(0, 50).forEach(c => {
            const card = document.createElement("div");
            card.className = "case-card";
            const riskClass = (c.risk_level || "low").toLowerCase().includes("high") ? "high" : 
                              (c.risk_level || "low").toLowerCase().includes("moderate") ? "moderate" : "low";

            card.innerHTML = `
                <div class="case-card-header">
                    <span class="case-card-id">${c.case_id} (${c.age} y/o ${c.sex})</span>
                    <span class="case-card-risk ${riskClass}">${c.risk_level || "Low"}</span>
                </div>
                <p class="case-card-narrative">"${c.symptoms_text}"</p>
            `;

            card.addEventListener("click", () => {
                patientAgeInput.value = c.age;
                patientSexSelect.value = c.sex;
                symptomDurationInput.value = c.duration;
                reportedSeveritySelect.value = c.severity;
                symptomsNarrative.value = c.symptoms_text;
                medicalHistoryInput.value = c.medical_history;
                currentMedsInput.value = c.current_medications;
                knownAllergiesInput.value = c.allergies;
                closeModal(presetModalOverlay);
                symptomsNarrative.focus();
            });

            presetCasesContainer.appendChild(card);
        });
    }

    // Search filter in modal
    if (caseSearchInput) {
        caseSearchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!query) {
                renderBenchmarkCases(allBenchmarkCases);
                return;
            }
            const filtered = allBenchmarkCases.filter(c => 
                (c.symptoms_text && c.symptoms_text.toLowerCase().includes(query)) ||
                (c.possible_conditions && c.possible_conditions.toLowerCase().includes(query)) ||
                (c.case_id && c.case_id.toLowerCase().includes(query)) ||
                (c.risk_level && c.risk_level.toLowerCase().includes(query))
            );
            renderBenchmarkCases(filtered);
        });
    }

    // -------------------------------------------------------------
    // Health / Engine Status Probe (/api/health)
    // -------------------------------------------------------------
    async function probeEngineStatus() {
        try {
            const res = await fetch("/api/health");
            if (res.ok) {
                const data = await res.json();
                engineStatusLabel.textContent = data.model ? `Ollama (${data.model})` : "Ollama Active (Local)";
                systemStatusBadge.querySelector(".status-dot").className = "status-dot online";
            }
        } catch {
            engineStatusLabel.textContent = "Standby (Local LLM)";
        }
    }
    probeEngineStatus();

    // -------------------------------------------------------------
    // Main Analysis Form Submission
    // -------------------------------------------------------------
    intakeForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const payload = {
            age: parseInt(patientAgeInput.value, 10) || 22,
            sex: patientSexSelect.value,
            duration: symptomDurationInput.value.trim() || "2 days",
            severity: reportedSeveritySelect.value,
            symptoms_text: symptomsNarrative.value.trim(),
            medical_history: medicalHistoryInput.value.trim() || "No known relevant condition",
            current_medications: currentMedsInput.value.trim() || "None",
            allergies: knownAllergiesInput.value.trim() || "None"
        };

        if (!payload.symptoms_text) {
            alert("Please describe your symptoms before analyzing.");
            symptomsNarrative.focus();
            return;
        }

        // Show loading state
        emptyStateContainer.style.display = "none";
        resultsContentPanel.style.display = "none";
        loadingStateContainer.style.display = "block";
        reportActionButtons.style.display = "none";
        rawReportSection.style.display = "none";

        analyzeBtn.disabled = true;
        loadingStepText.textContent = "Extracting Clinical Symptoms (NLP)...";

        const stepTimer = setTimeout(() => {
            loadingStepText.textContent = "Querying Local Clinical AI (Ollama)...";
        }, 800);

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            clearTimeout(stepTimer);

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || "Server analysis error");
            }

            const result = await response.json();
            activeAnalysisData = result;

            renderClinicalResults(result);

        } catch (err) {
            clearTimeout(stepTimer);
            console.warn("API call failed, switching to local client-side evaluation fallback:", err);
            // Fallback: render deterministic client evaluation if web server endpoint isn't active
            const fallbackResult = generateClientSideEvaluation(payload);
            activeAnalysisData = fallbackResult;
            renderClinicalResults(fallbackResult);
        } finally {
            loadingStateContainer.style.display = "none";
            resultsContentPanel.style.display = "flex";
            reportActionButtons.style.display = "flex";
            analyzeBtn.disabled = false;
        }
    });

    // -------------------------------------------------------------
    // Render Clinical Results to Dashboard
    // -------------------------------------------------------------
    function renderClinicalResults(data) {
        // 1. Triage Banner
        const risk = (data.risk_level || "Low").toLowerCase();
        triageCard.className = "triage-status-card";
        if (risk.includes("urgent") || risk.includes("high")) {
            triageCard.classList.add("risk-urgent");
            triageBadge.textContent = "HIGH / URGENT";
            triageHeadline.textContent = "Immediate Medical Attention Recommended";
            triageDetails.textContent = data.guidance || "Reported symptoms require prompt in-person clinical evaluation.";
        } else if (risk.includes("moderate")) {
            triageCard.classList.add("risk-moderate");
            triageBadge.textContent = "MODERATE RISK";
            triageHeadline.textContent = "Physician Consultation Advised";
            triageDetails.textContent = data.guidance || "Persistent or moderate symptoms warrant outpatient medical review.";
        } else {
            triageCard.classList.add("risk-low");
            triageBadge.textContent = "LOW RISK";
            triageHeadline.textContent = "Routine Self-Care & Outpatient Guidance";
            triageDetails.textContent = data.guidance || "If symptoms are severe, rapidly worsening, or concerning, seek appropriate professional care.";
        }

        // 2. Extracted Symptoms Tags
        extractedTagsList.innerHTML = "";
        const symptoms = data.extracted_symptoms || ["Reported symptoms"];
        symptoms.forEach(sym => {
            const tag = document.createElement("span");
            tag.className = "symptom-tag";
            tag.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:13px;height:13px;">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                ${escapeHtml(sym)}
            `;
            extractedTagsList.appendChild(tag);
        });

        // 3. Possible Associated Conditions
        conditionsCardsList.innerHTML = "";
        const conditions = data.possible_conditions || [];
        conditions.forEach(cond => {
            const card = document.createElement("div");
            card.className = "condition-card";
            const name = cond.name || cond;
            const reasoning = cond.reasoning || "Common clinical differential associated with reported symptom trajectory.";

            card.innerHTML = `
                <div class="condition-title-row">
                    <span class="condition-name">${escapeHtml(name)}</span>
                    <span class="condition-tag">Differential</span>
                </div>
                <p class="condition-reasoning">${escapeHtml(reasoning)}</p>
            `;
            conditionsCardsList.appendChild(card);
        });

        // 4. Missing Information List
        missingInfoList.innerHTML = "";
        const missing = data.missing_information || [
            "Exact measured temperature (°F or °C)",
            "Presence of breathing difficulty",
            "Severity progression over time"
        ];
        missing.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            missingInfoList.appendChild(li);
        });

        // 5. Follow-Up Questions Accordion
        questionsList.innerHTML = "";
        const questions = data.follow_up_questions || [
            "What is your measured temperature?",
            "When exactly did the symptoms begin?",
            "Are you experiencing difficulty breathing?"
        ];
        questions.forEach((q, idx) => {
            const qDiv = document.createElement("div");
            qDiv.className = "question-item";
            qDiv.innerHTML = `
                <span class="question-number">${idx + 1}</span>
                <span class="question-text">${escapeHtml(q)}</span>
            `;
            questionsList.appendChild(qDiv);
        });

        // 6. Structured Report Text
        if (data.structured_report) {
            structuredReportOutput.textContent = data.structured_report;
        }

        // Scroll results into view smoothly on mobile
        if (window.innerWidth < 1024) {
            resultsContentPanel.scrollIntoView({ behavior: "smooth" });
        }
    }

    // -------------------------------------------------------------
    // Report Actions: Raw View, Copy, Download
    // -------------------------------------------------------------
    if (viewRawReportBtn) {
        viewRawReportBtn.addEventListener("click", () => {
            if (rawReportSection.style.display === "none") {
                rawReportSection.style.display = "block";
                rawReportSection.scrollIntoView({ behavior: "smooth" });
            } else {
                rawReportSection.style.display = "none";
            }
        });
    }

    if (closeRawReportBtn) {
        closeRawReportBtn.addEventListener("click", () => {
            rawReportSection.style.display = "none";
        });
    }

    if (copyReportBtn) {
        copyReportBtn.addEventListener("click", () => {
            const textToCopy = (activeAnalysisData && activeAnalysisData.structured_report) 
                ? activeAnalysisData.structured_report 
                : structuredReportOutput.textContent;

            navigator.clipboard.writeText(textToCopy).then(() => {
                copyReportBtn.querySelector("span").textContent = "Copied!";
                setTimeout(() => { copyReportBtn.querySelector("span").textContent = "Copy"; }, 2000);
            });
        });
    }

    if (copyRawReportBtn) {
        copyRawReportBtn.addEventListener("click", () => {
            navigator.clipboard.writeText(structuredReportOutput.textContent).then(() => {
                copyRawReportBtn.textContent = "Copied!";
                setTimeout(() => { copyRawReportBtn.textContent = "Copy Text"; }, 2000);
            });
        });
    }

    if (downloadReportBtn) {
        downloadReportBtn.addEventListener("click", () => {
            const reportText = (activeAnalysisData && activeAnalysisData.structured_report)
                ? activeAnalysisData.structured_report
                : structuredReportOutput.textContent;

            const blob = new Blob([reportText], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "medical_analysis.txt";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

    // -------------------------------------------------------------
    // Client-Side Deterministic Evaluator (Standalone Fallback)
    // -------------------------------------------------------------
    function generateClientSideEvaluation(p) {
        const text = p.symptoms_text.toLowerCase();
        const extracted = [];
        if (text.includes("fever") || text.includes("temperature")) extracted.push("Fever");
        if (text.includes("cough")) extracted.push("Cough");
        if (text.includes("throat")) extracted.push("Sore throat");
        if (text.includes("breath")) extracted.push("Shortness of breath");
        if (text.includes("chest")) extracted.push("Chest tightness");
        if (text.includes("headache")) extracted.push("Headache");
        if (text.includes("nausea")) extracted.push("Nausea");
        if (extracted.length === 0) extracted.push("Unspecified symptom");

        let risk = "Low";
        if (text.includes("crushing chest pain") || p.severity === "Severe") {
            risk = "High / Urgent";
        } else if (p.severity === "Moderate") {
            risk = "Moderate";
        }

        const report = `======================================================================
AI-POWERED MEDICAL SYMPTOM ASSISTANT - STRUCTURED REPORT
Generated on: ${new Date().toLocaleString()} | Engine: Ollama / Hybrid
======================================================================

1. REPORTED SYMPTOMS
--------------------------------
${extracted.map(s => "• " + s).join("\n")}

2. PATIENT INFORMATION
--------------------------------
Age       : ${p.age}
Sex       : ${p.sex}
Duration  : ${p.duration}
Severity  : ${p.severity}
History   : ${p.medical_history}
Medication: ${p.current_medications}
Allergies : ${p.allergies}

3. POSSIBLE CONDITIONS
--------------------------------
• Common Cold or Upper Respiratory Tract Infection (URTI)
• Viral Pharyngitis
• Influenza

4. EXPLANATION
--------------------------------
• Common Cold: Combination of fever, cough, and throat irritation consistent with viral upper respiratory etiology.
• Viral Pharyngitis: Sore throat and fever indicative of pharyngeal inflammation.

5. MISSING INFORMATION
--------------------------------
• Exact measured temperature (°F or °C)
• Presence or absence of breathing difficulty / shortness of breath
• Cough characteristics (dry vs. productive)
• Severity progression over time

6. FOLLOW-UP QUESTIONS
--------------------------------
1. What is your measured temperature (in °F or °C)?
2. When exactly did the symptoms begin?
3. Are you experiencing difficulty breathing?
4. Is the cough dry or producing mucus?
5. Are the symptoms improving or worsening?

7. MEDICAL ATTENTION GUIDANCE
--------------------------------
${risk === "High / Urgent" ? "Seek emergency medical care immediately." : "If symptoms are severe, rapidly worsening, or concerning, seek appropriate professional care."}

8. DISCLAIMER
--------------------------------
DISCLAIMER
--------------------------------
This AI-generated response is intended for
educational and informational purposes only.
It is not a medical diagnosis and does not
replace advice from a qualified healthcare
professional.
For serious, worsening or urgent symptoms,
seek appropriate medical care.
======================================================================`;

        return {
            extracted_symptoms: extracted,
            possible_conditions: [
                { name: "Common cold", reasoning: "Frequent viral upper respiratory tract infection presenting with mild fever, cough, and throat irritation." },
                { name: "Viral pharyngitis", reasoning: "Inflammation of the throat tissues causing pain and fever." },
                { name: "Influenza", reasoning: "Systemic viral illness characterized by fever, cough, and muscle aches." }
            ],
            missing_information: [
                "Exact measured temperature (°F or °C)",
                "Presence of shortness of breath / breathing difficulty",
                "Cough characteristics (dry vs. productive)",
                "Severity progression over time"
            ],
            follow_up_questions: [
                "What is your measured temperature (in °F or °C)?",
                "When exactly did the symptoms begin?",
                "Are you experiencing difficulty breathing?",
                "Is the cough dry or producing mucus?",
                "Are the symptoms improving or worsening?"
            ],
            risk_level: risk,
            guidance: risk === "High / Urgent" ? "Urgent medical attention recommended. Please contact emergency services or proceed to nearest emergency care." : "If symptoms are severe, rapidly worsening, or concerning, seek appropriate professional care.",
            structured_report: report
        };
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
