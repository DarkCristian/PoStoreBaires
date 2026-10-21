"""SPDX-License-Identifier: GPL-3.0-only. Copyright (C) 2026 Cristian Carroccio."""
from dataclasses import replace
from html import escape
from pathlib import Path
import sys
import sqlite3
from PySide6.QtCore import Qt, QTimer, QUrl, QSize, QStandardPaths
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog,
    QDialogButtonBox, QScrollArea, QFileDialog, QMessageBox, QTextBrowser,
    QInputDialog, QSplitter, QFrame,
)
from . import __version__
from .domain import Store, Product, METHODS, CATEGORIES, amount, money, decimal_text
from .catalog import Catalog
from .catalog_ui import CatalogDialog
from .storage import LocalStore

ASSETS = Path(__file__).resolve().parent / "assets"
STYLE = """
QWidget { font-family: 'Segoe UI', sans-serif; font-size: 14px; color:#24324a; }
QMainWindow, QDialog { background:#eef2f8; }
QPushButton { padding:10px 15px; border:1px solid #d5deeb; border-radius:8px; background:white; }
QPushButton:hover { background:#e5edff; } QPushButton:disabled { color:#9ba6b5; }
QPushButton[primary="true"] { background:#3169de; color:white; border-color:#3169de; }
QLineEdit, QComboBox, QSpinBox { padding:9px; border:1px solid #d5deeb; border-radius:6px; background:white; }
QTableWidget { border:0; background:white; gridline-color:#e8edf5; selection-background-color:#dfeaff; selection-color:#24324a; }
QHeaderView::section { padding:10px; background:#f5f7fb; color:#76839a; border:0; }
QTabWidget::pane { border:0; } QTabBar::tab { padding:13px 28px; margin-right:5px; background:white; border-radius:6px; }
QTabBar::tab:selected { background:#3169de; color:white; }
QFrame#panel { background:white; border:1px solid #dce3ed; border-radius:12px; }
QLabel#title { font-size:26px; font-weight:bold; color:#2859ba; }
QLabel#amount { font-size:38px; font-weight:bold; color:#2859ba; }
QTextBrowser { background:white; border:0; padding:12px; }
QCheckBox { spacing:10px; padding:8px 0; }
QCheckBox::indicator { width:34px; height:19px; border-radius:9px; background:#cdd6e4; }
QCheckBox::indicator:checked { background:#25925a; }
"""

def button(text, action, primary=False):
    b = QPushButton(text)
    b.setProperty("primary", primary)
    b.clicked.connect(action)
    return b


def label(text, name=""):
    w = QLabel(text)
    w.setWordWrap(True)
    if name:
        w.setObjectName(name)
    return w


def table(headers):
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().hide()
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    return t


def fill(t, rows):
    t.setRowCount(len(rows))
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            t.setItem(i, j, QTableWidgetItem(str(value)))


def panel():
    frame = QFrame()
    frame.setObjectName("panel")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(22, 22, 22, 22)
    return frame, layout


def combo(values, current):
    w = QComboBox()
    w.addItems(values)
    w.setCurrentText(current)
    return w


def spin(value, minimum=0, maximum=10000000):
    w = QSpinBox()
    w.setRange(minimum, maximum)
    w.setValue(value)
    return w


def load_image(path, page=0):
    if not path:
        return QPixmap()
    if Path(path).suffix.lower() == ".pdf":
        from PySide6.QtPdf import QPdfDocument
        document = QPdfDocument()
        error = document.load(str(path))
        if error != QPdfDocument.Error.None_ or not 0 <= page < document.pageCount():
            raise ValueError("No se pudo abrir el PDF o la página elegida no existe.")
        size = document.pagePointSize(page)
        if size.width() <= 0 or size.height() <= 0:
            raise ValueError("La página PDF no es válida.")
        target = QSize(max(1, round(size.width() * 2)), max(1, round(size.height() * 2)))
        target.scale(QSize(1800, 1800), Qt.AspectRatioMode.KeepAspectRatio)
        image = document.render(page, target)
        if image.isNull():
            raise ValueError("No se pudo convertir la página PDF a imagen.")
        return QPixmap.fromImage(image)
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        raise ValueError("No se pudo leer la imagen.")
    return pixmap


class PathInput(QWidget):
    def __init__(self, path="", pdf=False):
        super().__init__()
        self.edit = QLineEdit(path)
        self.edit.setReadOnly(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.edit)
        filters = "Imágenes y PDF (*.png *.jpg *.jpeg *.pdf)" if pdf else "Imágenes (*.png *.jpg *.jpeg)"
        def choose():
            selected, _ = QFileDialog.getOpenFileName(self, "Elegir archivo", "", filters)
            if selected:
                self.edit.setText(selected)
        layout.addWidget(button("Elegir", choose))
        layout.addWidget(button("Quitar", self.edit.clear))

    def path(self):
        return self.edit.text()


class SettingsDialog(QDialog):
    def __init__(self, store, parent):
        super().__init__(parent)
        self.store = store
        self.result_config = None
        self.setWindowTitle("PoStoreBaires · Ajustes")
        self.resize(760, 760)
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)
        cfg = store.config
        self.fields = {}
        def text(key, title):
            w = QLineEdit(getattr(cfg, key))
            self.fields[key] = w
            form.addRow(title, w)
        form.addRow(label("Comercio y ticket", "title"))
        text("shop", "Nombre comercial")
        text("legal", "Razón social")
        self.logo = PathInput(cfg.logo)
        form.addRow("Logo", self.logo)
        self.paper = combo(["58 mm", "80 mm"], cfg.paper)
        form.addRow("Papel", self.paper)
        form.addRow(label("Caja y sesión", "title"))
        text("box", "Caja")
        text("cashier", "Cajero")
        self.role = combo(["Administrador", "Supervisor", "Cajero"], cfg.role)
        self.mode = combo(["Principal", "Secundaria", "Independiente"], cfg.mode)
        form.addRow("Perfil simulado", self.role)
        form.addRow("Modo simulado", self.mode)
        text("host", "IP principal")
        form.addRow(label("La red y los permisos todavía son ilustrativos. Cerrá el turno para cambiar caja/cajero."))
        form.addRow(label("Pantalla del cliente", "title"))
        self.enabled = QCheckBox("Activar pantalla del cliente")
        self.enabled.setChecked(cfg.customer_enabled)
        form.addRow(self.enabled)
        self.screen = QComboBox()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            g = screen.geometry()
            self.screen.addItem(f"Monitor {i+1}: {screen.name()} · {g.width()} × {g.height()}", i)
        self.screen.setCurrentIndex(min(cfg.screen, len(screens)-1))
        form.addRow("Monitor", self.screen)
        self.view = combo(["Solo QR", "Solo alias", "QR y alias"], cfg.wallet_view)
        form.addRow("Mostrar", self.view)
        self.qr = PathInput(cfg.qr, pdf=True)
        form.addRow("QR del comercio", self.qr)
        self.page = spin(cfg.qr_page + 1, 1, 100000)
        form.addRow("Página si es PDF", self.page)
        text("alias", "Alias")
        text("wallet", "Wallet / banco")
        text("holder", "Titular")
        form.addRow(label("El cliente escanea el QR o ingresa el alias en su app. El cobro se verifica manualmente."))
        preview = button("Vista previa del QR", self.preview)
        form.addRow(preview)
        form.addRow(label("Sonidos", "title"))
        self.scan_sound = QCheckBox("Bip al agregar producto")
        self.cash_sound = QCheckBox("Caja registradora al confirmar cobro")
        self.scan_sound.setChecked(cfg.scan_sound)
        self.cash_sound.setChecked(cfg.cash_sound)
        form.addRow(self.scan_sound, button("Probar bip", lambda: parent.play_sound("scan", True)))
        form.addRow(self.cash_sound, button("Probar caja", lambda: parent.play_sound("cash", True)))
        if store.repository:
            path_label = label(str(store.repository.path))
            path_label.setTextFormat(Qt.TextFormat.PlainText)
            form.addRow("Base local", path_label)
            form.addRow(button("Exportar copia de la base SQLite", parent.export_backup))
        scroll.setWidget(content)
        outer.addWidget(scroll)
        controls = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        controls.accepted.connect(self.save)
        controls.rejected.connect(self.reject)
        outer.addWidget(controls)

    def preview(self):
        try:
            pix = load_image(self.qr.path(), self.page.value()-1)
            if pix.isNull():
                raise ValueError("Elegí un archivo QR.")
            d = QDialog(self)
            d.setWindowTitle("Vista previa QR")
            layout = QVBoxLayout(d)
            image = QLabel()
            image.setPixmap(pix.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio))
            layout.addWidget(image)
            layout.addWidget(button("Cerrar", d.accept))
            d.exec()
        except ValueError as e:
            QMessageBox.warning(self, "QR", str(e))

    def save(self):
        try:
            cfg = replace(self.store.config, **{key: w.text().strip() for key, w in self.fields.items()},
                          logo=self.logo.path(), qr=self.qr.path(), qr_page=self.page.value()-1,
                          paper=self.paper.currentText(), role=self.role.currentText(), mode=self.mode.currentText(),
                          customer_enabled=self.enabled.isChecked(), screen=self.screen.currentIndex(),
                          wallet_view=self.view.currentText(), scan_sound=self.scan_sound.isChecked(),
                          cash_sound=self.cash_sound.isChecked())
            if cfg.logo:
                load_image(cfg.logo)
            if cfg.qr:
                load_image(cfg.qr, cfg.qr_page)
            self.store.configure(cfg)
            self.result_config = cfg
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Revisá los ajustes", str(e))


class ProductDialog(QDialog):
    def __init__(self, store, parent, index=None, code=""):
        super().__init__(parent)
        self.setWindowTitle("PoStoreBaires · Producto")
        self.store, self.index = store, index
        self.main = parent
        p = store.products[index] if index is not None else Product(code, "", CATEGORIES[-1], 0)
        self.reference = dict(p.reference)
        self.references = []
        self.resize(760, 720)
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.code, self.name = QLineEdit(p.code), QLineEdit(p.name)
        self.category = combo(list(CATEGORIES), p.category)
        self.price, self.cost = QLineEdit(decimal_text(p.price)), QLineEdit(decimal_text(p.cost))
        self.stock, self.pack, self.minimum = spin(p.stock), spin(p.pack, 1), spin(p.minimum)
        self.illustration = combo(["box", "chocolate", "cleaning", "cigarettes", "water"], p.illustration)
        self.photo = PathInput(p.photo)
        for title, w in [("Código", self.code), ("Nombre", self.name), ("Categoría", self.category),
                         ("Precio unitario (pesos enteros)", self.price), ("Costo unitario (pesos enteros)", self.cost), ("Stock unidades", self.stock),
                         ("Unidades por bulto", self.pack), ("Alerta mínimo", self.minimum),
                         ("Ilustración", self.illustration), ("Foto", self.photo)]:
            form.addRow(title, w)
        form.addRow(label("Sin foto se utiliza la ilustración. No se descargan imágenes externas automáticamente."))
        self.reference_label = label("")
        self.reference_label.setTextFormat(Qt.TextFormat.PlainText)
        self.reference_table = table(["Producto", "Referencia ARS", "Fecha", "Fuente"])
        self.reference_table.setMaximumHeight(150)
        form.addRow(button("Buscar código en catálogo de referencia", self.lookup))
        form.addRow(self.reference_table)
        form.addRow(self.reference_label)
        form.addRow(button("Usar nombre y datos de la referencia seleccionada", self.apply_reference))
        form.addRow(button("Usar precio de referencia seleccionado", self.apply_reference_price))
        self.code.returnPressed.connect(self.lookup)
        self.code.textChanged.connect(self.code_changed)
        if code and getattr(parent, 'catalog', None):
            self.lookup()

        controls = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        controls.accepted.connect(self.save)
        controls.rejected.connect(self.reject)
        outer.addWidget(controls)

    def save(self):
        try:
            if self.photo.path():
                load_image(self.photo.path())
            p = Product(self.code.text().strip(), self.name.text().strip(), self.category.currentText(),
                        amount(self.price.text()), amount(self.cost.text()), self.stock.value(), self.pack.value(),
                        self.minimum.value(), self.illustration.currentText(), self.photo.path(), dict(self.reference))
            if self.index is not None and p.code != self.store.products[self.index].code:
                if any(other.code == p.code and i != self.index for i, other in enumerate(self.store.products)):
                    raise ValueError("Código duplicado. Ya pertenece a otro producto.")
                old_code = self.store.products[self.index].code
                answer = QMessageBox.question(
                    self, "Confirmar cambio de código",
                    f"Vas a cambiar el código de {old_code} a {p.code}.\n"
                    "El código anterior dejará de encontrar este producto. ¿Guardar el cambio?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes:
                    return
            self.store.save_product(p, self.index)
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Producto", str(e))

    def code_changed(self):
        self.references = []
        self.reference = {}
        self.reference_table.setRowCount(0)
        self.reference_label.clear()

    def lookup(self):
        if not self.main.catalog:
            self.reference_label.setText("Catálogo no configurado. Podés completar el producto manualmente.")
            return
        try:
            self.references = self.main.catalog.lookup(self.code.text())
            fill(self.reference_table, [(r.name, money(r.price) if r.price is not None else "Sin precio entero",
                                        r.observed or "Fecha desconocida", r.source) for r in self.references])
            if self.references:
                self.reference_table.selectRow(0)
                self.reference_label.setText("Referencia externa: revisá fecha, presentación y sucursal. Tu precio solo cambia si elegís usarlo.")
            else:
                self.reference_label.setText("No encontrado en el catálogo local. Alta manual disponible.")
        except (ValueError, sqlite3.Error) as e:
            self.reference_label.setText("Catálogo no disponible: " + str(e) + ". Podés cargar el producto manualmente.")

    def selected_reference(self):
        row = self.reference_table.currentRow()
        return self.references[row] if 0 <= row < len(self.references) else None

    def apply_reference(self):
        from dataclasses import asdict
        ref = self.selected_reference()
        if not ref:
            return
        self.name.setText(ref.name)
        self.reference = asdict(ref)
        warning = " · DATOS ANTIGUOS O SIN FECHA" if ref.stale else ""
        self.reference_label.setText(f"{ref.source} · {ref.observed or 'Fecha desconocida'}{warning}\n"
                                     f"Marca: {ref.brand} · Presentación: {ref.presentation}\n"
                                     f"Imagen (no descargada): {ref.image_url or 'No disponible; se usa ilustración'}")

    def apply_reference_price(self):
        ref = self.selected_reference()
        if ref and ref.price is not None:
            self.apply_reference()
            self.price.setText(decimal_text(ref.price))



class ProductSearchDialog(QDialog):
    """Select only sellable products registered in the local commerce inventory."""
    def __init__(self, parent, query=""):
        super().__init__(parent)
        self.main = parent
        self.indices = []
        self.missing_timer = QTimer(self)
        self.missing_timer.setSingleShot(True)
        self.missing_timer.timeout.connect(self.not_found)
        self.setWindowTitle("PoStoreBaires · Buscar producto para la compra")
        self.resize(780, 500)
        layout = QVBoxLayout(self)
        self.query = QLineEdit()
        self.query.setPlaceholderText("Buscar por nombre o código de barras")
        self.query.setClearButtonEnabled(True)
        layout.addWidget(self.query)
        self.results = table(["Producto", "Código", "Precio", "Disponible"])
        layout.addWidget(self.results)
        self.message = QLabel()
        self.message.setTextFormat(Qt.TextFormat.PlainText)
        self.message.setWordWrap(True)
        layout.addWidget(self.message)
        row = QHBoxLayout()
        self.add_button = button("Agregar a la compra", self.add_selected, True)
        row.addWidget(self.add_button)
        row.addWidget(button("Cancelar", self.reject))
        layout.addLayout(row)
        self.query.textChanged.connect(self.refresh_results)
        self.query.returnPressed.connect(self.add_selected)
        self.results.cellDoubleClicked.connect(lambda *_: self.add_selected())
        self.query.setText(query)
        self.refresh_results()
        self.query.setFocus()

    def refresh_results(self):
        self.missing_timer.stop()
        terms = self.query.text().strip().casefold().split()
        store = self.main.store
        self.indices = [i for i, p in enumerate(store.products)
                        if all(term in (p.name + " " + p.code).casefold() for term in terms)]
        fill(self.results, [(store.products[i].name, store.products[i].code,
                             money(store.products[i].price),
                             max(0, store.products[i].stock - store.cart.get(i, 0)))
                            for i in self.indices])
        self.add_button.setEnabled(bool(self.indices))
        if self.indices:
            self.results.selectRow(0)
            self.message.setText("Elegí un producto. Enter o doble clic agrega una unidad a la compra.")
        else:
            self.message.setText("Sin coincidencias en el inventario del comercio.")
            if self.query.text().strip():
                self.missing_timer.start(800)

    def not_found(self):
        self.missing_timer.stop()
        if self.indices or not self.query.text().strip():
            return
        query = self.query.text().strip()
        self.reject()
        self.main.product_not_found(query)

    def done(self, result):
        self.missing_timer.stop()
        super().done(result)

    def add_selected(self):
        row = self.results.currentRow()
        if not 0 <= row < len(self.indices):
            self.not_found()
            return
        try:
            self.main.store.add(self.indices[row])
        except (ValueError, IndexError) as e:
            self.message.setText(str(e))
            return
        self.main.clear_result()
        self.main.refresh()
        self.main.play_sound("scan")
        self.main.scan_input.clear()
        self.accept()


class CustomerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PoStoreBaires · Pantalla del cliente")
        self.resize(1000, 800)
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        self.logo = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.heading = label("", "title")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary = QTextBrowser()
        self.summary.setMinimumHeight(180)
        self.amount_label = label("", "amount")
        self.amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumHeight(10)
        self.alias_label = label("", "title")
        self.alias_label.setTextFormat(Qt.TextFormat.PlainText)
        self.alias_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details = label("")
        self.details.setTextFormat(Qt.TextFormat.PlainText)
        self.details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo)
        layout.addWidget(self.heading)
        columns = QHBoxLayout()
        columns.addWidget(self.summary, 1)
        payment = QVBoxLayout()
        for w in (self.amount_label, self.qr_label, self.alias_label, self.details):
            payment.addWidget(w)
        payment.addStretch()
        columns.addLayout(payment, 1)
        layout.addLayout(columns)
        scroll.setWidget(body)
        outer.addWidget(scroll)
        self.image_cache = {}

    def image(self, path, page=0):
        key = (path, page)
        if key not in self.image_cache:
            self.image_cache[key] = load_image(path, page)
        return self.image_cache[key]

    def refresh(self, store, wallet_amount=None, sale=None):
        cfg = store.config
        self.heading.setText(cfg.shop)
        self.logo.setVisible(bool(cfg.logo))
        self.logo.clear()
        if cfg.logo:
            try:
                self.logo.setPixmap(self.image(cfg.logo).scaled(180, 80, Qt.AspectRatioMode.KeepAspectRatio))
            except ValueError:
                pass
        self.qr_label.clear()
        self.alias_label.clear()
        if sale is not None:
            title = "Cobrado OK" if sale.payments[1] == sale.total else "Venta confirmada"
            lines = "".join(f"<p>{escape(m)}: {money(n)}</p>" for m, n in zip(METHODS, sale.payments) if n)
            self.summary.setHtml(f"<h1 style='color:#16834d'>{title}</h1>{lines}")
            self.amount_label.setText(money(sale.total))
            self.details.setText((f"Tu vuelto: {money(sale.change)}\n" if sale.received else "") + "¡Gracias por tu compra!")
            return
        if store.cart:
            rows = "".join(f"<tr><td>{q} × {escape(store.products[i].name)}</td><td>{money(store.products[i].price*q)}</td></tr>"
                           for i, q in store.cart.items())
            self.summary.setHtml(f"<h2>Tu compra</h2><table width='100%' cellpadding='8'>{rows}</table>"
                                 + f"<p>Total de la compra: <b>{money(store.total())}</b></p>")
        else:
            self.summary.setHtml("<h2>¡Gracias por tu visita!</h2><p>Tu compra aparecerá aquí.</p>")
        due = store.total() if wallet_amount is None else wallet_amount
        self.amount_label.setText("Importe a pagar: " + money(due) if due else "Pagá desde tu celular")
        if cfg.wallet_view != "Solo alias" and cfg.qr:
            try:
                pix = self.image(cfg.qr, cfg.qr_page)
                self.qr_label.setPixmap(pix.scaled(340, 340, Qt.AspectRatioMode.KeepAspectRatio))
            except ValueError as e:
                self.qr_label.setText(str(e))
        if cfg.wallet_view != "Solo QR":
            self.alias_label.setText("ALIAS: " + cfg.alias)
        self.details.setText(f"{cfg.wallet}\nTitular: {cfg.holder or 'Consultar al cajero'}\n"
                             "Escaneá el QR o ingresá el alias en tu app.\n"
                             "Verificá titular e importe, realizá el pago y avisale al cajero.")


class PaymentDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main = parent
        self.setWindowTitle("PoStoreBaires · Cobrar venta")
        form = QFormLayout(self)
        form.addRow(label(money(parent.store.total()), "amount"))
        self.fields = []
        for i, method in enumerate(METHODS):
            field = QLineEdit(decimal_text(parent.store.total()) if i == 0 else "0")
            self.fields.append(field)
            form.addRow("Efectivo recibido" if i == 0 else method, field)
        self.verified = QCheckBox("Verifiqué la acreditación wallet en la cuenta del comercio")
        form.addRow(button("Cobrar por wallet / mostrar importe", self.wallet))
        form.addRow(self.verified)
        form.addRow(label("El QR y el alias no verifican pagos automáticamente."))
        for f in self.fields:
            f.textChanged.connect(self.changed)
        form.addRow(button("Confirmar cobro", self.complete, True))
        form.addRow(button("Volver", self.reject))

    def changed(self):
        self.verified.setChecked(False)
        try:
            n = amount(self.fields[1].text())
        except ValueError:
            n = 0
        self.main.wallet_amount = n if n else None
        self.main.refresh_customer()

    def wallet(self):
        if not self.main.store.config.customer_enabled:
            self.main.notify("Activá la pantalla del cliente desde Ajustes.")
            return
        try:
            value = amount(self.fields[1].text())
        except ValueError:
            value = 0
        if not value:
            for i, field in enumerate(self.fields):
                field.setText(decimal_text(self.main.store.total()) if i == 1 else "0")
        self.main.open_customer()

    def complete(self):
        try:
            payments = [amount(w.text()) for w in self.fields]
            sale = self.main.store.complete(payments, self.verified.isChecked())
            self.main.last_sale = sale
            self.main.result_sale = sale
            self.main.wallet_amount = None
            self.main.refresh()
            self.main.play_sound("cash")
            self.main.result_timer.start(12000)
            low = [p.name for p in self.main.store.products if p.stock <= p.minimum]
            self.main.notify("Reposición: " + ", ".join(low) if low else "Venta confirmada.")
            self.accept()
        except ValueError as e:
            self.main.notify(str(e))

    def reject(self):
        self.main.wallet_amount = None
        self.main.refresh_customer()
        super().reject()


class MainWindow(QMainWindow):
    def __init__(self, store=None, catalog=None):
        super().__init__()
        self.store = store or Store.demo()
        self.catalog = catalog
        self.last_sale = self.store.sales[-1] if self.store.sales else None
        self.result_sale = None
        self.wallet_amount = None
        self.customer = CustomerWindow()
        self.sounds = {}
        self.setWindowTitle(f"PoStoreBaires {__version__} · Beta Python/Qt")
        self.resize(1320, 850)
        self.setMinimumSize(1000, 680)
        self.result_timer = QTimer(self)
        self.result_timer.setSingleShot(True)
        self.result_timer.timeout.connect(self.clear_result)
        outer = QWidget()
        root = QVBoxLayout(outer)
        root.setContentsMargins(24, 20, 24, 20)
        self.setCentralWidget(outer)
        head = QHBoxLayout()
        head.addWidget(label("▣ PoStoreBaires", "title"))
        head.addStretch()
        head.addWidget(label(f"{__version__} · Base local"))
        head.addWidget(button("Ayuda", self.help))
        head.addWidget(button("Ajustes", self.settings))
        root.addLayout(head)
        self.identity = label("")
        root.addWidget(self.identity)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)
        self.build_cash()
        self.build_audit()
        self.build_inventory()
        self.statusBar().showMessage("Guardado local SQLite · Sin sincronización multicaja ni impresión fiscal." if self.store.repository else "Modo de prueba en memoria.")
        self.refresh()

    def notify(self, text):
        self.statusBar().showMessage(text, 9000)

    def guard(self, action):
        try:
            action()
            self.refresh()
        except (ValueError, IndexError) as e:
            self.notify(str(e))

    def build_cash(self):
        w = QWidget()
        self.tabs.addTab(w, "Caja")
        layout = QHBoxLayout(w)
        frame, left = panel()
        left.addWidget(label("Nueva venta", "title"))
        left.addWidget(label("Escaneá o ingresá un código, o usá la lupa para buscar por nombre."))
        row = QHBoxLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Código de barras + Enter")
        self.scan_input.returnPressed.connect(self.scan)
        row.addWidget(self.scan_input)
        self.search_product_button = button("Buscar", self.search_purchase_product)
        self.search_product_button.setIcon(QIcon(str(ASSETS / "search.svg")))
        self.search_product_button.setToolTip("Buscar un producto por nombre o código para agregarlo a la compra")
        self.search_product_button.setAccessibleName("Buscar producto para la compra")
        row.addWidget(self.search_product_button)
        row.addWidget(button("Agregar", self.scan, True))
        left.addLayout(row)
        self.cart_table = table(["Producto", "Cantidad", "Precio", "Subtotal"])
        left.addWidget(self.cart_table)
        actions = QHBoxLayout()
        for text, action in [("− Unidad", lambda: self.quantity(-1)), ("+ Unidad", lambda: self.quantity(1)),
                             ("Quitar", self.remove), ("Vaciar venta", self.empty_cart), ("Último ticket", self.ticket)]:
            actions.addWidget(button(text, action))
        left.addLayout(actions)
        quick = QHBoxLayout()
        for i in range(min(4, len(self.store.products))):
            quick.addWidget(button(self.store.products[i].name, lambda checked=False, index=i: self.add(index)))
        left.addLayout(quick)
        layout.addWidget(frame, 3)
        side, right = panel()
        self.turn = label("")
        self.total_label = label("", "amount")
        right.addWidget(self.turn)
        right.addWidget(label("Total a cobrar"))
        right.addWidget(self.total_label)
        right.addWidget(button("Cobrar venta", self.pay, True))
        right.addWidget(label("Efectivo · Wallet · Débito · Crédito\nPagos mixtos y cálculo de vuelto."))
        right.addWidget(button("Pantalla del cliente", self.open_customer))
        right.addStretch()
        right.addWidget(label("QR/alias visibles durante la compra. La acreditación se verifica manualmente."))
        layout.addWidget(side, 1)

    def build_audit(self):
        w = QWidget()
        self.tabs.addTab(w, "Arqueo")
        layout = QVBoxLayout(w)
        self.audit_label = label("", "title")
        layout.addWidget(self.audit_label)
        self.audit_table = table(["Medio", "Cobros del turno", "Esperado"])
        layout.addWidget(self.audit_table)
        row = QHBoxLayout()
        row.addWidget(button("Retirar efectivo", self.withdraw))
        row.addWidget(button("Abrir turno", self.open_turn))
        row.addWidget(button("Arqueo y cierre", self.close_turn, True))
        layout.addLayout(row)
        layout.addWidget(label("Historial de cierres de esta sesión"))
        self.closures_table = table(["Fecha", "Caja", "Cajero", "Diferencia total"])
        self.closures_table.cellDoubleClicked.connect(lambda *_: self.closure_detail())
        layout.addWidget(self.closures_table)
        layout.addWidget(button("Ver detalle del cierre seleccionado", self.closure_detail))

    def build_inventory(self):
        w = QWidget()
        self.tabs.addTab(w, "Insumos")
        layout = QVBoxLayout(w)
        row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar nombre o código")
        self.search.textChanged.connect(self.refresh_inventory)
        row.addWidget(self.search)
        self.category = combo(["Todas las categorías"] + list(CATEGORIES), "Todas las categorías")
        self.category.currentTextChanged.connect(self.refresh_inventory)
        row.addWidget(self.category)
        row.addWidget(button("Nuevo producto", lambda: self.product(), True))
        row.addWidget(button("Catálogo de referencia", self.manage_catalog))
        layout.addLayout(row)
        self.inventory = table(["Producto", "Código", "Categoría", "Precio", "Stock", "Bultos + unidades"])
        self.inventory.setIconSize(QSize(42, 42))
        self.inventory.cellDoubleClicked.connect(lambda *_: self.edit_product())
        layout.addWidget(self.inventory)
        row = QHBoxLayout()
        row.addWidget(button("Editar seleccionado", self.edit_product))
        row.addWidget(button("Ingresar bultos", self.receive))
        layout.addLayout(row)

    def refresh(self):
        cfg = self.store.config
        self.identity.setText(f"{cfg.shop} · {cfg.box} · {cfg.cashier} · {cfg.role} · {cfg.mode} (red/permisos simulados)")
        self.turn.setText("Turno abierto" if self.store.opened else "Turno cerrado")
        fill(self.cart_table, [(self.store.products[i].name, q, money(self.store.products[i].price),
                                money(q*self.store.products[i].price)) for i, q in self.store.cart.items()])
        self.total_label.setText(money(self.store.total()))
        totals, expected = self.store.totals(), self.store.expected()
        self.audit_label.setText(f"Inicial: {money(self.store.opening)} · Retiros: {money(self.store.withdrawals)}")
        fill(self.audit_table, [(m, money(t), money(e)) for m, t, e in zip(METHODS, totals, expected)])
        fill(self.closures_table, [(c['date'], c['box'], c['cashier'], money(sum(c['differences']))) for c in self.store.closures])
        self.refresh_inventory()
        self.refresh_customer()

    def refresh_inventory(self):
        query = self.search.text().lower()
        category = self.category.currentText()
        self.inventory_indices = [i for i, p in enumerate(self.store.products)
                                  if query in (p.name+' '+p.code).lower() and
                                  (category == "Todas las categorías" or category == p.category)]
        rows = []
        for i in self.inventory_indices:
            p = self.store.products[i]
            rows.append((p.name, p.code, p.category, money(p.price),
                         f"{'⚠ ' if p.stock <= p.minimum else ''}{p.stock} u.",
                         f"{p.stock//p.pack} bultos + {p.stock%p.pack} u. (x{p.pack})"))
        fill(self.inventory, rows)
        for row, i in enumerate(self.inventory_indices):
            p = self.store.products[i]
            icon = QIcon(p.photo) if p.photo else QIcon(str(ASSETS / f"{p.illustration}.svg"))
            if icon.isNull():
                icon = QIcon(str(ASSETS / f"{p.illustration}.svg"))
            self.inventory.item(row, 0).setIcon(icon)
        self.inventory.resizeRowsToContents()

    def add(self, i):
        try:
            self.store.add(i)
            self.clear_result()
            self.refresh()
            self.play_sound("scan")
            self.scan_input.clear()
            self.scan_input.setFocus()
        except ValueError as e:
            self.notify(str(e))

    def search_purchase_product(self):
        ProductSearchDialog(self, self.scan_input.text().strip()).exec()
        self.scan_input.setFocus()

    def scan(self):
        code = self.scan_input.text().strip()
        if not code:
            return
        for i, p in enumerate(self.store.products):
            if p.code == code:
                self.add(i)
                return
        self.product_not_found(code)

    def product_not_found(self, query=""):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Producto no encontrado")
        dialog.setText("Producto no encontrado")
        dialog.setInformativeText("Ingresá el código por teclado o registrá un producto nuevo en Insumos.")
        dialog.setIcon(QMessageBox.Icon.Information)
        manual = dialog.addButton("Agregar manualmente", QMessageBox.ButtonRole.ActionRole)
        new = dialog.addButton("Agregar nuevo", QMessageBox.ButtonRole.ActionRole)
        dialog.exec()
        if dialog.clickedButton() == manual:
            code, ok = QInputDialog.getText(self, "Agregar manualmente", "Código de barras:", text=query if query.isdigit() else "")
            if ok and code.strip():
                self.tabs.setCurrentIndex(0)
                self.scan_input.setText(code.strip())
                self.scan()
        elif dialog.clickedButton() == new:
            self.tabs.setCurrentIndex(2)
            self.product(code=query if query.isdigit() else "")

    def cart_index(self):
        row = self.cart_table.currentRow()
        return list(self.store.cart)[row] if 0 <= row < len(self.store.cart) else None

    def quantity(self, n):
        index = self.cart_index()
        if index is None:
            return
        if n > 0:
            self.add(index)
        else:
            self.guard(lambda: self.store.change_quantity(index, -1))

    def remove(self):
        index = self.cart_index()
        if index is not None:
            self.guard(lambda: self.store.remove(index))

    def empty_cart(self):
        if self.store.cart and QMessageBox.question(self, "Venta", "¿Vaciar esta venta?") == QMessageBox.StandardButton.Yes:
            self.guard(self.store.clear)

    def pay(self):
        if not self.store.opened or not self.store.cart:
            self.notify("Agregá productos en un turno abierto.")
            return
        self.clear_result()
        PaymentDialog(self).exec()

    def product(self, index=None, code=""):
        if self.store.cart and index is not None:
            self.notify("Terminá o vaciá la venta antes de editar productos.")
            return
        ProductDialog(self.store, self, index, code).exec()
        self.refresh()

    def inventory_index(self):
        row = self.inventory.currentRow()
        return self.inventory_indices[row] if 0 <= row < len(self.inventory_indices) else None

    def edit_product(self):
        i = self.inventory_index()
        if i is not None:
            self.product(i)

    def receive(self):
        i = self.inventory_index()
        if i is None:
            return
        n, ok = QInputDialog.getInt(self, "Ingresar stock", "Bultos completos", 1, 1, 100000)
        if ok:
            self.guard(lambda: self.store.receive(i, n))

    def manage_catalog(self):
        if not self.catalog:
            self.notify("Catálogo no disponible en el modo de prueba en memoria.")
            return
        try:
            CatalogDialog(self.catalog, self).exec()
        except sqlite3.Error as e:
            self.notify("No se pudo abrir el catálogo: " + str(e))

    def export_backup(self):
        if not self.store.repository:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar copia SQLite", "PoStoreBaires-backup.sqlite", "SQLite (*.sqlite)")
        if path:
            try:
                self.store.repository.backup(path)
                self.notify("Copia de la base local guardada.")
            except Exception as e:
                self.notify(str(e))

    def settings(self):
        if SettingsDialog(self.store, self).exec() == QDialog.DialogCode.Accepted:
            self.customer.image_cache.clear()
            self.refresh()
            if self.store.config.customer_enabled:
                self.open_customer()
            else:
                self.customer.hide()

    def open_customer(self):
        cfg = self.store.config
        if not cfg.customer_enabled:
            self.notify("Activá la pantalla del cliente desde Ajustes.")
            return
        self.refresh_customer()
        screens = QApplication.screens()
        screen = screens[min(max(0, cfg.screen), len(screens)-1)]
        self.customer.showNormal()
        self.customer.windowHandle().setScreen(screen)
        self.customer.setGeometry(screen.availableGeometry())
        self.customer.showMaximized()

    def refresh_customer(self):
        if self.store.config.customer_enabled:
            self.customer.refresh(self.store, self.wallet_amount, self.result_sale)

    def clear_result(self):
        self.result_timer.stop()
        self.result_sale = None
        self.wallet_amount = None
        self.refresh_customer()

    def play_sound(self, kind, force=False):
        cfg = self.store.config
        if not force and not (cfg.scan_sound if kind == "scan" else cfg.cash_sound):
            return
        try:
            from PySide6.QtMultimedia import QSoundEffect
            if kind not in self.sounds:
                effect = QSoundEffect(self)
                effect.setSource(QUrl.fromLocalFile(str(ASSETS / f"{kind}.wav")))
                effect.setVolume(0.5)
                self.sounds[kind] = effect
            self.sounds[kind].play()
        except ImportError:
            self.notify("No está disponible el componente de sonido Qt.")

    def withdraw(self):
        text, ok = QInputDialog.getText(self, "Retiro", "Importe en efectivo")
        if ok:
            self.guard(lambda: self.store.withdraw(amount(text)))

    def open_turn(self):
        if self.store.opened:
            self.notify("Ya hay un turno abierto.")
            return
        text, ok = QInputDialog.getText(self, "Abrir turno", "Saldo inicial")
        if ok:
            self.guard(lambda: self.store.open_turn(amount(text)))

    def close_turn(self):
        if not self.store.opened or self.store.cart:
            self.notify("El turno está cerrado o hay una venta pendiente.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Arqueo y cierre")
        form = QFormLayout(dialog)
        fields = []
        for method, expected in zip(METHODS, self.store.expected()):
            field = QLineEdit("0")
            form.addRow(f"{method} · esperado {money(expected)}", field)
            fields.append(field)
        def save():
            try:
                self.store.close_turn([amount(w.text()) for w in fields])
                dialog.accept()
                self.refresh()
                self.show_closure(len(self.store.closures)-1)
            except ValueError as e:
                self.notify(str(e))
        form.addRow(button("Confirmar cierre", save, True))
        form.addRow(button("Volver", dialog.reject))
        dialog.exec()

    def show_closure(self, index):
        c = self.store.closures[index]
        rows = "".join(f"<tr><td>{escape(m)}</td><td>{money(e)}</td><td>{money(d)}</td><td>{money(x)}</td></tr>"
                       for m, e, d, x in zip(METHODS, c['expected'], c['declared'], c['differences']))
        self.text_dialog("Detalle del cierre", f"<h2>{escape(c['box'])} · {escape(c['cashier'])}</h2>"
                         f"<p>{escape(c['date'])}</p><table cellpadding='10'><tr><th>Medio</th><th>Esperado</th>"
                         f"<th>Declarado</th><th>Diferencia</th></tr>{rows}</table>")

    def closure_detail(self):
        i = self.closures_table.currentRow()
        if i >= 0:
            self.show_closure(i)

    def text_dialog(self, title, html):
        d = QDialog(self)
        d.setWindowTitle(f"PoStoreBaires · {title}")
        d.resize(760, 650)
        layout = QVBoxLayout(d)
        view = QTextBrowser()
        view.setHtml(html)
        layout.addWidget(view)
        layout.addWidget(button("Cerrar", d.accept))
        d.exec()

    def ticket(self):
        if not self.last_sale:
            self.notify("Todavía no hay ventas.")
            return
        s, cfg = self.last_sale, self.store.config
        lines = "\n".join(f"{q} × {name}\n{money(price*q)}" for name, q, price in s.lines)
        payments = "\n".join(f"{m}: {money(n)}" for m, n in zip(METHODS, s.payments) if n)
        result = f"Vuelto: {money(s.change)}" if s.received else ("Cobrado OK" if s.payments[1] == s.total else "")
        text = (f"{cfg.shop}\n{cfg.legal}\nTICKET INTERNO · NO FISCAL\n{s.date}\nVenta {s.number} · {s.box} · {s.cashier}\n"
                f"---------------------------\n{lines}\nTOTAL {money(s.total)}\n{payments}\n{result}\n¡Gracias por tu compra!")
        logo = (f'<img src="{escape(QUrl.fromLocalFile(cfg.logo).toString())}" width="140"><br>' if cfg.logo else "")
        self.text_dialog("Ticket · " + cfg.paper, "<p>Vista previa; impresión pendiente.</p>" + logo + "<pre>" + escape(text) + "</pre>")

    def help(self):
        self.text_dialog("Guía de uso", HELP)

    def closeEvent(self, event):
        if QMessageBox.question(self, "PoStoreBaires", "¿Cerrar PoStoreBaires? Los cambios ya están guardados en la base local." if self.store.repository else "Modo de prueba: se perderán los datos al cerrar. ¿Cerrar?") != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        self.customer.close()
        event.accept()


HELP = """
<h1>PoStoreBaires · Guía Beta 1.0</h1>
<h2>Inicio y lector</h2><p>El primer inicio tiene inventario vacío y turno cerrado. Cargá productos y abrí un turno en Arqueo con el efectivo inicial real. El lector USB debe emular teclado y enviar Enter.</p>
<h2>Cajas, perfiles y cajeros</h2><p>En Ajustes nombrá caja y cajero. Cerrá primero el turno para cambiarlos. Principal/Secundaria/IP y roles son ilustrativos: no conectan equipos ni restringen acciones todavía.</p>
<h2>Productos</h2><p>En Insumos creá o editá productos, costo, precio, categoría, foto o ilustración, mínimo y unidades por bulto. El stock se conserva en unidades: tres bultos de doce suman treinta y seis. El aviso de reposición aparece en la barra inferior al cobrar. No hay consulta por Internet.</p>
<h2>Ticket</h2><p>Ingresá comercio, razón social, logo y papel 58/80 mm. Último ticket muestra un comprobante interno no fiscal. La impresión térmica está pendiente.</p>
<h2>Pantalla del cliente</h2><p>Activala en Ajustes y elegí monitor. Seleccioná Solo QR, Solo alias o ambos. Cargá PNG/JPG o PDF; para PDF elegí la página. Qt convierte esa página a imagen y conserva proporciones. Revisá Vista previa. El QR/alias queda visible durante la compra.</p>
<h2>Pagar desde el celular</h2><p>El cliente escanea el QR o ingresa el alias en su app. Verifica titular e importe y paga. El alias no es un código escaneable. Un QR estático puede requerir que el cliente ingrese el importe: el POS no lo transmite a la app.</p>
<h2>Pagos mixtos</h2><p>En Cobrar distribuí los importes. Efectivo es dinero recibido. Cobrar por wallet asigna todo a wallet si aún no hay importe en ese medio. La pantalla muestra solo la parte wallet en pagos mixtos.</p>
<h2>Verificación</h2><p>Comprobá la acreditación en la cuenta del comercio y marcá la casilla antes de confirmar. Editar importes desmarca la verificación. No hay API ni confirmación automática.</p>
<h2>Resultado</h2><p>Se muestran total y medios; efectivo muestra vuelto. Wallet íntegra muestra Cobrado OK después de confirmar. A los doce segundos vuelve la bienvenida con los datos de pago.</p>
<h2>Sonidos</h2><p>Activá bip y caja registradora por separado en Ajustes. Los botones Probar permiten escucharlos. Los WAV son originales y están incluidos.</p>
<h2>Arqueo y relevo</h2><p>Registrá retiros de efectivo. Cerrá declarando lo contado/verificado por cada medio. Revisá diferencias por separado en el detalle. El saldo inicial y los retiros afectan solo efectivo. Lotes bancarios de tarjetas pendientes.</p>
<h2>Base local y copias</h2><p>Ventas, productos, stock, turnos, carrito y ajustes se guardan en SQLite al modificar. La base está en la carpeta de datos de la aplicación del usuario, fuera del portable. Consultá su ruta y exportá una copia desde Ajustes. No sincroniza cajas ni verifica permisos. No abrir la misma base desde dos sesiones: los conflictos se rechazan.</p>
<h2>Créditos</h2><p>Preciazo: Nulo y colaboradores de catdevnull/preciazo (https://github.com/catdevnull/preciazo). Referencia para los formatos del catálogo; no incluye código ni datos externos.</p>
<h2>Catálogo Preciazo / SEPA</h2><p>En Insumos abrí Catálogo de referencia e importá un SQLite antiguo de Preciazo o productos.csv SEPA. Para CSV ingresá la fecha real del dataset. Se reemplaza solo el catálogo externo. Buscá desde el código en el alta/edición; elegí explícitamente usar nombre o precio. No cambia costo ni stock. Se muestra fuente/fecha; las imágenes externas no se descargan y se conserva la ilustración por defecto. No se incluyen datos ni código de Preciazo.</p>
"""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PoStoreBaires")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PoStoreBaires")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    if "--smoke-test" in sys.argv:
        window = MainWindow(Store.demo())
    else:
        try:
            data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
            if "--data-dir" in sys.argv:
                data_dir = Path(sys.argv[sys.argv.index("--data-dir") + 1]).expanduser().resolve()
            repository = LocalStore(data_dir / "store.sqlite")
            window = MainWindow(repository.load())
            if repository.migration_backup:
                window.notify("Base convertida a pesos enteros. Copia anterior: " + str(repository.migration_backup))
            try:
                window.catalog = Catalog(data_dir / "reference.sqlite")
            except (sqlite3.Error, ValueError) as e:
                window.notify("Catálogo no disponible; alta manual habilitada: " + str(e))
        except Exception as e:
            QMessageBox.critical(None, "No se pudo abrir la base", str(e) + "\nNo se reinició ni reemplazó la base.")
            return 1
    window.show()
    if "--smoke-test" in sys.argv:
        window.closeEvent = lambda event: event.accept()
        window.add(0)
        assert window.store.total() == 850
        print("PoStoreBaires native startup smoke test passed", flush=True)
        QTimer.singleShot(200, app.quit)
    return app.exec()
