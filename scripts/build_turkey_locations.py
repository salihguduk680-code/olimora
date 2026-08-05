"""Build Olimora's compact Türkiye province/district location asset.

District membership and names come from turkey-geo-api (MIT). Coordinates and
time zones come from GeoNames (CC BY 4.0). The script intentionally fails when
the expected administrative coverage or coordinate matching changes.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

EXPECTED_PROVINCES = 81
EXPECTED_DISTRICTS = 973


def normalize_turkish(value: str) -> str:
    value = value.strip().replace("Ð", "Ğ").replace("ð", "ğ")
    value = value.replace("I", "ı").replace("İ", "i").lower()
    value = re.sub(r"\s+ilçesi$", "", value)
    value = re.sub(r"\s+district$", "", value)
    value = value.split("/", maxsplit=1)[0].strip()
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    value = re.sub(r"[^a-zçğıöşü0-9]", "", value).replace("ı", "i")
    return {"19mayis": "ondokuzmayis"}.get(value, value)


def display_name(value: str) -> str:
    value = value.strip().replace("Ð", "Ğ").replace("ð", "ğ")
    words = value.replace("I", "ı").replace("İ", "i").lower().split()
    return " ".join(word[:1].upper().replace("I", "İ") + word[1:] for word in words)


def read_geonames(
    path: Path,
) -> tuple[
    dict[int, dict[str, Any]],
    dict[tuple[int, str], list[dict[str, Any]]],
    dict[tuple[int, str], list[dict[str, Any]]],
]:
    provinces: dict[int, dict[str, Any]] = {}
    districts: dict[tuple[int, str], list[dict[str, Any]]] = {}
    district_seats: dict[tuple[int, str], list[dict[str, Any]]] = {}

    with path.open(encoding="utf-8") as source:
        for line in source:
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 19:
                continue
            feature_code = columns[7]
            if feature_code not in {"ADM1", "ADM2", "PPLA2"}:
                continue

            province_id = int(columns[10])
            record = {
                "geoname_id": int(columns[0]),
                "name": columns[1],
                "latitude": float(columns[4]),
                "longitude": float(columns[5]),
                "timezone": columns[17] or "Europe/Istanbul",
            }
            if feature_code == "ADM1" and columns[6] == "A":
                provinces[province_id] = record
            elif feature_code == "ADM2" and columns[6] == "A":
                key = (province_id, normalize_turkish(columns[1]))
                districts.setdefault(key, []).append(record)
            elif feature_code == "PPLA2" and columns[6] == "P":
                key = (province_id, normalize_turkish(columns[1]))
                district_seats.setdefault(key, []).append(record)

    return provinces, districts, district_seats


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def read_current_districts(directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("province-*-districts.jsonl")):
        with path.open(encoding="utf-8") as source:
            rows.extend(json.loads(line) for line in source if line.strip())
    return rows


def build_asset(
    geonames_path: Path, provinces_path: Path, districts_directory: Path
) -> dict[str, Any]:
    geonames_provinces, geonames_districts, geonames_district_seats = read_geonames(geonames_path)
    current_provinces = read_jsonl(provinces_path)
    current_districts = read_current_districts(districts_directory)

    if len(current_provinces) != EXPECTED_PROVINCES:
        raise RuntimeError(
            f"Expected {EXPECTED_PROVINCES} provinces, found {len(current_provinces)}."
        )
    if len(current_districts) != EXPECTED_DISTRICTS:
        raise RuntimeError(
            f"Expected {EXPECTED_DISTRICTS} districts, found {len(current_districts)}."
        )

    geonames_province_by_name = {
        normalize_turkish(province["name"]): admin1
        for admin1, province in geonames_provinces.items()
    }
    province_by_id = {int(province["id"]): province for province in current_provinces}
    admin1_by_province_id: dict[int, int] = {}
    for province_id, province in province_by_id.items():
        admin1 = geonames_province_by_name.get(normalize_turkish(str(province["name"])))
        if admin1 is None:
            raise RuntimeError(f"Province matching failed: {province_id}:{province['name']}")
        admin1_by_province_id[province_id] = admin1

    by_province: dict[int, list[dict[str, Any]]] = {
        province_id: [] for province_id in province_by_id
    }
    unmatched: list[str] = []

    for district in current_districts:
        province_id = int(district["province_id"])
        province = province_by_id[province_id]
        if normalize_turkish(str(district["name"])) == "merkez":
            coordinates = province["coordinates"]
            by_province[province_id].append(
                {
                    "id": int(district["id"]),
                    "name": "Merkez",
                    "latitude": float(coordinates["latitude"]),
                    "longitude": float(coordinates["longitude"]),
                    "timezone": "Europe/Istanbul",
                }
            )
            continue

        key = (admin1_by_province_id[province_id], normalize_turkish(str(district["name"])))
        candidates = geonames_districts.get(key, [])
        if not candidates:
            candidates = geonames_district_seats.get(key, [])
        if len(candidates) != 1:
            unmatched.append(f"{province_id}:{district['name']} ({len(candidates)} matches)")
            continue
        location = candidates[0]
        by_province[province_id].append(
            {
                "id": int(district["id"]),
                "name": display_name(str(district["name"])),
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "timezone": location["timezone"],
            }
        )

    if unmatched:
        raise RuntimeError("District coordinate matching failed:\n" + "\n".join(unmatched))

    province_rows: list[dict[str, Any]] = []
    for province_id, province in province_by_id.items():
        coordinates = province["coordinates"]
        province_rows.append(
            {
                "id": province_id,
                "name": display_name(str(province["name"])),
                "latitude": float(coordinates["latitude"]),
                "longitude": float(coordinates["longitude"]),
                "timezone": "Europe/Istanbul",
                "districts": sorted(
                    by_province[province_id], key=lambda row: normalize_turkish(row["name"])
                ),
            }
        )

    province_rows.sort(key=lambda row: normalize_turkish(row["name"]))
    return {
        "schema_version": "1.0",
        "country": "Türkiye",
        "country_code": "TR",
        "sources": [
            {"name": "turkey-geo-api", "license": "MIT", "version": "1.3.0"},
            {"name": "GeoNames", "license": "CC BY 4.0", "download": "TR.zip"},
        ],
        "provinces": province_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geonames", required=True, type=Path)
    parser.add_argument("--provinces", required=True, type=Path)
    parser.add_argument("--districts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    asset = build_asset(args.geonames, args.provinces, args.districts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(asset, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    district_count = sum(len(province["districts"]) for province in asset["provinces"])
    print(
        f"Wrote {len(asset['provinces'])} provinces and {district_count} districts to {args.output}"
    )


if __name__ == "__main__":
    main()
