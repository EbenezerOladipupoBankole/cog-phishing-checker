"""THE per-cog module: the only file in src/ you edit.

Phishing Checker: one email goes in (split into parts), and each warning sign
comes out with a verbatim quote from the part it came from.
"""

STRONG = {"sensitive_request", "suspicious_link"}


def email_parts(bundle):
    """The email as {part_id: text}. The same text is shown to the model and
    used to check quotes, so the two can never disagree."""
    email = (bundle or {}).get("email") or {}
    parts = {}
    if email.get("from"):
        parts["from"] = str(email["from"])
    if email.get("reply_to"):
        parts["reply-to"] = str(email["reply_to"])
    if email.get("subject"):
        parts["subject"] = str(email["subject"])
    if email.get("body"):
        parts["body"] = str(email["body"])
    for n, link in enumerate(email.get("links") or [], start=1):
        parts[f"link-{n}"] = (f"shown text: {link.get('text') or '(none)'}\n"
                              f"actual address: {link.get('url', '')}")
    return parts


def check_input(bundle):
    """Input checks beyond the schema. error refuses; warning proceeds."""
    import cog_core
    problems = []
    email = (bundle or {}).get("email") or {}
    if not str(email.get("body", "")).strip():
        problems.append(cog_core.problem("input", "email.body is blank"))
    if not str(email.get("from", "")).strip():
        problems.append(cog_core.problem("input", "email.from is blank"))
    return problems


def render_input(bundle):
    """Input bundle -> the plain-text message the model sees."""
    lines = []
    if bundle.get("notes"):
        lines.append(f"Notes: {bundle['notes']}")
    lines += ["EMAIL PARTS"]
    for pid, text in email_parts(bundle).items():
        lines += ["", f"--- part: {pid}", text.rstrip()]
    return "\n".join(lines)


def check_output(parsed, bundle):
    """Semantic checks after the schema check: every quote must really be in
    the part it cites, and the risk level must agree with the findings."""
    import cog_core
    problems = []
    entries = parsed.get("entries") or []
    risk = parsed.get("risk_level")
    if parsed.get("abstained"):
        if entries:
            problems.append(cog_core.problem(
                "schema", "abstained is true but entries is non-empty"))
        if risk != "unsure":
            problems.append(cog_core.problem(
                "contract", "an abstained answer must have risk_level 'unsure'"))
        if not parsed.get("abstain_reason"):
            problems.append(cog_core.problem(
                "contract", "abstained without an abstain_reason"))
    cats = {e.get("category") for e in entries if isinstance(e, dict)}
    if risk == "low" and cats & STRONG:
        problems.append(cog_core.problem(
            "contract", "risk_level is 'low' despite a password/card request "
                        "or a suspicious link"))
    sources = email_parts(bundle)
    for e in entries:
        if isinstance(e, dict):
            problems.extend(cog_core.verbatim_quote_check(
                e, sources, quote_field="evidence_quote", ids_field="part_ids",
                label=e.get("category")))
    return problems
