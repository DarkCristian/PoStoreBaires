# PoStoreBaires

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

- Push/PR a `main` o ejecución manual: valida y genera artifacts, sin publicar releases.
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

[Documentación principal](main.md) · [Guía](docs/GUIA.md) · [Arquitectura](docs/ARCHITECTURE.md) · [Validación](docs/TESTING.md) · [Cambios](CHANGELOG.md) · [Seguridad](SECURITY.md).

## Licencia

Copyright (C) 2026 Cristian Carroccio. GPL-3.0-only, texto completo en [LICENSE](LICENSE). Libre uso, estudio, modificación y distribución bajo esa licencia, sin garantía. Ver [componentes de terceros](THIRD_PARTY.md). Las imágenes/QR del usuario no se incluyen en el proyecto.
