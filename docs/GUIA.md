# Guía PoStoreBaires — Beta Python/Qt

1. Ejecutá `python run.py` con las dependencias instaladas, o abrí `PoStoreBaires.exe` del portable Windows completo.
2. El primer inicio tiene inventario vacío y turno cerrado. Cargá productos y abrí turno con el saldo inicial real. El lector debe emular teclado y enviar Enter.
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

Ventas, stock, carrito, turnos y ajustes se guardan localmente en SQLite. Exportá una copia desde Ajustes. Las imágenes y QR se leen desde sus archivos: no los muevas mientras usás la beta. No hay sincronización multicaja ni autenticación. Ver [catálogo Preciazo/SEPA](PRECIAZO.md).

Podés editar códigos y precios propios desde Insumos, sin una venta pendiente. Cambiar el código de un producto existente solicita confirmación antes de guardar; el anterior deja de encontrarlo. Si el nuevo código ya pertenece a otro producto, se rechaza con un aviso. La guía se abre dentro de la aplicación desde Ayuda. El archivo de documentación del catálogo también está disponible en el repositorio.

### Buscar productos al vender

En Caja, el botón **Buscar** con lupa junto al código abre un buscador dentro de la aplicación. Filtra por nombre o código mientras escribís y muestra precio y unidades disponibles descontando el carrito. Seleccioná un resultado y presioná **Agregar a la compra**, Enter en la búsqueda o doble clic para sumar una unidad. Cancelar no modifica la venta. Incluye todos los productos guardados en el inventario local, tanto manuales como creados a partir de una referencia. El catálogo externo no se vende directamente: primero requiere alta en Insumos con precio y stock propios. Se mantienen las validaciones de turno abierto, stock y guardado en disco.
