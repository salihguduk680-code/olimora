"""Build the bundled Syria location picker data from the GeoNames country dump."""

import csv
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

GOVERNORATE_NAMES = {
    "01": "Haseke",
    "02": "Lazkiye",
    "03": "Kuneytire",
    "04": "Rakka",
    "05": "Süveyda",
    "06": "Dera",
    "07": "Deyrizor",
    "08": "Şam Kırsalı",
    "09": "Halep",
    "10": "Hama",
    "11": "Humus",
    "12": "İdlib",
    "13": "Şam",
    "14": "Tartus",
}


def main() -> None:
    source_zip, output_path = map(Path, sys.argv[1:3])
    places: dict[str, list[dict[str, object]]] = defaultdict(list)
    with zipfile.ZipFile(source_zip) as archive:
        source_name = next(name for name in archive.namelist() if name.upper() == "SY.TXT")
        with archive.open(source_name) as raw:
            rows = csv.reader((line.decode("utf-8") for line in raw), delimiter="\t")
            for row in rows:
                if len(row) < 15:
                    continue
                if row[6] != "P" or int(row[14] or 0) < 1_000 or row[10] not in GOVERNORATE_NAMES:
                    continue
                places[row[10]].append(
                    {
                        "id": int(row[0]),
                        "name": row[2],
                        "latitude": float(row[4]),
                        "longitude": float(row[5]),
                        "timezone": "Asia/Damascus",
                        "population": int(row[14] or 0),
                    }
                )

    provinces = []
    for code, name in GOVERNORATE_NAMES.items():
        districts = sorted(places[code], key=lambda item: str(item["name"]))
        center = max(districts, key=lambda item: int(item["population"]))
        for district in districts:
            district.pop("population")
        provinces.append(
            {
                "id": int(code),
                "name": name,
                "latitude": center["latitude"],
                "longitude": center["longitude"],
                "timezone": "Asia/Damascus",
                "districts": districts,
            }
        )
    document = {
        "schema_version": "1.0",
        "country": "Suriye",
        "country_code": "SY",
        "sources": [{"name": "GeoNames", "license": "CC BY 4.0", "download": "SY.zip"}],
        "provinces": sorted(provinces, key=lambda item: str(item["name"])),
    }
    output_path.write_text(json.dumps(document, ensure_ascii=False, separators=(",", ":")), "utf-8")


if __name__ == "__main__":
    main()
