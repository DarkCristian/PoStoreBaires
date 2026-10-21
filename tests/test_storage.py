from postorebaires.sqlite_utils import connect
from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from postorebaires.storage import LocalStore
from postorebaires.domain import Product

class Persistence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'store.sqlite'
        self.repo=LocalStore(self.path)
        self.store=self.repo.load()
        self.store.save_product(Product('00012345','Prueba','Productos varios',10000,5000,10,2))
        self.store.open_turn(20000)
    def tearDown(self):self.temp.cleanup()

    def test_reopen_cart_sale_stock_and_turns(self):
        self.store.add(0)
        self.store=LocalStore(self.path).load()
        self.assertEqual(self.store.cart,{0:1})
        self.store.complete([15000,0,0,0])
        self.store.withdraw(5000)
        self.store.close_turn(self.store.expected())
        self.store.configure(replace(self.store.config,cashier='María',alias='mi.alias',wallet_view='Solo alias',customer_enabled=True))
        reopened=LocalStore(self.path).load()
        self.assertEqual(reopened.products[0].stock,9)
        self.assertEqual(reopened.sales[0].change,5000)
        self.assertFalse(reopened.opened)
        self.assertEqual(reopened.closures[0]['differences'],[0,0,0,0])
        self.assertEqual(reopened.config.alias,'mi.alias')
        self.assertEqual(reopened.config.cashier,'María')
        self.assertEqual(reopened.products[0].code,'00012345')

    def test_failed_disk_save_rolls_back_entire_sale(self):
        self.store.add(0)
        with patch.object(self.repo,'save',side_effect=ValueError('Disco no disponible')):
            with self.assertRaises(ValueError):self.store.complete([10000,0,0,0])
        self.assertEqual(self.store.products[0].stock,10)
        self.assertEqual(self.store.cart,{0:1})
        self.assertEqual(self.store.sales,[])
        self.assertEqual(LocalStore(self.path).load().sales,[])

    def test_stale_session_cannot_overwrite_stock(self):
        other=LocalStore(self.path).load()
        self.store.receive(0,1)
        with self.assertRaises(ValueError):other.add(0)
        self.assertEqual(other.cart,{})
        self.assertEqual(LocalStore(self.path).load().products[0].stock,12)

    def test_quantity_removal_and_receipts_survive(self):
        self.store.add(0);self.store.change_quantity(0,1)
        self.assertEqual(LocalStore(self.path).load().cart,{0:2})
        self.store.remove(0)
        self.assertEqual(LocalStore(self.path).load().cart,{})
        self.store.add(0);self.store.clear()
        self.assertEqual(LocalStore(self.path).load().cart,{})

    def test_backup_can_be_opened_independently(self):
        self.store.add(0);self.store.complete([10000,0,0,0])
        dest=Path(self.temp.name)/'backup.sqlite'
        self.repo.backup(dest)
        restored=LocalStore(dest).load()
        self.assertEqual(restored.sales[0].total,10000)
        self.assertEqual(restored.products[0].stock,9)

    def test_corrupt_payload_does_not_reset_data(self):
        with connect(self.path) as c:c.execute("UPDATE store_state SET payload='not json'")
        with self.assertRaises(ValueError):LocalStore(self.path).load()
        with connect(self.path) as c:self.assertEqual(c.execute('SELECT payload FROM store_state').fetchone()[0],'not json')

    def test_first_database_is_empty_not_a_demo(self):
        empty=LocalStore(Path(self.temp.name)/'empty.sqlite').load()
        self.assertEqual(empty.products,[])
        self.assertFalse(empty.opened)
        self.assertEqual(empty.opening,0)

if __name__=='__main__':unittest.main()
