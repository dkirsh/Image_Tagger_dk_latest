# Smoke Test Runbook

## Ownership Notes

- Engineer A owns JWT provisioning for the smoke session.
- Engineer A must create and maintain three dedicated Supabase Auth test identities with top-level role claims: `admin`, `tagger`, and `supervisor`.
- The runbook uses only local environment variables for access tokens:
  - `SMOKE_ADMIN_JWT`
  - `SMOKE_TAGGER_JWT`
  - `SMOKE_SUPERVISOR_JWT`
- Raw JWTs, passwords, and refresh tokens must not be committed, pasted into this file, or stored anywhere in the repo.
- Canonical token-provisioning method: store the three test-account credentials in the team password manager, sign in shortly before the smoke session to obtain fresh access tokens, and export the resulting JWTs into the shell env vars above.

## Prerequisites

- `RENDER_URL` points to the deployed backend base URL.
- `FRONTEND_URL` points to the deployed frontend base URL.
- Engineer A has already exported fresh values for `SMOKE_ADMIN_JWT`, `SMOKE_TAGGER_JWT`, and `SMOKE_SUPERVISOR_JWT`.
- Render, Vercel, Supabase Auth, and storage configuration have already been verified by the owning engineer.

## Smoke Steps

1. Verify backend health.

```bash
curl -sS "$RENDER_URL/health"
```

Expected: `status` is `ok` or `degraded`, and the response includes `version`, `db`, and `storage`.

2. Verify the deployed explorer loads publicly.

Open:

```text
$FRONTEND_URL/
```

Expected: Explorer loads without auth prompts or console errors.

3. Submit one admin upload with the admin JWT.

```bash
curl -sS -X POST "$RENDER_URL/v1/admin/upload" \
  -H "Authorization: Bearer $SMOKE_ADMIN_JWT" \
  -F "files[]=@/absolute/path/to/test-image.jpg"
```

Expected: Response includes `job_id`, `items`, at least one created `image_id`, and `status: "queued"`.

4. Wait for the uploaded image to become discoverable and for science processing to complete.

Use the first returned `image_id` from step 3 and poll until ready:

```bash
IMAGE_ID="<first image_id from upload response>"

for i in $(seq 1 12); do
  RESPONSE="$(curl -sS "$RENDER_URL/v1/explorer/images/$IMAGE_ID")"
  echo "$RESPONSE"
  echo "$RESPONSE" | jq -e '.science != null and .science.run_status == "completed"' >/dev/null && break
  sleep 5
done
```

Expected:
- `GET /v1/explorer/images/$IMAGE_ID` starts returning `200` within 5 seconds of upload acceptance.
- Within 60 seconds, the response shows non-null `science` with `run_status: "completed"`.

5. Submit one workbench validation with the tagger JWT.

First fetch the current assignment:

```bash
ASSIGNMENT_RESPONSE="$(curl -sS "$RENDER_URL/v1/workbench/next" \
  -H "Authorization: Bearer $SMOKE_TAGGER_JWT")"

echo "$ASSIGNMENT_RESPONSE"

ASSIGNED_IMAGE_ID="$(echo "$ASSIGNMENT_RESPONSE" | jq -r '.image.id')"
ASSIGNED_ATTRIBUTE_KEY="$(echo "$ASSIGNMENT_RESPONSE" | jq -r '.assignment.attribute_key')"
```

Expected: Response includes non-null `image.id` and `assignment.attribute_key`.

```bash
curl -sS -X POST "$RENDER_URL/v1/workbench/validate" \
  -H "Authorization: Bearer $SMOKE_TAGGER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": '"$ASSIGNED_IMAGE_ID"',
    "attribute_key": "'"$ASSIGNED_ATTRIBUTE_KEY"'",
    "value": 0.9,
    "duration_ms": 5000
  }'
```

Expected: Response includes `validation_id` and `accepted: true`.

6. Verify explorer detail shows trust-wrapped science output.

Open the uploaded image detail in the deployed explorer UI.

Expected: Trust badges render, science feature rows display, and there are no console errors.

7. Verify the monitor IRR endpoint with the supervisor JWT.

```bash
curl -sS "$RENDER_URL/v1/monitor/irr" \
  -H "Authorization: Bearer $SMOKE_SUPERVISOR_JWT"
```

Expected: Response matches the contract shape `{ "rows": [...] }`. In Phase 1, both a populated `rows` array and an empty array are acceptable.

8. Verify the deployed monitor UI loads the same IRR table.

Open:

```text
$FRONTEND_URL/monitor
```

Expected: The monitor route loads without console errors and renders either a populated IRR table or the contracted empty state for `{ rows: [] }`.

## Final Expected Outcome

All four deployed journeys complete successfully:
- Explorer is publicly accessible.
- Admin upload succeeds with `SMOKE_ADMIN_JWT`.
- Workbench validation succeeds with `SMOKE_TAGGER_JWT`.
- Monitor loads with `SMOKE_SUPERVISOR_JWT` and correctly handles the contracted IRR response, including the empty state.
- No raw secrets are present in git-tracked files or pasted into this runbook.
