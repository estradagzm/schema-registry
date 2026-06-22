"""
Validation and deserialization logic.

1. Validates a JSON payload against a stored JSON Schema (draft-7).
2. On success, deserializes the payload into a typed Pydantic model
   built dynamically from the schema properties.
"""
from typing import Any

import jsonschema
from jsonschema import Draft7Validator, SchemaError, ValidationError
from pydantic import BaseModel, create_model

# ── JSON Schema validation ────────────────────────────────────────────────────

def validate_schema_document(schema: dict[str, Any]) -> list[str]:
    """
    Check that the submitted document is itself a valid JSON Schema.
    Returns a list of error messages (empty = valid).
    """
    try:
        Draft7Validator.check_schema(schema)
        return []
    except SchemaError as exc:
        return [str(exc.message)]


def validate_payload(
    schema: dict[str, Any],
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Validate *payload* against *schema*.
    Returns a list of structured error dicts (empty = valid).
    """
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    return [
        {
            "field": ".".join(str(p) for p in err.absolute_path) or "(root)",
            "message": err.message,
            "schema_path": ".".join(str(p) for p in err.absolute_schema_path),
        }
        for err in errors
    ]


# ── Dynamic Pydantic model ────────────────────────────────────────────────────

_JSON_TYPE_MAP = {
    "string": (str, ...),
    "integer": (int, ...),
    "number": (float, ...),
    "boolean": (bool, ...),
    "array": (list, ...),
    "object": (dict, ...),
}


def deserialize(
    schema: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a Pydantic model from the schema's top-level properties and
    return the validated, typed payload as a plain dict.

    Fields not listed in `required` are optional (default = None).
    Nested objects are left as plain dicts for MVP simplicity.
    """
    properties: dict[str, Any] = schema.get("properties", {})
    required_fields: set[str] = set(schema.get("required", []))

    field_definitions: dict[str, Any] = {}
    for field_name, field_schema in properties.items():
        json_type = field_schema.get("type", "object")
        python_type, _ = _JSON_TYPE_MAP.get(json_type, (Any, ...))
        if field_name in required_fields:
            field_definitions[field_name] = (python_type, ...)
        else:
            field_definitions[field_name] = (python_type | None, None)

    DynamicModel: type[BaseModel] = create_model("DynamicModel", **field_definitions)
    instance = DynamicModel(**payload)
    return instance.model_dump()
