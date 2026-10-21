# PoStoreBaires 1.0.0-beta.3

## Pesos enteros

Precios, costos, ventas, pagos, vuelto y arqueos se ingresan, calculan y guardan en pesos argentinos enteros. Ingresar 1500 guarda 1500 y muestra $ 1.500. No admite fracciones ni separadores de miles en los campos.

## Datos existentes

Migra exactamente bases de beta.2 (esquema 1) a esquema 2, con copia SQLite automática antes de escribir. No modifica cantidades, códigos ni stock. Si algún importe comercial tiene centavos, informa el problema y detiene la migración sin redondear ni alterar sus registros. Conservar la copia anterior para usar beta.2: la base convertida requiere beta.3.

Catálogo: precios en pesos enteros. Referencias externas con fracciones conservan descripción y procedencia, sin precio aplicable; el precio propio se ingresa manualmente. No se incluyen datasets externos.

## Descargar y probar

Windows: extraer todo PoStoreBaires-1.0.0-beta.3-Windows.zip y abrir PoStoreBaires.exe. Conservar _internal y recursos. EXE sin firma.

Linux x86_64: extraer PoStoreBaires-1.0.0-beta.3-Linux.tar.gz e iniciar ./PoStoreBaires/PoStoreBaires. Build sobre Ubuntu 22.04.

Código fuente y SHA256SUMS.txt incluidos. Tests, builds y arranque de ejecutables de ambos sistemas requeridos antes de publicar.

La base nueva comienza vacía y con turno cerrado. La base se guarda fuera del portable; ruta y exportación de copia en Ajustes. Fotos, logos y QR requieren copia aparte.

Mantiene búsqueda con lupa, alta de productos, persistencia y catálogo de beta.2. Sin servidor multicaja, autenticación efectiva, impresión térmica ni facturación fiscal. Wallet requiere verificación manual. Manual: main.md; formatos y créditos: docs/PRECIAZO.md.
