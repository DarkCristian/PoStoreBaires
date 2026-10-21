"""SPDX-License-Identifier: GPL-3.0-only. Local single-PC transactional state."""
from dataclasses import asdict, fields, is_dataclass
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
from .domain import Store, Config, Product, Sale

SCHEMA = 1

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

class LocalStore:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.revision = None
        with self.connection() as con:
            con.execute('CREATE TABLE IF NOT EXISTS store_state (id INTEGER PRIMARY KEY CHECK(id=1), schema_version INTEGER NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL)')

    def connection(self):
        con=sqlite3.connect(self.path,timeout=5)
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA synchronous=FULL')
        return con

    def load(self):
        try:
            with self.connection() as con:
                row=con.execute('SELECT schema_version,revision,payload FROM store_state WHERE id=1').fetchone()
            store=Store(products=[], opened=False, opening=0)
            if row:
                if row[0]!=SCHEMA:raise ValueError('Versión de base no compatible. No se modificó el archivo.')
                restore(store,json.loads(row[2]));self.revision=row[1]
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
                    cursor=con.execute('UPDATE store_state SET payload=?,revision=revision+1 WHERE id=1 AND revision=?',(payload,self.revision))
                    if cursor.rowcount!=1:raise ValueError('Otra sesión modificó esta base. Cerrá y volvé a abrir antes de continuar.')
                    revision=self.revision+1
            self.revision=revision
        except sqlite3.Error as e:
            raise ValueError('No se guardó la operación en disco: '+str(e)) from e

    def backup(self, destination):
        dest=Path(destination).resolve()
        if dest==self.path:raise ValueError('Elegí otro archivo para la copia.')
        with self.connection() as source, sqlite3.connect(dest) as target:
            source.backup(target)
