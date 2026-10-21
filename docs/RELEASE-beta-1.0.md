# PoStoreBaires 1.0.0-beta.2

Beta de pruebas para Windows y Linux. Código Python/PySide6 nativo, GPL-3.0-only.

## Novedades

- Persistencia SQLite local de ventas, stock, carrito, turnos y ajustes; copia exportable desde Ajustes.
- Buscador con lupa en Caja por nombre o código, precio y disponibilidad; permite agregar por botón, Enter o doble clic.
- Producto no encontrado: ingreso manual de código o alta en Insumos conservando la compra.
- Confirmación al reemplazar códigos; rechazo de duplicados.
- Catálogo compatible con SQLite antiguo de Preciazo y CSV SEPA, con fuente/fecha y aplicación manual de nombre/precio. No se incluyen datasets ni descarga de imágenes.
- Créditos a Nulo y colaboradores de Preciazo. Presentación y guía completas en main.md.

## Descargar y ejecutar

Windows: extraer todo PoStoreBaires-1.0.0-beta.2-Windows.zip y abrir PoStoreBaires.exe dentro de la carpeta. Conservar _internal y recursos. EXE sin firma.

Linux x86_64: extraer PoStoreBaires-1.0.0-beta.2-Linux.tar.gz e iniciar ./PoStoreBaires/PoStoreBaires desde un escritorio compatible. Build sobre Ubuntu 22.04.

Incluye código fuente y SHA256SUMS.txt. La publicación exige tests, builds y arranque de ejecutables de ambas plataformas, más verificación de hashes.

## Primer uso y datos

La base nueva comienza vacía y con turno cerrado. Configurar comercio/cajero, crear productos y abrir turno con el efectivo inicial real. Ayuda se abre dentro de la aplicación.

Los datos se guardan fuera del portable, en la carpeta de datos del usuario; consultar ruta y exportar copia desde Ajustes. Respaldar fotos, logos y QR por separado. No compartir SQLite por LAN. La beta.1 trabajaba en memoria y no generaba una base para migrar.

## Límites

Sin servidor multicaja, autenticación efectiva, impresión térmica ni facturación fiscal. Wallet requiere verificación manual de acreditación. Catálogo requiere archivo autorizado importado; no hay API ni dataset incluido. Las pruebas automatizadas usan datos sintéticos y no sustituyen pruebas con lector físico, monitores, audio y QR reales.

Manual: main.md y docs/GUIA.md. Importador: docs/PRECIAZO.md.
