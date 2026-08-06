import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL_PATTERN = re.compile(r"https?://[^\s<>()\]]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9-]+)", re.IGNORECASE
)
LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_%.-]+)", re.IGNORECASE
)


def extract_profile_links(resume_text):
    text = str(resume_text or "")
    github_match = GITHUB_PATTERN.search(text)
    linkedin_match = LINKEDIN_PATTERN.search(text)
    return {
        "github_url": (
            f"https://github.com/{github_match.group(1)}" if github_match else ""
        ),
        "github_username": github_match.group(1) if github_match else "",
        "linkedin_url": (
            f"https://www.linkedin.com/in/{linkedin_match.group(1)}"
            if linkedin_match
            else ""
        ),
    }


def _github_get(path, timeout=10):
    request = Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "OfferPilot-Profile-Verification",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_public_github_evidence(username):
    """Fetch only public account and repository metadata for a validated username."""
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", str(username or "")):
        raise ValueError("Invalid GitHub username.")
    try:
        profile = _github_get(f"/users/{username}")
        repos = _github_get(
            f"/users/{username}/repos?per_page=100&sort=updated&type=owner"
        )
    except HTTPError as exc:
        if exc.code == 404:
            raise ValueError("GitHub profile was not found or is not public.") from exc
        if exc.code == 403:
            raise ValueError("GitHub API rate limit reached. Try again later.") from exc
        raise ValueError(f"GitHub returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        raise ValueError("GitHub could not be reached from the app.") from exc

    public_repos = [repo for repo in repos if not repo.get("fork")]
    return {
        "profile_url": profile.get("html_url", f"https://github.com/{username}"),
        "display_name": profile.get("name") or profile.get("login", username),
        "bio": profile.get("bio") or "",
        "public_repo_count": profile.get("public_repos", len(public_repos)),
        "repos": [
            {
                "name": repo.get("name", ""),
                "description": repo.get("description") or "",
                "language": repo.get("language") or "",
                "url": repo.get("html_url", ""),
                "updated_at": repo.get("updated_at", ""),
            }
            for repo in public_repos
        ],
    }


def _tokens(text):
    return {
        token
        for token in re.findall(r"[a-z0-9+#.]{3,}", str(text or "").lower())
        if token not in {"and", "the", "with", "for", "from", "using"}
    }


def compare_resume_with_profiles(resume_text, github_evidence=None, linkedin_text=""):
    resume_tokens = _tokens(resume_text)
    github_evidence = github_evidence or {}
    repo_text = " ".join(
        " ".join([repo.get("name", ""), repo.get("description", ""), repo.get("language", "")])
        for repo in github_evidence.get("repos", [])
    )
    github_tokens = _tokens(repo_text + " " + github_evidence.get("bio", ""))
    linkedin_tokens = _tokens(linkedin_text)

    def overlap(external_tokens):
        shared = sorted(resume_tokens & external_tokens)
        return shared, round(100 * len(shared) / max(len(external_tokens), 1))

    github_shared, github_overlap = overlap(github_tokens)
    linkedin_shared, linkedin_overlap = overlap(linkedin_tokens)
    signals = []
    if github_evidence and not github_evidence.get("repos"):
        signals.append("The public GitHub profile has no non-fork public repositories to verify.")
    if github_evidence and github_shared:
        signals.append("Public GitHub metadata supports some resume technologies or project topics.")
    if github_evidence and not github_shared:
        signals.append("No clear text overlap was found; private or differently named work may be unverifiable.")
    if linkedin_text and linkedin_shared:
        signals.append("The recruiter-provided LinkedIn text overlaps with resume claims.")

    return {
        "github_overlap": github_overlap,
        "github_shared_terms": github_shared[:25],
        "linkedin_overlap": linkedin_overlap,
        "linkedin_shared_terms": linkedin_shared[:25],
        "review_signals": signals,
        "limitations": (
            "Public profiles can support a claim but cannot prove authorship, ownership, "
            "or that missing public evidence means a claim is false."
        ),
    }
