# Schema Registry — MVP

A lightweight Python microservice to register JSON Schemas and validate payloads against them.

Built with FastAPI · jsonschema · Pydantic · deployable to Railway in ~2 minutes.

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/schemas/{id}` | Register or overwrite a JSON schema |
| `GET` | `/schemas/{id}` | Retrieve a registered schema |
| `GET` | `/schemas/` | List all registered schema IDs |
| `DELETE` | `/schemas/{id}` | Delete a schema |
| `POST` | `/validate/{id}` | Validate + deserialize a payload |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (interactive) |

---

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

---

## Run with Docker

```bash
docker build -t schema-registry .
docker run -p 8000:8000 schema-registry
```

---

## Deploy to Railway (2 minutes)

1. Push this repo to GitHub.
2. Go to https://railway.app → **New Project** → **Deploy from GitHub repo**.
3. Select your repo. Railway auto-detects the Dockerfile and deploys.
4. Click **Generate Domain** in the Settings tab to get a public HTTPS URL.

No environment variables needed for the MVP.

---

## Usage examples

Replace `http://localhost:8000` with your Railway public URL when deployed.

### 1. Register a schema

```bash
curl -X POST http://localhost:8000/schemas/remittance-transfer \
  -H "Content-Type: application/json" \
  -d '{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["sender_id", "receiver_id", "amount_usd", "destination_country"],
    "properties": {
      "sender_id":           { "type": "string" },
      "receiver_id":         { "type": "string" },
      "amount_usd":          { "type": "number", "minimum": 0.01 },
      "destination_country": { "type": "string", "enum": ["MX", "CO", "GT", "SV", "HN"] },
      "notes":               { "type": "string" }
    }
  }'
```

**Response (201)**
```json
{ "id": "remittance-transfer", "message": "Schema registered successfully." }
```

---

### 2. Validate a valid payload

```bash
curl -X POST http://localhost:8000/validate/remittance-transfer \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "USR-001",
    "receiver_id": "USR-099",
    "amount_usd": 250.00,
    "destination_country": "MX"
  }'
```

**Response (200)**
```json
{
  "valid": true,
  "schema_id": "remittance-transfer",
  "data": {
    "sender_id": "USR-001",
    "receiver_id": "USR-099",
    "amount_usd": 250.0,
    "destination_country": "MX",
    "notes": null
  }
}
```

---

### 3. Validate an invalid payload (field-level errors)

```bash
curl -X POST http://localhost:8000/validate/remittance-transfer \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "USR-001",
    "amount_usd": -5,
    "destination_country": "US"
  }'
```

**Response (422)**
```json
{
  "detail": {
    "valid": false,
    "schema_id": "remittance-transfer",
    "errors": [
      {
        "field": "amount_usd",
        "message": "-5 is less than the minimum of 0.01",
        "schema_path": "properties.amount_usd.minimum"
      },
      {
        "field": "destination_country",
        "message": "'US' is not one of ['MX', 'CO', 'GT', 'SV', 'HN']",
        "schema_path": "properties.destination_country.enum"
      },
      {
        "field": "(root)",
        "message": "'receiver_id' is a required property",
        "schema_path": "required"
      }
    ]
  }
}
```

---

## Next steps (production hardening)

- [ ] **API key auth** — add a `X-API-Key` header check via FastAPI middleware
- [ ] **Redis store** — swap `app/store.py` for a Redis-backed implementation
- [ ] **Schema versioning** — `POST /schemas/{id}/versions` with full audit trail
- [ ] **Rate limiting** — add `slowapi` to protect the public endpoints
- [ ] **Structured logging** — add `structlog` for JSON logs (essential for fraud audit trails)
