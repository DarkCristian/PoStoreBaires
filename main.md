# PoStoreBaires

## Un punto de venta para el comercio de todos los días

**PoStoreBaires** es un proyecto gratuito y open source de punto de venta, creado por **Cristian Carroccio**, pensado para kioscos, almacenes y pequeños comercios. Reúne ventas, control de caja e inventario en una aplicación de escritorio con tres solapas: **Caja, Arqueo e Insumos**.

Desarrollado en **Python y PySide6/Qt**, cuenta con compilaciones para Windows y Linux. Permite trabajar con lector de códigos de barras o teclado, registrar distintos medios de pago y mostrar al cliente el QR o alias del comercio sin depender de una API de cobro.

**Estado del proyecto:** beta en desarrollo. Esta documentación corresponde a **1.0.0-beta.2**, con persistencia local, catálogo y búsqueda. La versión beta.1 conserva su historial y sus paquetes originales. Los campos de perfiles y conectividad anticipan funciones futuras, pero actualmente no autentican usuarios ni sincronizan cajas.

## Características

### Caja: vender con lector o teclado

- Entrada por lectores USB que emulan teclado y envían Enter. También admite código escrito a mano y botón Agregar.
- Botón **Buscar con lupa** junto al código: abre una ventana dentro de la aplicación y filtra productos por nombre o código mientras escribís.
- Resultados con nombre, código, precio y stock disponible, descontando las unidades del carrito. Incluye productos cargados manualmente y los registrados a partir del catálogo de referencia.
- Agregado de una unidad por botón, Enter desde la búsqueda o doble clic sobre un resultado.
- Carrito con cantidades, precios, subtotales y total; permite quitar unidades, eliminar productos o vaciar la venta.
- Validación de turno abierto y existencias antes de agregar o confirmar.
- Pagos en efectivo, wallet/transferencia, débito y crédito, incluidos pagos mixtos. Importes internos expresados en centavos enteros y cálculo de vuelto en efectivo.
- Sonidos opcionales de escaneo y caja registradora, con interruptores independientes.

**Cuando no se encuentra un producto:** un código desconocido o una búsqueda sin resultados al dejar de escribir abre el diálogo **Producto no encontrado**, con dos opciones:

| Botón | Acción |
| --- | --- |
| Agregar manualmente | Permite escribir el código de barras por teclado y buscarlo en el inventario |
| Agregar nuevo | Abre el formulario de alta en Insumos; conserva el código buscado si es numérico |

Registrar un nuevo producto conserva la compra pendiente. El alta no suma automáticamente unidades al carrito: una vez guardado, se agrega desde Caja. Editar productos existentes sigue bloqueado mientras hay una venta pendiente. Cerrar el diálogo no modifica la compra.

### Pantalla del cliente y pago desde el celular

- Ventana independiente con monitor seleccionable desde Ajustes.
- Muestra productos e importe, y permite elegir **Solo QR, Solo alias o QR y alias**.
- QR propio cargado desde PNG, JPG/JPEG o una página de PDF; Qt renderiza el PDF dentro de la aplicación. Alias ingresado como texto.
- El cliente escanea el QR o escribe el alias en su wallet. Un QR estático puede requerir ingresar el importe en la app del cliente.
- El cajero verifica la acreditación en la cuenta del comercio y marca la confirmación antes de completar una venta con wallet. Cambiar los importes desmarca esa verificación.
- Después del cobro muestra total, medios y vuelto si corresponde; una venta íntegramente por wallet muestra **Cobrado OK**. Luego vuelve a la pantalla de bienvenida con los datos de pago.

El POS registra el pago informado por el cajero: no procesa tarjetas, transmite importes a una wallet ni consulta automáticamente la acreditación. El alias es texto para ingresar en la app, no un código escaneable.

### Arqueo: seguir el dinero de cada turno

- Apertura de turno con saldo inicial de efectivo.
- Registro de retiros de caja.
- Totales esperados y declaración de importes por medio de pago al cerrar.
- Cálculo de diferencias y detalle de cierres conservados localmente.
- Relevo de caja/cajero después de cerrar el turno.

Los lotes bancarios y la conciliación automática de tarjetas todavía están pendientes.

### Insumos: productos, precios y existencias

- Alta manual y edición de código, nombre, categoría, costo y precio de venta.
- Búsqueda por nombre/código y filtro de categoría: Limpieza, Cigarrillos, Golosinas y Productos varios.
- Stock en unidades, unidades por bulto y entrada de bultos completos con conversión a unidades.
- Mínimo de stock y aviso de reposición en la interfaz al cobrar.
- Fotos locales o ilustraciones predeterminadas de productos.
- Confirmación antes de reemplazar un código existente; advierte que el anterior dejará de encontrar ese producto. Un código ya asignado a otro producto se rechaza con un aviso.

### Catálogo de referencia Preciazo / SEPA

El importador independiente admite archivos SQLite del formato antiguo de Preciazo y `productos.csv` de SEPA. Se accede desde **Insumos → Catálogo de referencia**.

- Importación en segundo plano, cancelable, a un índice separado del inventario comercial.
- Si falla o se cancela, conserva el catálogo anterior. Un import válido reemplaza solo el índice externo.
- Consulta exacta por código de barras, conservando ceros iniciales.
- Referencias con producto, precio, fuente y fecha. Para SEPA hay que declarar la fecha real del dataset.
- Uso explícito del nombre/datos o del precio sugerido; no importa el costo ni las existencias de otra tienda.
- Advertencia al aplicar datos de más de 30 días o sin fecha.
- Alta manual siempre disponible. No requiere Internet después de importar.

Los productos del catálogo externo deben darse de alta con precio y stock propios antes de venderse. No se incluyen datasets ni se descargan automáticamente datos o imágenes. Se conserva la foto local o ilustración del producto.

**Créditos:** a **Nulo y los colaboradores de [Preciazo](https://github.com/catdevnull/preciazo)** por el proyecto usado como referencia de los formatos. No se copia su código ni se redistribuyen sus datos. No se encontró una licencia explícita en el árbol revisado; la licencia del POS no otorga permisos sobre datasets externos. Detalles de formatos, campos y procedencia en [PRECIAZO.md](docs/PRECIAZO.md).

### Guardado local y copias

Ventas, productos, stock, carrito, turnos y ajustes se guardan en **SQLite** al modificar. Una venta no se confirma en la interfaz si falla su guardado; se revierte también el estado en memoria. Una sesión desactualizada no puede sobrescribir cambios de otra.

La ruta de `store.sqlite` aparece en Ajustes y queda fuera de la carpeta portable, en los datos de la aplicación del usuario. **Exportar copia** genera un backup SQLite consistente. El catálogo regenerable se guarda aparte como `reference.sqlite`. Fotos, logos y QR son archivos externos: conservá sus rutas y respaldalos por separado.

Esta persistencia está diseñada para una sola PC. No compartas el archivo SQLite por LAN ni lo uses como servidor multicaja.

Para restaurar una copia, cerrá todas las sesiones y conservá la base actual con sus archivos auxiliares. Colocá la copia como `store.sqlite` en una carpeta nueva e iniciá con `--data-dir RUTA`. Todavía no hay asistente de restauración en la interfaz.

### Ajustes, tickets y ayuda

- Nombre comercial, razón social, logo y ancho de papel 58/80 mm.
- Vista previa del último ticket interno **no fiscal**. Impresión térmica todavía pendiente.
- Configuración del monitor del cliente, QR/alias y sonidos.
- Nombres de caja y cajero; roles y modo Principal/Secundaria/IP son campos ilustrativos.
- Tutorial desde Ayuda, abierto dentro de la propia aplicación. No requiere abrir un PDF en el navegador.

## Primeros pasos

1. Iniciá la aplicación. Una base nueva tiene inventario vacío y turno cerrado.
2. En Ajustes, ingresá los datos del comercio, caja y cajero.
3. Registrá productos en Insumos, manualmente o tomando referencias del catálogo importado. Revisá código, presentación, precio, stock y unidades por bulto.
4. En Arqueo, abrí el turno con el efectivo inicial real.
5. En Caja, escaneá, escribí un código o usá la lupa. Elegí las cantidades y cobrá con los medios correspondientes.
6. Para wallet, verificá la acreditación desde la cuenta del comercio antes de confirmar.
7. Registrá retiros y cerrá el turno declarando los importes por cada medio. Revisá las diferencias.
8. Exportá copias desde Ajustes y respaldá también fotos, logos y QR.

## Ejecutar desde el código fuente

Python 3.12 de 64 bits:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Para usar una carpeta de datos específica:

```sh
python run.py --data-dir RUTA
```

## Compilar y probar

En Windows, con Python 3.12 x64 y el launcher `py`, ejecutá **Compilar-Windows.cmd**. El resultado es un portable completo: conservá el ejecutable, `_internal`, recursos y licencias. El EXE no está firmado.

La compilación debe realizarse en el sistema operativo destino. Los comandos comunes son:

```sh
python -m pip install -r requirements-build.txt
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build.py
python scripts/smoke.py
python scripts/package.py
```

Para Linux x86_64 con escritorio, el workflow utiliza Ubuntu 22.04. Bibliotecas de sistema y detalles de compilación en [README.md](README.md). El portable Linux se extrae completo del `tar.gz` y se inicia con `./PoStoreBaires/PoStoreBaires`.

El workflow [.github/workflows/beta-1.0.yml](.github/workflows/beta-1.0.yml) valida, prueba, compila y comprueba el arranque de los ejecutables Windows/Linux. Genera paquetes por plataforma, código fuente y hashes SHA-256. En los PR genera artifacts; la publicación de prerelease requiere la condición de publicación del workflow. No sobrescribe una release existente.

Consultá [Actions](https://github.com/DarkCristian/PoStoreBaires/actions) para el resultado de cada commit y [Releases](https://github.com/DarkCristian/PoStoreBaires/releases) para versiones publicadas. Un cambio en el PR no actualiza por sí solo los paquetes de una release anterior.

## Alcance y próximas etapas

La beta permite probar el flujo local. Todavía están pendientes:

- Servicio central en la PC principal y sincronización simultánea de cajas por LAN.
- Autenticación, perfiles con permisos efectivos y sesiones de cajeros.
- Impresión térmica, facturación fiscal y conciliación bancaria.
- Consulta de productos/imágenes por Internet y actualización de datasets desde la interfaz.
- Restauración guiada y validación operativa con hardware real.

Las pruebas automatizadas verifican dominio, persistencia, importación y widgets Qt en modo offscreen. No acreditan compatibilidad con un lector físico, la escaneabilidad de un QR, un segundo monitor o una impresora del comercio. Los datos del importador se prueban con fixtures sintéticos; no garantizan calidad ni actualidad de un dataset externo.

## Documentación y licencia

[Guía de uso](docs/GUIA.md) · [Catálogo Preciazo/SEPA](docs/PRECIAZO.md) · [Arquitectura](docs/ARCHITECTURE.md) · [Pruebas](docs/TESTING.md) · [Cambios](CHANGELOG.md) · [Seguridad](SECURITY.md) · [Componentes de terceros](THIRD_PARTY.md).

Copyright (C) 2026 Cristian Carroccio. **GPL-3.0-only**, texto completo en [LICENSE](LICENSE). Permite usar, estudiar, modificar y redistribuir conforme a esa licencia, sin garantía. Las imágenes y QR del usuario no se incluyen en el proyecto. La maqueta HTA previa se conserva en `prototypes/hta/`; el código activo utiliza Qt nativo.
