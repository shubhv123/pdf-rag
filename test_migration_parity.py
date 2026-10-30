# Auto-generated Differential Parity Test Suite by DriftZero
# Target Library: fastapi (0.162.0)
import os
import sys
import json
import pytest
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date

# Ensure workspace root and src directory are on sys.path
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
_src_dir = _repo_root / "src"
if _src_dir.exists() and str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

# Compatibility fix for Python 3.14+ PEP 649 deferred annotations with legacy Pydantic v1
try:
    import pydantic.main
    if hasattr(pydantic.main, "ModelMetaclass"):
        _orig_model_meta_new = pydantic.main.ModelMetaclass.__new__
        def _compat_model_meta_new(mcs, name, bases, namespace, **kwargs):
            if "__annotate_func__" in namespace and not namespace.get("__annotations__"):
                try:
                    namespace["__annotations__"] = namespace["__annotate_func__"](1)
                except Exception:
                    pass
            return _orig_model_meta_new(mcs, name, bases, namespace, **kwargs)
        pydantic.main.ModelMetaclass.__new__ = _compat_model_meta_new
except Exception:
    pass

GOLDEN_FILE = Path(__file__).resolve().parent / "golden.json"
IS_RECORDING = os.getenv("DRIFTZERO_RECORD_GOLDEN", "0") == "1"

# Module-level golden store
_golden_store: dict = {}

def _load_golden() -> dict:
    global _golden_store
    if _golden_store:
        return _golden_store
    if not GOLDEN_FILE.exists():
        if not IS_RECORDING:
            raise AssertionError(
                f"Golden baseline file '{GOLDEN_FILE}' not found! "
                "The old-version container must run with DRIFTZERO_RECORD_GOLDEN=1 first "
                "to record golden baseline outputs before running differential verification."
            )
        return _golden_store
    try:
        _golden_store.clear()
        _golden_store.update(json.loads(GOLDEN_FILE.read_text(encoding="utf-8")))
        return _golden_store
    except Exception as exc:
        raise AssertionError(f"Failed to read golden baseline file: {exc}")

def _save_golden():
    global _golden_store
    GOLDEN_FILE.write_text(json.dumps(_golden_store, indent=2, default=str), encoding="utf-8")


def _generate_sample_input_for_field(field_name: str, type_annotation: str = ""):
    name = field_name.lower()
    t_clean = type_annotation.lower().strip()

    if name == "postal_code":
        return "94105"
    if "email" in name:
        return "dev@example.com"
    if name in ("sender_country", "receiver_country", "country"):
        return "US"
    if name in ("amount", "amount_usd", "price", "rate", "fee", "balance", "cost", "fx_rate"):
        return 100.0
    if name in ("quantity", "count", "limit", "retries", "max_retries", "timeout_seconds", "attempt_count", "unit_price_cents", "qty"):
        return 5
    if name in ("created_at", "updated_at", "timestamp", "date"):
        return "2025-01-01T12:00:00"
    if name in ("is_", "has_", "active", "enabled", "requires_manual_compliance_review"):
        return False
    if name in ("tags", "list", "categories"):
        return ["item_1", "item_2"]
    if name in ("payload", "data", "meta", "metadata", "config", "data_object", "payload_snapshot"):
        return {"status": "ok", "env": "test"}
    if name == "street":
        return "123 Market St"
    if name == "city":
        return "San Francisco"
    if name == "sku":
        return "SKU-TEST-001"
    if name.endswith("_id") or name == "id" or name in ("order_id", "customer_id", "transaction_id", "trace_id", "actor_id", "event_id"):
        return f"test_{field_name}_123"
    if name == "primary_address":
        return {"street": "123 Market St", "city": "San Francisco", "postal_code": "94105"}
    if name == "items":
        return [{"sku": "SKU-001", "quantity": 2, "unit_price_cents": 500}]
    if name == "order":
        return {"order_id": "test_order_123", "created_at": "2025-01-01T12:00:00", "items": [{"sku": "SKU-1", "quantity": 1, "unit_price_cents": 100}]}
    if name == "raw_dict":
        return {"order_id": "test_order_123", "created_at": "2025-01-01T12:00:00", "items": [{"sku": "SKU-1", "quantity": 1, "unit_price_cents": 100}]}
    if name == "raw_json":
        return json.dumps({"order_id": "test_order_123", "created_at": "2025-01-01T12:00:00", "items": [{"sku": "SKU-1", "quantity": 1, "unit_price_cents": 100}]})
    if name == "raw_list" or ("list" in t_clean and "dict" in t_clean):
        return [{"trace_id": "test_trace_123", "attempt_count": 1, "payload": {"status": "ok"}, "scores": [0.2, 0.5, 0.8]}]
    if name == "prompt":
        return {"system_instruction": "Summarize", "user_transcript": "User dialog", "temperature": 0.5}
    if name in ("scores", "__root__", "root"):
        return [0.2, 0.5, 0.8]

    if "int" in t_clean and "list" not in t_clean:
        return 5
    if "float" in t_clean and "list" not in t_clean:
        return 10.5
    if "bool" in t_clean:
        return True
    if "list" in t_clean:
        if "float" in t_clean:
            return [0.2, 0.5, 0.8]
        if "int" in t_clean:
            return [1, 2, 3]
        return ["item_1", "item_2"]
    if "dict" in t_clean:
        return {"key": "value"}
    if "datetime" in t_clean or "date" in t_clean:
        return "2025-01-01T12:00:00"

    return f"sample_{field_name}"


def _build_model_sample_inputs(cls_obj, fallback=None):
    """
    Builds sample inputs at test runtime from the model's own fields
    (model_fields in Pydantic v2 or __fields__ in Pydantic v1, including all inherited ones).
    """
    fields_dict = getattr(cls_obj, "model_fields", None)
    if fields_dict is None:
        fields_dict = getattr(cls_obj, "__fields__", None)

    if not isinstance(fields_dict, dict):
        return dict(fallback or {})

    kwargs = dict(fallback or {})
    for f_name, f_info in fields_dict.items():
        type_str = ""
        if hasattr(f_info, "annotation") and f_info.annotation is not None:
            type_str = getattr(f_info.annotation, "__name__", str(f_info.annotation))
        elif hasattr(f_info, "type_") and f_info.type_ is not None:
            type_str = getattr(f_info.type_, "__name__", str(f_info.type_))
        elif hasattr(f_info, "outer_type_") and f_info.outer_type_ is not None:
            type_str = getattr(f_info.outer_type_, "__name__", str(f_info.outer_type_))

        if f_name not in kwargs or kwargs[f_name] is None:
            kwargs[f_name] = _generate_sample_input_for_field(f_name, type_str)
        elif kwargs[f_name] == f"sample_{f_name}" and type_str:
            kwargs[f_name] = _generate_sample_input_for_field(f_name, type_str)

    return kwargs


def _serialize_value(val, mode="json"):
    """
    Serializes models and Python values across legacy and modern library versions.
    Normalizes both sides through mode='json' (converts Decimals, datetimes, Enums, sets to JSON-safe types).
    """
    if val is None:
        return None

    if hasattr(val, "value"):
        return _serialize_value(val.value, mode=mode)

    # Modern Pydantic v2 / dataclasses with model_dump
    if hasattr(val, "model_dump") and callable(getattr(val, "model_dump")):
        if mode == "json":
            try:
                dumped = val.model_dump(mode="json")
                return _serialize_value(dumped, mode=mode)
            except Exception:
                try:
                    return json.loads(json.dumps(val.model_dump(), default=str))
                except Exception:
                    pass
        return val.model_dump()

    # Legacy Pydantic v1 / objects with dict()
    if hasattr(val, "dict") and callable(getattr(val, "dict")):
        if mode == "json":
            if hasattr(val, "json") and callable(getattr(val, "json")):
                try:
                    return json.loads(val.json())
                except Exception:
                    pass
            try:
                return json.loads(json.dumps(val.dict(), default=str))
            except Exception:
                pass
        return val.dict()

    if isinstance(val, str):
        s_val = val.strip()
        if (s_val.startswith("{") and s_val.endswith("}")) or (s_val.startswith("[") and s_val.endswith("]")):
            try:
                parsed_json = json.loads(s_val)
                return _serialize_value(parsed_json, mode=mode)
            except Exception:
                pass
        return val.replace("#/$defs/", "#/definitions/")

    if isinstance(val, (int, float, bool)):
        return val
    if isinstance(val, (list, tuple)):
        return [_serialize_value(item, mode=mode) for item in val]
    if isinstance(val, (set, frozenset)):
        serialized_items = [_serialize_value(item, mode=mode) for item in val]
        return sorted(serialized_items, key=lambda x: json.dumps(x, default=str) if isinstance(x, (dict, list)) else str(x))
    if isinstance(val, dict):
        norm_dict = {}
        for k, v in val.items():
            str_k = str(k)
            if str_k in ("$defs", "definitions"):
                str_k = "definitions"
            norm_dict[str_k] = _serialize_value(v, mode=mode)
        return norm_dict
    if isinstance(val, Decimal):
        return str(val) if mode == "json" else float(val)
    if isinstance(val, (datetime, date)):
        return val.isoformat()

    return str(val)


def _is_base_settings_subclass(cls_obj):
    try:
        if isinstance(cls_obj, type) and cls_obj.__name__ != "BaseSettings":
            return any(base.__name__ == "BaseSettings" for base in cls_obj.__mro__)
    except Exception:
        pass
    return False


def _get_field_env_vars_to_set(cls_obj, sample_kwargs):
    env_vars = {}
    env_prefix = ""
    model_config = getattr(cls_obj, "model_config", None)
    if isinstance(model_config, dict):
        env_prefix = model_config.get("env_prefix", "") or ""
    elif hasattr(model_config, "env_prefix"):
        env_prefix = getattr(model_config, "env_prefix", "") or ""

    if not env_prefix:
        cfg = getattr(cls_obj, "Config", None)
        if cfg and hasattr(cfg, "env_prefix"):
            env_prefix = getattr(cfg, "env_prefix", "") or ""

    fields_dict = getattr(cls_obj, "model_fields", None)
    if fields_dict is None:
        fields_dict = getattr(cls_obj, "__fields__", None)
    if not isinstance(fields_dict, dict):
        fields_dict = {k: None for k in sample_kwargs}

    for f_name, val in (sample_kwargs or {}).items():
        f_info = fields_dict.get(f_name)
        var_name = ""

        if f_info is not None:
            extra = getattr(getattr(f_info, "field_info", None), "extra", {})
            env_val = getattr(f_info, "env", None)
            if isinstance(extra, dict) and extra.get("env"):
                var_name = extra["env"]
            elif isinstance(env_val, str) and env_val:
                var_name = env_val
            elif getattr(getattr(f_info, "field_info", None), "env", None):
                var_name = getattr(f_info.field_info, "env")

            if not var_name:
                v_alias = getattr(f_info, "validation_alias", None)
                if isinstance(v_alias, str) and v_alias:
                    var_name = v_alias
                elif getattr(f_info, "has_alias", False) and isinstance(getattr(f_info, "alias", None), str):
                    var_name = f_info.alias

        if not var_name:
            var_name = f"{env_prefix}{f_name}".upper()

        if hasattr(val, "value"):
            val = val.value

        if isinstance(val, bool):
            str_val = "true" if val else "false"
        elif isinstance(val, (dict, list)):
            str_val = json.dumps(val)
        elif isinstance(val, (datetime, date)):
            str_val = val.isoformat()
        else:
            str_val = str(val)

        env_vars[var_name] = str_val
        env_vars[f"{env_prefix}{f_name}".upper()] = str_val

    return env_vars


def verify_base_settings_env_differential(mod_name: str, cls_name: str, cls_obj, sample_kwargs: dict = None):
    """
    Differential parity assertion for BaseSettings subclasses:
    Sets each field's environment variable, instantiates the model with no arguments,
    and records/verifies the resulting instance against golden.json.
    Restores original environment variables afterward.
    """
    global _golden_store
    golden_key = f"settings_env::{mod_name}.{cls_name}"

    final_kwargs = _build_model_sample_inputs(cls_obj, fallback=sample_kwargs)
    env_vars = _get_field_env_vars_to_set(cls_obj, final_kwargs)

    saved_env = {}
    keys_to_clean = []
    try:
        for k, v in env_vars.items():
            if k in os.environ:
                saved_env[k] = os.environ[k]
            else:
                keys_to_clean.append(k)
            os.environ[k] = v

        if IS_RECORDING:
            record = {}
            try:
                try:
                    instance = cls_obj(_env_file=None)
                except (TypeError, ValueError):
                    instance = cls_obj()
                record["status"] = "ok"
                record["output"] = _serialize_value(instance, mode="json")
            except Exception as exc:
                record["status"] = "error"
                record["error_type"] = type(exc).__name__

            _load_golden()
            _golden_store[golden_key] = record
            _save_golden()
            return

        golden = _load_golden()
        if golden_key not in golden:
            raise AssertionError(
                f"Missing golden baseline entry for BaseSettings '{mod_name}.{cls_name}'. "
                "Old-version container must record golden.json before verification."
            )

        expected = golden[golden_key]
        if expected["status"] == "ok":
            try:
                instance = cls_obj(_env_file=None)
            except (TypeError, ValueError):
                instance = cls_obj()
            actual_norm = _serialize_value(instance, mode="json")
            expected_norm = _serialize_value(expected["output"], mode="json")
            assert actual_norm == expected_norm, (
                f"Differential BaseSettings Parity Mismatch for '{cls_name}' when loaded from env vars:\n"
                f"Expected (Golden): {expected_norm}\n"
                f"Actual   (New):    {actual_norm}"
            )
        else:
            with pytest.raises(Exception) as exc_info:
                cls_obj()
            actual_type = exc_info.value.__class__.__name__
            expected_type = expected["error_type"]
            assert actual_type == expected_type, (
                f"Error type mismatch for BaseSettings '{cls_name}' loaded from env vars: "
                f"expected {expected_type}, got {actual_type}"
            )
    finally:
        for k in keys_to_clean:
            os.environ.pop(k, None)
        for k, v in saved_env.items():
            os.environ[k] = v


def verify_model_differential(mod_name: str, cls_name: str, cls_obj, sample_kwargs: dict = None):
    """
    Differential parity assertion for models:
    - Builds inputs at test runtime from model_fields or __fields__, including inherited ones.
    - Normalizes both sides through _serialize_value(mode="json") before comparing.
    - Compares error type only, not message.
    - For BaseSettings subclasses, runs environment variable check.
    """
    global _golden_store
    golden_key = f"model::{mod_name}.{cls_name}"

    runtime_inputs = _build_model_sample_inputs(cls_obj, fallback=sample_kwargs)
    final_kwargs = runtime_inputs if runtime_inputs else dict(sample_kwargs or {})

    if IS_RECORDING:
        record = {}
        try:
            instance = cls_obj(**final_kwargs)
            record["status"] = "ok"
            record["output"] = _serialize_value(instance, mode="json")
            record["model_dump"] = record["output"]
            record["model_dump_json"] = record["output"]
        except Exception as exc:
            record["status"] = "error"
            record["error_type"] = type(exc).__name__

        # Record error type on invalid / empty inputs
        try:
            cls_obj()
            record["empty_input_status"] = "ok"
        except Exception as exc:
            record["empty_input_status"] = "error"
            record["invalid_error_type"] = type(exc).__name__

        _load_golden()
        _golden_store[golden_key] = record
        _save_golden()

        # Runtime check for BaseSettings subclasses: set each field's env var and compare against golden
        if _is_base_settings_subclass(cls_obj):
            verify_base_settings_env_differential(mod_name, cls_name, cls_obj, sample_kwargs=final_kwargs)
        return

    # Verification Mode (New Container)
    golden = _load_golden()
    if golden_key not in golden:
        raise AssertionError(
            f"Missing golden baseline entry for model '{mod_name}.{cls_name}'. "
            "Old-version container must record golden.json before verification."
        )

    expected = golden[golden_key]

    if expected["status"] == "ok":
        instance = cls_obj(**final_kwargs)

        # Normalize both sides through _serialize_value(mode="json") before comparing
        actual_norm = _serialize_value(instance, mode="json")
        expected_norm = _serialize_value(
            expected.get("output") or expected.get("model_dump_json") or expected.get("model_dump"),
            mode="json"
        )
        assert actual_norm == expected_norm, (
            f"Differential Model Parity Mismatch for '{cls_name}':\n"
            f"Expected (Golden): {expected_norm}\n"
            f"Actual   (New):    {actual_norm}"
        )
    else:
        # Expected error on instantiation: compare error type only, not message
        with pytest.raises(Exception) as exc_info:
            cls_obj(**final_kwargs)
        actual_type = exc_info.value.__class__.__name__
        expected_type = expected["error_type"]
        assert actual_type == expected_type, (
            f"Error type mismatch for '{cls_name}': expected {expected_type}, got {actual_type}"
        )

    # Assert error type on invalid / empty inputs: compare error type only, not message
    if expected.get("empty_input_status") == "error":
        with pytest.raises(Exception) as exc_info:
            cls_obj()
        actual_type = exc_info.value.__class__.__name__
        expected_type = expected["invalid_error_type"]
        assert actual_type == expected_type, (
            f"Validation error type mismatch for invalid inputs on '{cls_name}': "
            f"expected {expected_type}, got {actual_type}"
        )

    # Runtime check for BaseSettings subclasses: set each field's env var and compare against golden
    if _is_base_settings_subclass(cls_obj):
        verify_base_settings_env_differential(mod_name, cls_name, cls_obj, sample_kwargs=final_kwargs)


def verify_function_differential(mod_name: str, fn_name: str, fn_obj, sample_kwargs: dict = None):
    """
    Differential parity assertion for functions:
    - Normalizes both sides through _serialize_value(mode="json") before comparing.
    - Compares error type only, not message.
    """
    global _golden_store
    golden_key = f"func::{mod_name}.{fn_name}"
    final_kwargs = dict(sample_kwargs or {})

    if IS_RECORDING:
        record = {}
        try:
            res = fn_obj(**final_kwargs)
            record["status"] = "ok"
            record["output"] = _serialize_value(res, mode="json")
        except Exception as exc:
            record["status"] = "error"
            record["error_type"] = type(exc).__name__

        _load_golden()
        _golden_store[golden_key] = record
        _save_golden()
        return

    # Verification Mode (New Container)
    golden = _load_golden()
    if golden_key not in golden:
        raise AssertionError(
            f"Missing golden baseline entry for function '{mod_name}.{fn_name}'. "
            "Old-version container must record golden.json before verification."
        )

    expected = golden[golden_key]

    if expected["status"] == "ok":
        res = fn_obj(**final_kwargs)
        actual_norm = _serialize_value(res, mode="json")
        expected_norm = _serialize_value(expected["output"], mode="json")
        assert actual_norm == expected_norm, (
            f"Differential Function Parity Mismatch for '{fn_name}':\n"
            f"Expected (Golden): {expected_norm}\n"
            f"Actual   (New):    {actual_norm}"
        )
    else:
        # Expected error on function execution: compare error type only, not message
        with pytest.raises(Exception) as exc_info:
            fn_obj(**final_kwargs)
        actual_type = exc_info.value.__class__.__name__
        expected_type = expected["error_type"]
        assert actual_type == expected_type, (
            f"Function error type mismatch for '{fn_name}': expected {expected_type}, got {actual_type}"
        )


def test_differential_parity_0_backend_app_config():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.config import Settings

    # Differential Parity Test for Model: backend.app.config.Settings
    sample_kwargs = _build_model_sample_inputs(Settings, fallback={'hf_api_key': 'sample_hf_api_key', 'llm_model_id': 'test_llm_model_id_123', 'embedding_model_id': 'test_embedding_model_id_123', 'chunk_size': 5, 'chunk_overlap': 5, 'top_k': 5, 'upload_dir': 'sample_upload_dir', 'vector_store_dir': 'sample_vector_store_dir'})
    verify_model_differential("backend.app.config", "Settings", Settings, sample_kwargs)



def test_differential_parity_1_backend_app_main():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.main import lifespan, health

    # Differential Parity Test for Function: backend.app.main.lifespan
    sample_kwargs = {'app': 'sample_app'}
    verify_function_differential("backend.app.main", "lifespan", lifespan, sample_kwargs)

    # Differential Parity Test for Function: backend.app.main.health
    sample_kwargs = {}
    verify_function_differential("backend.app.main", "health", health, sample_kwargs)



def test_differential_parity_2_backend_app_models_schemas():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.models.schemas import UploadResponse, QueryRequest, SourceChunk, QueryResponse, ErrorResponse

    # Differential Parity Test for Model: backend.app.models.schemas.UploadResponse
    sample_kwargs = _build_model_sample_inputs(UploadResponse, fallback={'session_id': 'test_session_id_123', 'filename': 'sample_filename', 'chunk_count': 5, 'message': 'sample_message'})
    verify_model_differential("backend.app.models.schemas", "UploadResponse", UploadResponse, sample_kwargs)

    # Differential Parity Test for Model: backend.app.models.schemas.QueryRequest
    sample_kwargs = _build_model_sample_inputs(QueryRequest, fallback={'session_id': 'test_session_id_123', 'question': 'sample_question'})
    verify_model_differential("backend.app.models.schemas", "QueryRequest", QueryRequest, sample_kwargs)

    # Differential Parity Test for Model: backend.app.models.schemas.SourceChunk
    sample_kwargs = _build_model_sample_inputs(SourceChunk, fallback={'content': 'sample_content', 'source': 'sample_source', 'page': 5, 'chunk_index': 5})
    verify_model_differential("backend.app.models.schemas", "SourceChunk", SourceChunk, sample_kwargs)

    # Differential Parity Test for Model: backend.app.models.schemas.QueryResponse
    sample_kwargs = _build_model_sample_inputs(QueryResponse, fallback={'question': 'sample_question', 'answer': 'sample_answer', 'sources': ['item_1', 'item_2']})
    verify_model_differential("backend.app.models.schemas", "QueryResponse", QueryResponse, sample_kwargs)

    # Differential Parity Test for Model: backend.app.models.schemas.ErrorResponse
    sample_kwargs = _build_model_sample_inputs(ErrorResponse, fallback={'detail': 'sample_detail'})
    verify_model_differential("backend.app.models.schemas", "ErrorResponse", ErrorResponse, sample_kwargs)



def test_differential_parity_3_backend_app_routes_query():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.routes.query import query_document
    from backend.app.models.schemas import QueryRequest

    # Differential Parity Test for Function: backend.app.routes.query.query_document
    sample = _build_model_sample_inputs(QueryRequest, fallback={'session_id': 'test_session_id_123', 'question': 'sample_question'})
    sample_kwargs = {'body': QueryRequest(**sample)}
    verify_function_differential("backend.app.routes.query", "query_document", query_document, sample_kwargs)



def test_differential_parity_4_backend_app_routes_upload():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.routes.upload import upload_document

    # Differential Parity Test for Function: backend.app.routes.upload.upload_document
    sample_kwargs = {'file': 'sample_file'}
    verify_function_differential("backend.app.routes.upload", "upload_document", upload_document, sample_kwargs)



def test_differential_parity_5_backend_app_services_document_processor():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.services.document_processor import parse_document, chunk_documents, process_file

    # Differential Parity Test for Function: backend.app.services.document_processor.parse_document
    sample_kwargs = {'file_path': 'sample_file_path'}
    verify_function_differential("backend.app.services.document_processor", "parse_document", parse_document, sample_kwargs)

    # Differential Parity Test for Function: backend.app.services.document_processor.chunk_documents
    sample_kwargs = {'documents': ['item_1', 'item_2']}
    verify_function_differential("backend.app.services.document_processor", "chunk_documents", chunk_documents, sample_kwargs)

    # Differential Parity Test for Function: backend.app.services.document_processor.process_file
    sample_kwargs = {'file_path': 'sample_file_path'}
    verify_function_differential("backend.app.services.document_processor", "process_file", process_file, sample_kwargs)



def test_differential_parity_6_backend_app_services_embeddings():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.services.embeddings import get_embeddings

    # Differential Parity Test for Function: backend.app.services.embeddings.get_embeddings
    sample_kwargs = {}
    verify_function_differential("backend.app.services.embeddings", "get_embeddings", get_embeddings, sample_kwargs)



def test_differential_parity_7_backend_app_services_rag_pipeline():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.services.rag_pipeline import get_local_model_and_tokenizer, run_rag

    # Differential Parity Test for Function: backend.app.services.rag_pipeline.get_local_model_and_tokenizer
    sample_kwargs = {}
    verify_function_differential("backend.app.services.rag_pipeline", "get_local_model_and_tokenizer", get_local_model_and_tokenizer, sample_kwargs)

    # Differential Parity Test for Function: backend.app.services.rag_pipeline.run_rag
    sample_kwargs = {'session_id': 'test_session_id_123', 'question': 'sample_question'}
    verify_function_differential("backend.app.services.rag_pipeline", "run_rag", run_rag, sample_kwargs)



def test_differential_parity_8_backend_app_services_vector_store():
    # Direct import: fails loudly with ImportError if the symbol was renamed or deleted
    from backend.app.services.vector_store import build_and_persist, load_store, session_exists

    # Differential Parity Test for Function: backend.app.services.vector_store.build_and_persist
    sample_kwargs = {'session_id': 'test_session_id_123', 'chunks': ['item_1', 'item_2']}
    verify_function_differential("backend.app.services.vector_store", "build_and_persist", build_and_persist, sample_kwargs)

    # Differential Parity Test for Function: backend.app.services.vector_store.load_store
    sample_kwargs = {'session_id': 'test_session_id_123'}
    verify_function_differential("backend.app.services.vector_store", "load_store", load_store, sample_kwargs)

    # Differential Parity Test for Function: backend.app.services.vector_store.session_exists
    sample_kwargs = {'session_id': 'test_session_id_123'}
    verify_function_differential("backend.app.services.vector_store", "session_exists", session_exists, sample_kwargs)


