# PoStoreBaires — Documentación principal

POS gratuito y open source, por Cristian Carroccio. **Beta 1.0 nativa en Python + PySide6/Qt**, con tres solapas: Caja, Arqueo e Insumos. Licencia **GPL-3.0-only**.

La versión HTA anterior se conserva como referencia en `prototypes/hta/`. El producto y el repositorio previsto se llaman **PoStoreBaires**. El código activo ya no ejecuta HTA ni JavaScript, ni utiliza WebEngine o un navegador embebido.

## Alcance real

Beta local **con datos temporales en memoria**. Permite probar ventas, pagos registrados, inventario y arqueo. Todavía no es apta para operación productiva: cerrar descarta ventas, productos y ajustes.

- Caja con lector USB que emula teclado y envía Enter; códigos de ejemplo 779001–779004.
- Efectivo con vuelto, wallet, débito/crédito y pagos mixtos; importes en centavos enteros.
- Confirmación wallet solo después de verificar manualmente la acreditación en la cuenta del comercio.
- Pantalla del cliente en monitor seleccionable: productos, total, QR/alias y resultado.
- QR propio PNG/JPG/JPEG o página seleccionada de un PDF, renderizada por Qt a imagen. Alias es texto para ingresar en la app, no un código escaneable.
- Arqueo con saldo inicial, retiros, declaración y diferencias por medio, historial y relevo de cajero al cerrar turno.
- Insumos: categoría, costo, precio, stock mínimo, bultos/unidades, fotos e ilustraciones originales.
- Sonidos opcionales independientes: bip y caja registradora. Tutorial integrado.
- Datos de comercio, logo, papel 58/80 mm y vista previa de ticket interno no fiscal.

**Pendiente:** persistencia, base PostgreSQL, servidor y sincronización multicaja, autenticación/roles efectivos, lotes bancarios de tarjetas, impresión térmica, facturación fiscal, consulta de productos y precios por Internet, copias de seguridad. Principal/secundaria/IP y perfiles siguen siendo campos ilustrativos.

## Ejecutar desde Python

Python 3.12 de 64 bits:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

No requiere API de cobro. El cliente paga desde su app usando el QR/alias del comercio y el cajero verifica la acreditación.

## Compilar para Windows

Con Python 3.12 de 64 bits y el launcher `py` instalado, ejecutá **`Compilar-Windows.cmd`**. Crea un entorno local, instala las dependencias declaradas, ejecuta pruebas y genera:

- `dist/PoStoreBaires/PoStoreBaires.exe` y bibliotecas Qt.
- `dist/PoStoreBaires-1.0.0-beta.1-Windows.zip` portable.
- Archivo de código fuente y `SHA256SUMS-Windows.txt`.

El portable es una carpeta completa, no un EXE suelto: extraé todo el ZIP y conservá `_internal`, recursos y licencias. El EXE no está firmado. El build Windows debe hacerse en Windows; un build Linux no produce un ejecutable Windows.

También se puede ejecutar manualmente:

```sh
python -m pip install -r requirements-build.txt
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build.py
python scripts/package.py
```

## Compilar y probar en Linux

La distribución prevista usa Linux x86_64 con escritorio; el workflow compila sobre Ubuntu 22.04. No se promete compatibilidad con todas las distribuciones. En Debian/Ubuntu pueden requerirse bibliotecas Qt/X11 del sistema:

```sh
sudo apt-get install libegl1 libgl1 libopengl0 libxkbcommon0 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libxcb-shape0 libpulse0
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build.py
python scripts/smoke.py
python scripts/package.py
```

Para ejecutar el paquete Linux publicado:

```sh
tar -xzf PoStoreBaires-1.0.0-beta.1-Linux.tar.gz
./PoStoreBaires/PoStoreBaires
```

Conservá toda la carpeta. `tar.gz` preserva permisos y enlaces de bibliotecas. No requiere Python instalado; sí un escritorio y bibliotecas de sistema compatibles. El build local probado en este entorno Linux no acredita por sí solo el build Ubuntu 22.04 de Actions.

## Workflow Beta 1.0 — ambos sistemas

`.github/workflows/beta-1.0.yml` usa dos runners nativos: Windows x64 y Ubuntu 22.04 x64. Cada uno valida, prueba, compila con PyInstaller, inicia su ejecutable empaquetado y genera su archivo y SHA-256. Un tercer job empaqueta el código fuente. Los artifacts tienen nombres distintos por plataforma.

- Push/PR a `main` o ejecución manual sin marcar publicación: valida y genera artifacts.
- Ejecución manual con `publish_prerelease` activado: compila ambos sistemas y publica la beta sobre el commit exacto del run, creando el tag si hace falta.
- Push del tag `v1.0.0-beta.1`: espera **ambas compilaciones y el código fuente**, verifica checksums y crea un borrador de prerelease.
- Solo después de subir Windows, Linux, fuente y SHA256SUMS.txt se hace público el prerelease. Si falla una compilación no se publica; si falla la subida, el borrador permanece privado para revisión.
- No sobrescribe releases existentes ni usa una compilación antigua como si fuera nueva.

Archivos de prerelease previstos:

| Archivo | Contenido |
| --- | --- |
| `PoStoreBaires-1.0.0-beta.1-Windows.zip` | Portable Windows x64 completo |
| `PoStoreBaires-1.0.0-beta.1-Linux.tar.gz` | Portable Linux x64 completo |
| `PoStoreBaires-1.0.0-beta.1-source.zip` | Código fuente, documentación, licencia y scripts |
| `SHA256SUMS.txt` | Hashes de los tres archivos |

**Repositorio:** [DarkCristian/PoStoreBaires](https://github.com/DarkCristian/PoStoreBaires). Consultá [Actions](https://github.com/DarkCristian/PoStoreBaires/actions) para el estado de las compilaciones y [Releases](https://github.com/DarkCristian/PoStoreBaires/releases) para paquetes publicados. Un workflow escrito no equivale a una compilación exitosa.

## Documentación

[Guía](docs/GUIA.md) · [Arquitectura](docs/ARCHITECTURE.md) · [Validación](docs/TESTING.md) · [Cambios](CHANGELOG.md) · [Seguridad](SECURITY.md).

## Licencia

Copyright (C) 2026 Cristian Carroccio. GPL-3.0-only, texto completo en [LICENSE](LICENSE). Libre uso, estudio, modificación y distribución bajo esa licencia, sin garantía. Ver [componentes de terceros](THIRD_PARTY.md). Las imágenes/QR del usuario no se incluyen en el proyecto.

## Configuración paso a paso


1. Ejecutá `python run.py` con las dependencias instaladas, o abrí `PoStoreBaires.exe` del portable Windows completo.
2. El turno inicial contiene $10.000 de efectivo. Probá códigos 779001–779004. El lector debe emular teclado y enviar Enter.
3. En Insumos creá/seleccioná productos. Editá costo, precio, mínimo, unidades por bulto y foto/ilustración. Ingresar bultos suma su conversión a unidades. No se editan productos con un carrito pendiente.
4. En Ajustes ingresá nombre comercial, razón social, logo y papel. Último ticket es una vista previa interna no fiscal; no imprime.
5. Cerrá el turno antes de cambiar caja/cajero; luego abrí otro con saldo inicial. Principal/Secundaria, IP y roles son ilustrativos.
6. Activá la pantalla del cliente, elegí monitor y Solo QR, Solo alias o QR y alias. Cargá la imagen o PDF y seleccioná página. Vista previa permite revisar el QR. Qt convierte PDF sin un visor externo.
7. En la pantalla del cliente QR/alias están visibles durante la compra junto a productos y total. El cliente paga desde su app. Un alias se ingresa como texto. Un QR estático puede requerir cargar el importe manualmente en la app.
8. En Cobrar distribuí efectivo recibido, wallet, débito y crédito. Cobrar por wallet asigna todo a wallet si no se ingresó importe en ese medio. Los cambios se reflejan en la pantalla del cliente.
9. Verificá la acreditación desde la cuenta del comercio y marcá la casilla para confirmar. Cambiar importes desmarca esa verificación. No hay API ni validación automática.
10. La venta confirmada muestra total y medios; efectivo muestra vuelto. Wallet íntegra muestra Cobrado OK. Después de 12 segundos vuelve a bienvenida con QR/alias.
11. Sonidos independientes en Ajustes: bip al agregar y caja registradora al confirmar. Probar permite escucharlos antes de guardar.
12. Arqueo: registrá retiros, cerrá con los declarados por medio y consultá diferencias en Detalle. El esperado de efectivo incluye inicial, cobros y retiros. Lotes bancarios de tarjetas pendientes.

Al cerrar se pierde toda la sesión. Las imágenes y QR se leen desde sus archivos: no los muevas mientras usás la beta. No hay persistencia, red real ni uso productivo.

## Arquitectura y próximas etapas


## Beta 1.0 actual

Aplicación nativa Python/PySide6-Qt con estado en memoria. Un único turno activo y múltiples registros de cierres durante la sesión. No existe conexión entre máquinas.

El dominio separa validación de pago/stock de la interfaz. Importes en centavos enteros; pagos insuficientes, excedentes no efectivos y wallet no verificada se rechazan antes de modificar inventario. La pantalla del cliente es un QWidget independiente; PDF se renderiza con QtPdf y el audio con QSoundEffect.

## Producción planificada

- Cliente de escritorio Qt/PySide. Base PostgreSQL y servicio central en la PC principal.
- Principal también puede vender; rol administrador independiente del modo de equipo.
- Cajas secundarias se conectan al servicio por LAN. Sin acceso compartido directo a archivos de base.
- Ventas, pagos y stock confirmados en una transacción central con claves de idempotencia y control de concurrencia.
- Autenticación y permisos Administrador/Supervisor/Cajero aplicados en el servidor.
- Turnos por caja, relevo explícito y trazabilidad de anulaciones/ajustes.
- Sin Internet puede seguir la operación LAN; sin servidor se bloquea la confirmación y se conserva carrito.
- Tickets térmicos, ajustes de logo/razón social, perfiles de impresora 58/80 mm.
- Facturación fiscal y procesamiento/validación automática de wallets como módulos separados.
- Búsqueda opcional por EAN, con fuente/fecha, alta manual siempre disponible. Nunca actualizar precios automáticamente desde una referencia externa.
- Copias de seguridad y restauración comprobadas antes del uso productivo.

No hay fechas prometidas para estas etapas. La próxima entrega debe priorizar persistencia y pruebas transaccionales antes de multicaja o integraciones.

## Validación y límites de las pruebas


## Automática

`python scripts/validate.py` comprueba sintaxis, versión, licencia y recursos.
`python -m unittest discover -s tests -p "test_*.py" -v` prueba importes decimales, pagos exactos/mixtos, vuelto, rechazos atómicos, stock, arqueo, relevo, códigos con ceros, configuración wallet y widgets Qt en modo offscreen. Incluye QR visible antes del cobro, alias, importe mixto, desmarcado de verificación, resultado y renderizado de página PDF.

El build usa PyInstaller onedir en el sistema operativo destino. `PoStoreBaires --smoke-test` inicia la aplicación y carga un producto, sin entrar en la confirmación de salida. El workflow Windows ejecuta ese smoke-test contra el EXE empaquetado. El build local Linux prueba un ejecutable Linux; no valida el EXE Windows.

## Manual por plataforma

- Escaneo por lector físico, atajos y foco de entrada.
- Cobros efectivo, mixto y wallet verificada; errores no alteran stock.
- Arqueo, retiros, cierres/relevo y detalle por medio.
- Imagen y PDF reales de QR: proporciones y lectura desde una app del celular.
- Segundo monitor, escala y resolución del comercio.
- Dispositivo de audio y ambos interruptores.
- Apertura del portable extraído completo sin Python instalado.
- Logo en ticket/vista previa. No implica prueba de impresión (todavía pendiente).

Estas pruebas manuales siguen pendientes; los tests offscreen no prueban lectores, monitores, audio, escaneabilidad del QR ni funcionamiento de una wallet.

## Resultado de esta preparación

- 15 tests de dominio, UI Qt y control de publicación aprobados (revalidación en esta actualización).
- Arranque y carrito comprobados en Qt offscreen.
- Build PyInstaller generado en Linux y ejecutable empaquetado probado con `--smoke-test`, con salida correcta.
- Se corrigió el diálogo de confirmación de salida para que no bloquee el smoke-test.
- Build nativo y arranque de ejecutables Windows/Linux aprobados en [GitHub Actions](https://github.com/DarkCristian/PoStoreBaires/actions/runs/39663807821). Las pruebas manuales de hardware siguen pendientes.
