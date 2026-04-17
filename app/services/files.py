from datetime import datetime
from pathlib import Path
import re

from fastapi import UploadFile

from app.core.settings import settings

_INVALID_CHARS = re.compile(r"[\\/:*?\"<>|]+")


def _sanitize_segment(value: str, fallback: str) -> str:
    cleaned = _INVALID_CHARS.sub("-", value).strip().replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned if cleaned else fallback


def supply_folder_name(supply_id: int, description: str | None) -> str:
    safe_desc = _sanitize_segment(description or "Sin descripción", "Sin descripción")
    return f"Suministro N° {supply_id} - {safe_desc}"


def memo_folder_name(number: str, description: str) -> str:
    safe_number = _sanitize_segment(number, "S/N")
    safe_desc = _sanitize_segment(description, "Sin descripción")
    return f"Memo N° {safe_number} - {safe_desc}"


def ensure_folder(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload_to_folder(folder: Path, uploaded_file: UploadFile) -> str:
    ensure_folder(folder)
    original_name = _sanitize_segment(uploaded_file.filename or "archivo", "archivo")
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    target = folder / f"{stamp}-{original_name}"

    with target.open("wb") as f:
        while True:
            chunk = uploaded_file.file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    return str(target)


def base_storage_dir() -> Path:
    return ensure_folder(Path(settings.storage_base_dir))
