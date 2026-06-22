from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app import store, validator

router = APIRouter()


class SchemaRequest(BaseModel):
    schema_: dict[str, Any] = None

    model_config = {"populate_by_name": True}

    # Accept the body directly as the schema document
    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "SchemaRequest":
        return cls(schema_=raw)


class SchemaResponse(BaseModel):
    id: str
    message: str


@router.post(
    "/{schema_id}",
    response_model=SchemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register or update a JSON schema",
    description=(
        "Submit a valid JSON Schema (draft-7) document. "
        "If a schema with this ID already exists it will be overwritten."
    ),
)
def register_schema(schema_id: str, body: dict[str, Any]) -> SchemaResponse:
    errors = validator.validate_schema_document(body)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors},
        )

    store.save(schema_id, body)
    return SchemaResponse(id=schema_id, message="Schema registered successfully.")


@router.get(
    "/{schema_id}",
    summary="Retrieve a registered schema",
)
def get_schema(schema_id: str) -> dict[str, Any]:
    schema = store.get(schema_id)
    if schema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No schema found with id '{schema_id}'.",
        )
    return schema


@router.get(
    "/",
    summary="List all registered schema IDs",
)
def list_schemas() -> dict[str, list[str]]:
    return {"schema_ids": store.list_ids()}


@router.delete(
    "/{schema_id}",
    summary="Delete a registered schema",
    status_code=status.HTTP_200_OK,
)
def delete_schema(schema_id: str) -> dict[str, str]:
    deleted = store.delete(schema_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No schema found with id '{schema_id}'.",
        )
    return {"message": f"Schema '{schema_id}' deleted."}
