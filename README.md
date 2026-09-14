# Business Automation OS

**Business Automation OS** is our Fourth-Year BE Final Year Project — an agentic platform designed to automate end-to-end business workflows across **recruitment, employee onboarding, leave management, procurement, and more**.

## Overview

Business Automation OS is a general-purpose agentic system focused on understanding, coordinating, and executing business workflows with minimal manual intervention.

Instead of building a separate application for every business process, the system provides a common automation platform where different workflows can be built and orchestrated using **AI agents, workflow logic, business rules, tools, and external integrations**.

The platform is designed to support human oversight where required while automating repetitive coordination and decision-support tasks.

## Initial Use Case — Recruitment Automation

The first major workflow being implemented is an **end-to-end recruitment automation system**.

The recruitment workflow aims to automate:

- Resume screening against a Job Description
- Candidate pre-interview assessments
- AI-led interviews
- Interview and assessment proctoring
- Calendar-based interview scheduling
- Candidate evaluation
- Final evaluation and recommendation reports

The goal is to reduce manual coordination while maintaining a **structured, auditable, and consistent recruitment process**.

## Planned Business Workflows

The Business Automation OS is designed to support multiple business processes.

### Recruitment

Automate the candidate journey from resume screening to final evaluation.

### Employee Onboarding

Automate onboarding activities such as:

- Document collection
- Task assignment
- Approval workflows
- Account setup
- Onboarding checklists
- Notifications and follow-ups

### Employee Leave Management

Automate:

- Leave requests
- Policy validation
- Manager approvals
- Notifications
- Calendar updates
- Leave tracking

### Procurement

Automate procurement workflows including:

- Purchase requests
- Approval workflows
- Vendor interactions
- Purchase orders
- Procurement tracking
- Notifications and follow-ups

### Future Workflows

The platform can be extended to support additional business workflows as the system evolves.

## Core Concept

The system is built around an **agentic workflow orchestration model**.

```text
                         Business Automation OS
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
              Agents          Workflows          Tools
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                         Business Processes
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
        Recruitment          Onboarding           Procurement
             │                    │                    │
      Resume Screening      Task Automation       Approvals
      AI Interview          Documents             Vendors
      Proctoring            Accounts              Purchase Orders
      Scheduling            Notifications         Tracking
      Evaluation
```

## Resume <-> JD Matching (Screening)

Week 1–2 screening agent: parse a resume, score it against a job description with Groq, and return structured JSON for the orchestrator / DB layer.

### Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GROQ_API_KEY`. On Windows PowerShell:

```powershell
Copy-Item .env.example .env
$env:GROQ_API_KEY = "gsk_..."
```

### Run

```bash
python -m screening.main --resume samples/sample_resume.txt --jd samples/sample_jd.txt
python -m screening.main --resume-dir samples --jd samples/sample_jd.txt
python -m unittest discover -s tests -v
```

### Orchestrator integration

```python
from screening import parse_resume, match_resume_to_jd

resume_text = parse_resume("candidate.pdf")
result = match_resume_to_jd(resume_text, jd_text)

if result.is_shortlisted():  # default threshold 60
    save_to_db(candidate_id, result.to_dict())
```

`match_batch()` scores many candidates; `sort_by_score()` ranks them. Shortlist threshold can be set with `SHORTLIST_THRESHOLD` in `.env`. Default model is `openai/gpt-oss-20b` (`GROQ_MODEL`).

### Interactive Showcase Dashboard

Open the standalone HTML dashboard directly in your browser:

```powershell
Start-Process dashboard.html
```

Or open `dashboard.html` in any modern web browser. Features:
- Candidate profile presets and animated radial scoring gauge
- Drag-and-drop resume intake & client-side screening parser
- Direct terminal JSON paste & live re-rendering
- Formatted report export / print to PDF

