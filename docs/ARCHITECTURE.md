# Arquitectura y alcance

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
