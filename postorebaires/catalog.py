"""SPDX-License-Identifier: GPL-3.0-only.
Independent local-file adapter; no upstream code or datasets are bundled.
"""
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from pathlib import Path
import csv
import re
import sqlite3
from decimal import Decimal, InvalidOperation
from .sqlite_utils import connect

UPSTREAM = 'https://github.com/catdevnull/preciazo'

@dataclass(frozen=True)
class Reference:
    ean: str
    name: str
    price: int | None
    observed: str
    source: str
    url: str = ''
    image_url: str = ''
    brand: str = ''
    presentation: str = ''

    @property
    def stale(self):
        return not self.observed or (date.today()-date.fromisoformat(self.observed[:10])).days>30

class Cancelled(ValueError): pass

def barcode(value):
    text=str(value or '').strip()
    if not re.fullmatch(r'(?:\d{8}|\d{12}|\d{13}|\d{14})',text):
        raise ValueError('El catálogo requiere EAN/UPC/GTIN de 8, 12, 13 o 14 dígitos.')
    return text

def observation(value):
    text=str(value or '').strip()
    if not text:return ''
    if re.fullmatch(r'\d+(?:\.0)?',text):
        timestamp=float(text)
        if timestamp>1e12:timestamp/=1000
        if not 0<=timestamp<=4102444800:raise ValueError('Fecha fuera de rango')
        return datetime.fromtimestamp(timestamp,timezone.utc).date().isoformat()
    return date.fromisoformat(text[:10]).isoformat()

def public_url(value):
    text=str(value or '').strip()
    # Store a reference only; no network fetch and no file/HTML loading.
    return text if text.startswith('https://') else ''

def reference_price(value):
    try:
        price = Decimal(str(value).strip().replace(',', '.'))
        if not price.is_finite() or not 0 < price <= 9_000_000_000:
            raise ValueError('Precio inválido')
        return int(price) if price == price.to_integral_value() else None
    except InvalidOperation as e:
        raise ValueError('Precio inválido') from e

class Catalog:
    def __init__(self,path):
        self.path=Path(path).resolve()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with connect(self.path) as con:
            con.execute('CREATE TABLE IF NOT EXISTS refs (ean TEXT NOT NULL,name TEXT NOT NULL,price INTEGER,observed TEXT NOT NULL,source TEXT NOT NULL,url TEXT NOT NULL,image_url TEXT NOT NULL,brand TEXT NOT NULL,presentation TEXT NOT NULL)')
            con.execute('CREATE INDEX IF NOT EXISTS refs_ean ON refs(ean,observed)')
            version = con.execute('PRAGMA user_version').fetchone()[0]
            if version == 0:
                con.execute('UPDATE refs SET price=CASE WHEN price % 100 = 0 THEN price / 100 ELSE NULL END WHERE price IS NOT NULL')
                con.execute('PRAGMA user_version=2')
            elif version != 2:
                raise ValueError('Versión de catálogo no compatible.')

    def count(self):
        with connect(self.path) as con:
            return con.execute('SELECT count(*) FROM refs').fetchone()[0]

    def lookup(self,ean):
        ean=barcode(ean)
        with connect(self.path) as con:
            rows=con.execute('SELECT * FROM refs WHERE ean=? ORDER BY observed DESC, price IS NULL, price ASC LIMIT 50',(ean,)).fetchall()
        return [Reference(*r) for r in rows]

    def import_file(self,path,source='Preciazo / SEPA · archivo local',observed='',cancel=None,progress=None):
        path=Path(path).resolve()
        if path==self.path:raise ValueError('No selecciones el índice del propio catálogo como fuente.')
        source=source.strip()
        if not source:raise ValueError('Ingresá el nombre de la fuente.')
        sqlite=path.suffix.lower() in ('.db','.sqlite','.sqlite3')
        if not sqlite and not observed:raise ValueError('Indicá la fecha real del dataset SEPA (AAAA-MM-DD).')
        observed=observation(observed)
        iterator=self._legacy(path,source) if sqlite else self._sepa(path,source,observed)
        imported=skipped=0
        with connect(self.path,timeout=5) as con:
            con.execute('BEGIN IMMEDIATE')
            con.execute('CREATE TEMP TABLE incoming AS SELECT * FROM refs WHERE 0')
            for record in iterator:
                if cancel and cancel.is_set():raise Cancelled('Importación cancelada; el catálogo anterior se conserva.')
                if record is None:
                    skipped+=1
                else:
                    con.execute('INSERT INTO incoming VALUES (?,?,?,?,?,?,?,?,?)',tuple(asdict(record).values()))
                    imported+=1
                if (imported+skipped)%1000==0 and progress:progress(imported,skipped)
            if cancel and cancel.is_set():raise Cancelled('Importación cancelada; el catálogo anterior se conserva.')
            if imported==0:raise ValueError('No se encontraron referencias válidas. El catálogo anterior se conserva.')
            # Only the reference index is replaced; commerce data is separate.
            con.execute('DELETE FROM refs')
            con.execute('INSERT INTO refs SELECT * FROM incoming')
        return {'imported':imported,'skipped':skipped}

    def _legacy(self,path,source):
        con=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=3)
        try:
            con.execute('PRAGMA query_only=ON')
            con.execute('PRAGMA trusted_schema=OFF')
            schema=con.execute("SELECT type FROM sqlite_master WHERE name='precios'").fetchone()
            if not schema or schema[0]!='table':raise ValueError('El SQLite no tiene la tabla precios compatible con Preciazo antiguo.')
            columns={r[1] for r in con.execute('PRAGMA table_info(precios)')}
            required={'ean','name','precio_centavos','fetched_at'}
            if not required<=columns:raise ValueError('Faltan columnas del formato Preciazo antiguo.')
            extra=[c if c in columns else "''" for c in ('url','image_url')]
            query='SELECT ean,name,precio_centavos,fetched_at,'+','.join(extra)+' FROM precios'
            for ean,name,price,seen,url,image in con.execute(query):
                try:
                    ean=barcode(ean)
                    if not name or not str(name).strip():raise ValueError('Sin nombre')
                    if price is not None and (type(price) is not int or not 0<price<=900_000_000_000):raise ValueError('Precio inválido')
                    yield Reference(ean,str(name).strip(),price // 100 if price is not None and price % 100 == 0 else None,observation(seen),source,public_url(url),public_url(image))
                except (ValueError,TypeError,OverflowError):yield None
        finally:con.close()

    def _sepa(self,path,source,observed):
        with path.open('r',encoding='utf-8-sig',newline='') as handle:
            sample=handle.read(8192);handle.seek(0)
            if not sample.strip():raise ValueError('El CSV está vacío; se conserva el catálogo anterior.')
            delimiter=';' if sample.splitlines()[0].count(';')>sample.splitlines()[0].count(',') else ','
            reader=csv.DictReader(handle,delimiter=delimiter)
            required={'id_producto','productos_ean','productos_descripcion','productos_precio_lista'}
            if not reader.fieldnames or not required<=set(reader.fieldnames):raise ValueError('El CSV no tiene las columnas SEPA requeridas.')
            for row in reader:
                try:
                    # productos_ean is a flag, NOT the barcode. Internal IDs are skipped.
                    if str(row['productos_ean']).strip()!='1':raise ValueError('ID interno')
                    ean=barcode(row['id_producto'])
                    name=(row['productos_descripcion'] or '').strip()
                    if not name:raise ValueError('Sin descripción')
                    # precio_referencia is per reference unit, not the package price.
                    price=reference_price(row['productos_precio_lista'])
                    branch='/'.join(str(row.get(k,'')).strip() for k in ('id_comercio','id_bandera','id_sucursal'))
                    presentation=' '.join(str(row.get(k,'') or '').strip() for k in ('productos_cantidad_presentacion','productos_unidad_medida_presentacion')).strip()
                    yield Reference(ean,name,price,observed,source+' · '+branch,brand=str(row.get('productos_marca','') or ''),presentation=presentation)
                except (ValueError,TypeError):yield None
