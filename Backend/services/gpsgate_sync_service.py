# services/gpsgate_sync_service.py

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from extensions import db
from models import RegistroLitro
from services.Ejemplo import ThingsBoardSimple


CONFIGURACION_CODIGOS = {
    "codigo1": {
        "dispositivo_id": 1,
        "clave_litros": "Litros_total",
        "clave_ibutton": "iButton_total",
    },
    "codigo2": {
        "dispositivo_id": 2,
        "clave_litros": "litrosFTotal",
        "clave_ibutton": "iButton",
    },
}


def _timestamp_a_fecha_utc_naive(
    raw_timestamp: Any,
) -> datetime:
    """
    Convierte un timestamp en milisegundos a datetime UTC
    sin zona horaria.

    Ese es el formato utilizado actualmente por RegistroLitro.fecha.
    """

    timestamp = int(raw_timestamp)

    return datetime.fromtimestamp(
        timestamp / 1000,
        tz=timezone.utc,
    ).replace(
        tzinfo=None,
        microsecond=0,
    )


def _normalizar_litros(
    valor: Any,
) -> Optional[float]:
    if valor is None:
        return None

    try:
        return float(
            str(valor).strip().replace(",", ".")
        )
    except (TypeError, ValueError):
        return None


def _crear_mapa_ibutton(
    registros: List[Dict[str, Any]],
) -> Dict[int, Any]:
    resultado: Dict[int, Any] = {}

    for registro in registros or []:
        if not isinstance(registro, dict):
            continue

        try:
            timestamp = int(
                registro.get("ts")
            )
        except (TypeError, ValueError):
            continue

        resultado[timestamp] = registro.get(
            "value"
        )

    return resultado


def _buscar_ibutton_cercano(
    timestamp: int,
    mapa_ibutton: Dict[int, Any],
    tolerancia_ms: int = 5000,
) -> Optional[str]:
    """
    Busca primero un iButton con el mismo timestamp.

    Si no existe, utiliza el más cercano dentro de la
    tolerancia configurada.
    """

    if timestamp in mapa_ibutton:
        valor = mapa_ibutton[timestamp]

        if valor in (None, "", "None"):
            return None

        return str(valor)

    mejor_valor = None
    mejor_distancia = tolerancia_ms + 1

    for timestamp_ibutton, valor in mapa_ibutton.items():
        distancia = abs(
            timestamp_ibutton - timestamp
        )

        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_valor = valor

    if (
        mejor_distancia <= tolerancia_ms
        and mejor_valor not in (
            None,
            "",
            "None",
        )
    ):
        return str(mejor_valor)

    return None


def _extraer_registros_gpsgate(
    resultado_gpsgate: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Convierte la estructura codigo1/codigo2 del servicio
    GpsGate al formato utilizado por RegistroLitro.
    """

    registros_por_clave: Dict[
        Tuple[datetime, int],
        Dict[str, Any],
    ] = {}

    for codigo, configuracion in (
        CONFIGURACION_CODIGOS.items()
    ):
        datos_codigo = (
            resultado_gpsgate.get(codigo)
            or {}
        )

        litros_data = datos_codigo.get(
            configuracion["clave_litros"],
            [],
        )

        ibutton_data = datos_codigo.get(
            configuracion["clave_ibutton"],
            [],
        )

        mapa_ibutton = _crear_mapa_ibutton(
            ibutton_data
        )

        dispositivo_id = configuracion[
            "dispositivo_id"
        ]

        for registro_litros in litros_data:
            if not isinstance(
                registro_litros,
                dict,
            ):
                continue

            raw_timestamp = registro_litros.get(
                "ts"
            )

            litros = _normalizar_litros(
                registro_litros.get("value")
            )

            # ============================================================
            # IGNORAR LITROS VACÍOS, EN 0 O NEGATIVOS
            # ============================================================
            #
            # GpsGate puede entregar telemetrías cuyo valor de litros
            # sea 0. Esos registros no deben ser insertados ni utilizados
            # para actualizar registros existentes.
            #
            # ============================================================

            if (
                raw_timestamp is None
                or litros is None
                or litros <= 0
            ):
                continue

            try:
                timestamp = int(
                    raw_timestamp
                )

                fecha_utc = (
                    _timestamp_a_fecha_utc_naive(
                        timestamp
                    )
                )

            except (
                TypeError,
                ValueError,
                OSError,
                OverflowError,
            ):
                continue

            ibutton = _buscar_ibutton_cercano(
                timestamp=timestamp,
                mapa_ibutton=mapa_ibutton,
            )

            clave = (
                fecha_utc,
                dispositivo_id,
            )

            # Si GpsGate entrega dos registros con la misma
            # fecha y dispositivo, se conserva el último.
            registros_por_clave[clave] = {
                "fecha": fecha_utc,
                "litros": litros,
                "ibutton": ibutton,
                "dispositivo_id": dispositivo_id,
            }

    return list(
        registros_por_clave.values()
    )


def _cargar_registros_existentes(
    registros_nuevos: List[Dict[str, Any]],
) -> Dict[
    Tuple[datetime, int],
    RegistroLitro,
]:
    if not registros_nuevos:
        return {}

    fechas = [
        registro["fecha"]
        for registro in registros_nuevos
    ]

    dispositivos = {
        registro["dispositivo_id"]
        for registro in registros_nuevos
    }

    fecha_minima = min(fechas)
    fecha_maxima = max(fechas)

    registros_existentes = (
        RegistroLitro.query
        .filter(
            RegistroLitro.fecha
            >= fecha_minima,
            RegistroLitro.fecha
            <= fecha_maxima,
            RegistroLitro.dispositivo_id.in_(
                dispositivos
            ),
        )
        .all()
    )

    return {
        (
            registro.fecha.replace(
                microsecond=0
            ),
            registro.dispositivo_id,
        ): registro
        for registro in registros_existentes
    }


def sincronizar_rango(
    fecha_inicio: str,
    fecha_fin: str,
) -> Dict[str, Any]:
    """
    Consulta GpsGate y guarda los datos procesados en
    registros_litros.

    Reglas:

    - No duplica fecha + dispositivo_id.
    - Conserva dato1_id y dato2_id existentes.
    - Actualiza litros e iButton cuando el registro existe.
    - Inserta los registros nuevos con las referencias en null.
    - Ignora litros iguales o menores a 0.
    - Hace un solo commit al finalizar.
    """

    print(
        "[GPSGATE-SYNC] "
        f"Sincronizando {fecha_inicio} "
        f"al {fecha_fin}"
    )

    try:
        with ThingsBoardSimple() as servicio:
            resultado_gpsgate = (
                servicio.consultar_por_fechas(
                    fecha_inicio,
                    fecha_fin,
                )
            )

        registros_gpsgate = (
            _extraer_registros_gpsgate(
                resultado_gpsgate
            )
        )

        if not registros_gpsgate:
            return {
                "ok": True,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "recibidos": 0,
                "insertados": 0,
                "actualizados": 0,
                "sin_cambios": 0,
            }

        mapa_existentes = (
            _cargar_registros_existentes(
                registros_gpsgate
            )
        )

        insertados = 0
        actualizados = 0
        sin_cambios = 0

        for registro_gpsgate in registros_gpsgate:
            clave = (
                registro_gpsgate["fecha"],
                registro_gpsgate[
                    "dispositivo_id"
                ],
            )

            registro_existente = (
                mapa_existentes.get(clave)
            )

            if registro_existente is None:
                nuevo_registro = RegistroLitro(
                    fecha=registro_gpsgate["fecha"],
                    litros=registro_gpsgate["litros"],
                    ibutton=registro_gpsgate[
                        "ibutton"
                    ],
                    dispositivo_id=(
                        registro_gpsgate[
                            "dispositivo_id"
                        ]
                    ),
                    dato1_id=None,
                    dato2_id=None,
                )

                db.session.add(
                    nuevo_registro
                )

                mapa_existentes[clave] = (
                    nuevo_registro
                )

                insertados += 1
                continue

            cambio = False

            litros_nuevos = registro_gpsgate[
                "litros"
            ]

            ibutton_nuevo = registro_gpsgate[
                "ibutton"
            ]

            if (
                registro_existente.litros
                != litros_nuevos
            ):
                registro_existente.litros = (
                    litros_nuevos
                )

                cambio = True

            if (
                ibutton_nuevo is not None
                and registro_existente.ibutton
                != ibutton_nuevo
            ):
                registro_existente.ibutton = (
                    ibutton_nuevo
                )

                cambio = True

            # No modificar jamás:
            #
            # registro_existente.dato1_id
            # registro_existente.dato2_id

            if cambio:
                actualizados += 1
            else:
                sin_cambios += 1

        db.session.commit()

        resumen = {
            "ok": True,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "recibidos": len(
                registros_gpsgate
            ),
            "insertados": insertados,
            "actualizados": actualizados,
            "sin_cambios": sin_cambios,
        }

        print(
            "[GPSGATE-SYNC] "
            f"Resultado: {resumen}"
        )

        return resumen

    except Exception:
        db.session.rollback()
        raise