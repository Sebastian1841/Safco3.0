# routes_datos.py

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import RegistroLitro, Dato1, Dato2
from services.Ejemplo import ThingsBoardSimple
from utils.timezone import CHILE_TZ


datos_bp = Blueprint("datos_bp", __name__)


# ============================================================
# HELPERS DE FECHAS
# ============================================================

def _resolver_rango_consulta():
    """
    Resuelve el rango solicitado por GET /datos.

    Sin parámetros:
        Devuelve las últimas 24 horas exactas.

    Con fecha_inicio y/o fecha_fin:
        Devuelve el rango manual seleccionado.
    """

    fecha_inicio_param = (
        request.args.get("fecha_inicio") or ""
    ).strip()

    fecha_fin_param = (
        request.args.get("fecha_fin") or ""
    ).strip()

    ahora_chile = datetime.now(CHILE_TZ)

    # --------------------------------------------------------
    # COMPORTAMIENTO PREDETERMINADO: ÚLTIMAS 24 HORAS
    # --------------------------------------------------------

    if not fecha_inicio_param and not fecha_fin_param:
        fecha_inicio_exacta = (
            ahora_chile - timedelta(hours=24)
        )

        fecha_fin_exacta = ahora_chile

        return (
            fecha_inicio_exacta.strftime("%Y-%m-%d"),
            fecha_fin_exacta.strftime("%Y-%m-%d"),
            fecha_inicio_exacta,
            fecha_fin_exacta,
            True,
        )

    # --------------------------------------------------------
    # CONSULTA MANUAL
    # --------------------------------------------------------

    if fecha_fin_param:
        try:
            fecha_fin = datetime.strptime(
                fecha_fin_param,
                "%Y-%m-%d",
            ).date()

        except ValueError as error:
            raise ValueError(
                "fecha_fin debe tener formato YYYY-MM-DD."
            ) from error

    else:
        fecha_fin = ahora_chile.date()

    if fecha_inicio_param:
        try:
            fecha_inicio = datetime.strptime(
                fecha_inicio_param,
                "%Y-%m-%d",
            ).date()

        except ValueError as error:
            raise ValueError(
                "fecha_inicio debe tener formato YYYY-MM-DD."
            ) from error

    else:
        fecha_inicio = fecha_fin

    if fecha_inicio > fecha_fin:
        raise ValueError(
            "fecha_inicio no puede ser posterior a fecha_fin."
        )

    cantidad_dias = (
        fecha_fin - fecha_inicio
    ).days + 1

    # Límite máximo de consulta: 366 días.
    if cantidad_dias > 366:
        fecha_inicio = (
            fecha_fin - timedelta(days=365)
        )

    return (
        fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin.strftime("%Y-%m-%d"),
        None,
        None,
        False,
    )


def _resolver_rango_base_datos(
    fecha_inicio_str,
    fecha_fin_str,
    fecha_inicio_exacta,
    fecha_fin_exacta,
    usar_ultimas_24_horas,
):
    """
    Convierte el rango solicitado en horario de Chile
    a UTC naive, que es el formato guardado en PostgreSQL.
    """

    if usar_ultimas_24_horas:
        inicio_db = (
            fecha_inicio_exacta
            .astimezone(timezone.utc)
            .replace(
                tzinfo=None,
                microsecond=0,
            )
        )

        fin_db_exclusivo = (
            fecha_fin_exacta
            .astimezone(timezone.utc)
            .replace(
                tzinfo=None,
                microsecond=0,
            )
            + timedelta(seconds=1)
        )

        return inicio_db, fin_db_exclusivo

    inicio_local = datetime.strptime(
        fecha_inicio_str,
        "%Y-%m-%d",
    ).replace(
        tzinfo=CHILE_TZ
    )

    fin_local_exclusivo = (
        datetime.strptime(
            fecha_fin_str,
            "%Y-%m-%d",
        )
        + timedelta(days=1)
    ).replace(
        tzinfo=CHILE_TZ
    )

    inicio_db = (
        inicio_local
        .astimezone(timezone.utc)
        .replace(
            tzinfo=None,
            microsecond=0,
        )
    )

    fin_db_exclusivo = (
        fin_local_exclusivo
        .astimezone(timezone.utc)
        .replace(
            tzinfo=None,
            microsecond=0,
        )
    )

    return inicio_db, fin_db_exclusivo


def _construir_mapas_nombres(db_items):
    """
    Obtiene los nombres de Dato1 y Dato2 utilizando
    consultas agrupadas.

    Evita ejecutar una consulta SQL por cada registro.
    """

    dato1_ids = {
        item.dato1_id
        for item in db_items
        if item.dato1_id is not None
    }

    dato2_ids = {
        item.dato2_id
        for item in db_items
        if item.dato2_id is not None
    }

    dato1_map = {}
    dato2_map = {}

    if dato1_ids:
        datos1 = (
            Dato1.query
            .filter(
                Dato1.id.in_(dato1_ids)
            )
            .all()
        )

        dato1_map = {
            item.id: item.nombre
            for item in datos1
        }

    if dato2_ids:
        datos2 = (
            Dato2.query
            .filter(
                Dato2.id.in_(dato2_ids)
            )
            .all()
        )

        dato2_map = {
            item.id: item.nombre
            for item in datos2
        }

    return dato1_map, dato2_map


def _fecha_db_a_chile(fecha_db):
    """
    Convierte una fecha UTC almacenada en PostgreSQL
    a horario local de Chile.
    """

    if fecha_db.tzinfo is None:
        fecha_utc = fecha_db.replace(
            tzinfo=timezone.utc
        )
    else:
        fecha_utc = fecha_db.astimezone(
            timezone.utc
        )

    return fecha_utc.astimezone(
        CHILE_TZ
    )


# ============================================================
# GET /datos
# ============================================================

@datos_bp.route(
    "/datos",
    methods=["GET"],
)
def get_datos_fusionados():
    """
    Obtiene los registros exclusivamente desde PostgreSQL.

    GpsGate ya no se consulta cuando el frontend abre
    la página. El contenedor gpsgate_sync mantiene la tabla
    registros_litros actualizada automáticamente.
    """

    try:
        try:
            (
                fecha_inicio_str,
                fecha_fin_str,
                fecha_inicio_exacta,
                fecha_fin_exacta,
                usar_ultimas_24_horas,
            ) = _resolver_rango_consulta()

        except ValueError as error:
            return jsonify({
                "error": str(error),
            }), 400

        (
            inicio_db,
            fin_db_exclusivo,
        ) = _resolver_rango_base_datos(
            fecha_inicio_str,
            fecha_fin_str,
            fecha_inicio_exacta,
            fecha_fin_exacta,
            usar_ultimas_24_horas,
        )

        # ----------------------------------------------------
        # CONSULTA EXCLUSIVA A POSTGRESQL
        # ----------------------------------------------------

        db_items = (
            RegistroLitro.query
            .filter(
                RegistroLitro.fecha >= inicio_db,
                RegistroLitro.fecha < fin_db_exclusivo,
            )
            .order_by(
                RegistroLitro.fecha.desc(),
                RegistroLitro.id.desc(),
            )
            .all()
        )

        (
            dato1_map,
            dato2_map,
        ) = _construir_mapas_nombres(
            db_items
        )

        resultado = []

        for item in db_items:
            fecha_local = _fecha_db_a_chile(
                item.fecha
            )

            resultado.append({
                "id": item.id,
                "fecha": fecha_local.isoformat(),
                "litros": item.litros,
                "ibutton": (
                    item.ibutton
                    if item.ibutton not in (
                        None,
                        "",
                    )
                    else "N/A"
                ),
                "dispositivo_id": (
                    item.dispositivo_id
                ),
                "dato1_id": item.dato1_id,
                "dato2_id": item.dato2_id,
                "dato1_nombre": dato1_map.get(
                    item.dato1_id
                ),
                "dato2_nombre": dato2_map.get(
                    item.dato2_id
                ),
            })

        # El frontend espera directamente un arreglo.
        respuesta = jsonify(resultado)

        respuesta.headers[
            "X-Fecha-Inicio"
        ] = fecha_inicio_str

        respuesta.headers[
            "X-Fecha-Fin"
        ] = fecha_fin_str

        respuesta.headers[
            "X-Rango-Predeterminado"
        ] = (
            "ultimas-24-horas"
            if usar_ultimas_24_horas
            else "rango-manual"
        )

        respuesta.headers[
            "X-Fuente-Datos"
        ] = "postgresql"

        respuesta.headers[
            "X-Total-Registros"
        ] = str(len(resultado))

        if usar_ultimas_24_horas:
            respuesta.headers[
                "X-Fecha-Inicio-Exacta"
            ] = fecha_inicio_exacta.isoformat()

            respuesta.headers[
                "X-Fecha-Fin-Exacta"
            ] = fecha_fin_exacta.isoformat()

        return respuesta, 200

    except Exception as error:
        return jsonify({
            "error": "Error interno en /datos",
            "detail": str(error),
        }), 500


# ============================================================
# POST /datos
# ============================================================

@datos_bp.route(
    "/datos",
    methods=["POST"],
)
def create_datos_referencia():
    data = request.get_json(
        silent=True
    ) or {}

    try:
        if "fecha" not in data:
            return jsonify({
                "error": (
                    "El campo fecha es obligatorio."
                )
            }), 400

        raw_fecha = data["fecha"]

        dispositivo_id = data.get(
            "dispositivo_id"
        )

        if dispositivo_id is None:
            return jsonify({
                "error": (
                    "El campo dispositivo_id "
                    "es obligatorio."
                )
            }), 400

        fecha_obj = None

        if isinstance(
            raw_fecha,
            (int, float),
        ):
            fecha_obj = datetime.utcfromtimestamp(
                float(raw_fecha) / 1000
            )

        elif (
            isinstance(raw_fecha, str)
            and raw_fecha.isdigit()
        ):
            fecha_obj = datetime.utcfromtimestamp(
                int(raw_fecha) / 1000
            )

        elif isinstance(raw_fecha, str):
            try:
                fecha_obj = datetime.fromisoformat(
                    raw_fecha.replace(
                        "Z",
                        "+00:00",
                    )
                )

                if fecha_obj.tzinfo is not None:
                    fecha_obj = (
                        fecha_obj
                        .astimezone(timezone.utc)
                    )

                else:
                    fecha_obj = (
                        fecha_obj
                        .replace(tzinfo=CHILE_TZ)
                        .astimezone(timezone.utc)
                    )

            except ValueError:
                return jsonify({
                    "error": (
                        "Formato de fecha "
                        "ISO 8601 no válido."
                    )
                }), 400

        else:
            return jsonify({
                "error": (
                    "Formato de fecha "
                    "no compatible."
                )
            }), 400

        fecha_db = fecha_obj.replace(
            microsecond=0,
            tzinfo=None,
        )

        item = RegistroLitro.query.filter_by(
            fecha=fecha_db,
            dispositivo_id=dispositivo_id,
        ).first()

        if item:
            if "litros" in data:
                item.litros = data["litros"]

            if "ibutton" in data:
                item.ibutton = data["ibutton"]

            if "dato1_id" in data:
                item.dato1_id = data["dato1_id"]

            if "dato2_id" in data:
                item.dato2_id = data["dato2_id"]

            db.session.commit()

            return jsonify(
                item.to_dict()
            ), 200

        nuevo_item = RegistroLitro(
            fecha=fecha_db,
            litros=data.get("litros"),
            ibutton=data.get("ibutton"),
            dispositivo_id=dispositivo_id,
            dato1_id=data.get("dato1_id"),
            dato2_id=data.get("dato2_id"),
        )

        db.session.add(nuevo_item)
        db.session.commit()

        return jsonify(
            nuevo_item.to_dict()
        ), 201

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": (
                "Conflicto: ya existe un registro "
                "con esta fecha y dispositivo."
            )
        }), 409

    except (
        TypeError,
        KeyError,
        ValueError,
        exc.SQLAlchemyError,
    ) as error:
        db.session.rollback()

        return jsonify({
            "error": (
                "Error general al guardar o "
                f"actualizar el registro: {error}"
            )
        }), 400


# ============================================================
# PATCH /datos/<item_id>
# ============================================================

@datos_bp.route(
    "/datos/<int:item_id>",
    methods=["PATCH"],
)
def update_datos_referencia(item_id):
    item = db.session.get(
        RegistroLitro,
        item_id,
    )

    if not item:
        return jsonify({
            "message": (
                "Registro no encontrado. "
                "Use POST para crear."
            )
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    try:
        if "litros" in data:
            item.litros = data["litros"]

        if "ibutton" in data:
            item.ibutton = data["ibutton"]

        if "dato1_id" in data:
            item.dato1_id = data["dato1_id"]

        if "dato2_id" in data:
            item.dato2_id = data["dato2_id"]

        db.session.commit()

        return jsonify(
            item.to_dict()
        ), 200

    except exc.SQLAlchemyError as error:
        db.session.rollback()

        return jsonify({
            "error": (
                "Error al actualizar: "
                f"{error}"
            )
        }), 400


# ============================================================
# GET /dispositivos
# ============================================================

@datos_bp.route(
    "/dispositivos",
    methods=["GET"],
)
def dispositivos():
    """
    Obtiene la lista de dispositivos configurados.

    Esta ruta puede consultar la configuración de GpsGate,
    pero no descarga los tracks ni los litros históricos.
    """

    try:
        servicio = ThingsBoardSimple()

        try:
            dispositivos_configurados = (
                servicio.listar_dispositivos()
            )
        finally:
            servicio.cerrar()

        equivalencias = {
            "codigo1": {
                "id": 1,
                "nombre": "Tanque Fijo",
            },
            "codigo2": {
                "id": 2,
                "nombre": "Tanque Movil",
            },
        }

        payload = []

        for dispositivo in dispositivos_configurados:
            codigo = dispositivo.get(
                "codigo"
            )

            configuracion = equivalencias.get(
                codigo
            )

            if not configuracion:
                continue

            payload.append({
                "id": configuracion["id"],
                "nombre": configuracion["nombre"],
            })

        payload.sort(
            key=lambda item: item["id"]
        )

        return jsonify(payload), 200

    except Exception as error:
        return jsonify({
            "error": (
                "Error interno en /dispositivos"
            ),
            "detail": str(error),
        }), 500