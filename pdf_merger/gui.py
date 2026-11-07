"""
gui.py
======
Interface graphique Windows (Tkinter) de pdf_merger.

Description :
    Fenêtre qui liste les PDF à fusionner, permet de les ordonner, de choisir
    les pages à garder pour chacun, puis lance la fusion en arrière-plan.
    Le glisser-déposer depuis l'Explorateur est activé si le paquet
    optionnel « tkinterdnd2 » est installé.

Cas d'usage :
    - Double-cliquer sur PDFMerger.exe et fusionner des fichiers à la souris
    - Double-cliquer sur une ligne pour choisir les pages à garder

Entrée  : actions de l'utilisateur
Sortie  : fichier PDF fusionné à l'emplacement choisi
"""

import logging
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from pdf_merger import config
from pdf_merger.merger import MergeError, MergeItem, count_pages, merge_pdfs
from pdf_merger.page_range import parse_page_range

try:  # glisser-déposer optionnel
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:  # pragma: no cover - dépend de l'installation
    TkinterDnD = None


class MergerApp:
    """Fenêtre principale : liste des fichiers + boutons d'action."""

    def __init__(self, root, dnd_enabled):
        """
        Construit la fenêtre.

        Args:
            root (tk.Tk): fenêtre racine.
            dnd_enabled (bool): True si le glisser-déposer est disponible.

        Returns:
            None
        """
        self.root = root
        self.items = {}  # id de ligne -> MergeItem
        self.results = queue.Queue()
        self.bookmarks = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value=config.MSG_READY if dnd_enabled else config.MSG_READY_NO_DND)

        root.title(config.WINDOW_TITLE)
        root.geometry(config.WINDOW_GEOMETRY)
        root.minsize(*config.WINDOW_MIN_SIZE)
        self._build_widgets()
        if dnd_enabled:
            self.tree.drop_target_register(DND_FILES)
            self.tree.dnd_bind("<<Drop>>", self._on_drop)

    # ------------------------------------------------------------------ UI
    def _build_widgets(self):
        """
        Crée la liste, la barre de boutons et la barre d'état.

        Returns:
            None
        """
        pad = config.UI_PADDING
        frame = ttk.Frame(self.root, padding=pad)
        frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame, columns=config.COLUMNS, show="headings", selectmode="extended")
        for col in config.COLUMNS:
            self.tree.heading(col, text=config.COLUMN_HEADERS[col])
            self.tree.column(col, width=config.COLUMN_WIDTHS[col], anchor=tk.W)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Double-1>", lambda _e: self.edit_range())
        self.tree.bind("<Delete>", lambda _e: self.remove_selected())

        side = ttk.Frame(frame, padding=(pad, 0, 0, 0))
        side.grid(row=0, column=2, sticky="n")
        buttons = [
            (config.BTN_ADD, self.ask_files),
            (config.BTN_REMOVE, self.remove_selected),
            (config.BTN_UP, lambda: self.move(-1)),
            (config.BTN_DOWN, lambda: self.move(1)),
            (config.BTN_SORT, self.sort_by_name),
            (config.BTN_RANGE, self.edit_range),
            (config.BTN_CLEAR, self.clear),
        ]
        for label, command in buttons:
            ttk.Button(side, text=label, command=command).pack(fill=tk.X, pady=2)

        bottom = ttk.Frame(frame, padding=(0, pad, 0, 0))
        bottom.grid(row=1, column=0, columnspan=3, sticky="ew")
        ttk.Checkbutton(bottom, text=config.CHK_BOOKMARKS, variable=self.bookmarks).pack(side=tk.LEFT)
        self.merge_button = ttk.Button(bottom, text=config.BTN_MERGE, command=self.merge)
        self.merge_button.pack(side=tk.RIGHT)
        ttk.Label(frame, textvariable=self.status, anchor=tk.W).grid(row=2, column=0, columnspan=3, sticky="ew")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

    # ------------------------------------------------------------ fichiers
    def ask_files(self):
        """
        Ouvre la boîte de dialogue de sélection de fichiers.

        Returns:
            None
        """
        paths = filedialog.askopenfilenames(filetypes=config.FILE_DIALOG_TYPES)
        self.add_files(paths)

    def _on_drop(self, event):
        """
        Reçoit les fichiers glissés depuis l'Explorateur Windows.

        Args:
            event: événement tkinterdnd2 (event.data = liste de chemins).

        Returns:
            None
        """
        self.add_files(self.root.tk.splitlist(event.data))

    def add_files(self, paths):
        """
        Ajoute des PDF à la fin de la liste (les dossiers sont parcourus).

        Args:
            paths (Iterable[str]): chemins de fichiers ou de dossiers.

        Returns:
            None
        """
        skipped = []
        for path in _expand_paths(paths):
            try:
                pages = count_pages(path)
            except MergeError:
                skipped.append(os.path.basename(path))
                continue
            row = self.tree.insert(
                "", tk.END,
                values=(os.path.basename(path), pages, config.ALL_PAGES_LABEL, os.path.dirname(path)),
            )
            self.items[row] = MergeItem(path)
        if skipped:
            messagebox.showwarning(config.APP_NAME, config.MSG_SKIPPED.format(files="\n".join(skipped)))

    def remove_selected(self):
        """
        Retire les lignes sélectionnées.

        Returns:
            None
        """
        for row in self.tree.selection():
            self.tree.delete(row)
            self.items.pop(row, None)

    def clear(self):
        """
        Vide entièrement la liste.

        Returns:
            None
        """
        self.tree.delete(*self.tree.get_children())
        self.items.clear()

    def move(self, direction):
        """
        Déplace la sélection d'un cran vers le haut (-1) ou le bas (+1).

        Args:
            direction (int): -1 pour monter, +1 pour descendre.

        Returns:
            None
        """
        rows = list(self.tree.selection())
        if direction > 0:
            rows.reverse()
        for row in rows:
            index = self.tree.index(row) + direction
            if 0 <= index < len(self.tree.get_children()):
                self.tree.move(row, "", index)

    def sort_by_name(self):
        """
        Trie la liste par nom de fichier (ordre alphabétique, sans casse).

        Returns:
            None
        """
        rows = sorted(self.tree.get_children(), key=lambda r: os.path.basename(self.items[r].path).lower())
        for index, row in enumerate(rows):
            self.tree.move(row, "", index)

    def edit_range(self):
        """
        Demande les pages à garder pour la ligne sélectionnée.

        Returns:
            None
        """
        selection = self.tree.selection()
        if not selection:
            return
        row = selection[0]
        item = self.items[row]
        name, pages = self.tree.set(row, "fichier"), int(self.tree.set(row, "pages"))
        spec = simpledialog.askstring(
            config.APP_NAME,
            config.MSG_RANGE_PROMPT.format(name=name, count=pages),
            initialvalue=item.pages or "",
            parent=self.root,
        )
        if spec is None:
            return
        try:
            parse_page_range(spec, pages)
        except ValueError as exc:
            messagebox.showerror(config.MSG_ERROR_TITLE, str(exc))
            return
        item.pages = spec.strip() or None
        self.tree.set(row, "plage", item.pages or config.ALL_PAGES_LABEL)

    # --------------------------------------------------------------- fusion
    def merge(self):
        """
        Demande le fichier de sortie puis lance la fusion dans un thread.

        Returns:
            None
        """
        items = [self.items[row] for row in self.tree.get_children()]
        if not items:
            messagebox.showinfo(config.APP_NAME, config.MSG_NEED_FILES)
            return
        output = filedialog.asksaveasfilename(
            defaultextension=config.PDF_EXTENSION,
            filetypes=config.FILE_DIALOG_TYPES,
            initialfile=config.DEFAULT_OUTPUT_NAME,
            initialdir=os.path.dirname(items[0].path),
        )
        if not output:
            return
        self.merge_button.state(["disabled"])
        self.status.set(config.MSG_MERGING)
        self.root.config(cursor="watch")
        args = ([MergeItem(i.path, i.pages) for i in items], output, self.bookmarks.get())
        threading.Thread(target=self._merge_worker, args=args, daemon=True).start()
        self.root.after(config.POLL_INTERVAL_MS, self._poll_result)

    def _merge_worker(self, items, output, bookmarks):
        """
        Exécute la fusion hors du thread de l'interface.

        Args:
            items (list[MergeItem]): fichiers à fusionner.
            output (str): chemin de sortie.
            bookmarks (bool): ajout des signets.

        Returns:
            None (le résultat est déposé dans self.results)
        """
        try:
            self.results.put(("ok", merge_pdfs(items, output, bookmarks), output))
        except MergeError as exc:
            self.results.put(("error", str(exc), output))

    def _poll_result(self):
        """
        Vérifie si la fusion est terminée et affiche le résultat.

        Returns:
            None
        """
        try:
            kind, value, output = self.results.get_nowait()
        except queue.Empty:
            self.root.after(config.POLL_INTERVAL_MS, self._poll_result)
            return
        self.merge_button.state(["!disabled"])
        self.root.config(cursor="")
        if kind == "ok":
            message = config.MSG_DONE.format(pages=value, path=output)
            self.status.set(message)
            messagebox.showinfo(config.MSG_DONE_TITLE, message)
        else:
            self.status.set(value)
            messagebox.showerror(config.MSG_ERROR_TITLE, value)


def _expand_paths(paths):
    """
    Remplace chaque dossier par les PDF qu'il contient (triés par nom).

    Args:
        paths (Iterable[str]): chemins de fichiers ou de dossiers.

    Returns:
        list[str]: chemins de fichiers.
    """
    files = []
    for path in paths:
        if os.path.isdir(path):
            names = sorted(n for n in os.listdir(path) if n.lower().endswith(config.PDF_EXTENSION))
            files.extend(os.path.join(path, n) for n in names)
        else:
            files.append(path)
    return files


def run_gui(initial_files=()):
    """
    Lance l'interface graphique.

    Args:
        initial_files (Iterable[str]): PDF à charger au démarrage (ex. glissés sur l'exe).

    Returns:
        None
    """
    logging.getLogger("pypdf").setLevel(config.PYPDF_LOG_LEVEL)
    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    app = MergerApp(root, dnd_enabled=TkinterDnD is not None)
    if initial_files:
        app.add_files(initial_files)
    root.mainloop()
