"""
Sarvam AI Forensic Document Restorer & Gap Auditor
Zero-Hallucination text reconstruction for historical documents.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from sarvamai import SarvamAI
from sarvamai.core.api_error import ApiError

def load_env():
    """Load environment variables from .env file without external dependencies."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip().strip("'\"")

def get_sarvam_client() -> SarvamAI:
    load_env()
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        print("[ERROR] SARVAM_API_KEY not found in environment or .env file.")
        print("Please set your key in .env first: SARVAM_API_KEY=your_key_here")
        sys.exit(1)
    return SarvamAI(api_subscription_key=api_key)

SYSTEM_PROMPT = """You are a specialized forensic document archivist analyzing degraded historical records (e.g. from the 1960s).
Your primary mandate is ABSOLUTE ZERO HALLUCINATION.

Rules:
1. NEVER guess or invent proper names, dates, plot/survey/khasra numbers, acreage, or monetary amounts.
2. Every damaged/missing slot must be classified into one of three statuses:
   - "CONFIRMED": 100% deterministically verifiable from statutory law, legal formula, or rigid syntax where no other wording exists.
   - "CORROBORATED": Confirmed against the supplied Reference Data with unambiguous, 1-to-1 matching evidence.
   - "UNRECOVERABLE": ANY slot where multiple possibilities exist, or where the entity is an arbitrary historical fact (names, numbers, currency) not uniquely proven by the reference data.
3. For every "UNRECOVERABLE" slot, you MUST explicitly detail the forensic reason why it cannot be deduced without hallucination.
4. Output MUST be valid JSON adhering to this schema:
{
  "document_summary": "Brief explanation of document jurisdiction, year, and type",
  "slots": [
    {
      "slot_id": "[SLOT_X]",
      "context": "surrounding text snippet",
      "status": "CONFIRMED | CORROBORATED | UNRECOVERABLE",
      "predicted_text": "string or null if UNRECOVERABLE",
      "confidence": 0.0 to 1.0 (must be 0.0 for UNRECOVERABLE, >=0.95 for CONFIRMED, >=0.85 for CORROBORATED),
      "evidence": "Statutory citation, syntactic rule, or reference link",
      "unrecoverable_reason": "Detailed forensic explanation of why guessing is forbidden here (null if recovered)"
    }
  ],
  "unrecoverable_audit": [
    {
      "slot_id": "[SLOT_X]",
      "type": "PROPER_NAME | ARBITRARY_NUMBER | CALENDAR_DATE | JURISDICTION_AMBIGUITY | OTHER",
      "reason": "Clear explanation of the missing evidence"
    }
  ],
  "reconstructed_document": "The full text with slots replaced as [CONFIRMED: text], [CORROBORATED: text], or [UNRECOVERABLE: slot_id - reason]"
}
"""

def restore_document(document_text: str, reference_data: str, model: str = "sarvam-105b") -> dict:
    client = get_sarvam_client()
    
    user_prompt = f"""### REFERENCE DATA (Real-World Evidence):
{reference_data if reference_data.strip() else "No external reference data supplied."}

### DEGRADED HISTORICAL DOCUMENT:
{document_text}

Perform forensic reconstruction and zero-hallucination gap audit. Output pure JSON.
"""

    print(f"Connecting to Sarvam AI using model '{model}' with temperature=0.0 (zero-hallucination mode)...")
    try:
        response = client.chat.completions(
            model=model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        raw_content = response.choices[0].message.content
        return json.loads(raw_content)
    except ApiError as e:
        if e.status_code == 402:
            print("\n[API NOTICE - 402 Payment Required]")
            print("Your Sarvam AI API key is authenticated, but your account currently has 0 credits.")
            print("To run live predictions, add credits at: https://dashboard.sarvam.ai")
            print("Once credits are added, this exact script will process live documents.")
            sys.exit(0)
        else:
            print(f"\n[Sarvam API Error {e.status_code}]: {e.body}")
            sys.exit(1)
    except Exception as e:
        print(f"\n[Unexpected Error]: {e}")
        sys.exit(1)

def print_audit_report(result: dict, output_path: str = None):
    slots = result.get("slots", [])
    unrecoverable = [s for s in slots if s.get("status") == "UNRECOVERABLE"]
    confirmed = [s for s in slots if s.get("status") in ("CONFIRMED", "CORROBORATED")]
    
    print("\n" + "=" * 80)
    print(" SARVAM AI FORENSIC DOCUMENT RESTORATION REPORT (ZERO HALLUCINATION)")
    print("=" * 80)
    print(f"Document Overview: {result.get('document_summary', 'N/A')}")
    print(f"Total Slots Analyzed: {len(slots)}")
    print(f"  - Confirmed / Corroborated: {len(confirmed)}")
    print(f"  - Strictly Unrecoverable  : {len(unrecoverable)} (Rejected to avoid hallucination)")
    print("=" * 80)

    if confirmed:
        print("\n[VERIFIED PREDICTIONS]")
        for s in confirmed:
            print(f"  {s.get('slot_id')}: \"{s.get('predicted_text')}\" [{s.get('status')} | Confidence: {s.get('confidence')}]")
            print(f"    Evidence: {s.get('evidence')}")

    print("\n[UNRECOVERABLE AUDIT - EXPLICIT REJECTIONS]")
    for s in unrecoverable:
        print(f"  X {s.get('slot_id')} in context: \"{s.get('context')}\"")
        print(f"    Reason: {s.get('unrecoverable_reason')}")

    print("\n" + "-" * 80)
    print(" RECONSTRUCTED DOCUMENT PREVIEW:")
    print("-" * 80)
    print(result.get("reconstructed_document", ""))
    print("-" * 80)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nFull forensic JSON report saved to: {output_path}")

def get_mock_result() -> dict:
    """Simulated output showing how sarvam-105b evaluates the sample document."""
    return {
        "document_summary": "1963 Revenue Court Eviction Order under the Punjab Security of Land Tenures Act, 1953 (Ambala District)",
        "slots": [
            {
                "slot_id": "[SLOT_1]",
                "context": "SUB-DIVISIONAL OFFICER, TEHSIL [SLOT_1], DISTRICT AMBALA",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Multiple tehsils existed in Ambala in 1963 (Ambala, Jagadhri, Naraingarh, Kharar, Rupnagar). Context has no distinguishing qualifier."
            },
            {
                "slot_id": "[SLOT_2]",
                "context": "Dated: 16th [SLOT_2], 1963",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Arbitrary calendar month; cannot be inferred without court dispatch register."
            },
            {
                "slot_id": "[SLOT_3]",
                "context": "application under Section [SLOT_3] of the Punjab Security of Land Tenures Act, 1953 ... seeking eviction",
                "status": "CONFIRMED",
                "predicted_text": "9(1)(ii)",
                "confidence": 0.98,
                "evidence": "Section 9(1)(ii) of Punjab Act 10 of 1953 specifically governs eviction petitions grounded on non-payment of rent without sufficient cause.",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_4]",
                "context": "landowner Shri [SLOT_4], son of Shri Ram Saran",
                "status": "CORROBORATED",
                "predicted_text": "Shahzadpur Zamindar Heir",
                "confidence": 0.90,
                "evidence": "Cross-referenced with verified village registry where Ram Saran is recorded as registered zamindar.",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_5]",
                "context": "resident of Village [SLOT_5]",
                "status": "CORROBORATED",
                "predicted_text": "Shahzadpur",
                "confidence": 0.92,
                "evidence": "Matches verified village registry linked to landowner family lineage in Ambala/Naraingarh.",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_6]",
                "context": "seeking eviction of the tenant Shri [SLOT_6]",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Personal proper name of tenant. Unattested in general gazetteer; strictly unrecoverable without specific Tehsil Jamabandi register."
            },
            {
                "slot_id": "[SLOT_7]",
                "context": "comprised in Khasra No. [SLOT_7]",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Arbitrary cadastral parcel number. Zero mathematical or grammatical predictability."
            },
            {
                "slot_id": "[SLOT_8]",
                "context": "measuring [SLOT_8] standard acres",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Numeric land area is arbitrary factual data. Must not be guessed."
            },
            {
                "slot_id": "[SLOT_9]",
                "context": "without sufficient cause for [SLOT_9] consecutive harvest seasons, namely Rabi 1961 and Kharif 1961",
                "status": "CONFIRMED",
                "predicted_text": "two",
                "confidence": 1.0,
                "evidence": "Strict grammatical enumeration: text enumerates exactly two seasons ('Rabi 1961 and Kharif 1961').",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_10]",
                "context": "powers conferred under Section [SLOT_10] of the said Act",
                "status": "CONFIRMED",
                "predicted_text": "14-A",
                "confidence": 0.99,
                "evidence": "Section 14-A provides the exclusive statutory mechanism for Assistant Collectors to execute eviction orders under this Act.",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_11]",
                "context": "within [SLOT_11] days of this order",
                "status": "CONFIRMED",
                "predicted_text": "30",
                "confidence": 0.95,
                "evidence": "Standard statutory grace period under Punjab Revenue Court Procedure Rules.",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_12]",
                "context": "arrears of rent amounting to Rs. [SLOT_12]",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Monetary debt amount cannot be syntactically deduced without revenue account ledger."
            },
            {
                "slot_id": "[SLOT_13]",
                "context": "under Head \"[SLOT_13]\"",
                "status": "CORROBORATED",
                "predicted_text": "0029 - Land Revenue / Revenue Deposits",
                "confidence": 0.95,
                "evidence": "Confirmed against 1960s Punjab Government Accounting Head Registry for tenancy revenue deposits.",
                "unrecoverable_reason": None
            },
            {
                "slot_id": "[SLOT_14]",
                "context": "Sub-Division [SLOT_14]",
                "status": "UNRECOVERABLE",
                "predicted_text": None,
                "confidence": 0.0,
                "evidence": None,
                "unrecoverable_reason": "Linked to SLOT_1; cannot be resolved without Tehsil certainty."
            }
        ],
        "unrecoverable_audit": [
            {"slot_id": "[SLOT_1]", "type": "JURISDICTION_AMBIGUITY", "reason": "Multiple candidate tehsils in district"},
            {"slot_id": "[SLOT_2]", "type": "CALENDAR_DATE", "reason": "Missing court diary / dispatch register"},
            {"slot_id": "[SLOT_6]", "type": "PROPER_NAME", "reason": "Tenant identity absent from gazetteer"},
            {"slot_id": "[SLOT_7]", "type": "ARBITRARY_NUMBER", "reason": "Khasra/cadastral survey number"},
            {"slot_id": "[SLOT_8]", "type": "ARBITRARY_NUMBER", "reason": "Acreage area measurement"},
            {"slot_id": "[SLOT_12]", "type": "ARBITRARY_NUMBER", "reason": "Monetary currency amount"},
            {"slot_id": "[SLOT_14]", "type": "JURISDICTION_AMBIGUITY", "reason": "Sub-division name corresponds to ambiguous tehsil"}
        ],
        "reconstructed_document": (
            "IN THE REVENUE COURT OF THE SUB-DIVISIONAL OFFICER, TEHSIL [UNRECOVERABLE: SLOT_1 - Multiple tehsils], DISTRICT AMBALA\n"
            "CASE NO. 42 OF 1963\n\n"
            "Dated: 16th [UNRECOVERABLE: SLOT_2 - Calendar month], 1963\n\n"
            "ORDER UNDER THE PUNJAB SECURITY OF LAND TENURES ACT, 1953\n\n"
            "Whereas an application under Section [CONFIRMED: 9(1)(ii)] of the Punjab Security of Land Tenures Act, 1953 (Act No. 10 of 1953) "
            "was presented before this Court by the landowner Shri [CORROBORATED: Shahzadpur Zamindar Heir], son of Shri Ram Saran, resident of Village [CORROBORATED: Shahzadpur], "
            "seeking eviction of the tenant Shri [UNRECOVERABLE: SLOT_6 - Proper name] from agricultural land comprised in Khasra No. [UNRECOVERABLE: SLOT_7 - Survey number], "
            "measuring [UNRECOVERABLE: SLOT_8 - Acreage] standard acres situated within the revenue estate of the said village.\n\n"
            "And whereas upon perusal of the Jamabandi for the year 1959-60, it appears that the tenant has defaulted in payment of rent without sufficient cause for "
            "[CONFIRMED: two] consecutive harvest seasons, namely Rabi 1961 and Kharif 1961.\n\n"
            "Now, therefore, in exercise of powers conferred under Section [CONFIRMED: 14-A] of the said Act, it is hereby ordered that:\n"
            "1. The tenant shall deliver possession of the said parcel to the landowner within [CONFIRMED: 30] days of this order.\n"
            "2. The arrears of rent amounting to Rs. [UNRECOVERABLE: SLOT_12 - Arrears sum] shall be deposited into the Government Treasury under Head \"[CORROBORATED: 0029 - Land Revenue / Revenue Deposits]\" by or before the end of next month.\n\n"
            "Given under my hand and the seal of this Court.\n\n"
            "(Sd/-)\n"
            "Sub-Divisional Magistrate & Assistant Collector 1st Grade\n"
            "Sub-Division [UNRECOVERABLE: SLOT_14 - Sub-division name]\n"
        )
    }

def main():
    parser = argparse.ArgumentParser(description="Sarvam AI Zero-Hallucination Document Restorer")
    parser.add_argument("--doc", "-d", default="sample_document.txt", help="Path to degraded document file")
    parser.add_argument("--ref", "-r", default="sample_reference.json", help="Path to reference data file")
    parser.add_argument("--output", "-o", default="audit_report.json", help="Path to save output JSON report")
    parser.add_argument("--model", "-m", default="sarvam-105b", help="Sarvam model to use (default: sarvam-105b)")
    parser.add_argument("--demo", action="store_true", help="Run in demonstration mode to preview report output")
    
    args = parser.parse_args()

    if args.demo:
        print("[DEMO MODE] Running zero-hallucination document audit simulation...")
        result = get_mock_result()
        print_audit_report(result, output_path=args.output)
        return

    doc_path = Path(args.doc)
    if not doc_path.exists():
        print(f"[ERROR] Document file not found: {args.doc}")
        sys.exit(1)
    
    doc_text = doc_path.read_text(encoding="utf-8")

    ref_text = ""
    ref_path = Path(args.ref)
    if ref_path.exists():
        ref_text = ref_path.read_text(encoding="utf-8")
    else:
        print(f"[INFO] No reference file found at '{args.ref}'. Running without external grounding.")

    result = restore_document(doc_text, ref_text, model=args.model)
    print_audit_report(result, output_path=args.output)

if __name__ == "__main__":
    main()
