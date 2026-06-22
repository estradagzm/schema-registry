from typing import Any

from fastapi import APIRouter, HTTPException, status

from app import store, validator

router = APIRouter()


class ValidationSuccess:
    pass


@router.post(
    "/{schema_id}",
    summary="Validate and deserialize a JSON payload",
    description=(
        "Submit any JSON payload. The service looks up the schema registered "
        "under `schema_id`, validates the payload against it, and — if valid — "
        "returns the deserialized, typed object. Validation errors are returned "
        "with field-level detail."
    ),
)
def validate_payload(schema_id: str, body: dict[str, Any]) -> dict[str, Any]:
    schema = store.get(schema_id)
    if schema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No schema found with id '{schema_id}'. Register it first via POST /schemas/{schema_id}.",
        )

    errors = validator.validate_payload(schema, body)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "valid": False,
                "schema_id": schema_id,
                "errors": errors,
            },
        )

    deserialized = validator.deserialize(schema, body)

    return {
        "valid": True,
        "schema_id": schema_id,
        "data": deserialized,
    }
