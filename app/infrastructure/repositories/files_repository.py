# app/repositories/files_repo.py
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal
from app.infrastructure.config.config import get_settings
from app.domain.entities.item import Item

_settings = get_settings()


# ---------------------------
# Paths
# ---------------------------

def _data_path(file: str) -> Path:
    return Path(_settings.data_dir).joinpath(file)


# ---------------------------
# Parsers / helpers (KISS)
# ---------------------------

def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def _to_int(v: Any, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default


def _to_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"true", "1", "yes", "y", "t", "si", "sí"}


def _split_list(
    s: Optional[str],
    seps: tuple[str, ...] = ("|", ";", ",", ">"),
) -> List[str]:
    if not s:
        return []
    # Reemplaza múltiples separadores por coma y split
    tmp = str(s)
    for sep in seps:
        tmp = tmp.replace(sep, ",")
    parts = [p.strip() for p in tmp.split(",") if p.strip()]
    return parts


def _parse_json_if_possible(s: Optional[str]) -> Any:
    if not s or not isinstance(s, str):
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def _parse_pictures(value: Any) -> List[Dict]:
    """
    Admite:
      - lista de objetos (ya válida)
      - string JSON con lista
      - string con URLs separadas por coma/;/>/|
    """
    if isinstance(value, list):
        # Normaliza a lista de dicts Picture
        pics: List[Dict] = []
        for i, p in enumerate(value, start=1):
            if isinstance(p, dict):
                # Deja los campos conocidos, ignora extras
                pics.append({
                    "id": p.get("id") or f"PIC-{i}",
                    "url": p.get("url") or p.get("secure_url") or "",
                    "secure_url": p.get("secure_url"),
                    "size": p.get("size"),
                    "max_size": p.get("max_size"),
                    "quality": p.get("quality"),
                })
            elif isinstance(p, str):
                pics.append({
                    "id": f"PIC-{i}",
                    "url": p,
                    "secure_url": p if p.startswith("https://") else None,
                })
        return pics

    if isinstance(value, str):
        # ¿Es JSON?
        parsed = _parse_json_if_possible(value)
        if isinstance(parsed, list):
            return _parse_pictures(parsed)
        # Si es lista de urls separadas
        urls = _split_list(value)
        pics: List[Dict] = []
        for i, u in enumerate(urls, start=1):
            pics.append({
                "id": f"PIC-{i}",
                "url": u,
                "secure_url": u if u.startswith("https://") else None,
            })
        return pics

    return []


def _parse_attributes(value: Any) -> List[Dict]:
    """
    Admite:
      - lista de objetos (ya válida)
      - string JSON con lista
      - string tipo "BRAND:Apple;MODEL:iPhone 11"
    """
    if isinstance(value, list):
        attrs: List[Dict] = []
        for a in value:
            if isinstance(a, dict):
                attrs.append({
                    "id": a.get("id") or (a.get("name") or "").upper().replace(" ", "_") or "ATTR",
                    "name": a.get("name") or a.get("id") or "Atributo",
                    "value_id": a.get("value_id"),
                    "value_name": a.get("value_name"),
                    "attribute_group_id": a.get("attribute_group_id"),
                    "attribute_group_name": a.get("attribute_group_name"),
                })
        return attrs

    if isinstance(value, str):
        parsed = _parse_json_if_possible(value)
        if isinstance(parsed, list):
            return _parse_attributes(parsed)

        # Formato simple clave:valor;clave:valor
        pairs = _split_list(value)
        attrs: List[Dict] = []
        for p in pairs:
            if ":" in p:
                k, v = p.split(":", 1)
                k = k.strip()
                v = v.strip()
                attrs.append({
                    "id": k.upper().replace(" ", "_"),
                    "name": k,
                    "value_name": v or None,
                })
        return attrs

    return []


def _build_shipping(row: Dict[str, Any]) -> Optional[Dict]:
    # Intenta armar shipping si hay al menos un campo presente
    keys = ("shipping_free_shipping", "shipping_mode", "shipping_logistic_type", "shipping_store_pick_up")
    if not any(k in row and str(row.get(k)).strip() != "" for k in keys):
        return None

    return {
        "free_shipping": _to_bool(row.get("shipping_free_shipping")),
        "mode": str(row.get("shipping_mode") or "me2"),
        "logistic_type": str(row.get("shipping_logistic_type") or "drop_off"),
        "store_pick_up": _to_bool(row.get("shipping_store_pick_up")),
    }


def _build_seller(row: Dict[str, Any]) -> Optional[Dict]:
    sid = row.get("seller_id")
    nick = row.get("seller_nickname")
    if not sid and not nick:
        return None
    return {
        "id": str(sid or "SELLER001"),
        "nickname": str(nick) if nick else None,
    }


def _coerce_item_from_row(row: Dict[str, Any]) -> Dict:
    """Convierte una fila CSV o un dict suelto a diccionario normalizado.
    
    Retorna un diccionario que puede ser usado para crear entidades DDD.
    """
    item_dict = {
        "id": str(row.get("id", "")).strip(),
        "title": str(row.get("title", "")).strip(),
        "category_id": str(row.get("category_id", "")).strip(),
        "price": _to_float(row.get("price")),
        "currency_id": str(row.get("currency_id", "ARS")),
        "available_quantity": _to_int(row.get("available_quantity")),
        "sold_quantity": _to_int(row.get("sold_quantity")),
        "condition": str(row.get("condition", "new")),
        "permalink": str(row.get("permalink", "")),
        # pictures / attributes pueden venir en varios formatos:
        "pictures": _parse_pictures(row.get("pictures") or row.get("picture_urls")),
        "attributes": _parse_attributes(row.get("attributes") or row.get("attributes_json")),
        # shipping / seller
        "shipping": _build_shipping(row),
        "seller": _build_seller(row),
        # warranty / category_path
        "warranty": (str(row.get("warranty")).strip() if row.get("warranty") not in (None, "") else None),
        "category_path": _split_list(row.get("category_path")),
    }

    return item_dict


# ---------------------------
# Loaders públicos (SOLID)
# ---------------------------

def load_items() -> List[Item]:
    """
    Carga items desde JSON o CSV según DATA_SOURCE.
    - Crea entidades DDD Item validadas.
    - Devuelve lista de entidades Item.
    """
    source = (_settings.data_source or "json").lower()

    if source == "csv":
        return _load_items_from_csv()

    # JSON por defecto
    return _load_items_from_json()


def _load_items_from_json() -> List[Item]:
    """Carga items desde JSON."""
    path = _data_path("items.json")
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return []

    items: List[Item] = []
    for raw in data:
        try:
            item_dict = _coerce_item_from_row(raw)
            item = Item.from_dict(item_dict)
            items.append(item)
        except Exception as e:
            print(f"Error procesando item {raw.get('id', '?')}: {e}")
    return items


def _load_items_from_csv() -> List[Item]:
    """Carga items desde CSV."""
    path = _data_path("items.csv")
    if not path.exists():
        return []

    items: List[Item] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                item_dict = _coerce_item_from_row(row)
                item = Item.from_dict(item_dict)
                items.append(item)
            except Exception as e:
                print(f"Error procesando fila {row.get('id', '?')}: {e}")
    return items
