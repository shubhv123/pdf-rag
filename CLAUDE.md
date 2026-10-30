# CLAUDE.md — Repository Context & Migration Guardrails

## Active Dependency Standards
- **fastapi**: `0.162.0` (Upgraded from `0.111.0` via DriftZero)
- **Verification Suite**: `pytest test_migration_parity.py -v`

## Strict Coding Rules for AI Agents
### @router.post('', response_model=UploadResponse, status_code=status.HTTP_201_CREATED, summary='Upload and index a document')
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of @router.post('', response_model=UploadResponse, status_code=status.HTTP_201_CREATED, summary='Upload and index a document')`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for @router.post('', response_model=UploadResponse, status_code=status.HTTP_201_CREATED, summary='Upload and index a document') in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol '@router.post('', response_model=UploadResponse, status_code=status.HTTP_201_CREATED, summary='Upload and index a document')' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### APIRouter()
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of APIRouter()`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for APIRouter() in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'APIRouter()' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### FastAPI()
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of FastAPI()`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for FastAPI() in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'FastAPI()' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### File()
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of File()`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for File() in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'File()' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### HTTPException()
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of HTTPException()`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for HTTPException() in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'HTTPException()' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### TestClient()
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of TestClient()`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for TestClient() in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'TestClient()' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### fastapi.APIRouter
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of fastapi.APIRouter`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for fastapi.APIRouter in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'fastapi.APIRouter' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes

### fastapi.FastAPI
- **FORBIDDEN (Legacy 0.111.0):** `# Legacy usage of fastapi.FastAPI`
- **REQUIRED (Target 0.162.0):** `# Modern replacement for fastapi.FastAPI in fastapi 0.162.0`
- **Required Imports:** ``
- **Silent Semantic Drift Warning:** Symbol 'fastapi.FastAPI' updated in fastapi 0.162.0. Check import path and argument signature.
- **Verified Source:** https://fastapi.tiangolo.com/release-notes


## Sandbox Quality Assurance
- Autonomous self-healing patched `backend/app/config.py, backend/app/main.py, backend/app/models/schemas.py, backend/app/routes/query.py, backend/app/routes/upload.py, backend/app/services/document_processor.py, backend/app/services/embeddings.py, backend/app/services/rag_pipeline.py, backend/app/services/vector_store.py` to eliminate silent semantic drift. Always verify default arguments, validation lifecycles, and keyword arguments in fastapi 0.162.0.
- Autonomous self-healing patched `backend/app/config.py, backend/app/main.py, backend/app/models/schemas.py, backend/app/routes/query.py, backend/app/routes/upload.py, backend/app/services/document_processor.py, backend/app/services/embeddings.py, backend/app/services/rag_pipeline.py, backend/app/services/vector_store.py` to eliminate silent semantic drift. Always verify default arguments, validation lifecycles, and keyword arguments in fastapi 0.162.0.
