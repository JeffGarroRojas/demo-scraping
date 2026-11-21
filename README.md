# Demo de scraping en Python

Extractor de datos con **paginación, reintentos y salida a CSV/JSON**. Sin dependencias
externas: solo la biblioteca estándar de Python.

Pensado como muestra de trabajo: hace lo mismo que un scraping de cliente, pero contra
[books.toscrape.com](https://books.toscrape.com), un sitio creado para practicar.

## Resultado

```
60 libros en 3 páginas
  titulo, precio, moneda, disponible, valoracion, url
  A Light in the Attic, 51.77, GBP, True, 3, https://...
```

## Uso

```bash
python3 scrape.py                     # 3 páginas
python3 scrape.py --paginas 10        # hasta 200 libros
python3 scrape.py --pausa 2           # más lento y más educado
python3 scrape.py --salida precios.csv
```

## Qué demuestra

| Capacidad | Dónde está |
|---|---|
| Paginación automática | `parsear()` sigue el enlace "next" |
| Reintentos con espera creciente | `pedir()` |
| Pausa entre peticiones (no abusar del servidor) | `--pausa`, por defecto 1 s |
| Parseo sin dependencias | expresiones regulares + `html` |
| URLs relativas resueltas correctamente | `urllib.parse.urljoin` |
| Salida doble para humano y para programa | CSV + JSON con resumen |
| Errores claros | mensajes en `stderr`, código de salida 1 |

## Adaptarlo a un cliente

1. Cambiar `parsear()` por los selectores del sitio del cliente.
2. Ajustar la paginación (botón "siguiente", parámetro `?page=`, API interna con JSON).
3. Validar 5 registros a mano antes de correr todo.

## Aviso legal

Este código es una demostración. Antes de usarlo en un sitio real, revisa sus términos
de servicio, su `robots.txt` y la legislación aplicable. Si el sitio exige login o
prohíbe la extracción, no se hace.

## Autor

Jefferson Garro Rojas · [jeffgarrorojas.github.io](https://jeffgarrorojas.github.io)
