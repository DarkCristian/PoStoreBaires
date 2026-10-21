# Catálogo Preciazo / SEPA

Compatibilidad de formatos implementada independientemente para PoStoreBaires. Referencia revisada: [catdevnull/preciazo](https://github.com/catdevnull/preciazo), commit `2642ece2a284417b267e1e9d74ea59c55d89c1a3`. No se encontró una licencia explícita en ese árbol: no se copia código ni se redistribuyen sus datos. La licencia GPL del POS no concede permisos sobre datasets externos. El usuario obtiene un archivo cuyo uso esté autorizado.

## Uso

1. En Insumos elegí **Catálogo de referencia**.
2. Elegí el archivo SQLite antiguo o `productos.csv` de SEPA, ya extraído. Ingresá fuente y, para CSV, la fecha real del dataset en formato AAAA-MM-DD.
3. Importá. Reemplaza solamente el índice de referencias, nunca productos, ventas o stock del comercio. Cancelar o un error conserva el índice anterior. Un archivo sin filas válidas no lo borra.
4. Al crear/editar un producto escaneá su código y usá Buscar. Los códigos se conservan como texto, incluidos ceros iniciales. Se admiten longitudes GTIN 8, 12, 13 y 14; no se calcula su dígito verificador.
5. Elegí una referencia por producto, fecha y sucursal. **Usar nombre y datos** no cambia el precio. **Usar precio** aplica también el nombre y conserva procedencia. No se carga costo ni stock. Revisá presentación, impuestos y margen antes de guardar.

No hay descarga automática de bases ni conexión a una API pública. El catálogo funciona sin Internet después de importarlo. Una referencia no garantiza disponibilidad o precio actual; más de 30 días o fecha desconocida genera advertencia al aplicarla. Se muestran hasta 50 resultados por código, primero los más recientes. Podés cargar o editar todo manualmente aunque no haya coincidencia.

## Formatos admitidos

| Entrada | Campos usados |
| --- | --- |
| SQLite antiguo | Tabla real `precios`: `ean`, `name`, `precio_centavos`, `fetched_at`; opcionales `url`, `image_url` |
| CSV SEPA UTF-8, coma o punto y coma | `id_producto`, `productos_ean`, `productos_descripcion`, `productos_precio_lista`; opcionales marca, presentación e IDs de comercio/bandera/sucursal |

SQLite se abre en modo lectura. `precio_centavos` ya está en centavos; `fetched_at` conserva fecha de observación. `in_stock` de otra tienda nunca se convierte en inventario propio.

En SEPA, **`productos_ean` es un indicador 0/1, no el código**. Solo se importan filas con indicador 1 y un `id_producto` válido. Se usa precio de lista de la presentación, no `productos_precio_referencia` por unidad de medida. IDs internos, precios inválidos y filas incompletas se omiten y contabilizan. La fecha se toma del dataset declarado, no del día de importación.

ZIP, tar.zst, PostgreSQL y Parquet no se importan directamente. Primero se necesita uno de los archivos admitidos. No se incluye un dataset de muestra real; las pruebas usan datos sintéticos.

## Imágenes y almacenamiento

Las URLs HTTPS se guardan como metadatos, sin descargar imágenes. Se conserva la ilustración o foto local del producto. El índice `reference.sqlite` queda separado de `store.sqlite` en la carpeta de datos del usuario. La copia comercial exportada no incluye el índice regenerable ni archivos de fotos/QR.

Consultar también `db-datos/schema.js`, `rust/src/api/main.rs` y `sepa/db/schema.ts` del repositorio de referencia para contrastar los formatos; no se presupone que exista un servicio público estable.
