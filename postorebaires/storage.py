"""SPDX-License-Identifier: GPL-3.0-only. Local single-PC transactional state."""
from dataclasses import asdict, fields, is_dataclass
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
from .domain import Store, Config, Product, Sale
from .sqlite_utils import connect
from contextlib import contextmanager

SCHEMA = 2

def snapshot(store):
    return {f.name: (asdict(getattr(store,f.name)) if is_dataclass(getattr(store,f.name)) else
                     [asdict(x) if is_dataclass(x) else deepcopy(x) for x in getattr(store,f.name)] if isinstance(getattr(store,f.name),list) else
                     deepcopy(getattr(store,f.name))) for f in fields(Store) if f.name != 'repository'}

def restore(store, data):
    store.products = [Product(**p) for p in data['products']]
    store.config = Config(**data['config'])
    store.cart = {int(k): v for k, v in data['cart'].items()}
    store.sales = [Sale(**dict(s, lines=tuple(tuple(x) for x in s['lines']), payments=tuple(s['payments']))) for s in data['sales']]
    for name in ('closures','opened','opening','withdrawals','turn_start'):
        setattr(store,name,data[name])

def pesos_from_legacy(data):
    """Convert schema 1 cents exactly; never round commercial records."""
    data = deepcopy(data)
    def convert(value):
        if type(value) is not int or value % 100:
            raise ValueError("La base anterior contiene importes con centavos. No se convirtió ni redondeó. Revisá esos importes con beta.2 antes de migrar a pesos enteros.")
        return value // 100
    def reference(ref):
        if ref.get('price') is not None:
            value = ref['price']
            ref['price'] = value // 100 if type(value) is int and value % 100 == 0 else None
    for product in data['products']:
        for key in ('price', 'cost'):product[key] = convert(product[key])
        reference(product.get('reference', {}))
    for sale in data['sales']:
        for key in ('received', 'change', 'total'):sale[key] = convert(sale[key])
        sale['payments'] = [convert(v) for v in sale['payments']]
        sale['lines'] = [[name, qty, convert(price)] for name, qty, price in sale['lines']]
    for closure in data['closures']:
        for key in ('expected', 'declared', 'differences'):
            closure[key] = [convert(v) for v in closure[key]]
    for key in ('opening', 'withdrawals'):data[key] = convert(data[key])
    return data

class LocalStore:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.revision = None
        self.migration_backup = None
        with self.connection() as con:
            con.execute('CREATE TABLE IF NOT EXISTS store_state (id INTEGER PRIMARY KEY CHECK(id=1), schema_version INTEGER NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL)')

    @contextmanager
    def connection(self):
        with connect(self.path,timeout=5) as con:
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA synchronous=FULL')
            yield con

    def load(self):
        try:
            with self.connection() as con:
                row=con.execute('SELECT schema_version,revision,payload FROM store_state WHERE id=1').fetchone()
            store=Store(products=[], opened=False, opening=0)
            if row:
                data = json.loads(row[2])
                if row[0] == 1:
                    data = pesos_from_legacy(data)
                    restore(store, data)
                    from uuid import uuid4
                    backup = self.path.with_name(self.path.name + '.before-pesos-' + uuid4().hex + '.sqlite')
                    self.backup(backup)
                    with self.connection() as con:
                        cursor = con.execute('UPDATE store_state SET schema_version=?,revision=revision+1,payload=? WHERE id=1 AND schema_version=1 AND revision=?',
                                             (SCHEMA,json.dumps(data,ensure_ascii=False,allow_nan=False),row[1]))
                        if cursor.rowcount != 1:raise ValueError('La base cambió durante la migración. Volvé a abrirla.')
                    self.revision = row[1] + 1
                    self.migration_backup = backup
                elif row[0] == SCHEMA:
                    restore(store, data)
                    self.revision = row[1]
                else:
                    raise ValueError('Versión de base no compatible. No se modificó el archivo.')
            store.repository=self
            if not row:self.save(store)
            return store
        except (sqlite3.Error,KeyError,TypeError,json.JSONDecodeError) as e:
            raise ValueError('No se pudo abrir la base local. No se reinició ni reemplazó: '+str(e)) from e

    def save(self, store):
        payload=json.dumps(snapshot(store),ensure_ascii=False,allow_nan=False)
        try:
            with self.connection() as con:
                if self.revision is None:
                    con.execute('INSERT INTO store_state VALUES (1,?,?,?)',(SCHEMA,1,payload))
                    revision=1
                else:
                    cursor=con.execute('UPDATE store_state SET payload=?,revision=revision+1 WHERE id=1 AND schema_version=2 AND revision=?',(payload,self.revision))
                    if cursor.rowcount!=1:raise ValueError('Otra sesión modificó esta base. Cerrá y volvé a abrir antes de continuar.')
                    revision=self.revision+1
            self.revision=revision
        except sqlite3.Error as e:
            raise ValueError('No se guardó la operación en disco: '+str(e)) from e

    def backup(self, destination):
        dest=Path(destination).resolve()
        if dest==self.path:raise ValueError('Elegí otro archivo para la copia.')
        with self.connection() as source, connect(dest) as target:
            source.backup(target)
