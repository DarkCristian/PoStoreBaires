# Cambios

## 1.0.0-beta.2

- Aviso de producto no encontrado con entrada manual o alta en Insumos conservando la compra.
- Créditos de Preciazo y confirmación al reemplazar un código.
- Presentación y guía actualizadas en main.md.

- Botón de lupa en Caja: búsqueda por nombre/código del inventario local, selección y agregado a la compra con validación de stock y turno.

- Persistencia SQLite local de ventas, stock, carrito, turnos y ajustes, con rollback ante fallo y rechazo de sesiones desactualizadas.
- Exportación de copias SQLite desde Ajustes; primer inicio vacío y turno cerrado.
- Catálogo independiente compatible con SQLite antiguo de Preciazo y CSV SEPA, sin datos ni código upstream incluidos.
- Consulta exacta por código, fuente/fecha y aplicación manual del nombre o precio; costo y stock no se importan.
- Importación en segundo plano, cancelable y atómica; imágenes externas sin descarga automática.


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
