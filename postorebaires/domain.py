"""SPDX-License-Identifier: GPL-3.0-only
Copyright (C) 2026 Cristian Carroccio.

Local state. Money uses integer cents; no external payment processing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from functools import wraps

def durable(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.repository is None:
            return method(self, *args, **kwargs)
        from .storage import snapshot, restore
        before = snapshot(self)
        try:
            result = method(self, *args, **kwargs)
            self.repository.save(self)
            return result
        except Exception:
            restore(self, before)
            raise
    return wrapped


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
    reference: dict = field(default_factory=dict)

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
    repository: object = field(default=None, repr=False, compare=False)

    @classmethod
    def demo(cls):
        return cls(products=[
            Product("779001", "Alfajor chocolate", "Golosinas", 85000, 50000, 36, 12, 8, "chocolate"),
            Product("779002", "Detergente 750 ml", "Limpieza", 190000, 120000, 18, 6, 6, "cleaning"),
            Product("779003", "Cigarrillos x20", "Cigarrillos", 420000, 350000, 7, 10, 8, "cigarettes"),
            Product("779004", "Agua mineral 500 ml", "Productos varios", 120000, 70000, 24, 6, 6, "water"),
        ])

    def total(self):
        return sum(self.products[i].price * q for i, q in self.cart.items())

    @durable
    def add(self, index):
        if not self.opened:
            raise ValueError("Abrí un turno desde Arqueo.")
        p = self.products[index]
        q = self.cart.get(index, 0)
        if q >= p.stock:
            raise ValueError("Stock insuficiente.")
        self.cart[index] = q + 1

    def scan(self, code):
        for i, p in enumerate(self.products):
            if p.code == code:
                self.add(i)
                return i
        raise KeyError(code)

    @durable
    def save_product(self, product, index=None):
        if self.cart:
            raise ValueError("Terminá o vaciá la venta antes de editar productos.")
        if not product.name.strip() or not product.code.strip():
            raise ValueError("Completá nombre y código.")
        if any(p.code == product.code and i != index for i, p in enumerate(self.products)):
            raise ValueError("Código duplicado.")
        for value in (product.price, product.cost, product.stock, product.minimum):
            if type(value) is not int or value < 0:
                raise ValueError("Precio, costo y existencias deben ser válidos.")
        if type(product.pack) is not int or product.pack < 1:
            raise ValueError("El bulto debe contener al menos una unidad.")
        if index is None:
            self.products.append(product)
        else:
            self.products[index] = product

    @durable
    def complete(self, payments, verified=False):
        if not self.opened or not self.cart:
            raise ValueError("La venta está vacía o el turno está cerrado.")
        if len(payments) != 4 or any(type(n) is not int or n < 0 or n > 900_000_000_000 for n in payments):
            raise ValueError("Importes inválidos.")
        due = self.total()
        change = sum(payments) - due
        if change < 0:
            raise ValueError("El pago es insuficiente.")
        if change > payments[0]:
            raise ValueError("El excedente debe provenir del efectivo.")
        if payments[1] and not verified:
            raise ValueError("Verificá la acreditación wallet en la cuenta del comercio.")
        lines = []
        for i, q in self.cart.items():
            p = self.products[i]
            if type(q) is not int or q < 1 or q > p.stock:
                raise ValueError(f"Stock o cantidad inválida: {p.name}")
            lines.append((p.name, q, p.price))
        net = list(payments)
        net[0] -= change
        sale = Sale(len(self.sales) + 1, datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S"),
                    self.config.box, self.config.cashier, tuple(lines), tuple(net), payments[0], change, due)
        for i, q in self.cart.items():
            self.products[i].stock -= q
        self.sales.append(sale)
        self.cart.clear()
        return sale

    def totals(self):
        return [sum(s.payments[i] for s in self.sales[self.turn_start:]) for i in range(4)]

    def expected(self):
        totals = self.totals()
        totals[0] += self.opening - self.withdrawals
        return totals

    @durable
    def withdraw(self, value):
        if not self.opened or value <= 0 or value > self.expected()[0]:
            raise ValueError("Retiro inválido o superior al efectivo esperado.")
        self.withdrawals += value

    @durable
    def close_turn(self, declared):
        if not self.opened or self.cart:
            raise ValueError("El turno está cerrado o hay una venta pendiente.")
        if len(declared) != 4 or any(type(n) is not int or n < 0 for n in declared):
            raise ValueError("Revisá los importes declarados.")
        expected = self.expected()
        result = {"date": datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S"),
                  "box": self.config.box, "cashier": self.config.cashier,
                  "expected": expected, "declared": list(declared),
                  "differences": [d-e for d, e in zip(declared, expected)]}
        self.closures.append(result)
        self.turn_start = len(self.sales)
        self.opening = self.withdrawals = 0
        self.opened = False
        return result

    @durable
    def open_turn(self, value):
        if self.opened:
            raise ValueError("Ya hay un turno abierto.")
        if type(value) is not int or value < 0:
            raise ValueError("Saldo inicial inválido.")
        self.opening = value
        self.opened = True

    @durable
    def configure(self, cfg):
        if not cfg.shop.strip() or not cfg.box.strip() or not cfg.cashier.strip():
            raise ValueError("Completá comercio, caja y cajero.")
        if self.opened and (cfg.box != self.config.box or cfg.cashier != self.config.cashier):
            raise ValueError("Cerrá el turno antes de cambiar caja o cajero.")
        if cfg.customer_enabled and not cfg.wallet_ready():
            raise ValueError("Completá QR, alias o ambos según la opción elegida.")
        self.config = cfg

    @durable
    def change_quantity(self, index, delta):
        if index not in self.cart:raise ValueError("Producto no incluido en la venta.")
        quantity=self.cart[index]+delta
        if quantity>self.products[index].stock:raise ValueError("Stock insuficiente.")
        if quantity<=0:del self.cart[index]
        else:self.cart[index]=quantity

    @durable
    def remove(self,index):
        self.cart.pop(index,None)

    @durable
    def clear(self):
        self.cart.clear()

    @durable
    def receive(self,index,packs):
        if type(packs) is not int or packs<1:raise ValueError("Cantidad de bultos inválida.")
        self.products[index].stock+=packs*self.products[index].pack
