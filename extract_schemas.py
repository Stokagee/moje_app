#!/usr/bin/env python3
"""
Extrahuje JSON Schema z OpenAPI specifikace pro TalosForge DataGenerator.

Extrahuje request body schema ze všech POST endpointů, rekurzivně rozbalí
všechny $ref reference a uloží výsledek do talosforge_schemas.json
"""

import json
import sys
from pathlib import Path
from typing import Any


def resolve_refs(schema: Any, components: dict, visited: set | None = None) -> Any:
    """
    Rekurzivně rozbalí všechny $ref reference v schema.

    Args:
        schema: Schema objekt (může být dict, list nebo primitivní typ)
        components: Sekce components/schemas z OpenAPI spec
        visited: Set navštívených $ref pro detekci cyklů

    Returns:
        Rozbalené schema bez $ref
    """
    if visited is None:
        visited = set()

    if isinstance(schema, dict):
        # Pokud je to $ref, rozbalíme ji
        if "$ref" in schema:
            ref_path = schema["$ref"]

            # Podpora různých formátů $ref
            if ref_path.startswith("#/components/schemas/"):
                schema_name = ref_path.split("/")[-1]
                ref_key = f"components.schemas.{schema_name}"
            elif ref_path.startswith("#/schemas/"):
                schema_name = ref_path.split("/")[-1]
                ref_key = f"schemas.{schema_name}"
            else:
                # Neznámý formát, vrátíme původní
                return schema

            # Detekce cyklů
            if ref_key in visited:
                return {"$ref": f"[CYCLE: {ref_key}]"}

            visited.add(ref_key)

            # Najdeme schema v components
            if schema_name in components:
                resolved = resolve_refs(components[schema_name], components, visited.copy())
                # Přidáme popis z původního ref, pokud existuje
                if "description" in schema and "description" not in resolved:
                    resolved["description"] = schema["description"]
                return resolved
            else:
                return {"$ref": f"[NOT FOUND: {ref_key}]"}

        # Rekurzivně zpracujeme všechny hodnoty v dict
        result = {}
        for key, value in schema.items():
            if key == "$ref":
                continue  # už zpracováno výše
            result[key] = resolve_refs(value, components, visited.copy())
        return result

    elif isinstance(schema, list):
        # Rekurzivně zpracujeme všechny prvky v listu
        return [resolve_refs(item, components, visited.copy()) for item in schema]

    else:
        # Primitivní typy vrátíme tak jak jsou
        return schema


def get_post_endpoints_with_body(openapi_spec: dict) -> dict[str, dict]:
    """
    Najde všechny POST endpointy, které mají request body.

    Args:
        openapi_spec: Kompletní OpenAPI specifikace

    Returns:
        Slovník {endpoint_path: schema}
    """
    paths = openapi_spec.get("paths", {})
    components = openapi_spec.get("components", {}).get("schemas", {})

    endpoints = {}

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        if "post" not in methods:
            continue

        post_spec = methods["post"]

        # Získat requestBody
        request_body = post_spec.get("requestBody")
        if not request_body:
            continue

        # Získat content (typicky application/json)
        content = request_body.get("content", {})
        json_content = content.get("application/json") or content.get("application/octet-stream")

        if not json_content:
            continue

        # Získat schema
        schema = json_content.get("schema")
        if not schema:
            continue

        # Rozbalit všechny $ref
        resolved_schema = resolve_refs(schema, components)

        # Přidat popis z endpointu, pokud existuje
        endpoint_info = {
            "schema": resolved_schema,
            "summary": post_spec.get("summary", ""),
            "description": post_spec.get("description", ""),
        }

        # Celá cesta endpointu
        endpoint_key = f"POST {path}"
        endpoints[endpoint_key] = endpoint_info

    return endpoints


def extract_json_schemas(openapi_path: str, output_path: str) -> None:
    """
    Hlavní funkce pro extrakci JSON schemas.

    Args:
        openapi_path: Cesta k openapi.json souboru
        output_path: Cesta pro výstupní soubor
    """
    # Načíst OpenAPI spec
    with open(openapi_path, "r", encoding="utf-8") as f:
        openapi_spec = json.load(f)

    # Exraktovat POST endpointy
    endpoints = get_post_endpoints_with_body(openapi_spec)

    # Připravit výstup
    output = {}

    for endpoint_key, info in endpoints.items():
        output[endpoint_key] = {
            "schema": info["schema"],
            "summary": info["summary"],
            "description": info["description"],
        }

    # Uložit do souboru
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Extrahováno {len(output)} POST endpointů")
    print(f"Výstup uložen do: {output_path}")

    # Vypsat seznam endpointů
    print("\nExtrahované endpointy:")
    for endpoint_key in output.keys():
        print(f"  - {endpoint_key}")


def main():
    """Entry point."""
    script_dir = Path(__file__).parent
    openapi_path = script_dir / "openapi.json"
    output_path = script_dir / "talosforge_schemas.json"

    if not openapi_path.exists():
        print(f"Chyba: Soubor {openapi_path} neexistuje")
        print("Nejprve spusťte: curl http://localhost:20300/openapi.json > openapi.json")
        sys.exit(1)

    extract_json_schemas(str(openapi_path), str(output_path))


if __name__ == "__main__":
    main()
