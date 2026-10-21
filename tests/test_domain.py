import unittest
from dataclasses import replace
from postorebaires.domain import Store, Product, amount

class Transactions(unittest.TestCase):
    def setUp(self):
        self.store = Store.demo()
        self.store.add(0)

    def test_exact_money(self):
        self.assertEqual(amount('0,29'), 29)
        self.assertEqual(amount('1200.50'), 120050)
        for invalid in ('', '-1', 'NaN', 'Infinity', '0.001', '1e3'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                amount(invalid)

    def test_cash_change_and_net_totals(self):
        s = self.store.complete([100000, 0, 0, 0])
        self.assertEqual(s.change, 15000)
        self.assertEqual(s.payments[0], 85000)
        self.assertEqual(s.received, 100000)
        self.assertEqual(self.store.products[0].stock, 35)

    def test_rejections_are_atomic(self):
        for payments, verified in (([0,85000,0,0],False), ([0,85001,0,0],True), ([84999,0,0,0],True)):
            with self.assertRaises(ValueError):
                self.store.complete(payments, verified)
            self.assertEqual(self.store.products[0].stock, 36)
            self.assertEqual(len(self.store.sales), 0)
            self.assertEqual(self.store.cart, {0:1})

    def test_wallet_mixed_and_duplicate(self):
        s = self.store.complete([20000,65000,0,0], True)
        self.assertEqual(sum(s.payments), s.total)
        with self.assertRaises(ValueError):
            self.store.complete([20000,65000,0,0], True)
        self.assertEqual(len(self.store.sales),1)

    def test_stock_rechecked_before_commit(self):
        self.store.products[0].stock = 0
        with self.assertRaises(ValueError):
            self.store.complete([85000,0,0,0])
        self.assertEqual(self.store.sales, [])

    def test_arqueo_and_new_turn(self):
        self.store.complete([20000,65000,0,0], True)
        self.store.withdraw(10000)
        expected = self.store.expected()
        result = self.store.close_turn(expected)
        self.assertEqual(result['differences'], [0,0,0,0])
        self.assertEqual(expected, [1010000,65000,0,0])
        self.store.open_turn(20000)
        self.assertEqual(self.store.expected(),[20000,0,0,0])

    def test_relevo_requires_close(self):
        self.store.cart.clear()
        cfg = replace(self.store.config, cashier='María')
        with self.assertRaises(ValueError): self.store.configure(cfg)
        self.store.close_turn(self.store.expected())
        self.store.configure(cfg)
        self.assertEqual(self.store.config.cashier,'María')

    def test_barcode_zeros_and_unique(self):
        self.store.cart.clear()
        p=Product('000123','Prueba','Productos varios',100,stock=1)
        self.store.save_product(p)
        self.store.scan('000123')
        self.assertEqual(self.store.total(),100)
        self.store.cart.clear()
        with self.assertRaises(ValueError): self.store.save_product(p)

    def test_wallet_config_requires_selected_data(self):
        cfg=replace(self.store.config, customer_enabled=True, wallet_view='QR y alias',alias='local.alias')
        with self.assertRaises(ValueError):self.store.configure(cfg)
        cfg=replace(cfg,wallet_view='Solo alias')
        self.store.configure(cfg)

if __name__ == '__main__': unittest.main()
