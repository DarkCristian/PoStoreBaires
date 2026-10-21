"""SPDX-License-Identifier: GPL-3.0-only. Offline catalog import UI."""
from datetime import date
from threading import Event
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QLabel,QPushButton,QFileDialog,QProgressBar
from .catalog import Catalog

class ImportWorker(QThread):
    done=Signal(dict)
    failed=Signal(str)
    progress=Signal(int,int)
    def __init__(self,catalog,path,source,observed,parent):
        super().__init__(parent)
        self.catalog,self.path,self.source,self.observed=catalog,path,source,observed
        self.cancel=Event()
    def run(self):
        try:
            result=self.catalog.import_file(self.path,self.source,self.observed,self.cancel,self.progress.emit)
            self.done.emit(result)
        except Exception as e:self.failed.emit(str(e))

class CatalogDialog(QDialog):
    def __init__(self,catalog,parent):
        super().__init__(parent)
        self.catalog=catalog;self.worker=None;self.path=''
        self.setWindowTitle('PoStoreBaires · Catálogo de referencia')
        self.resize(700,420)
        layout=QVBoxLayout(self)
        intro=QLabel('Importa un SQLite antiguo de Preciazo o productos.csv de SEPA.\nReemplaza solo el catálogo de referencia; nunca ventas, precios propios o stock.\nPrecios fraccionarios: se conserva el producto sin precio entero aplicable.\nEl paquete no incluye datos externos ni realiza descargas automáticas.')
        intro.setWordWrap(True);layout.addWidget(intro)
        self.status=QLabel(f'Referencias disponibles: {catalog.count()}');layout.addWidget(self.status)
        form=QFormLayout()
        self.file=QLineEdit();self.file.setReadOnly(True)
        self.source=QLineEdit('Preciazo / SEPA · archivo local')
        self.observed=QLineEdit();self.observed.setPlaceholderText('AAAA-MM-DD · fecha real del dataset SEPA')
        form.addRow('Archivo',self.file);form.addRow('Fuente',self.source);form.addRow('Fecha SEPA',self.observed)
        layout.addLayout(form)
        self.choose=QPushButton('Elegir SQLite o CSV');self.choose.clicked.connect(self.select);layout.addWidget(self.choose)
        self.run_button=QPushButton('Importar y reemplazar catálogo de referencia');self.run_button.clicked.connect(self.start);layout.addWidget(self.run_button)
        self.progress=QProgressBar();self.progress.setRange(0,0);self.progress.hide();layout.addWidget(self.progress)
        self.close_button=QPushButton('Cerrar');self.close_button.clicked.connect(self.reject);layout.addWidget(self.close_button)
    def select(self):
        path,_=QFileDialog.getOpenFileName(self,'Catálogo local','','Catálogos (*.db *.sqlite *.sqlite3 *.csv)')
        if path:self.path=path;self.file.setText(path)
    def start(self):
        if not self.path:self.status.setText('Elegí un archivo.');return
        self.choose.setEnabled(False);self.run_button.setEnabled(False)
        self.source.setEnabled(False);self.observed.setEnabled(False)
        self.progress.show();self.close_button.setText('Cancelar importación')
        self.worker=ImportWorker(self.catalog,self.path,self.source.text(),self.observed.text(),self)
        self.worker.progress.connect(lambda n,s:self.status.setText(f'{n} referencias válidas · {s} filas omitidas'))
        self.worker.done.connect(lambda r:self.status.setText(f"Importadas: {r['imported']} · Omitidas: {r['skipped']}. No se modificó tu comercio."))
        self.worker.failed.connect(self.status.setText)
        self.worker.finished.connect(self.finished_import)
        self.worker.start()
    def finished_import(self):
        self.choose.setEnabled(True);self.run_button.setEnabled(True)
        self.source.setEnabled(True);self.observed.setEnabled(True)
        self.progress.hide();self.close_button.setText('Cerrar')
    def reject(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel.set();self.status.setText('Cancelando; se conserva el catálogo anterior...')
        else:super().reject()
    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():
            self.reject();event.ignore()
        else:event.accept()
