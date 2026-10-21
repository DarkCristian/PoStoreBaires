# Cambios

## 1.0.0-beta.1 — PoStoreBaires

- Nombre de producto y repositorio previsto: PoStoreBaires.
- Migración de la maqueta HTA a Python 3.12 + PySide6/Qt nativo, sin WebEngine.
- Caja, pagos mixtos, stock, arqueo y detalle de cierres en memoria.
- Pantalla del cliente: monitor seleccionable, QR/alias visibles durante la compra y resultado.
- PDF: selección de página y renderizado a imagen con QtPdf, sin visor externo.
- Ayuda integrada, fotos/ilustraciones, sonidos opcionales, configuración de ticket.
- Build portable PyInstaller, script Windows y workflow matriz Windows/Linux con tests y smoke-test.
- Publicación de prerelease condicionada a ambos builds, fuente y checksums; documentación completa en main.md.
- Licencia GPL-3.0-only y avisos de dependencias.

La versión HTA previa se conserva en prototypes/hta. Persistencia, servidor, multicaja real, permisos efectivos, impresión y facturación quedan fuera de esta beta.
