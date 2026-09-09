# SAFCO – Backend (Flask + SQLAlchemy + PostgreSQL)

API Flask que integra datos de ThingsBoard y la base de datos local para exponer registros de combustible y referencias.

## Arranque rapido

- Con Docker (recomendado)
  1. Desde la raiz del repo: `docker compose up --build`
  2. Backend: http://localhost:5000
  3. Base de datos: Postgres expuesto en host `localhost:5433` (contenedor `5432`)

- Local (Python 3.11)
  1. `cd Backend`
  2. (opcional) crear venv
  3. `pip install -r requirements.txt`
  4. Exportar `DATABASE_URL` (por ejemplo `postgresql://safcouser:safcopassword@localhost:5433/safcodb`)
  5. `python app.py`

## Variables de entorno

- `DATABASE_URL` – cadena de conexion a PostgreSQL.
- `THINGSBOARD_HOST` – URL base de ThingsBoard.

En docker-compose ya se configuran:

```
DATABASE_URL=postgresql://safcouser:safcopassword@db:5432/safcodb
THINGSBOARD_HOST=http://localhost:8080
```

## Endpoints principales

- `GET /datos`
  - Params: `fecha_inicio` (YYYY-MM-DD), `fecha_fin` (YYYY-MM-DD)
  - Fusiona datos de TB con la DB. Convierte `fecha` a hora de Chile (ISO con offset) para el cliente.
- `POST /datos` – insercion de registros manuales (ver campos del modelo `RegistroLitro`).
- `PATCH /datos/<id>` – actualizacion puntual (ej: `dato1_id`, `dato2_id`).
- `GET /dato1`, `POST /dato1`, `PUT/DELETE /dato1/<id>` – CRUD referencias Dato1.
- `GET /dato2`, `POST /dato2`, `PUT/DELETE /dato2/<id>` – CRUD referencias Dato2.
- `GET /litros_control`, `POST /litros_control`, `PUT/DELETE /litros_control/<id>` – control de litros por dia/dispositivo.
- `GET /dispositivos` – IDs detectados en TB con nombres amigables.

## Modelos

- `RegistroLitro`: `id`, `fecha` (naive UTC), `litros`, `ibutton`, `dispositivo_id`, `dato1_id`, `dato2_id`.
  - Unicidad: `(fecha, dispositivo_id)`.
- `Dato1` / `Dato2`: referencias simples `id`, `nombre`.
- `LitrosControl`: `fecha`, `dispositivo`, `litros_inicio`, `litros_final`, `diferencia_manual`.

## Zona horaria

- La fecha se almacena como NAIVE en UTC. Al serializar al cliente se hace:
  1) `fecha.replace(tzinfo=timezone.utc)`
  2) `.astimezone(CHILE_TZ)` donde `CHILE_TZ` se define con `timedelta(hours=-3)` (ajustar a -4 en invierno)
  3) `.isoformat()`

## Persistencia

- `db.create_all()` crea tablas si no existen al iniciar la app.
- Volumen de Postgres en docker-compose: `pgdata`.

## Requisitos y notas

- Python 3.11, Flask, Flask-CORS, Flask-SQLAlchemy, psycopg2-binary.
- Si compilas local y psycopg2 falla, usa Docker o instala dependencias de libpq.
- CORS esta habilitado para desarrollo; restringir origenes en produccion.

## Solucion de problemas

- `409 Conflicto` al insertar en `/datos`: existe un registro con el mismo `(fecha, dispositivo_id)`.
- Desfase de fechas: el cliente opera con dias locales; si prefieres UTC en cliente ajusta conversion en `app.py` o normaliza en el frontend.
- Conectividad DB en host: usa puerto `5433` (mapeado a `5432` del contenedor).

## Estructura

- `Backend/app.py` – app Flask, modelos, endpoints
- `Backend/Ejemplo.py` – integracion ThingsBoard (stub/implementacion)
- `Backend/requirements.txt` – dependencias
- `Backend/Dockerfile` – imagen de la API

