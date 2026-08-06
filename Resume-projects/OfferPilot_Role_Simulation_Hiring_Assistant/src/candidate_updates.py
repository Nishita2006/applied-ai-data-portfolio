import base64
import json
import re
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


MILESTONES = [
    ("application_received", "Application received"),
    ("resume_review", "Resume review"),
    ("skills_verification", "Skills verification"),
    ("work_simulation", "Work simulation"),
    ("interview", "Interview"),
    ("final_review", "Final review"),
    ("decision_shared", "Decision shared"),
]

STATUS_OPTIONS = ["Not started", "In progress", "Completed"]


def extract_phone_number(text, default_country_code=""):
    """Extract a likely phone number; only normalize when a country code is explicit/configured."""
    source = str(text or "")
    international = re.search(r"\+[1-9](?:[\s().-]*\d){7,14}", source)
    if international:
        digits = re.sub(r"\D", "", international.group(0))
        return "+" + digits
    national = re.search(r"(?<!\d)(?:\(?\d{3}\)?[\s.-]*)\d{3}[\s.-]*\d{4}(?!\d)", source)
    if not national:
        return ""
    digits = re.sub(r"\D", "", national.group(0))
    code = str(default_country_code or "").strip()
    if code and re.fullmatch(r"\+[1-9]\d{0,3}", code):
        return code + digits
    return national.group(0).strip()


def extract_email_address(text):
    match = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", str(text or ""), re.IGNORECASE)
    return match.group(0).lower() if match else ""


def validate_phone_number(phone_number):
    """Require E.164 formatting without trying to infer a candidate's country."""
    return re.fullmatch(r"\+[1-9]\d{7,14}", str(phone_number or "").strip()) is not None


def milestone_progress(statuses):
    completed = sum(
        statuses.get(key, "Not started") == "Completed"
        for key, _ in MILESTONES
    )
    in_progress = any(
        statuses.get(key, "Not started") == "In progress"
        for key, _ in MILESTONES
    )
    progress = completed / len(MILESTONES)
    if in_progress and completed < len(MILESTONES):
        progress += 0.5 / len(MILESTONES)
    return min(progress, 1.0)


def build_status_message(candidate_name, milestone_label, status, next_step=""):
    first_name = str(candidate_name or "Candidate").strip().split()[0]
    message = (
        f"OfferPilot update for {first_name}: {milestone_label} is now "
        f"{status.lower()}."
    )
    if next_step.strip():
        message += f" Next: {next_step.strip()}"
    message += " Reply to your recruiting contact if you need assistance."
    return message


def send_twilio_sms(
    account_sid,
    auth_token,
    from_number,
    to_number,
    body,
    timeout=15,
):
    if not validate_phone_number(to_number) or not validate_phone_number(from_number):
        raise ValueError("Sender and recipient numbers must use E.164 format, such as +15551234567.")
    if not account_sid or not auth_token:
        raise ValueError("Twilio credentials are not configured.")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    encoded = urlencode({"To": to_number, "From": from_number, "Body": body}).encode("utf-8")
    basic_auth = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    request = Request(
        url,
        data=encoded,
        method="POST",
        headers={
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "OfferPilot-Candidate-Updates",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Twilio rejected the message (HTTP {exc.code}): {detail[:240]}") from exc
    except (URLError, TimeoutError) as exc:
        raise ValueError("The SMS provider could not be reached.") from exc

    return {
        "sid": payload.get("sid", ""),
        "status": payload.get("status", "queued"),
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
