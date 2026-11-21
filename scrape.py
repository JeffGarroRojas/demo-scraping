#!/usr/bin/env python3
"""
Demo de scraping: extrae libros (título, precio, disponibilidad, valoración)
de una tienda de práctica y los exporta a CSV y JSON.

Usa books.toscrape.com, un sitio creado específicamente para practicar scraping.
No uses este código contra sitios que lo prohíban en sus términos de servicio.

Uso:
    python3 scrape.py                          # 3 páginas (60 libros)
    python3 scrape.py --paginas 10             # hasta 200 libros
    python3 scrape.py --salida libros.csv
    python3 scrape.py --url https://ejemplo/   # para probar otra estructura

Salidas: libros.csv y libros.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
UA = "RadarDemo/1.0 (+https://jeffgarrorojas.github.io; uso educativo)"

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def pedir(url: str, intentos: int = 3) -> str:
    """Descarga una página con reintentos y espera entre intentos."""
    for n in range(1, intentos + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError) as e:
            if n == intentos:
                raise
            print(f"  ! reintento {n}/{intentos - 1} ({e})", file=sys.stderr)
            time.sleep(2 * n)
    return ""


def limpiar(texto: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", texto)).strip()


def parsear(html: str, base_url: str) -> tuple[list[dict], str | None]:
    """Devuelve los libros de una página y la URL de la siguiente."""
    libros = []
    for bloque in re.split(r'<article class="product_pod">', html)[1:]:
        titulo = re.search(r'<h3><a[^>]*title="([^"]+)"', bloque)
        precio = re.search(r'<p class="price_color">([^<]+)</p>', bloque)
        estado = re.search(r'<p class="instock[^"]*">([^<]*(?:<[^>]+>[^<]*)*?)</p>', bloque)
        estrellas = re.search(r'<p class="star-rating (\w+)"', bloque)
        enlace = re.search(r'<h3><a href="([^"]+)"', bloque)

        if not titulo:
            continue

        libros.append({
            "titulo": limpiar(titulo.group(1)),
            "precio": (precio.group(1).replace("£", "").strip() if precio else ""),
            "moneda": "GBP",
            "disponible": "In stock" in (estado.group(1) if estado else ""),
            "valoracion": RATINGS.get(estrellas.group(1), 0) if estrellas else 0,
            "url": urllib.parse.urljoin(base_url, enlace.group(1)) if enlace else "",
        })

    siguiente = re.search(r'<li class="next"><a href="([^"]+)"', html)
    if siguiente:
        return libros, urllib.parse.urljoin(base_url, siguiente.group(1))
    return libros, None


def main() -> int:
    ap = argparse.ArgumentParser(description="Demo de scraping de libros")
    ap.add_argument("--url", default="https://books.toscrape.com/catalogue/page-1.html")
    ap.add_argument("--paginas", type=int, default=3)
    ap.add_argument("--pausa", type=float, default=1.0,
                    help="segundos entre peticiones (sé educado)")
    ap.add_argument("--salida", default="libros.csv")
    args = ap.parse_args()

    libros: list[dict] = []
    url = args.url

    for pagina in range(1, args.paginas + 1):
        if not url:
            break
        print(f"Página {pagina}: {url}")
        html = pedir(url)
        encontrados, siguiente = parsear(html, url)
        libros.extend(encontrados)
        print(f"  → {len(encontrados)} libros (acumulado: {len(libros)})")
        url = siguiente
        if url:
            time.sleep(args.pausa)

    if not libros:
        print("No se extrajo ningún libro. Revisa la URL o la estructura del sitio.",
              file=sys.stderr)
        return 1

    csv_path = BASE / args.salida
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(libros[0].keys()))
        w.writeheader()
        w.writerows(libros)

    json_path = csv_path.with_suffix(".json")
    resumen = {
        "total": len(libros),
        "disponibles": sum(1 for x in libros if x["disponible"]),
        "precio_promedio": round(
            sum(float(x["precio"]) for x in libros if x["precio"]) / len(libros), 2
        ),
        "mejor_valorados": [x["titulo"] for x in libros if x["valoracion"] == 5][:10],
        "libros": libros,
    }
    json_path.write_text(json.dumps(resumen, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    print(f"\nListo: {len(libros)} libros")
    print(f"  CSV:  {csv_path.name}")
    print(f"  JSON: {json_path.name}")
    print(f"  Precio promedio: £{resumen['precio_promedio']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
