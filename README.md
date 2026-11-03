# Pilgrim API Gateway - LAIKA Club (pilgrim)

Puerta de enlace perimetral (API Gateway), enrutador asincrono de alto rendimiento y proxy inverso centralizado para el ecosistema distribuido de LAIKA Club.

---

## 1. Descripcion General

`Pilgrim` constituye el nucleo de interconexion de la plataforma LAIKA Club. Su proposito es aislar la infraestructura de microservicios internos del trafico exterior, proporcionando un punto unico de entrada (`Single Entry Point`) en el puerto 8000. 

Pilgrim gestiona la resolucion de peticiones procedentes de los cuatro modulos web desacoplados (`laika-admin`, `laika-gestor`, `laika-operador`, `matis-solid`), la aplicacion movil (`LaikaMobil`) y el cliente web publico, enrutando cada llamada hacia su respectivo microservicio en funcion del rol, la ruta y las cabeceras de autorizacion.

---

## 2. Stack Tecnologico

- **Lenguaje de Programacion**: Python 3.11 / 3.13
- **Framework Web**: FastAPI 0.115+
- **Servidor ASGI**: Uvicorn
- **Cliente HTTP Asincrono (Proxy Inverso)**: HTTPX 0.28+
- **Control de Acceso y Cabeceras**: FastAPI CORSMiddleware
- **Persistencia Directa de Auditoria**: Driver PyMySQL para contingencias y anuncios

---

## 3. Mapa de Enrutamiento y Rangos de Microservicios

Pilgrim unifica el acceso mediante prefijos `/api/*` y mapea hacia la arquitectura de microservicios distribuida:

| Prefijo de Ruta | Microservicio de Destino | Tecnologia | Puerto Interno |
| :--- | :--- | :--- | :--- |
| `/api/auth/*` | Autenticacion y Cuentas (`laika_auth`) | Java Spring Boot | 8101 |
| `/api/admin/*` | Administracion Central (`laika_admin`) | Java Spring Boot | 8102 |
| `/api/stats/*` | Estadisticas y Monitoreo (`laika_stats`) | Java Spring Boot | 8103 |
| `/api/events/*` | Eventos y Recintos (`laika_events`) | Java Spring Boot | 8201 |
| `/api/manager/*` | Rutas de Gestores (`laika_events` / `tickets`) | Java Spring Boot | 8201 / 8202 |
| `/api/tickets/*` | Compra y Validacion (`laika_tickets`) | Java Spring Boot | 8202 |
| `/api/staff/*` | Terminal Operativa (`laika_tickets` / `admin`) | Java Spring Boot | 8202 / 8102 |
| `/api/merchandise/*` | Tienda Oficial (`laika_merchandise`) | Java Spring Boot | 8203 |
| `/api/wearables/*` | Dispositivos IoT (`wearables_backend`) | Node.js Express | 8204 |
| `/api/achievements/*`| Gamificacion (`laika_achievements`) | Java Spring Boot | 8301 |
| `/api/analytics/*` | Analitica Transaccional (`laika_analytics`) | Java Spring Boot | 8302 |
| `/api/analytics/ml/*` | Modelos Predictivos y Big Data | Python PySpark | 8303 |

---

## 4. Caracteristicas de Seguridad y Monitoreo

1. **Politica CORS Universal**:
   - Middleware configurado para admitir llamadas seguras con credenciales (`allow_credentials=True`) desde cualquier origen autorizado (puertos locales 3000, 3010, 3020, 3030, 3040 y tuneles externos).

2. **Registro de Logs de Peticiones y Errores**:
   - Middleware HTTP nativo que intercepta y registra cada peticion en el directorio `tiradero/logpruebas/`:
     - `api_gateway.log`: Registra metodo, ruta, codigo de estado, IP cliente y tiempo de respuesta en milisegundos.
     - `errores_sistema.log`: Captura excepciones 4xx y volcados de pila completos ante errores 500 para diagnostico rapido.

3. **Tunelizacion para Dispositivos Moviles (LaikaMobil)**:
   - Integracion con LocalTunnel mediante el script `iniciar_tunel_pilgrim.bat`, permitiendo exponer el puerto 8000 a internet de forma temporal para que la aplicacion movil pueda interactuar con el backend desde redes moviles (4G/5G).

---

## 5. Estructura del Modulo

```
pilgrim/
├── core/
│   ├── cache.py             # Logica de almacenamiento en cache de respuestas
│   ├── config.py            # Carga de variables de entorno y puertos de servicios
│   └── proxy.py             # Motor HTTPX para reenvio de peticiones y respuestas
├── data/                    # Archivos auxiliares de soporte
├── routers/
│   ├── __init__.py          # Exportacion unificada de routers
│   ├── admin.py             # Rutas exclusivas del panel de administracion
│   ├── auth.py              # Proxy de autenticacion y validacion de tokens
│   ├── gestor.py            # Proxy para gestion de eventos y transacciones
│   ├── operador.py          # Proxy para escaneo y validacion en torniquetes
│   └── public.py            # Catalogo general, eventos, tienda y boletos
├── Dockerfile               # Configuracion de contenedor para despliegue
├── main.py                  # Instancia principal de FastAPI y registro de middlewares
├── requirements.txt         # Dependencias Python
├── run_pilgrim.py           # Script de ejecucion local con Uvicorn
└── test_gateway.py          # Pruebas de conectividad y latencia
```

---

## 6. Variables de Entorno

Pilgrim lee su configuracion desde el archivo `.env` o variables del sistema:

| Variable | Descripcion | Valor Predeterminado |
| :--- | :--- | :--- |
| `PILGRIM_HOST` | Direccion de enlace del servidor | `0.0.0.0` |
| `PILGRIM_PORT` | Puerto de escucha | `8000` |
| `PILGRIM_PROXY_TIMEOUT` | Timeout para respuestas de microservicios | `35.0` (segundos) |
| `PILGRIM_CACHE_TTL` | Tiempo de vida para cache publica | `60` (segundos) |
| `AUTH_SERVICE_URL` | URL del microservicio de autenticacion | `http://127.0.0.1:8101` |
| `ADMIN_SERVICE_URL` | URL del microservicio de administracion | `http://127.0.0.1:8102` |
| `STATS_SERVICE_URL` | URL del microservicio de estadisticas | `http://127.0.0.1:8103` |
| `EVENTS_SERVICE_URL` | URL del microservicio de eventos | `http://127.0.0.1:8201` |
| `TICKETS_SERVICE_URL` | URL del microservicio de boletos | `http://127.0.0.1:8202` |
| `MERCHANDISE_SERVICE_URL` | URL del microservicio de mercancia | `http://127.0.0.1:8203` |
| `WEARABLES_SERVICE_URL` | URL del microservicio de wearables | `http://127.0.0.1:8204` |
| `ACHIEVEMENTS_SERVICE_URL`| URL del microservicio de logros | `http://127.0.0.1:8301` |
| `ANALYTICS_SERVICE_URL` | URL del microservicio de analitica Java | `http://127.0.0.1:8302` |
| `ANALYTICS_BIGDATA_URL` | URL del microservicio PySpark BigData | `http://127.0.0.1:8303` |

---

## 7. Instalacion y Ejecucion

### Ejecucion con Entorno Virtual de Python
```bash
# Desde la raiz del proyecto LaikaClub
.venv\Scripts\python.exe pilgrim\run_pilgrim.py
```
O bien:
```bash
cd pilgrim
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Ejecucion en Contenedor Docker
```bash
docker build -t laika-pilgrim -f pilgrim/Dockerfile .
docker run -p 8000:8000 --name laika_gateway laika-pilgrim
```

### Verificacion de Estado
Visita `http://localhost:8000/api/health` en el navegador para confirmar que el gateway se encuentra operativo. La documentacion OpenAPI interactiva estara disponible en `http://localhost:8000/docs`.
