# Componentes de terceros

PoStoreBaires es GPL-3.0-only. Las ilustraciones SVG y WAV del proyecto son originales y llevan la misma licencia.

La aplicación nativa usa Python 3.12, PySide6/Shiboken6 y Qt 6.8.3. PySide6 y Shiboken6 son componentes de Qt for Python, copyright de The Qt Company y sus contribuidores, disponibles bajo LGPLv3/GPLv3 y licencias comerciales. PoStoreBaires utiliza su distribución open source. El texto LGPLv3 se incluye en `licenses/LGPL-3.0.txt`; GPLv3 está en `LICENSE`.

- Qt for Python, código fuente y avisos: https://code.qt.io/cgit/pyside/pyside-setup.git/tree/?h=v6.8.3
- Qt 6.8.3, código fuente: https://download.qt.io/archive/qt/6.8/6.8.3/single/
- Licencias y avisos de componentes de Qt: https://doc.qt.io/qt-6.8/licenses-used-in-qt.html
- Python, licencia PSF y avisos: https://docs.python.org/3.12/license.html
- PyInstaller (herramienta de empaquetado), GPL con excepción para el bootloader: https://pyinstaller.org/en/v6.16.0/license.html

Los componentes de Qt se distribuyen como bibliotecas dinámicas en el portable `onedir`. Conservá sus avisos y los de los plugins al redistribuir. Qt incluye componentes de terceros con sus licencias propias. El portable no restringe la sustitución de bibliotecas compatibles ni la ingeniería inversa necesaria para depurar esas modificaciones. Los avisos/licencias disponibles en el entorno de build se copian a `licenses/dependencies`.

Los QR, logos y fotos que seleccione el usuario no se incluyen en el código ni en los paquetes del proyecto.

## Compatibilidad Preciazo / SEPA

El importador propio documentado en [PRECIAZO.md](docs/PRECIAZO.md) lee formatos del proyecto [Preciazo](https://github.com/catdevnull/preciazo). No incluye código ni datos de ese repositorio y no es una dependencia de ejecución. La revisión indicada no mostró una licencia explícita; los permisos del dataset deben verificarse por separado antes de usarlo o redistribuirlo.
