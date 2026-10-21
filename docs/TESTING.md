# Validación — PoStoreBaires Python/Qt

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
