"""SPDX-License-Identifier: GPL-3.0-only
Copyright (C) 2026 Cristian Carroccio.

In-memory beta. Money uses integer cents; no external payment processing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

METHODS = ("Efectivo", "Wallet / transferencia", "Débito", "Crédito")
CATEGORIES = ("Limpieza", "Cigarrillos", "Golosinas", "Productos varios")

def amount(value: str) -> int:
    value = str(value).strip().replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
        raise ValueError("Ingresá un importe positivo con hasta dos decimales.")
    try:
        result = int(Decimal(value) * 100)
    except (InvalidOperation, ValueError):
        raise ValueError("Importe inválido.") from None
    if result > 900_000_000_000:
        raise ValueError("Importe fuera de rango.")
    return result

def money(value: int) -> str:
    sign = "−" if value < 0 else ""
    value = abs(value)
    return f"{sign}$ {value // 100:,}".replace(",", ".") + f",{value % 100:02d}"

def decimal_text(value: int) -> str:
    return f"{value // 100}.{value % 100:02d}"

@dataclass
class Product:
    code: str
    name: str
    category: str
    price: int
    cost: int = 0
    stock: int = 0
    pack: int = 1
    minimum: int = 5
    illustration: str = "box"
    photo: str = ""

@dataclass
class Config:
    shop: str = "Mi comercio"
    legal: str = "Razón social de ejemplo"
    box: str = "Caja 01"
    cashier: str = "Cajero de prueba"
    role: str = "Administrador"
    mode: str = "Principal"
    host: str = "192.168.1.10"
    paper: str = "80 mm"
    logo: str = ""
    customer_enabled: bool = False
    screen: int = 0
    wallet_view: str = "QR y alias"
    qr: str = ""
    qr_page: int = 0
    alias: str = ""
    wallet: str = "Mercado Pago"
    holder: str = ""
    scan_sound: bool = False
    cash_sound: bool = False

    def wallet_ready(self) -> bool:
        return ((self.wallet_view == "Solo QR" and bool(self.qr))
                or (self.wallet_view == "Solo alias" and bool(self.alias.strip()))
                or (self.wallet_view == "QR y alias" and bool(self.qr) and bool(self.alias.strip())))

@dataclass(frozen=True)
class Sale:
    number: int
    date: str
    box: str
    cashier: str
    lines: tuple
    payments: tuple
    received: int
    change: int
    total: int

@dataclass
class Store:
    products: list = field(default_factory=list)
    config: Config = field(default_factory=Config)
    cart: dict = field(default_factory=dict)
    sales: list = field(default_factory=list)
    closures: list = field(default_factory=list)
    opened: bool = True
    opening: int = 1_000_000
    withdrawals: int = 0
    turn_start: int = 0

    @classmethod
    def demo(cls):
        return cls(products=[
            Product(…5491 tokens truncated…d><td>{money(store.products[i].price*q)}</td></tr>"
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
            field = QLineEdit(decimal_text(parent.store.total()) if i == 0 else "0.00")
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
                field.setText(decimal_text(self.main.store.total()) if i == 1 else "0.00")
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
    def __init__(self, store=None):
        super().__init__()
        self.store = store or Store.demo()
        self.last_sale = self.result_sale = None
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
        head.addWidget(label(f"{__version__} · Datos temporales"))
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
        self.statusBar().showMessage("Beta local: datos temporales, sin sincronización ni impresión fiscal.")
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
        left.addWidget(label("Escaneá un código. Ejemplos: 779001 · 779002 · 779003 · 779004"))
        row = QHBoxLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Código de barras + Enter")
        self.scan_input.returnPressed.connect(self.scan)
        row.addWidget(self.scan_input)
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
        for i in range(4):
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

    def scan(self):
        code = self.scan_input.text().strip()
        if not code:
            return
        for i, p in enumerate(self.store.products):
            if p.code == code:
                self.add(i)
                return
        self.product(code=code)

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
            self.store.cart[index] -= 1
            if self.store.cart[index] == 0:
                del self.store.cart[index]
            self.refresh()

    def remove(self):
        index = self.cart_index()
        if index is not None:
            del self.store.cart[index]
            self.refresh()

    def empty_cart(self):
        if self.store.cart and QMessageBox.question(self, "Venta", "¿Vaciar esta venta?") == QMessageBox.StandardButton.Yes:
            self.store.cart.clear()
            self.refresh()

    def pay(self):
        if not self.store.opened or not self.store.cart:
            self.notify("Agregá productos en un turno abierto.")
            return
        self.clear_result()
        PaymentDialog(self).exec()

    def product(self, index=None, code=""):
        if self.store.cart:
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
            self.store.products[i].stock += n*self.store.products[i].pack
            self.refresh()

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
            field = QLineEdit("0.00")
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
        if QMessageBox.question(self, "PoStoreBaires", "Al cerrar se pierde toda la sesión, productos y ajustes. ¿Cerrar?") != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        self.customer.close()
        event.accept()


HELP = """
<h1>PoStoreBaires · Guía Beta 1.0</h1>
<h2>Inicio y lector</h2><p>Turno de ejemplo con $10.000 iniciales. Códigos 779001–779004. El lector USB debe emular teclado y enviar Enter.</p>
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
<h2>Datos temporales</h2><p>Esta beta Python/Qt conserva datos en memoria. Cerrar pierde ventas, productos y ajustes. No usa una base de datos, no sincroniza cajas ni verifica permisos. No usar en producción.</p>
"""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PoStoreBaires")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PoStoreBaires")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    if "--smoke-test" in sys.argv:
        window.closeEvent = lambda event: event.accept()
        window.add(0)
        assert window.store.total() == 85000
        print("PoStoreBaires native startup smoke test passed", flush=True)
        QTimer.singleShot(200, app.quit)
    return app.exec()
