from pathlib import Path
from threading import Event
import csv
import hashlib
import sqlite3
import tempfile
import unittest
from postorebaires.catalog import Catalog,Cancelled

class CatalogImport(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.catalog=Catalog(self.root/'index.sqlite')
    def tearDown(self):self.temp.cleanup()
    def legacy(self):
        path=self.root/'legacy.sqlite'
        with sqlite3.connect(path) as con:
            con.execute('CREATE TABLE precios(ean TEXT,name TEXT,precio_centavos INTEGER,fetched_at INTEGER,url TEXT,image_url TEXT)')
            con.executemany('INSERT INTO precios VALUES (?,?,?,?,?,?)',[
                ('00012345','Producto de prueba',12550,1767225600,'https://example.invalid/item','https://example.invalid/image.jpg'),
                ('00012345','Producto reciente',13000,1767312000,'https://example.invalid/item','file:///private.png'),
                ('123','Interno',100,1767225600,'','')])
        return path
    def sepa(self,rows):
        path=self.root/'productos.csv'
        with path.open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['id_producto','productos_ean','productos_descripcion','productos_precio_lista','productos_precio_referencia','id_comercio','id_bandera','id_sucursal'],delimiter=';')
            writer.writeheader();writer.writerows(rows)
        return path

    def test_legacy_readonly_dates_cents_and_leading_zeros(self):
        path=self.legacy();before=hashlib.sha256(path.read_bytes()).digest()
        stats=self.catalog.import_file(path)
        refs=self.catalog.lookup('00012345')
        self.assertEqual(stats,{'imported':2,'skipped':1})
        self.assertEqual(refs[0].price,13000)
        self.assertEqual(refs[0].observed,'2026-01-02')
        self.assertEqual(refs[1].image_url,'https://example.invalid/image.jpg')
        self.assertEqual(refs[0].image_url,'')
        self.assertEqual(before,hashlib.sha256(path.read_bytes()).digest())

    def test_sepa_flag_and_package_price_not_reference_unit(self):
        row={'id_producto':'00012345','productos_ean':'1','productos_descripcion':'Presentación de prueba','productos_precio_lista':'100,50','productos_precio_referencia':'999','id_comercio':'1','id_bandera':'2','id_sucursal':'3'}
        path=self.sepa([row,dict(row,id_producto='00099999',productos_ean='0')])
        stats=self.catalog.import_file(path,'SEPA prueba','2026-10-01')
        self.assertEqual(stats,{'imported':1,'skipped':1})
        refs=self.catalog.lookup('00012345')
        self.assertEqual(refs[0].price,10050)
        self.assertIn('1/2/3',refs[0].source)
        self.assertEqual(self.catalog.lookup('00099999'),[])

    def test_csv_requires_actual_dataset_date(self):
        path=self.sepa([])
        with self.assertRaises(ValueError):self.catalog.import_file(path)

    def test_bad_import_keeps_previous_catalog(self):
        self.catalog.import_file(self.legacy())
        bad=self.root/'bad.csv';bad.write_text('wrong;schema\n1;2')
        with self.assertRaises(ValueError):self.catalog.import_file(bad,observed='2026-10-01')
        self.assertEqual(self.catalog.count(),2)

    def test_cancelled_import_keeps_previous_catalog(self):
        path=self.legacy();self.catalog.import_file(path)
        cancel=Event();cancel.set()
        with self.assertRaises(Cancelled):self.catalog.import_file(path,cancel=cancel)
        self.assertEqual(self.catalog.count(),2)

    def test_views_are_not_treated_as_source_tables(self):
        path=self.root/'view.sqlite'
        with sqlite3.connect(path) as c:c.execute("CREATE VIEW precios AS SELECT 'bad' AS ean")
        with self.assertRaises(ValueError):self.catalog.import_file(path)

    def test_no_match_is_not_a_new_product_or_synthetic_price(self):
        self.catalog.import_file(self.legacy())
        self.assertEqual(self.catalog.lookup('7791234567890'),[])
        with self.assertRaises(ValueError):self.catalog.lookup("' OR 1=1 --")

    def test_empty_or_internal_only_does_not_erase_catalog(self):
        self.catalog.import_file(self.legacy())
        path=self.sepa([{'id_producto':'00012345','productos_ean':'0','productos_descripcion':'Interno','productos_precio_lista':'1'}])
        with self.assertRaises(ValueError):self.catalog.import_file(path,observed='2026-10-01')
        self.assertEqual(self.catalog.count(),2)

if __name__=='__main__':unittest.main()
