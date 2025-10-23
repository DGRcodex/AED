# Diario & Poesía

Aplicación de escritorio sencilla para macOS (compatible también con otros sistemas con Python) que permite escribir un diario y poesía cada día.

## Características

- Vista principal tipo hoja en blanco que muestra la fecha del día.
- Sección dedicada para poesía independiente del diario.
- Navegación por calendario de entradas generadas automáticamente desde el 1 de enero de 2024 hasta la fecha actual con texto de ejemplo.
- Posibilidad de cambiar el color de fondo del papel.
- Exportación de la entrada seleccionada a archivos de texto (`.txt`), Markdown (`.md`) o PDF (`.pdf`).

## Requisitos

- Python 3.10 o superior.
- Dependencias adicionales para exportar a PDF: `reportlab`.

Instala la dependencia opcional con:

```bash
pip install -r requirements.txt
```

o simplemente:

```bash
pip install reportlab
```

## Ejecución

Desde la raíz del repositorio ejecuta:

```bash
python -m journal_app.app
```

Al iniciar la aplicación se creará (si no existe) un archivo `journal_data.json` junto al código donde se guardan todas las entradas.

## Exportar y compartir

Utiliza el botón **Exportar** para elegir el formato y la ubicación del archivo. Si se selecciona PDF y no está instalada la dependencia `reportlab`, la aplicación mostrará un aviso indicando cómo instalarla.
