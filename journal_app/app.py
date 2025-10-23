"""Aplicación de diario y poesía para escritorio."""
from __future__ import annotations

import datetime as _dt
import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

DATA_FILE = Path(__file__).with_name("journal_data.json")
START_DATE = _dt.date(2024, 1, 1)


@dataclass
class Entry:
    """Representa una entrada del diario y poesía."""

    journal: str
    poetry: str


class JournalApp:
    """Aplicación principal del diario."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Diario & Poesía")
        self.root.geometry("960x600")

        self.data: Dict[str, Entry] = {}
        self.current_date: _dt.date = _dt.date.today()
        self.background_color = "#fffef5"

        self._load_data()

        self._build_ui()
        self._load_entry(self.current_date)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Datos
    def _load_data(self) -> None:
        if DATA_FILE.exists():
            try:
                with DATA_FILE.open("r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                self.data = {key: Entry(**value) for key, value in raw.items()}
            except (json.JSONDecodeError, OSError, TypeError) as exc:
                messagebox.showerror(
                    "Datos corruptos",
                    "No se pudieron cargar los datos existentes. Se generará un archivo nuevo.",
                )
                print(f"Error cargando datos: {exc}")
                self.data = {}
        else:
            self.data = {}

        today_key = self.current_date.isoformat()
        if today_key not in self.data:
            self.data[today_key] = Entry(journal="", poetry="")

        self._ensure_sample_entries()

    def _ensure_sample_entries(self) -> None:
        today = _dt.date.today()
        date = START_DATE
        generator = SampleTextGenerator()
        while date <= today:
            key = date.isoformat()
            if key not in self.data:
                self.data[key] = Entry(
                    journal=generator.generate_text(kind="journal"),
                    poetry=generator.generate_text(kind="poetry"),
                )
            date += _dt.timedelta(days=1)

        self._save_data()

    def _save_data(self) -> None:
        serializable = {key: asdict(value) for key, value in self.data.items()}
        try:
            with DATA_FILE.open("w", encoding="utf-8") as fh:
                json.dump(serializable, fh, ensure_ascii=False, indent=2)
        except OSError as exc:
            messagebox.showerror(
                "Error al guardar",
                f"No fue posible guardar el diario. Detalles: {exc}",
            )

    # ------------------------------------------------------------------
    # Interfaz
    def _build_ui(self) -> None:
        mainframe = ttk.Frame(self.root, padding=12)
        mainframe.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(mainframe)
        header.pack(fill=tk.X, pady=(0, 12))

        self.date_label = ttk.Label(header, text="", font=("Helvetica", 18, "bold"))
        self.date_label.pack(side=tk.LEFT)

        ttk.Button(header, text="Hoy", command=self._go_to_today).pack(side=tk.RIGHT, padx=6)

        body = ttk.Frame(mainframe)
        body.pack(fill=tk.BOTH, expand=True)

        sidebar = ttk.Frame(body)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(sidebar, text="Entradas disponibles", font=("Helvetica", 12, "bold")).pack(
            anchor=tk.W, pady=(0, 6)
        )

        self.date_list = tk.Listbox(sidebar, width=18, exportselection=False)
        self.date_list.pack(fill=tk.Y, expand=False)
        for key in sorted(self.data.keys(), reverse=True):
            self.date_list.insert(tk.END, key)
        self.date_list.bind("<<ListboxSelect>>", self._on_date_selected)
        self._select_date_in_list(self.current_date)

        content = ttk.Frame(body)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))

        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.journal_text = tk.Text(self.notebook, wrap=tk.WORD, font=("Georgia", 14))
        self.poetry_text = tk.Text(self.notebook, wrap=tk.WORD, font=("Georgia", 14))
        for widget in (self.journal_text, self.poetry_text):
            widget.configure(bg=self.background_color)
            widget.bind("<Control-s>", self._handle_save_shortcut)

        self.notebook.add(self.journal_text, text="Diario")
        self.notebook.add(self.poetry_text, text="Poesía")

        toolbar = ttk.Frame(mainframe)
        toolbar.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(
            toolbar, text="Guardar", command=lambda: self._save_current_entry(notify=True)
        ).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Cambiar fondo", command=self._change_background_color).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(toolbar, text="Exportar", command=self._export_entry).pack(side=tk.LEFT)

    def _on_close(self) -> None:
        self._save_current_entry()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Eventos
    def _handle_save_shortcut(self, event: tk.Event) -> str:
        self._save_current_entry(notify=True)
        return "break"

    def _on_date_selected(self, event: tk.Event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        key = event.widget.get(index)
        self._switch_to_date(_dt.date.fromisoformat(key))

    def _go_to_today(self) -> None:
        self._switch_to_date(_dt.date.today())
        today_key = self.current_date.isoformat()
        self._select_date_in_list(self.current_date)

    def _select_date_in_list(self, target_date: _dt.date) -> None:
        key = target_date.isoformat()
        for idx in range(self.date_list.size()):
            if self.date_list.get(idx) == key:
                self.date_list.selection_clear(0, tk.END)
                self.date_list.selection_set(idx)
                self.date_list.see(idx)
                break

    # ------------------------------------------------------------------
    # Utilidad
    def _switch_to_date(self, target_date: _dt.date) -> None:
        self._save_current_entry()
        self.current_date = target_date
        self._load_entry(target_date)

    def _load_entry(self, target_date: _dt.date) -> None:
        key = target_date.isoformat()
        entry = self.data.setdefault(key, Entry(journal="", poetry=""))
        self.date_label.configure(text=target_date.strftime("%d de %B de %Y"))
        self._set_text(self.journal_text, entry.journal)
        self._set_text(self.poetry_text, entry.poetry)

    def _set_text(self, widget: tk.Text, value: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, value)
        widget.configure(bg=self.background_color)

    def _save_current_entry(self, *, notify: bool = False) -> None:
        key = self.current_date.isoformat()
        self.data[key] = Entry(
            journal=self.journal_text.get("1.0", tk.END).rstrip(),
            poetry=self.poetry_text.get("1.0", tk.END).rstrip(),
        )
        self._save_data()
        if notify:
            messagebox.showinfo("Guardado", f"Se guardó la entrada del {key}.")

    def _change_background_color(self) -> None:
        color_code = colorchooser.askcolor(color=self.background_color, title="Selecciona un color")
        if color_code and color_code[1]:
            self.background_color = color_code[1]
            for widget in (self.journal_text, self.poetry_text):
                widget.configure(bg=self.background_color)

    def _export_entry(self) -> None:
        key = self.current_date.isoformat()
        entry = self.data.get(key)
        if entry is None:
            messagebox.showwarning("Sin contenido", "No hay información para exportar.")
            return

        filetypes = [
            ("Texto", "*.txt"),
            ("Markdown", "*.md"),
            ("PDF", "*.pdf"),
        ]
        filepath = filedialog.asksaveasfilename(
            title="Exportar entrada",
            initialfile=f"diario-{key}",
            defaultextension=".txt",
            filetypes=filetypes,
        )
        if not filepath:
            return

        path = Path(filepath)
        try:
            if path.suffix.lower() == ".pdf":
                self._export_to_pdf(path, key, entry)
            else:
                self._export_to_text(path, key, entry)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Exportación fallida", f"No se pudo exportar el archivo. Detalles: {exc}")
        else:
            messagebox.showinfo("Exportación lista", f"Se exportó la entrada a {path}.")

    def _export_to_text(self, path: Path, key: str, entry: Entry) -> None:
        header = f"Diario y poesía - {key}\n\n"
        body = [
            "=== Diario ===\n",
            entry.journal,
            "\n\n=== Poesía ===\n",
            entry.poetry,
        ]
        with path.open("w", encoding="utf-8") as fh:
            fh.write(header)
            fh.write("".join(body))

    def _export_to_pdf(self, path: Path, key: str, entry: Entry) -> None:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError as exc:  # pragma: no cover - dependencias externas
            raise RuntimeError(
                "Se necesita la librería 'reportlab' para exportar a PDF. Instálala con 'pip install reportlab'."
            ) from exc

        pdf = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        pdf.setTitle(f"Diario {key}")
        pdf.setFont("Times-Roman", 16)
        pdf.drawString(72, height - 72, f"Entrada del {key}")

        pdf.setFont("Times-Roman", 12)
        text = pdf.beginText(72, height - 108)
        text.textLine("=== Diario ===")
        for line in entry.journal.splitlines():
            text.textLine(line)
        text.textLine("")
        text.textLine("=== Poesía ===")
        for line in entry.poetry.splitlines():
            text.textLine(line)
        pdf.drawText(text)
        pdf.showPage()
        pdf.save()


class SampleTextGenerator:
    """Generador de texto de muestra para poblar el diario."""

    JOURNAL_FRAGMENTS = [
        "El cielo estaba cubierto de nubes suaves.",
        "Tomé una taza de café mirando por la ventana.",
        "Anoté las ideas que surgieron en la madrugada.",
        "Encontré un momento de calma en medio del ruido.",
        "La caminata corta me ayudó a aclarar la mente.",
        "Un nuevo proyecto comenzó a tomar forma hoy.",
        "Me acompañó la música mientras escribía.",
        "Decidí enfocarme en agradecer las pequeñas cosas.",
        "Guardé este pensamiento para revisarlo más tarde.",
        "Terminó el día con una sonrisa silenciosa.",
    ]

    POETRY_FRAGMENTS = [
        "Brilla la tarde sobre el rincón del eco.",
        "La luna borda silencios de plata.",
        "Un río de suspiros cruza la memoria.",
        "Las palabras germinan bajo la lluvia lenta.",
        "En el pecho crece un jardín de luciérnagas.",
        "Danza el viento con las hojas dormidas.",
        "Se despierta el verso con aroma a madrugada.",
        "La sombra canta a la luz que no termina.",
        "Cada latido sostiene un puente de espuma.",
        "El poema sueña con voces de agua clara.",
    ]

    def generate_text(self, *, kind: str) -> str:
        fragments = self.JOURNAL_FRAGMENTS if kind == "journal" else self.POETRY_FRAGMENTS
        lines = random.randint(3, 6)
        return "\n".join(random.choice(fragments) for _ in range(lines))


def main() -> None:
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
