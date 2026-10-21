# PoStoreBaires 1.0.0-beta.1

Primera beta nativa Python/Qt, gratuita y open source GPL-3.0-only. El prototipo anterior HTA se conserva como referencia.

Caja/Arqueo/Insumos, pagos registrados y mixtos, stock por bultos/unidades, QR/alias del comercio, pantalla del cliente, PDF renderizado por Qt, sonidos opcionales y tutorial.

## Probar

- Windows x64: extraé el ZIP completo y abrí `PoStoreBaires.exe` dentro de su carpeta.
- Linux x64: extraé el tar.gz y ejecutá `./PoStoreBaires/PoStoreBaires`. Conservá bibliotecas y permisos. Objetivo del workflow: Ubuntu 22.04 o entorno compatible; no hay garantía universal para todas las distros.
- No requiere Python instalado. Windows no está firmado. El código fuente y SHA-256 acompañan ambos paquetes.
- Leé `main.md` para configuración, QR/alias, arqueo, monitores, sonidos, licencia y limitaciones.

La publicación espera Windows, Linux y fuente; verifica los hashes antes de hacer público el prerelease. Esta nota describe el contenido previsto: no demuestra que el workflow remoto ya se haya ejecutado.

**Datos temporales: al cerrar se pierde la sesión. Sin servidor, sincronización, autenticación, impresión ni facturación fiscal. No procesa pagos externos ni confirma acreditaciones. No usar en producción.**

Las pruebas automáticas no sustituyen lector físico, segundo monitor, sonido ni escaneo real del QR.
