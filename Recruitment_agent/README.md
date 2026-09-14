# Recruitment Agent

Recruitment Agent is the recruitment module of **Business Automation OS**. It provides backend APIs for managing jobs, candidates, applications, candidate screening, assessments, test attempts, answers, and scoring.

---

## Current Status

The current MVP backend includes:
- Job management
- Candidate management
- Application management
- Candidate screening records
- Tests
- Questions
- Test attempts
- Answers
- MCQ answer evaluation
- Assessment scoring
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- FastAPI REST APIs

The project is currently focused on building the backend and database foundation for the recruitment workflow.

---

## Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python** | Backend programming language |
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM |
| **PostgreSQL** | Relational database |
| **Alembic** | Database migrations |
| **Pydantic** | Request/response validation |
| **Uvicorn** | ASGI server |

---

## Project Structure

```text
Recruitment_agent/       <-- ROOT DIRECTORY (Execute Setup & Migrations Here)
│
├── app/                  <-- APP DIRECTORY (Execute Uvicorn Server Here)
│   ├── routers/
│   ├── schemas/
│   ├── __init__.py
│   ├── create_tables.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── test_db.py
│
├── alembic/
│   └── versions/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Setup & Virtual Environment Management

Follow these sequential steps to set up your isolated environment, configure dependencies, and align your code editor:

### 1. Clone and Navigate
Clone the repository and enter the workspace root folder:
```bash
git clone <repository-url>
cd Recruitment_agent
```

### 2. Configure Your IDE / VS Code Interpreter
To remove import warnings and enable autocomplete:
1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS) to open the Command Palette.
2. Select **Python: Select Interpreter**.
3. Set it to explicitly point to the local instance: `.\.venv\Scripts\python.exe` (Windows) or `./.venv/bin/python` (macOS/Linux).

### 3. Initialize and Activate the Virtual Environment
Always initialize and activate your environment from the `Recruitment_agent` **root directory** to guarantee dependencies map seamlessly:

* **Windows (PowerShell / CMD):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

*Verification:* Your terminal prompt will change to show `(.venv) PS C:\...>`, confirming isolation is active.

### 4. Install Project Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` configuration template file at the project root level using `.env.example` as your reference:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/recruitment_db
```
*Note: Do not check `.env` into git version control.*

### 6. Create the Database Engine Target
Confirm your PostgreSQL database instance manager is running locally, then initialize a structural workspace matching your URL string:
```sql
CREATE DATABASE recruitment_db;
```

### 7. Run Initial Database Migrations
Apply the structural MVP database schema to your clean database instance:
```bash
alembic upgrade head
```

---

## Adding Database Records (Seeding Data)

To test the application endpoints, you need initial database entries. You can populate the tables using either of the following two pathways:

### Method A: Automated System Script
From the project **root directory** (`Recruitment_agent/`), execute the test database script directly using Python's module flag:
```bash
python -m app.test_db
```
*(This triggers your `app/test_db.py` module to verify the table connections and write initial test candidate/job objects straight to your PostgreSQL database).*

### Method B: Interactive Swagger API Form
1. Start your application server (see the *Running the Application* section below).
2. Open your web browser and navigate to the interactive dashboard at: [http://127.0.0](http://127.0.0)
3. Expand your target workspace category (e.g., `POST /jobs` or `POST /candidates`).
4. Click **Try it out**, fill in the automatically generated JSON payload fields, and hit **Execute** to write mock values straight to your tables.

---

## Running the Application

To fire up the live development server, change directories into the `app/` folder and execute the ASGI layer via Uvicorn:

```bash
cd app
uvicorn main:app --reload
```

* **Local API Base URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive Swagger Documentation Tool:** [http://127.0.0](http://127.0.0)

---

## FastAPI REST API Endpoints Map

When the application is running, the following API resource routes are available for managing your recruitment data engine:

### 1. Job Architecture Workspace
* **`GET /jobs/`** — Retrieve a comprehensive list of all active recruitment job postings.
* **`POST /jobs/`** — Create and configure a brand-new job requisition profile.
* **`GET /jobs/{job_id}`** — Fetch granular description properties for a specific job token.

### 2. Candidate Profiles Hub
* **`GET /candidates/`** — Fetch a paginated index containing information for all registered candidates.
* **`POST /candidates/`** — Submit credentials to register a brand-new candidate profile inside the engine.

### 3. Core Application Subsystem
* **`GET /applications/`** — Extract a complete history tracking sheet containing all job applications.
* **`POST /applications/`** — Link a candidate token to an active job profile to register a live workflow application.
* **`GET /applications/{application_id}/screening`** — Review the automated candidate screening records for a specific application.

### 4. Assessment & Test Framework
* **`GET /tests/`** — Look up available evaluation testing structures and challenge modules.
* **`POST /tests/`** — Build a brand-new assessment containing specialized question banks.
* **`POST /test-attempts/`** — Open an active session token allowing a candidate to start answering tests.
* **`POST /answers/`** — Submit structural answers (e.g., multiple-choice question responses) for active evaluation.
* **`GET /test-attempts/{attempt_id}/score`** — Access the automated MCQ answer evaluation and overall assessment scoring sheet.

---

## Database Migrations (Alembic Workflow)

⚠️ **Critical Operations Guide:** Alembic's orchestration file (`alembic.ini`) resides at the root level. Running migrations from inside the `app/` directory will drop terminal faults. 

Open a secondary terminal window or exit back up out of the application subsystem folder to return to the project root directory before running commands:
```bash
cd ..
```

1. **Check Current Database Migration State:**
   ```bash
   alembic current
   ```
2. **Generate Structural Database Updates:**
   *(Run this whenever you modify models inside `app/models.py`)*
   ```bash
   alembic revision --autogenerate -m "description of database changes"
   ```
3. **Apply Schema Changes:**
   ```bash
   alembic upgrade head
   ```

---

## Troubleshooting & Critical Configuration Gotchas

### 1. `ModuleNotFoundError: No module named 'models'` (During Migrations)
* **Cause:** Alembic runs from the root context but cannot capture absolute project path definitions when parsing flat relative statements (`import models`) inside the `app/` cluster.
* **Resolution:** Open `alembic.ini` sitting in the project root folder. Locate the configuration setting `prepend_sys_path` and update it to bridge this folder pathing gap directly:
  ```ini
  prepend_sys_path = ./app
  ```

### 2. Silent Empty Migration Scripts Generated
* **Cause:** Alembic creates automated scripts containing absolute blank `upgrade()` and `downgrade()` code blocks because `alembic/env.py` references structural components before they load into memory.
* **Resolution:** Open your `alembic/env.py` script and explicitly force import references to execute directly above metadata mappings:
  ```python
  from app.database import Base
  from app import models  # Crucial! Registers database structures into python's runtime memory
  target_metadata = Base.metadata
  ```

### 3. Special Character Failures inside Connection Strings
* **Cause:** If your database password contains characters like `@` or `%`, Alembic's configuration reader intercepts these characters incorrectly.
* **Resolution:** If using plain configuration parameters within `alembic.ini`, change `%` flags to doubled properties (`%%`). Alternatively, parse the string via local system variables using `dotenv` explicitly inside `alembic/env.py`.

---

## Exiting the Workspace (Deactivation)

Whenever you complete your local working session and want to leave the isolated development virtual container framework, run the lifecycle deactivation script from any directory position:
```bash
deactivate
```
