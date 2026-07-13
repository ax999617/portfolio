from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile

from .service import (
    CONTRACT_VERSION,
    InputValidationError,
    PredictionService,
    ProviderContractError,
    ProviderExecutionError,
)


service = PredictionService()
app = FastAPI(
    title="Wheat Disease API Contract Demo",
    version=CONTRACT_VERSION,
    description="A deterministic mock and API-contract demo; it does not perform real diagnosis.",
)


@app.get("/v1/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "contract_version": CONTRACT_VERSION,
        "model_status": "demo_only",
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict[str, object]:
    image_bytes = await file.read(service.max_file_size + 1)
    try:
        return service.predict(image_bytes, file.filename or "", file.content_type)
    except InputValidationError as exc:
        raise HTTPException(status_code=422, detail={"code": exc.code, "message": str(exc)}) from exc
    except ProviderContractError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "provider_contract_error", "message": str(exc)},
        ) from exc
    except ProviderExecutionError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "provider_execution_error", "message": str(exc)},
        ) from exc
