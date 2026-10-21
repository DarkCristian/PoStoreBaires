from pathlib import Path
import json
import tempfile
import unittest
from postorebaires.domain import Store, money, amount
from postorebaires.storage import LocalStore, snapshot
from postorebaires.sqlite_utils import connect
from postorebaires.catalog import Catalog, reference_price

class WholePesos(unittest.TestCase):
    def legacy(self,path,fraction=False):
        repo=LocalStore(path)
        state=snapshot(Store.demo())
        state['products'][0]['price']=85001 if fraction else 85000
        state['products'][0]['cost']=50000
        state['products']=state['products'][:1]
        state['products'][0]['reference']={'price':85000}
        state['opening']=1000000;state['withdrawals']=10000
        state['sales']=[dict(number=1,date='test',box='Caja',cashier='Test',lines=[['Alfajor',2,85000]],payments=[170000,0,0,0],received=200000,change=30000,total=170000)]
        state['closures']=[dict(date='test',box='Caja',cashier='Test',expected=[1160000,0,0,0],declared=[1150000,0,0,0],differences=[-10000,0,0,0])]
        state['cart']={0:1}
        with repo.connection() as con:
            con.execute('INSERT INTO store_state VALUES (1,1,4,?)',(json.dumps(state),))
        return state

    def test_exact_migration_backup_and_no_second_conversion(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'store.sqlite';self.legacy(path)
            store=LocalStore(path).load()
            self.assertEqual((store.products[0].price,store.products[0].cost),(850,500))
            self.assertEqual(store.products[0].stock,36)
            self.assertEqual(store.cart,{0:1})
            self.assertEqual(store.products[0].reference['price'],850)
            self.assertEqual((store.opening,store.withdrawals),(10000,100))
            self.assertEqual(store.sales[0].lines,(('Alfajor',2,850),))
            self.assertEqual((store.sales[0].total,store.sales[0].received,store.sales[0].change),(1700,2000,300))
            self.assertEqual(store.closures[0]['differences'],[-100,0,0,0])
            backups=list(Path(folder).glob('*.before-pesos-*.sqlite'))
            self.assertEqual(len(backups),1)
            with connect(backups[0]) as con:
                version,payload=con.execute('SELECT schema_version,payload FROM store_state').fetchone()
                self.assertEqual(version,1)
                self.assertEqual(json.loads(payload)['products'][0]['price'],85000)
            self.assertEqual(LocalStore(path).load().products[0].price,850)
            self.assertEqual(len(list(Path(folder).glob('*.before-pesos-*.sqlite'))),1)
            with connect(path) as con:self.assertEqual(con.execute('SELECT schema_version FROM store_state').fetchone()[0],2)

    def test_fractional_legacy_is_not_modified_or_rounded(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'store.sqlite';self.legacy(path,True)
            with self.assertRaisesRegex(ValueError,'centavos'):LocalStore(path).load()
            with connect(path) as con:
                version,payload=con.execute('SELECT schema_version,payload FROM store_state').fetchone()
                self.assertEqual(version,1)
                self.assertEqual(json.loads(payload)['products'][0]['price'],85001)

    def test_catalog_cache_converts_once_fraction_has_no_applicable_price(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'refs.sqlite'
            catalog=Catalog(path)
            with connect(path) as con:
                con.execute('INSERT INTO refs VALUES (?,?,?,?,?,?,?,?,?)',('00012345','Test',12550,'2026-10-01','Test','','','',''))
                con.execute('PRAGMA user_version=0')
            self.assertIsNone(Catalog(path).lookup('00012345')[0].price)
            self.assertIsNone(reference_price('125,50'))
            self.assertEqual(reference_price('125.00'),125)
            self.assertEqual(money(1500),'$ 1.500')
            self.assertEqual(amount('1500'),1500)
