# Sarvam AI Historical Document Restorer (Zero-Hallucination Engine)

A forensic document restoration and gap-auditing tool powered by **Sarvam AI (`sarvam-105b`)**. Designed specifically for degraded, torn, or ink-faded historical records (e.g., 1960s administrative, revenue, and legal documents), this system reconstructs legible text based on real-world reference datasets while **strictly eliminating hallucinations**.

---

## 🎯 Key Features

- **Zero-Hallucination Architecture**: Operates with `temperature=0.0` (greedy decoding) and strict forensic guardrails. Any entity that cannot be proven with 100% certainty is rejected and cataloged.
- **Three-Tier Forensic Classification**:
  - `CONFIRMED`: Syntactically or legally deterministic boilerplates, standard statutory phrases, and procedural rules.
  - `CORROBORATED`: Unambiguous 1-to-1 matches verified against external reference data (gazetteers, village registries, census lists).
  - `UNRECOVERABLE`: Arbitrary facts (personal names, survey/khasra numbers, land acreage, currency amounts, dates) lacking secondary proof are flagged with an explicit reason why guessing is forbidden.
- **Structured Audit Trail**: Outputs both a reconstructed document preview and a JSON audit report detailing every slot and evidence trail.
- **Built-in Offline Demo**: Includes a simulation mode (`--demo`) to test the audit workflow without calling the live API.

---

## 📁 Repository Structure

```text
├── .env                  # Environment variables (ignored by git; stores SARVAM_API_KEY)
├── .gitignore            # Ignores .env and generated audit reports
├── main.py               # Minimal one-call connection test script
├── restorer.py           # Core document restoration and gap-auditing CLI
├── sample_document.txt   # Degraded 1963 Indian revenue court order with damaged slots
├── sample_reference.json # Grounding dataset (1960s gazetteer, statutes, village registry)
└── README.md             # Project documentation and setup guide
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10 or higher
- A Sarvam AI API Key from the [Sarvam AI Dashboard](https://dashboard.sarvam.ai)

### 2. Install Dependencies
Install the official Sarvam AI Python SDK:

```bash
pip install sarvamai
```

### 3. Configure API Key
Create a `.env` file in the root directory (make sure it is never committed to GitHub):

```env
SARVAM_API_KEY=your_actual_sarvam_api_key_here
```

Verify that `.env` is listed in your `.gitignore` to prevent exposing your credentials.

---

## 💻 Usage

### 1. Test Connection
Run the minimal connectivity script:
```bash
python main.py
```

### 2. Preview Audit Report (Demo Mode)
Run the built-in offline simulation to inspect how degraded slots are evaluated:
```bash
python restorer.py --demo
```

### 3. Restore a Document with Live AI
To process a document with external reference data:
```bash
python restorer.py --doc sample_document.txt --ref sample_reference.json --output audit_report.json
```

### 4. Custom Document & Reference File
Supply your own degraded text and reference records:
```bash
python restorer.py --doc path/to/document.txt --ref path/to/references.json --output my_report.json
```

#### CLI Options:
| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--doc` | `-d` | `sample_document.txt` | Path to text file with damaged slots (`[SLOT_1]`, `[?]`, etc.) |
| `--ref` | `-r` | `sample_reference.json` | Path to external reference facts or historical gazetteer |
| `--output` | `-o` | `audit_report.json` | Path where JSON audit report will be saved |
| `--model` | `-m` | `sarvam-105b` | Sarvam model to use (`sarvam-105b` or `sarvam-105b-conversations`) |
| `--demo` | | `False` | Run offline demonstration without making API requests |

---

## 📤 Pushing to GitHub

Follow these steps to upload this project to your GitHub repository safely:

### Step 1: Initialize Git
```bash
git init
```

### Step 2: Verify Secrets are Excluded
Ensure `.gitignore` contains `.env`:
```bash
git status
```
> **Warning**: Ensure `.env` is **NOT** listed under `Untracked files`.

### Step 3: Stage and Commit
```bash
git add .
git commit -m "Initial commit: Sarvam AI zero-hallucination document restorer"
```

### Step 4: Link Remote Repository & Push
Create a new repository on [GitHub](https://github.com/new), then run:
```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

---

## ⚖️ License & Ethical Archival Guidelines
This software is intended for archival research, historic record preservation, and document verification. Reconstructed text should always be cross-referenced with official archives before being relied upon in legal or administrative proceedings.
