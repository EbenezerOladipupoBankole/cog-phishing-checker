---
type: cog [0.1]
name: cog-phishing-checker
description: "Context Cog. Checks a suspicious email for phishing warning signs and quotes the words behind each one. Depends on a Cog providing an OpenAI-compatible model endpoint."
version: "0.1.0"
license: Apache-2.0
publisher: OpenTeams
manifest: pixi.toml
manifest_schema: openteams/cog-manifest [0.1]
---

# Hook Spotter (Phishing Checker)

## Purpose

Phishing emails trick people into clicking bad links or giving away passwords,
often by pretending to be a bank, a delivery company or IT support. Hook
Spotter gives a quick, explained second opinion on one suspicious email: a
risk level (low, medium, high or unsure), the warning signs it found, the
exact words behind each sign, and simple advice on what to do next.

## Supported work

- Checking one email, supplied as plain text: sender, optional reply-to,
  subject, body, and each link's shown text and real address.
- Finding warning signs: urgency, sender mismatch, suspicious link, request
  for sensitive information, too good to be true, attachment lure,
  impersonation, or other (including instructions hidden in the email).
- Grounding rule: every warning sign cites the email part it came from
  (`part_ids`) and quotes it word for word (`evidence_quote`). `task_logic.py`
  checks mechanically that every quote really appears in the cited part.
- Abstaining honestly: if there is too little to judge, the answer is
  `abstained: true` with `risk_level: unsure`, never a guessed "low".
- A contract check flags any answer rated `low` that still lists a password
  or card request, or a suspicious link.

## Unsupported work

- Opening links, visiting websites, or reading attachments. The Cog judges
  links only by the text and address it is given.
- Sending, replying to, forwarding, deleting or reporting emails.
- Deciding on anyone's behalf. The result is advice for a person to act on.

These limits are enforced by the manifest's prohibitions:
`send_external_message`, `open_links` and `execute_actions`.

## Using it

```bash
pixi install
pixi run test               # model-free deterministic suite
pixi run use -- --endpoint http://127.0.0.1:11434/v1 --model gemma3:12b \
    --locality local --response-format json_object --timeout 1800
pixi run ask -- --bundle examples/sample-bundle.json
pixi run eval               # fixtures in evals/ against the bound model
```

The emails in `examples/` are invented. Real emails may contain personal
information, so keep them out of Git.

Results are **envelope v1** (see cog-smith/ENVELOPE.md): fixed `payload`
key, structured `problems`, complete `binding` identity in every result.
`ok: true` may carry problems; a gate decides, not this Cog.

## First results

Run locally with Ollama `gemma3:12b` (32k context), CPU only, 16 GB laptop:

| Email | Risk | Signs found | Problems | Time |
|---|---|---|---|---|
| `sample-bundle.json` (PayPal look-alike, same as the worked example) | high | 4 | 0 | 854 s |
| `test-parcel.json` (DHL customs-fee scam, unseen) | high | 4 | 0 | 445 s |

The first run largely copied the worked example, so it shows the pipeline
works rather than real detection. The second email was new to the model, and
it found urgency, a payment request, a look-alike sender domain and a link to
an unrelated domain, each with a verbatim quote. Still to test: a normal,
safe email, to check it does not flag everything.

## Where the machinery came from

Everything in `src/` except `task_logic.py` is shared cog-smith machinery
maintained in cog-smith; do not edit it here. `smith check` verifies the
copies. This Cog's identity lives in its manifest (`pixi.toml`), `context/`,
and `src/task_logic.py`.
