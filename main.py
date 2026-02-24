import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import date, datetime, timedelta
import os

COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
os.makedirs(COVERS_DIR, exist_ok=True)

GENRE_RATES = {
    "Fiction":        5,
    "Non-Fiction":    8,
    "Science":       10,
    "Science Fiction":10,
    "Technology":    15,
    "History":        8,
    "Biography":      8,
    "Fantasy":        5,
    "Romance":        5,
    "Mystery":        7,
    "Business":      12,
    "Self-Help":     10,
}
DEFAULT_RATE = 8

BG_CREAM  = "#FFF8F0" #Colors
BG_BEIGE  = "#F5E6D3"
BG_WARM   = "#EDD9C4"
BG_CARD   = "#FFFAF5"
ACCENT_BROWN         = "#8B6914"
ACCENT_RUST          = "#C17744"
ACCENT_DARK          = "#5C4033"
HIGHLIGHT            = "#D4956A"
BUTTON_PRIMARY       = "#C17744"
BUTTON_PRIMARY_HOVER = "#A85D32"
BUTTON_SUCCESS       = "#7CAE7A"
BUTTON_SUCCESS_HOVER = "#5E9460"
BUTTON_DANGER        = "#D47B6C"
BUTTON_DANGER_HOVER  = "#B85A4A"
BUTTON_INFO          = "#8BA5B5"
BUTTON_INFO_HOVER    = "#6E8A9E"
BUTTON_GOLD          = "#C9A84C"
BUTTON_GOLD_HOVER    = "#A8893A"
TEXT_DARK    = "#3E2723"
TEXT_MEDIUM  = "#6D4C41"
TEXT_LIGHT   = "#8D6E63"
TEXT_WHITE   = "#FFFDF9"
ENTRY_BG     = "#FFF3E6"
ENTRY_BORDER = "#D7CCC8"
DIVIDER      = "#D7CCC8"
STATUS_AVAILABLE = "#6B8E6B"
STATUS_BORROWED  = "#C17744"

COVER_W = 130
COVER_H = 180
CARD_W  = 155


def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="library_db"
        )
        return conn
    except mysql.connector.Error:
        messagebox.showerror(
            "Database Error",
            "Failed to connect to MySQL.\n\n"
            "Please make sure:\n"
            "1. XAMPP MySQL is running\n"
            "2. Database 'library_db' exists\n"
            "3. Run the SQL setup in phpMyAdmin first!"
        )
        return None

connection = connect_db()
if connection is None:
    exit()

#covers
def cover_path_for(book_id):
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join(COVERS_DIR, f"{book_id}.{ext}")
        if os.path.exists(p):
            return p
    return None

def make_placeholder(w, h):
    img  = Image.new("RGB", (w, h), "#D9CFCA")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w-1, h-1], outline="#B8ADA7", width=2)
    try:    font_big = ImageFont.truetype("seguiemj.ttf", 38)
    except: font_big = ImageFont.load_default()
    try:    font_sm  = ImageFont.truetype("arial.ttf", 11)
    except: font_sm  = ImageFont.load_default()
    text = "📚"
    bb = draw.textbbox((0,0), text, font=font_big)
    tx = (w-(bb[2]-bb[0]))//2;  ty = (h-(bb[3]-bb[1]))//2 - 12
    draw.text((tx, ty), text, font=font_big, fill="#7A6E6A")
    label = "No Cover"
    lb = draw.textbbox((0,0), label, font=font_sm)
    draw.text(((w-(lb[2]-lb[0]))//2, ty+52), label, font=font_sm, fill="#9E928E")
    return img

def load_cover_tk(book_id, w, h):
    path = cover_path_for(book_id)
    if path:
        try:
            return ImageTk.PhotoImage(
                Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS))
        except: pass
    return ImageTk.PhotoImage(make_placeholder(w, h))

def save_cover(book_id, src_path):
    for ext in ("jpg","jpeg","png","webp"):
        old = os.path.join(COVERS_DIR, f"{book_id}.{ext}")
        if os.path.exists(old): os.remove(old)
    ext = os.path.splitext(src_path)[1].lower().lstrip(".")
    if ext not in ("jpg","jpeg","png","webp"): ext = "jpg"
    dest = os.path.join(COVERS_DIR, f"{book_id}.{ext}")
    Image.open(src_path).convert("RGB").save(
        dest, "JPEG" if ext in ("jpg","jpeg") else ext.upper())

class LibraryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kandy Library")
        self.root.geometry("520x400")
        self.root.configure(bg=BG_CREAM)
        self.root.resizable(False, False)
        self.center_window(self.root, 520, 400)

        self._photo_refs      = []
        self._card_widgets    = []
        self.current_form     = None
        self._current_book_id = None
        self._add_cover_src   = None
        self._upd_cover_src   = None

        self.show_welcome()
        self.root.mainloop()

    def center_window(self, win, w, h):
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    #Welcome window
    def show_welcome(self):
        self.welcome_frame = tk.Frame(self.root, bg=BG_CREAM)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
        tk.Frame(self.welcome_frame, bg=ACCENT_RUST, height=4).pack(fill=tk.X)

        card = tk.Frame(self.welcome_frame, bg=BG_CARD, padx=40, pady=30)
        card.pack(expand=True, padx=40, pady=30)
        tk.Frame(card, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(0,15))
        tk.Label(card, text="📚", font=("Segoe UI Emoji", 42), bg=BG_CARD).pack(pady=(5,8))
        tk.Label(card, text="Kandy Library", font=("Georgia", 26, "bold"),
                 bg=BG_CARD, fg=ACCENT_DARK).pack(pady=(0,4))
        tk.Label(card, text="— Management System —", font=("Georgia", 11, "italic"),
                 bg=BG_CARD, fg=TEXT_LIGHT).pack(pady=(0,5))
        tk.Label(card, text="Your gateway to knowledge and adventure",
                 font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_LIGHT).pack(pady=(0,20))

        btn = tk.Button(card, text="Enter Main Menu  →",
                        font=("Segoe UI", 12, "bold"),
                        bg=BUTTON_PRIMARY, fg=TEXT_WHITE,
                        activebackground=BUTTON_PRIMARY_HOVER, activeforeground=TEXT_WHITE,
                        relief=tk.FLAT, cursor="hand2", padx=30, pady=10, bd=0,
                        command=self.open_main_window)
        btn.pack(pady=(5,10))
        btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_PRIMARY_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_PRIMARY))
        tk.Frame(card, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(15,0))
        tk.Frame(self.welcome_frame, bg=ACCENT_RUST, height=4).pack(fill=tk.X, side=tk.BOTTOM)

    def open_main_window(self):
        self.welcome_frame.destroy()
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self.root.minsize(1000, 600)
        self.center_window(self.root, 1200, 700)
        self.root.title("Kandy Library — Management System")
        self.build_main_ui()

    #Main Menu
    def build_main_ui(self):
        self.root.configure(bg=BG_CREAM)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", background=BG_WARM,
                        troughcolor=BG_BEIGE, arrowcolor=ACCENT_BROWN)
        style.configure("TCombobox", fieldbackground=ENTRY_BG,
                        background=BG_WARM, foreground=TEXT_DARK, arrowcolor=ACCENT_BROWN)

        top_bar = tk.Frame(self.root, bg=BG_BEIGE, pady=12) #bar
        top_bar.pack(side=tk.TOP, fill=tk.X)
        tk.Frame(self.root, bg=ACCENT_RUST, height=3).pack(side=tk.TOP, fill=tk.X)

        tf = tk.Frame(top_bar, bg=BG_BEIGE)
        tf.pack(side=tk.LEFT, padx=20)
        tk.Label(tf, text="📚", font=("Segoe UI Emoji", 18), bg=BG_BEIGE).pack(side=tk.LEFT, padx=(0,8))
        tk.Label(tf, text="Kandy Library", font=("Georgia", 16, "bold"),
                 bg=BG_BEIGE, fg=ACCENT_DARK).pack(side=tk.LEFT)

        sf = tk.Frame(top_bar, bg=BG_BEIGE)
        sf.pack(side=tk.RIGHT, padx=20)
        tk.Label(sf, text="Search:", font=("Segoe UI", 10),
                 bg=BG_BEIGE, fg=TEXT_MEDIUM).pack(side=tk.LEFT, padx=(0,8))
        sc = tk.Frame(sf, bg=ENTRY_BORDER, padx=1, pady=1)
        sc.pack(side=tk.LEFT, padx=(0,8))
        self.search_entry = tk.Entry(sc, width=30, font=("Segoe UI", 10),
                                     bg=ENTRY_BG, fg=TEXT_LIGHT,
                                     insertbackground=ACCENT_BROWN, relief=tk.FLAT, bd=6)
        self.search_entry.pack()
        self.search_entry.insert(0, "Search title, author, genre...")
        self.search_entry.bind("<FocusIn>",  self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)
        self.search_entry.bind("<Return>", lambda e: self.search_books())

        for txt, cmd, bg, hov, fg in [
            ("🔍 Search", self.search_books, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER, TEXT_WHITE),
            ("↻ Reset",   self.reset_search,  BG_WARM,        DIVIDER,              TEXT_MEDIUM),
        ]:
            b = tk.Button(sf, text=txt, font=("Segoe UI", 9, "bold"),
                          bg=bg, fg=fg, activebackground=hov,
                          relief=tk.FLAT, cursor="hand2", padx=12, pady=4, command=cmd)
            b.pack(side=tk.LEFT, padx=2)
            b.bind("<Enter>", lambda e, btn=b, h=hov: btn.config(bg=h))
            b.bind("<Leave>", lambda e, btn=b, n=bg:  btn.config(bg=n))

        sidebar = tk.Frame(self.root, bg=BG_BEIGE, width=200) #sidebar
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="── MENU ──", font=("Georgia", 11, "bold"),
                 bg=BG_BEIGE, fg=TEXT_LIGHT).pack(pady=(25,15))

        menu_items = [
            ("📕  Add Book",       self.show_add_form),
            ("✏️  Update Book",    self.show_update_form),
            ("🗑️  Delete Book",    self.show_delete_form),
            ("📖  Borrow Book",    self.show_borrow_form),
            ("🔄  Return Book",    self.show_return_form),
            ("💰  Calculate Cost", self.show_cost_form),
        ]
        for text, cmd in menu_items:
            btn = tk.Button(sidebar, text=text, font=("Segoe UI", 11), anchor="w",
                            bg=BG_BEIGE, fg=TEXT_DARK, activebackground=BG_WARM,
                            relief=tk.FLAT, cursor="hand2", padx=20, pady=10, bd=0, command=cmd)
            btn.pack(fill=tk.X, padx=12, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BG_WARM))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_BEIGE))

        tk.Frame(sidebar, bg=DIVIDER, height=1).pack(fill=tk.X, padx=20, pady=15)
        vb = tk.Button(sidebar, text="📋  View All Books", font=("Segoe UI", 10), anchor="w",
                       bg=BG_WARM, fg=TEXT_MEDIUM, activebackground=DIVIDER,
                       relief=tk.FLAT, cursor="hand2", padx=20, pady=8, bd=0,
                       command=self.reset_search)
        vb.pack(fill=tk.X, padx=12, pady=3)
        vb.bind("<Enter>", lambda e: vb.config(bg=DIVIDER))
        vb.bind("<Leave>", lambda e: vb.config(bg=BG_WARM))

        stats = tk.Frame(sidebar, bg=BG_BEIGE)
        stats.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)
        tk.Frame(stats, bg=DIVIDER, height=1).pack(fill=tk.X, pady=(0,10))
        self.total_label = tk.Label(stats, text="Total: 0", font=("Segoe UI", 9),
                                    bg=BG_BEIGE, fg=TEXT_LIGHT, anchor="w")
        self.total_label.pack(fill=tk.X)
        self.borrowed_label = tk.Label(stats, text="Borrowed: 0", font=("Segoe UI", 9),
                                       bg=BG_BEIGE, fg=STATUS_BORROWED, anchor="w")
        self.borrowed_label.pack(fill=tk.X)
        self.available_label = tk.Label(stats, text="Available: 0", font=("Segoe UI", 9),
                                        bg=BG_BEIGE, fg=STATUS_AVAILABLE, anchor="w")
        self.available_label.pack(fill=tk.X)

        centre = tk.Frame(self.root, bg=BG_CREAM)
        centre.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        hdr = tk.Frame(centre, bg=BG_CREAM)
        hdr.pack(fill=tk.X, padx=15, pady=(15,5))
        tk.Label(hdr, text="📋 Book Collection", font=("Georgia", 13, "bold"),
                 bg=BG_CREAM, fg=ACCENT_DARK).pack(side=tk.LEFT)
        self.result_label = tk.Label(hdr, text="", font=("Segoe UI", 9, "italic"),
                                     bg=BG_CREAM, fg=TEXT_LIGHT)
        self.result_label.pack(side=tk.RIGHT)

        cb = tk.Frame(centre, bg=ENTRY_BORDER, padx=1, pady=1)
        cb.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        self.canvas = tk.Canvas(cb, bg=BG_CREAM, highlightthickness=0)
        vs = ttk.Scrollbar(cb, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vs.set)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cards_frame = tk.Frame(self.canvas, bg=BG_CREAM)
        self._cards_win = self.canvas.create_window((0,0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.right_panel = tk.Frame(self.root, width=300, bg=BG_CARD)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_panel.pack_propagate(False)
        tk.Frame(self.right_panel, bg=DIVIDER, width=1).pack(side=tk.LEFT, fill=tk.Y)
        self.form_container = tk.Frame(self.right_panel, bg=BG_CARD)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=2)

        self.build_add_form()
        self.build_update_form()
        self.build_delete_form()
        self.build_borrow_form()
        self.build_return_form()
        self.build_cost_form()

        self.load_books()
        self.show_add_form()

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self._cards_win, width=event.width)
        if self._card_widgets:
            cols = max(1, event.width // (CARD_W + 24))
            for idx, card in enumerate(self._card_widgets):
                r, c = divmod(idx, cols)
                card.grid(row=r, column=c, padx=12, pady=12)

    def clear_placeholder(self, event):
        if self.search_entry.get().strip() == "Search title, author, genre...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=TEXT_DARK)

    def add_placeholder(self, event):
        if self.search_entry.get().strip() == "":
            self.search_entry.insert(0, "Search title, author, genre...")
            self.search_entry.config(fg=TEXT_LIGHT)

    def make_form_title(self, parent, text, emoji=""):
        hdr = tk.Frame(parent, bg=BG_CARD)
        hdr.pack(fill=tk.X, padx=20, pady=(25,0))
        tk.Label(hdr, text=f"{emoji}  {text}", font=("Georgia", 14, "bold"),
                 bg=BG_CARD, fg=ACCENT_DARK).pack(anchor="w")
        tk.Frame(parent, bg=HIGHLIGHT, height=2).pack(fill=tk.X, padx=20, pady=(8,15))

    def make_label(self, parent, text):
        return tk.Label(parent, text=text, font=("Segoe UI", 10),
                        bg=BG_CARD, fg=TEXT_MEDIUM)

    def make_entry(self, parent, width=24):
        c = tk.Frame(parent, bg=ENTRY_BORDER, padx=1, pady=1)
        e = tk.Entry(c, width=width, font=("Segoe UI", 10),
                     bg=ENTRY_BG, fg=TEXT_DARK,
                     insertbackground=ACCENT_BROWN, relief=tk.FLAT, bd=5)
        e.pack()
        return c, e

    def make_combo(self, parent, width=22):
        return ttk.Combobox(parent, values=[
            "Fiction","Non-Fiction","Science","Science Fiction",
            "Technology","History","Biography","Fantasy",
            "Romance","Mystery","Business","Self-Help"
        ], state="readonly", width=width, font=("Segoe UI", 10))

    def make_button(self, parent, text, command, bg_color, hover_color):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
                        bg=bg_color, fg=TEXT_WHITE,
                        activebackground=hover_color, activeforeground=TEXT_WHITE,
                        relief=tk.FLAT, cursor="hand2", padx=25, pady=8, bd=0,
                        command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
        return btn

    def make_date_entry(self, parent, label_text, default_date=None):
        """Returns a frame containing a labeled date entry (YYYY-MM-DD)."""
        self.make_label(parent, label_text).pack(anchor="w", padx=25, pady=(8,2))
        cont = tk.Frame(parent, bg=ENTRY_BORDER, padx=1, pady=1)
        cont.pack(fill=tk.X, padx=25, pady=(0,4))
        entry = tk.Entry(cont, font=("Segoe UI", 10), bg=ENTRY_BG, fg=TEXT_DARK,
                         insertbackground=ACCENT_BROWN, relief=tk.FLAT, bd=5)
        entry.pack(fill=tk.X)
        if default_date:
            entry.insert(0, str(default_date))
        return entry

    def hide_all_forms(self):
        for w in self.form_container.winfo_children():
            w.pack_forget()

    def _pick_image(self, preview_label, filename_label, store_attr):
        path = filedialog.askopenfilename(
            title="Choose Cover Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")]
        )
        if not path: return
        setattr(self, store_attr, path)
        filename_label.config(text=os.path.basename(path))
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((52,70))
            ph = ImageTk.PhotoImage(img)
            self._photo_refs.append(ph)
            preview_label.config(image=ph, text="", width=52, height=70)
            preview_label.image = ph
        except: pass

    def _reset_cover_preview(self, preview_label, filename_label, default_text):
        preview_label.config(image="", text="📚", font=("Segoe UI Emoji", 18),
                             fg="#7A6E6A", width=6, height=3)
        filename_label.config(text=default_text)

    def _build_cover_section(self, parent, store_attr, default_label_text):
        tk.Frame(parent, bg=DIVIDER, height=1).pack(fill=tk.X, padx=25, pady=(6,10))
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(padx=25, fill=tk.X, pady=(0,4))
        preview = tk.Label(row, bg="#D9CFCA", width=6, height=3,
                           text="📚", font=("Segoe UI Emoji", 18), fg="#7A6E6A", relief=tk.FLAT)
        preview.pack(side=tk.LEFT, padx=(0,10))
        rc = tk.Frame(row, bg=BG_CARD)
        rc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(rc, text="Cover Image", font=("Segoe UI", 10),
                 bg=BG_CARD, fg=TEXT_MEDIUM).pack(anchor="w")
        tk.Label(rc, text="Optional – jpg / png",
                 font=("Segoe UI", 8, "italic"), bg=BG_CARD, fg=TEXT_LIGHT).pack(anchor="w")
        fname_lbl = tk.Label(rc, text=default_label_text, font=("Segoe UI", 8),
                             bg=BG_CARD, fg=TEXT_LIGHT, wraplength=160)
        choose = tk.Button(rc, text="📁  Choose Image", font=("Segoe UI", 9),
                           bg=BG_WARM, fg=TEXT_DARK, activebackground=DIVIDER,
                           relief=tk.FLAT, cursor="hand2", padx=8, pady=4,
                           command=lambda: self._pick_image(preview, fname_lbl, store_attr))
        choose.pack(anchor="w", pady=(6,2))
        choose.bind("<Enter>", lambda e: choose.config(bg=DIVIDER))
        choose.bind("<Leave>", lambda e: choose.config(bg=BG_WARM))
        fname_lbl.pack(anchor="w")
        return preview, fname_lbl

    def build_add_form(self):
        self.add_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.make_form_title(self.add_frame, "Add New Book", "📕")
        fg = tk.Frame(self.add_frame, bg=BG_CARD)
        fg.pack(padx=25, pady=(0,4))
        self.make_label(fg, "Title").grid(row=0, column=0, sticky="w", pady=(6,2))
        self.add_title_container, self.add_title = self.make_entry(fg)
        self.add_title_container.grid(row=1, column=0, sticky="ew", pady=(0,6))
        self.make_label(fg, "Author").grid(row=2, column=0, sticky="w", pady=(6,2))
        self.add_author_container, self.add_author = self.make_entry(fg)
        self.add_author_container.grid(row=3, column=0, sticky="ew", pady=(0,6))
        self.make_label(fg, "Genre").grid(row=4, column=0, sticky="w", pady=(6,2))
        self.add_genre = self.make_combo(fg)
        self.add_genre.grid(row=5, column=0, sticky="ew", pady=(0,6))
        self.make_label(fg, "Year").grid(row=6, column=0, sticky="w", pady=(6,2))
        self.add_year_container, self.add_year = self.make_entry(fg)
        self.add_year_container.grid(row=7, column=0, sticky="ew", pady=(0,6))
        self.add_cover_preview, self.add_cover_label = \
            self._build_cover_section(self.add_frame, "_add_cover_src", "No image chosen")
        self.make_button(self.add_frame, "➕  Add Book",
                         self.add_book_db, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER).pack(pady=12)
        self.add_status = tk.Label(self.add_frame, text="", font=("Segoe UI", 9, "italic"),
                                   bg=BG_CARD, fg=STATUS_AVAILABLE)
        self.add_status.pack()

    def build_update_form(self):
        self.update_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.make_form_title(self.update_frame, "Update Book", "✏️")
        ff = tk.Frame(self.update_frame, bg=BG_CARD)
        ff.pack(fill=tk.X, padx=25, pady=(0,6))
        self.make_label(ff, "Book ID").pack(anchor="w", pady=(0,2))
        id_row = tk.Frame(ff, bg=BG_CARD)
        id_row.pack(fill=tk.X)
        id_cont = tk.Frame(id_row, bg=ENTRY_BORDER, padx=1, pady=1)
        id_cont.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
        self.upd_id_entry = tk.Entry(id_cont, font=("Segoe UI", 10), bg=ENTRY_BG, fg=TEXT_DARK,
                                     insertbackground=ACCENT_BROWN, relief=tk.FLAT, bd=5)
        self.upd_id_entry.pack(fill=tk.X)
        self.upd_id_entry.bind("<Return>", lambda e: self.find_book_by_id())
        fb = tk.Button(id_row, text="🔍 Find", font=("Segoe UI", 9, "bold"),
                       bg=BUTTON_INFO, fg=TEXT_WHITE, activebackground=BUTTON_INFO_HOVER,
                       relief=tk.FLAT, cursor="hand2", padx=10, pady=4,
                       command=self.find_book_by_id)
        fb.pack(side=tk.LEFT)
        fb.bind("<Enter>", lambda e: fb.config(bg=BUTTON_INFO_HOVER))
        fb.bind("<Leave>", lambda e: fb.config(bg=BUTTON_INFO))
        tk.Frame(self.update_frame, bg=DIVIDER, height=1).pack(fill=tk.X, padx=25, pady=(8,4))
        tk.Label(self.update_frame, text="or click a book card",
                 font=("Segoe UI", 8, "italic"), bg=BG_CARD, fg=TEXT_LIGHT).pack(pady=(0,6))
        fg = tk.Frame(self.update_frame, bg=BG_CARD)
        fg.pack(padx=25, pady=(0,4))
        self.make_label(fg, "Title").grid(row=0, column=0, sticky="w", pady=(4,2))
        self.upd_title_container, self.upd_title = self.make_entry(fg)
        self.upd_title_container.grid(row=1, column=0, sticky="ew", pady=(0,6))
        self.make_label(fg, "Author").grid(row=2, column=0, sticky="w", pady=(4,2))
        self.upd_author_container, self.upd_author = self.make_entry(fg)
        self.upd_author_container.grid(row=3, column=0, sticky="ew", pady=(0,6))
        self.make_label(fg, "Genre").grid(row=4, column=0, sticky="w", pady=(4,2))
        self.upd_genre = self.make_combo(fg)
        self.upd_genre.grid(row=5, column=0, sticky="ew", pady=(0,6))
        self.make_label(fg, "Year").grid(row=6, column=0, sticky="w", pady=(4,2))
        self.upd_year_container, self.upd_year = self.make_entry(fg)
        self.upd_year_container.grid(row=7, column=0, sticky="ew", pady=(0,6))
        self.upd_cover_preview, self.upd_cover_label = \
            self._build_cover_section(self.update_frame, "_upd_cover_src", "No new image chosen")
        self.upd_selected_label = tk.Label(self.update_frame, text="No book selected",
                                           font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_LIGHT,
                                           wraplength=240, justify="center")
        self.upd_selected_label.pack(pady=(4,0))
        self.make_button(self.update_frame, "💾  Save Changes",
                         self.update_book_db, BUTTON_INFO, BUTTON_INFO_HOVER).pack(pady=10)

    def build_delete_form(self):
        self.delete_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.make_form_title(self.delete_frame, "Delete Book", "🗑️")
        tk.Label(self.delete_frame, text="Click a book card\nthen click Delete",
                 font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_MEDIUM,
                 justify="center").pack(pady=(10,15))
        card = tk.Frame(self.delete_frame, bg=BG_BEIGE, padx=15, pady=12)
        card.pack(padx=25, fill=tk.X)
        self.del_info = tk.Label(card, text="No book selected",
                                 font=("Segoe UI", 10), bg=BG_BEIGE, fg=TEXT_DARK,
                                 wraplength=220, justify="center")
        self.del_info.pack()
        tk.Label(self.delete_frame, text="⚠ This action cannot be undone!",
                 font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=BUTTON_DANGER).pack(pady=15)
        self.make_button(self.delete_frame, "🗑️  Delete Book",
                         self.delete_book_db, BUTTON_DANGER, BUTTON_DANGER_HOVER).pack(pady=10)

    def build_borrow_form(self):
        self.borrow_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.make_form_title(self.borrow_frame, "Borrow Book", "📖")

        tk.Label(self.borrow_frame, text="Click a book card to select it,\nthen fill in the dates below.",
                 font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=TEXT_LIGHT,
                 justify="center").pack(pady=(0,10))

        sel_card = tk.Frame(self.borrow_frame, bg=BG_BEIGE, padx=15, pady=10)
        sel_card.pack(padx=25, fill=tk.X)
        self.borrow_info = tk.Label(sel_card, text="No book selected",
                                    font=("Segoe UI", 10), bg=BG_BEIGE, fg=TEXT_DARK,
                                    wraplength=220, justify="center")
        self.borrow_info.pack()

        self.borrow_status_badge = tk.Label(self.borrow_frame, text="",
                                            font=("Segoe UI", 9, "bold"),
                                            bg=BG_CARD, fg=TEXT_MEDIUM)
        self.borrow_status_badge.pack(pady=(8,0))

        today      = date.today()
        due_default = today + timedelta(days=14)
        self.borrow_date_entry = self.make_date_entry(
            self.borrow_frame, "Borrow Date (YYYY-MM-DD)", today)
        self.due_date_entry = self.make_date_entry(
            self.borrow_frame, "Due Date (YYYY-MM-DD)", due_default)

        tk.Label(self.borrow_frame, text="Default due date is 14 days from today",
                 font=("Segoe UI", 8, "italic"), bg=BG_CARD, fg=TEXT_LIGHT).pack(pady=(0,6))

        self.make_button(self.borrow_frame, "📖  Confirm Borrow",
                         self.borrow_book_db, BUTTON_PRIMARY, BUTTON_PRIMARY_HOVER).pack(pady=10)

        self.borrow_result = tk.Label(self.borrow_frame, text="",
                                      font=("Segoe UI", 9, "italic"),
                                      bg=BG_CARD, fg=STATUS_AVAILABLE, wraplength=240)
        self.borrow_result.pack()

    def build_return_form(self):
        self.return_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.make_form_title(self.return_frame, "Return Book", "🔄")

        tk.Label(self.return_frame, text="Click a borrowed book card\nto select it, then return.",
                 font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=TEXT_LIGHT,
                 justify="center").pack(pady=(0,10))

        sel_card = tk.Frame(self.return_frame, bg=BG_BEIGE, padx=15, pady=10)
        sel_card.pack(padx=25, fill=tk.X)
        self.return_info = tk.Label(sel_card, text="No book selected",
                                    font=("Segoe UI", 10), bg=BG_BEIGE, fg=TEXT_DARK,
                                    wraplength=220, justify="center")
        self.return_info.pack()

        self.return_borrow_detail = tk.Label(self.return_frame, text="",
                                             font=("Segoe UI", 9), bg=BG_CARD,
                                             fg=TEXT_MEDIUM, wraplength=240, justify="center")
        self.return_borrow_detail.pack(pady=(8,0))

        self.make_button(self.return_frame, "🔄  Confirm Return",
                         self.return_book_db, BUTTON_SUCCESS, BUTTON_SUCCESS_HOVER).pack(pady=15)

        self.return_result = tk.Label(self.return_frame, text="",
                                      font=("Segoe UI", 9, "italic"),
                                      bg=BG_CARD, fg=STATUS_AVAILABLE, wraplength=240)
        self.return_result.pack()

    def build_cost_form(self):
        self.cost_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.make_form_title(self.cost_frame, "Calculate Cost", "💰")

        tk.Label(self.cost_frame,
                 text="Click a book card or enter a Book ID\nto calculate borrowing cost.",
                 font=("Segoe UI", 9, "italic"), bg=BG_CARD, fg=TEXT_LIGHT,
                 justify="center").pack(pady=(0,8))

        idf = tk.Frame(self.cost_frame, bg=BG_CARD)
        idf.pack(fill=tk.X, padx=25, pady=(0,6))
        self.make_label(idf, "Book ID").pack(anchor="w", pady=(0,2))
        id_row = tk.Frame(idf, bg=BG_CARD)
        id_row.pack(fill=tk.X)
        id_cont = tk.Frame(id_row, bg=ENTRY_BORDER, padx=1, pady=1)
        id_cont.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))
        self.cost_id_entry = tk.Entry(id_cont, font=("Segoe UI", 10), bg=ENTRY_BG, fg=TEXT_DARK,
                                      insertbackground=ACCENT_BROWN, relief=tk.FLAT, bd=5)
        self.cost_id_entry.pack(fill=tk.X)
        self.cost_id_entry.bind("<Return>", lambda e: self.cost_find_book())
        lb = tk.Button(id_row, text="🔍 Find", font=("Segoe UI", 9, "bold"),
                       bg=BUTTON_INFO, fg=TEXT_WHITE, activebackground=BUTTON_INFO_HOVER,
                       relief=tk.FLAT, cursor="hand2", padx=10, pady=4,
                       command=self.cost_find_book)
        lb.pack(side=tk.LEFT)
        lb.bind("<Enter>", lambda e: lb.config(bg=BUTTON_INFO_HOVER))
        lb.bind("<Leave>", lambda e: lb.config(bg=BUTTON_INFO))

        sel = tk.Frame(self.cost_frame, bg=BG_BEIGE, padx=12, pady=8)
        sel.pack(padx=25, fill=tk.X, pady=(6,0))
        self.cost_book_info = tk.Label(sel, text="No book selected",
                                       font=("Segoe UI", 9), bg=BG_BEIGE, fg=TEXT_DARK,
                                       wraplength=220, justify="center")
        self.cost_book_info.pack()

        self.cost_rate_label = tk.Label(self.cost_frame, text="",
                                        font=("Segoe UI", 9, "italic"),
                                        bg=BG_CARD, fg=TEXT_LIGHT)
        self.cost_rate_label.pack(pady=(6,0))

        today = date.today()
        self.cost_borrow_entry = self.make_date_entry(
            self.cost_frame, "Borrow Date (YYYY-MM-DD)", today)
        self.cost_due_entry = self.make_date_entry(
            self.cost_frame, "Due / Return Date (YYYY-MM-DD)", today + timedelta(days=14))

        self.make_button(self.cost_frame, "💰  Calculate",
                         self.calculate_cost, BUTTON_GOLD, BUTTON_GOLD_HOVER).pack(pady=12)

        result_box = tk.Frame(self.cost_frame, bg=BG_BEIGE, padx=15, pady=12)
        result_box.pack(padx=25, fill=tk.X)
        self.cost_result_label = tk.Label(result_box, text="",
                                          font=("Segoe UI", 11, "bold"),
                                          bg=BG_BEIGE, fg=ACCENT_DARK,
                                          wraplength=230, justify="center")
        self.cost_result_label.pack()

        tk.Frame(self.cost_frame, bg=DIVIDER, height=1).pack(fill=tk.X, padx=25, pady=(12,6))
        #cost calc
        self._cost_book = None   # (book_id, title, genre)

    def show_add_form(self):
        self.hide_all_forms(); self.add_frame.pack(fill=tk.BOTH, expand=True); self.current_form="add"

    def show_update_form(self):
        self.hide_all_forms(); self.update_frame.pack(fill=tk.BOTH, expand=True); self.current_form="update"

    def show_delete_form(self):
        self.hide_all_forms(); self.delete_frame.pack(fill=tk.BOTH, expand=True); self.current_form="delete"

    def show_borrow_form(self):
        self.hide_all_forms(); self.borrow_frame.pack(fill=tk.BOTH, expand=True); self.current_form="borrow"

    def show_return_form(self):
        self.hide_all_forms(); self.return_frame.pack(fill=tk.BOTH, expand=True); self.current_form="return"

    def show_cost_form(self):
        self.hide_all_forms(); self.cost_frame.pack(fill=tk.BOTH, expand=True); self.current_form="cost"

#grid boxes
    def render_cards(self, rows):
        for w in self.cards_frame.winfo_children(): w.destroy()
        self._photo_refs.clear(); self._card_widgets.clear()

        canvas_w = self.canvas.winfo_width() or 700
        cols = max(1, canvas_w // (CARD_W + 24))

        for idx, row in enumerate(rows):
            book_id, title, author, genre, year, is_borrowed = row
            borrowed = bool(is_borrowed)

            card = tk.Frame(self.cards_frame, bg=BG_CARD,
                            highlightbackground=DIVIDER, highlightthickness=1,
                            cursor="hand2", width=CARD_W)
            r, c = divmod(idx, cols)
            card.grid(row=r, column=c, padx=12, pady=12)

            photo = load_cover_tk(book_id, COVER_W, COVER_H)
            self._photo_refs.append(photo)
            tk.Label(card, image=photo, bg=BG_CARD).pack(padx=10, pady=(10,4))

            short_title = (title[:22]+"…") if len(title)>23 else title
            tk.Label(card, text=short_title, font=("Georgia", 9, "bold"),
                     bg=BG_CARD, fg=ACCENT_DARK, wraplength=CARD_W-10,
                     justify="center").pack(padx=6)
            tk.Label(card, text=f"ID: {book_id}", font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_LIGHT).pack()

            short_author = (author[:20]+"…") if len(author)>21 else author
            tk.Label(card, text=short_author, font=("Segoe UI", 8, "italic"),
                     bg=BG_CARD, fg=TEXT_MEDIUM).pack()
            tk.Label(card, text=str(year), font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_LIGHT).pack()

            status_text  = "📖 Borrowed"  if borrowed else "✅ Available"
            status_color = STATUS_BORROWED if borrowed else STATUS_AVAILABLE
            tk.Label(card, text=status_text, font=("Segoe UI", 8, "bold"),
                     bg=BG_CARD, fg=status_color).pack(pady=(2,8))

            def _click(e, bid=book_id, t=title, a=author, g=genre, y=year, b=borrowed):
                self._on_card_click(bid, t, a, g, y, b)
            for child in list(card.winfo_children()) + [card]:
                child.bind("<Button-1>", _click)

            def _enter(e, f=card): f.config(highlightbackground=HIGHLIGHT, highlightthickness=2)
            def _leave(e, f=card): f.config(highlightbackground=DIVIDER,   highlightthickness=1)
            card.bind("<Enter>", _enter); card.bind("<Leave>", _leave)
            self._card_widgets.append(card)

        self.canvas.yview_moveto(0)

    def _on_card_click(self, book_id, title, author, genre, year, is_borrowed):
        self._current_book_id = book_id
        borrowed = bool(is_borrowed)
        self._populate_update_form(book_id, title, author, genre, year)
        self.upd_id_entry.delete(0, tk.END)
        self.upd_id_entry.insert(0, str(book_id))
        self.del_info.config(
            text=f"📖  {title}\n✍  {author}\n📂  {genre}  |  📅  {year}\n🆔  ID: {book_id}"
        )

        status_text  = "📖 Already Borrowed" if borrowed else "✅ Available to Borrow"
        status_color = STATUS_BORROWED        if borrowed else STATUS_AVAILABLE
        self.borrow_info.config(
            text=f"📖  {title}\n✍  {author}\n📂  {genre}  |  📅  {year}\n🆔  ID: {book_id}"
        )
        self.borrow_status_badge.config(text=status_text, fg=status_color)

        #show if borrowed or not
        self.return_info.config(
            text=f"📖  {title}\n✍  {author}\n🆔  ID: {book_id}"
        )
        if borrowed:
            try:
                cur = self.get_cursor()
                cur.execute(
                    "SELECT borrow_date, due_date FROM borrowings "
                    "WHERE book_id=%s AND returned=FALSE ORDER BY id DESC LIMIT 1",
                    (book_id,)
                )
                rec = cur.fetchone()
                cur.close()
                if rec:
                    self.return_borrow_detail.config(
                        text=f"Borrowed: {rec[0]}   |   Due: {rec[1]}",
                        fg=STATUS_BORROWED
                    )
                else:
                    self.return_borrow_detail.config(text="", fg=TEXT_MEDIUM)
            except: pass
        else:
            self.return_borrow_detail.config(
                text="This book is not currently borrowed.", fg=TEXT_LIGHT
            )

        self._cost_book = (book_id, title, genre) #COSTs
        self.cost_id_entry.delete(0, tk.END)
        self.cost_id_entry.insert(0, str(book_id))
        rate = GENRE_RATES.get(genre, DEFAULT_RATE)
        self.cost_book_info.config(
            text=f"📖  {title}\n📂  {genre}\n🆔  ID: {book_id}"
        )
        self.cost_rate_label.config(text=f"Rate: Rs. {rate} per day")
        self.cost_result_label.config(text="")

    def get_cursor(self):
        try: connection.ping(reconnect=True, attempts=3, delay=1)
        except mysql.connector.Error:
            messagebox.showerror("Connection Lost", "Lost connection to MySQL. Please restart the app.")
        return connection.cursor()

    def load_books(self):
        try:
            cur = self.get_cursor()
            cur.execute(
                "SELECT book_id, title, author, genre, year, is_borrowed "
                "FROM books ORDER BY book_id ASC"
            )
            rows = cur.fetchall()
            cur.close()
            self.render_cards(rows)
            total    = len(rows)
            borrowed = sum(1 for r in rows if r[5])
            self.total_label.config(text=f"📚 Total: {total}")
            self.borrowed_label.config(text=f"📖 Borrowed: {borrowed}")
            self.available_label.config(text=f"✅ Available: {total - borrowed}")
            self.result_label.config(text=f"Showing {total} books")
        except mysql.connector.Error as err:
            messagebox.showerror("Load Error", f"Could not load books:\n{err}")

    def search_books(self):
        raw = self.search_entry.get()
        keyword = "" if raw.strip() == "Search title, author, genre..." else raw.strip()
        if not keyword:
            self.load_books(); return
        try:
            cur = self.get_cursor()
            cur.execute(
                "SELECT book_id, title, author, genre, year, is_borrowed FROM books "
                "WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s "
                "   OR CAST(year AS CHAR) LIKE %s ORDER BY book_id ASC",
                tuple([f"%{keyword}%"] * 4)
            )
            rows = cur.fetchall()
            cur.close()
            self.render_cards(rows)
            count = len(rows)
            self.result_label.config(
                text=f"Found {count} result(s) for '{keyword}'" if count
                else f"No results for '{keyword}'"
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Search Error", f"Could not search books:\n{err}")

    def reset_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Search title, author, genre...")
        self.search_entry.config(fg=TEXT_LIGHT)
        self.load_books()

    def add_book_db(self):
        title  = self.add_title.get().strip()
        author = self.add_author.get().strip()
        genre  = self.add_genre.get()
        year   = self.add_year.get().strip()
        if not title or not author or not genre or not year:
            messagebox.showerror("Missing Fields", "Please fill in all fields!"); return
        try: year_int = int(year)
        except ValueError:
            messagebox.showerror("Invalid Year", "Year must be a valid number!"); return
        try:
            cur = self.get_cursor()
            cur.execute(
                "INSERT INTO books (title, author, genre, year) VALUES (%s,%s,%s,%s)",
                (title, author, genre, year_int)
            )
            connection.commit()
            new_id = cur.lastrowid
            cur.close()
            if self._add_cover_src:
                try: save_cover(new_id, self._add_cover_src)
                except Exception as ex:
                    messagebox.showwarning("Cover Warning",
                                           f"Book added but cover not saved:\n{ex}")
            self.add_title.delete(0, tk.END); self.add_author.delete(0, tk.END)
            self.add_genre.set(""); self.add_year.delete(0, tk.END)
            self._add_cover_src = None
            self._reset_cover_preview(self.add_cover_preview, self.add_cover_label, "No image chosen")
            self.load_books()
            self.add_status.config(text=f"✅ '{title}' added successfully!", fg=STATUS_AVAILABLE)
            self.root.after(3000, lambda: self.add_status.config(text=""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not add book:\n{err}")

    def find_book_by_id(self):
        raw = self.upd_id_entry.get().strip()
        if not raw:
            messagebox.showerror("Missing ID", "Please enter a Book ID."); return
        try: book_id = int(raw)
        except ValueError:
            messagebox.showerror("Invalid ID", "Book ID must be a number!"); return
        try:
            cur = self.get_cursor()
            cur.execute(
                "SELECT book_id, title, author, genre, year FROM books WHERE book_id=%s",
                (book_id,)
            )
            row = cur.fetchone(); cur.close()
            if row is None:
                messagebox.showwarning("Not Found", f"No book found with ID {book_id}."); return
            self._populate_update_form(*row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not find book:\n{err}")

    def _populate_update_form(self, book_id, title, author, genre, year):
        self._current_book_id = book_id
        self._upd_cover_src   = None
        self.upd_title.delete(0, tk.END);  self.upd_title.insert(0, title)
        self.upd_author.delete(0, tk.END); self.upd_author.insert(0, author)
        self.upd_genre.set(genre)
        self.upd_year.delete(0, tk.END);   self.upd_year.insert(0, year)
        self.upd_selected_label.config(text=f"Editing ID {book_id}: {title}", fg=BUTTON_INFO)
        self.upd_cover_label.config(text="No new image chosen")
        path = cover_path_for(book_id)
        if path:
            try:
                img = Image.open(path).convert("RGB"); img.thumbnail((52,70))
                ph  = ImageTk.PhotoImage(img); self._photo_refs.append(ph)
                self.upd_cover_preview.config(image=ph, text="", width=52, height=70)
                self.upd_cover_preview.image = ph; return
            except: pass
        self._reset_cover_preview(self.upd_cover_preview, self.upd_cover_label, "No new image chosen")

    def update_book_db(self):
        if not self._current_book_id:
            messagebox.showerror("No Book Selected", "Please find a book by ID or click a card first!"); return
        book_id = self._current_book_id
        title   = self.upd_title.get().strip()
        author  = self.upd_author.get().strip()
        genre   = self.upd_genre.get()
        year    = self.upd_year.get().strip()
        if not title or not author or not genre or not year:
            messagebox.showerror("Missing Fields", "Please fill in all fields!"); return
        try: year_int = int(year)
        except ValueError:
            messagebox.showerror("Invalid Year", "Year must be a valid number!"); return
        try:
            cur = self.get_cursor()
            cur.execute(
                "UPDATE books SET title=%s, author=%s, genre=%s, year=%s WHERE book_id=%s",
                (title, author, genre, year_int, book_id)
            )
            connection.commit(); cur.close()
            if self._upd_cover_src:
                try: save_cover(book_id, self._upd_cover_src)
                except Exception as ex:
                    messagebox.showwarning("Cover Warning",
                                           f"Book updated but cover not saved:\n{ex}")
            self._current_book_id = None; self._upd_cover_src = None
            self.upd_selected_label.config(text="No book selected", fg=TEXT_LIGHT)
            self.upd_id_entry.delete(0, tk.END)
            self._reset_cover_preview(self.upd_cover_preview, self.upd_cover_label, "No new image chosen")
            self.load_books()
            messagebox.showinfo("Updated", f"'{title}' has been updated successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not update book:\n{err}")

    def delete_book_db(self):
        if not self._current_book_id:
            messagebox.showerror("No Selection", "Please click a book card to select it first!"); return
        book_id    = self._current_book_id
        info       = self.del_info.cget("text")
        book_title = info.split("\n")[0].replace("📖  ","") if info != "No book selected" else "?"
        if not messagebox.askyesno("Confirm Deletion",
            f"Are you sure you want to permanently delete:\n\n'{book_title}'?\n\nThis cannot be undone."):
            return
        try:
            cur = self.get_cursor()
            cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
            connection.commit(); cur.close()
            path = cover_path_for(book_id)
            if path:
                try: os.remove(path)
                except: pass
            self._current_book_id = None
            self.del_info.config(text="No book selected")
            self.load_books()
            messagebox.showinfo("Deleted", f"'{book_title}' has been deleted.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not delete book:\n{err}")

    def borrow_book_db(self):
        if not self._current_book_id:
            messagebox.showerror("No Book Selected", "Please click a book card first!"); return
        book_id = self._current_book_id

        try:
            cur = self.get_cursor()
            cur.execute("SELECT is_borrowed, title FROM books WHERE book_id=%s", (book_id,))
            row = cur.fetchone(); cur.close()
            if row is None:
                messagebox.showerror("Error", "Book not found."); return
            if bool(row[0]):
                messagebox.showwarning("Already Borrowed",
                                       f"'{row[1]}' is already borrowed!\nReturn it first."); return
            title = row[1]
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err)); return

        try:
            borrow_date = datetime.strptime(self.borrow_date_entry.get().strip(), "%Y-%m-%d").date()
            due_date    = datetime.strptime(self.due_date_entry.get().strip(),    "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Dates must be in YYYY-MM-DD format."); return
        if due_date <= borrow_date:
            messagebox.showerror("Invalid Dates", "Due date must be after borrow date."); return

        try:
            cur = self.get_cursor()
            cur.execute(
                "INSERT INTO borrowings (book_id, borrow_date, due_date) VALUES (%s,%s,%s)",
                (book_id, borrow_date, due_date)
            )
            cur.execute("UPDATE books SET is_borrowed=TRUE WHERE book_id=%s", (book_id,))
            connection.commit(); cur.close()
            self.load_books()
            days = (due_date - borrow_date).days
            self.borrow_result.config(
                text=f"✅ '{title}' borrowed!\nFrom {borrow_date} → Due {due_date} ({days} days)",
                fg=STATUS_AVAILABLE
            )
            self.root.after(5000, lambda: self.borrow_result.config(text=""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not borrow book:\n{err}")

    def return_book_db(self):
        if not self._current_book_id:
            messagebox.showerror("No Book Selected", "Please click a book card first!"); return
        book_id = self._current_book_id
        try:
            cur = self.get_cursor()
            cur.execute("SELECT is_borrowed, title FROM books WHERE book_id=%s", (book_id,))
            row = cur.fetchone(); cur.close()
            if row is None:
                messagebox.showerror("Error", "Book not found."); return
            if not bool(row[0]):
                messagebox.showwarning("Not Borrowed", f"'{row[1]}' is not currently borrowed."); return
            title = row[1]
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err)); return

        try:
            cur = self.get_cursor()
            cur.execute(
                "UPDATE borrowings SET returned=TRUE "
                "WHERE book_id=%s AND returned=FALSE ORDER BY id DESC LIMIT 1",
                (book_id,)
            )
            cur.execute("UPDATE books SET is_borrowed=FALSE WHERE book_id=%s", (book_id,))
            connection.commit(); cur.close()
            self.load_books()
            self.return_result.config(text=f"✅ '{title}' returned successfully!", fg=STATUS_AVAILABLE)
            self.return_borrow_detail.config(text="")
            self.root.after(4000, lambda: self.return_result.config(text=""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not return book:\n{err}")

    def cost_find_book(self):
        raw = self.cost_id_entry.get().strip()
        if not raw:
            messagebox.showerror("Missing ID", "Please enter a Book ID."); return
        try: book_id = int(raw)
        except ValueError:
            messagebox.showerror("Invalid ID", "Book ID must be a number!"); return
        try:
            cur = self.get_cursor()
            cur.execute(
                "SELECT book_id, title, genre FROM books WHERE book_id=%s", (book_id,)
            )
            row = cur.fetchone(); cur.close()
            if row is None:
                messagebox.showwarning("Not Found", f"No book found with ID {book_id}."); return
            self._cost_book = (row[0], row[1], row[2])
            rate = GENRE_RATES.get(row[2], DEFAULT_RATE)
            self.cost_book_info.config(
                text=f"📖  {row[1]}\n📂  {row[2]}\n🆔  ID: {row[0]}"
            )
            self.cost_rate_label.config(text=f"Rate: Rs. {rate} per day")
            self.cost_result_label.config(text="")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def calculate_cost(self):
        if not self._cost_book:
            messagebox.showerror("No Book Selected",
                                 "Please find a book by ID or click a card first!"); return
        book_id, title, genre = self._cost_book
        try:
            borrow_date = datetime.strptime(self.cost_borrow_entry.get().strip(), "%Y-%m-%d").date()
            due_date    = datetime.strptime(self.cost_due_entry.get().strip(),    "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Dates must be in YYYY-MM-DD format."); return
        if due_date <= borrow_date:
            messagebox.showerror("Invalid Dates", "Return date must be after borrow date."); return

        days = (due_date - borrow_date).days
        rate = GENRE_RATES.get(genre, DEFAULT_RATE)
        cost = days * rate

        self.cost_result_label.config(
            text=f"{days} day(s)  ×  Rs. {rate}/day\n"
                 f"────────────────\n"
                 f"Total:  Rs. {cost:,}.00",
            fg=ACCENT_DARK
        )

if __name__ == "__main__":
    LibraryApp()