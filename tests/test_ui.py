from postorebaires.sqlite_utils import connect
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
from pathlib import Path
import unittest
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtGui import QPixmap, QColor, QPdfWriter, QPainter
from PySide6.QtCore import Qt
from postorebaires.ui import MainWindow, PaymentDialog, SettingsDialog, STYLE, load_image, ProductDialog

class NativeUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.app.setStyleSheet(STYLE)

    def setUp(self):
        self.window=MainWindow()
        self.window.add(0)

    def tearDown(self):
        self.window.result_timer.stop()
        self.window.customer.hide()
        self.window.hide()
        self.window.customer.deleteLater()
        self.window.deleteLater()
        self.app.processEvents()

    def test_native_payments_customer_alias_and_verify_reset(self):
        w=self.window
        w.store.config.customer_enabled=True
        w.store.config.wallet_view='Solo alias'
        w.store.config.alias='mi.comercio'
        w.refresh_customer()
        self.assertIn('mi.comercio',w.customer.alias_label.text())
        self.assertIn('850,00',w.customer.amount_label.text())
        d=PaymentDialog(w)
        d.fields[0].setText('0')
        d.fields[1].setText('850')
        d.complete()
        self.assertEqual(len(w.store.sales),0)
        d.verified.setChecked(True)
        d.fields[1].setText('300')
        self.assertFalse(d.verified.isChecked())
        self.assertIn('300,00',w.customer.amount_label.text())
        d.fields[1].setText('850')
        d.verified.setChecked(True)
        d.complete()
        self.assertEqual(len(w.store.sales),1)
        self.assertEqual(d.result(),QDialog.DialogCode.Accepted)
        self.assertIn('Cobrado OK',w.customer.summary.toPlainText())
        w.clear_result()
        self.assertIn('mi.comercio',w.customer.alias_label.text())

    def test_qr_image_and_pdf_page_conversion(self):
        with tempfile.TemporaryDirectory() as folder:
            image=Path(folder)/'qr.png'
            p=QPixmap(100,100);p.fill(QColor('black'));p.save(str(image))
            self.assertFalse(load_image(str(image)).isNull())
            cfg=self.window.store.config
            cfg.customer_enabled=True;cfg.wallet_view='QR y alias';cfg.alias='mi.alias';cfg.qr=str(image)
            self.window.refresh_customer()
            self.assertFalse(self.window.customer.qr_label.pixmap().isNull())
            pdf=Path(folder)/'qr.pdf'
            writer=QPdfWriter(str(pdf))
            painter=QPainter(writer)
            painter.fillRect(0,0,300,300,QColor('black'))
            writer.newPage()
            painter.drawText(100,100,'Second page')
            painter.end()
            self.assertFalse(load_image(str(pdf),1).isNull())
            with self.assertRaises(ValueError):load_image(str(pdf),2)

    def test_catalog_selection_is_explicit_and_does_not_import_stock_or_cost(self):
        from postorebaires.catalog import Catalog
        with tempfile.TemporaryDirectory() as folder:
            import sqlite3
            source=Path(folder)/'source.sqlite'
            with connect(source) as con:
                con.execute('CREATE TABLE precios(ean TEXT,name TEXT,precio_centavos INTEGER,fetched_at INTEGER)')
                con.execute("INSERT INTO precios VALUES ('00012345','Referencia',12550,1767225600)")
            self.window.catalog=Catalog(Path(folder)/'catalog.sqlite')
            self.window.catalog.import_file(source)
            d=ProductDialog(self.window.store,self.window)
            d.code.setText('00012345')
            d.price.setText('200');d.cost.setText('80');d.stock.setValue(7)
            d.lookup()
            self.assertEqual(d.price.text(),'200')
            d.apply_reference()
            self.assertEqual(d.name.text(),'Referencia')
            self.assertEqual(d.price.text(),'200')
            d.apply_reference_price()
            self.assertEqual(d.price.text(),'125.50')
            self.assertEqual(d.cost.text(),'80')
            self.assertEqual(d.stock.value(),7)
            d.deleteLater()

    def test_settings_and_tables_create(self):
        d=SettingsDialog(self.window.store,self.window)
        self.assertEqual(d.view.count(),3)
        self.assertEqual(self.window.tabs.count(),3)
        self.assertEqual(self.window.inventory.rowCount(),4)
        self.assertEqual(self.window.cart_table.rowCount(),1)
        d.deleteLater()

if __name__ == '__main__': unittest.main()
