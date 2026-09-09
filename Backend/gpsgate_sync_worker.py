# gpsgate_sync_worker.py

import argparse
import os
import signal
import sys
import time
from datetime import datetime, timedelta

from app import app
from services.gpsgate_sync_service import sincronizar_rango
from utils.timezone import CHILE_TZ


_detener_worker = False


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Sincronización rápida:
# cada 60 segundos revisa ayer + hoy.
INTERVALO_RAPIDO_DEFAULT = 60

# Reconciliación intermedia:
# cada 1 hora vuelve a revisar los últimos 15 días.
INTERVALO_RECONCILIACION_DEFAULT = 60 * 60
DIAS_RECONCILIACION_DEFAULT = 15

# Reconciliación profunda:
# una vez al día vuelve a revisar los últimos 30 días.
INTERVALO_RECONCILIACION_PROFUNDA_DEFAULT = 24 * 60 * 60
DIAS_RECONCILIACION_PROFUNDA_DEFAULT = 30


def _manejar_senal(signum, frame):
    """
    Permite detener el worker limpiamente cuando Docker
    envía SIGTERM o cuando se presiona Ctrl+C.
    """
    global _detener_worker

    print(
        f"[GPSGATE-WORKER] Señal {signum} recibida. "
        "Deteniendo worker..."
    )

    _detener_worker = True


def _fecha_chile_actual():
    return datetime.now(CHILE_TZ).date()


def _rango_ultimos_dias(cantidad_dias):
    """
    Devuelve un rango inclusivo terminado en hoy.

    Ejemplo:
        cantidad_dias=2
        -> ayer / hoy

        cantidad_dias=15
        -> hace 14 días / hoy
    """
    cantidad_dias = max(1, int(cantidad_dias))

    fecha_hoy = _fecha_chile_actual()
    fecha_inicio = fecha_hoy - timedelta(
        days=cantidad_dias - 1
    )

    return (
        fecha_inicio.strftime("%Y-%m-%d"),
        fecha_hoy.strftime("%Y-%m-%d"),
    )


def _obtener_rango_rapido():
    """
    El rango rápido siempre revisa ayer + hoy.
    """
    return _rango_ultimos_dias(2)


def ejecutar_sincronizacion(
    fecha_inicio=None,
    fecha_fin=None,
    tipo="rápida",
):
    """
    Ejecuta una sincronización dentro del contexto Flask.
    """

    if not fecha_inicio or not fecha_fin:
        fecha_inicio, fecha_fin = _obtener_rango_rapido()

    print(
        "[GPSGATE-WORKER] "
        f"Inicio de sincronización {tipo}: "
        f"{fecha_inicio} al {fecha_fin}"
    )

    inicio = time.monotonic()

    try:
        with app.app_context():
            resultado = sincronizar_rango(
                fecha_inicio,
                fecha_fin,
            )

        duracion = round(
            time.monotonic() - inicio,
            2,
        )

        print(
            "[GPSGATE-WORKER] "
            f"Sincronización {tipo} completada en "
            f"{duracion} segundos: {resultado}"
        )

        return resultado

    except Exception as error:
        duracion = round(
            time.monotonic() - inicio,
            2,
        )

        print(
            "[GPSGATE-WORKER][ERROR] "
            f"Sincronización {tipo} falló después de "
            f"{duracion} segundos: {error}",
            file=sys.stderr,
        )

        return {
            "ok": False,
            "tipo": tipo,
            "error": str(error),
        }


def ejecutar_reconciliacion(
    cantidad_dias,
    tipo="reconciliación",
):
    """
    Vuelve a consultar días anteriores para recuperar
    telemetría histórica que haya llegado tarde a GpsGate.
    """

    fecha_inicio, fecha_fin = _rango_ultimos_dias(
        cantidad_dias
    )

    print(
        "[GPSGATE-WORKER] "
        f"Ejecutando {tipo} de los últimos "
        f"{cantidad_dias} días."
    )

    return ejecutar_sincronizacion(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo=tipo,
    )


def _esperar_hasta_siguiente_iteracion(segundos):
    """
    Espera en bloques de un segundo para responder rápidamente
    a SIGTERM / Ctrl+C.
    """
    global _detener_worker

    segundos_esperados = 0

    while (
        segundos_esperados < segundos
        and not _detener_worker
    ):
        restante = segundos - segundos_esperados
        bloque = min(1, restante)

        time.sleep(bloque)
        segundos_esperados += bloque


def ejecutar_worker(
    intervalo_segundos,
    intervalo_reconciliacion,
    dias_reconciliacion,
    intervalo_reconciliacion_profunda,
    dias_reconciliacion_profunda,
):
    """
    Worker permanente.

    Estrategia:

    1. Cada intervalo rápido:
       revisa ayer + hoy.

    2. Cada hora:
       revisa los últimos 15 días.

    3. Una vez al día:
       revisa los últimos 30 días.

    sincronizar_rango() ya evita duplicados y conserva las
    referencias manuales dato1_id y dato2_id existentes.
    """

    global _detener_worker

    print("[GPSGATE-WORKER] Worker iniciado.")
    print(
        "[GPSGATE-WORKER] "
        f"Sincronización rápida: cada "
        f"{intervalo_segundos} segundos, ayer + hoy."
    )
    print(
        "[GPSGATE-WORKER] "
        f"Reconciliación: cada "
        f"{intervalo_reconciliacion} segundos, "
        f"últimos {dias_reconciliacion} días."
    )
    print(
        "[GPSGATE-WORKER] "
        f"Reconciliación profunda: cada "
        f"{intervalo_reconciliacion_profunda} segundos, "
        f"últimos {dias_reconciliacion_profunda} días."
    )

    # Al iniciar, actualiza lo reciente y además revisa
    # inmediatamente los últimos 15 días para recuperar
    # información atrasada después de reiniciar el contenedor.
    ejecutar_sincronizacion(
        tipo="rápida inicial"
    )

    if _detener_worker:
        return

    ejecutar_reconciliacion(
        dias_reconciliacion,
        tipo="reconciliación inicial",
    )

    if _detener_worker:
        return

    ahora_monotonic = time.monotonic()
    ultima_reconciliacion = ahora_monotonic
    ultima_reconciliacion_profunda = ahora_monotonic

    while not _detener_worker:
        _esperar_hasta_siguiente_iteracion(
            intervalo_segundos
        )

        if _detener_worker:
            break

        # Sincronización rápida de ayer + hoy.
        ejecutar_sincronizacion(
            tipo="rápida"
        )

        if _detener_worker:
            break

        ahora_monotonic = time.monotonic()

        # Reconciliación de los últimos 15 días.
        if (
            ahora_monotonic
            - ultima_reconciliacion
            >= intervalo_reconciliacion
        ):
            ejecutar_reconciliacion(
                dias_reconciliacion,
                tipo="reconciliación",
            )

            ultima_reconciliacion = time.monotonic()

        if _detener_worker:
            break

        ahora_monotonic = time.monotonic()

        # Reconciliación profunda de los últimos 30 días.
        if (
            ahora_monotonic
            - ultima_reconciliacion_profunda
            >= intervalo_reconciliacion_profunda
        ):
            ejecutar_reconciliacion(
                dias_reconciliacion_profunda,
                tipo="reconciliación profunda",
            )

            ultima_reconciliacion_profunda = time.monotonic()

    print(
        "[GPSGATE-WORKER] "
        "Worker detenido correctamente."
    )


def crear_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Sincroniza información de GpsGate "
            "con registros_litros."
        )
    )

    parser.add_argument(
        "--una-vez",
        action="store_true",
        help=(
            "Ejecuta una sincronización rápida "
            "y termina."
        ),
    )

    parser.add_argument(
        "--desde",
        type=str,
        default=None,
        help="Fecha inicial YYYY-MM-DD.",
    )

    parser.add_argument(
        "--hasta",
        type=str,
        default=None,
        help="Fecha final YYYY-MM-DD.",
    )

    parser.add_argument(
        "--intervalo",
        type=int,
        default=int(
            os.getenv(
                "GPSGATE_SYNC_INTERVAL",
                str(INTERVALO_RAPIDO_DEFAULT),
            )
        ),
        help=(
            "Segundos entre sincronizaciones rápidas. "
            "Predeterminado: 60."
        ),
    )

    parser.add_argument(
        "--intervalo-reconciliacion",
        type=int,
        default=int(
            os.getenv(
                "GPSGATE_RECONCILIATION_INTERVAL",
                str(INTERVALO_RECONCILIACION_DEFAULT),
            )
        ),
        help=(
            "Segundos entre reconciliaciones históricas. "
            "Predeterminado: 3600."
        ),
    )

    parser.add_argument(
        "--dias-reconciliacion",
        type=int,
        default=int(
            os.getenv(
                "GPSGATE_RECONCILIATION_DAYS",
                str(DIAS_RECONCILIACION_DEFAULT),
            )
        ),
        help=(
            "Días a revisar en la reconciliación. "
            "Predeterminado: 15."
        ),
    )

    parser.add_argument(
        "--intervalo-reconciliacion-profunda",
        type=int,
        default=int(
            os.getenv(
                "GPSGATE_DEEP_RECONCILIATION_INTERVAL",
                str(
                    INTERVALO_RECONCILIACION_PROFUNDA_DEFAULT
                ),
            )
        ),
        help=(
            "Segundos entre reconciliaciones profundas. "
            "Predeterminado: 86400."
        ),
    )

    parser.add_argument(
        "--dias-reconciliacion-profunda",
        type=int,
        default=int(
            os.getenv(
                "GPSGATE_DEEP_RECONCILIATION_DAYS",
                str(DIAS_RECONCILIACION_PROFUNDA_DEFAULT),
            )
        ),
        help=(
            "Días a revisar en la reconciliación profunda. "
            "Predeterminado: 30."
        ),
    )

    return parser


def _validar_fecha(valor, nombre_argumento, parser):
    try:
        return datetime.strptime(
            valor,
            "%Y-%m-%d",
        )
    except ValueError:
        parser.error(
            f"{nombre_argumento} debe tener "
            "formato YYYY-MM-DD."
        )


def main():
    signal.signal(
        signal.SIGTERM,
        _manejar_senal,
    )

    signal.signal(
        signal.SIGINT,
        _manejar_senal,
    )

    parser = crear_parser()
    argumentos = parser.parse_args()

    if argumentos.intervalo < 10:
        parser.error(
            "El intervalo rápido mínimo permitido "
            "es de 10 segundos."
        )

    if (
        argumentos.intervalo_reconciliacion
        < argumentos.intervalo
    ):
        parser.error(
            "El intervalo de reconciliación no puede "
            "ser menor que el intervalo rápido."
        )

    if (
        argumentos.intervalo_reconciliacion_profunda
        < argumentos.intervalo_reconciliacion
    ):
        parser.error(
            "El intervalo de reconciliación profunda "
            "no puede ser menor que el de reconciliación."
        )

    if argumentos.dias_reconciliacion < 2:
        parser.error(
            "La reconciliación debe revisar al menos "
            "2 días."
        )

    if (
        argumentos.dias_reconciliacion_profunda
        < argumentos.dias_reconciliacion
    ):
        parser.error(
            "Los días de reconciliación profunda "
            "deben ser mayores o iguales a los de "
            "reconciliación."
        )

    if bool(argumentos.desde) != bool(
        argumentos.hasta
    ):
        parser.error(
            "--desde y --hasta deben utilizarse juntos."
        )

    # Rango manual: conserva el funcionamiento anterior.
    if argumentos.desde and argumentos.hasta:
        fecha_inicio = _validar_fecha(
            argumentos.desde,
            "--desde",
            parser,
        )

        fecha_fin = _validar_fecha(
            argumentos.hasta,
            "--hasta",
            parser,
        )

        if fecha_fin < fecha_inicio:
            parser.error(
                "--hasta no puede ser anterior "
                "a --desde."
            )

        resultado = ejecutar_sincronizacion(
            fecha_inicio=argumentos.desde,
            fecha_fin=argumentos.hasta,
            tipo="manual",
        )

        sys.exit(
            0 if resultado.get("ok") else 1
        )

    # Una sola ejecución: conserva el funcionamiento anterior.
    if argumentos.una_vez:
        resultado = ejecutar_sincronizacion(
            tipo="rápida única"
        )

        sys.exit(
            0 if resultado.get("ok") else 1
        )

    ejecutar_worker(
        intervalo_segundos=argumentos.intervalo,
        intervalo_reconciliacion=(
            argumentos.intervalo_reconciliacion
        ),
        dias_reconciliacion=(
            argumentos.dias_reconciliacion
        ),
        intervalo_reconciliacion_profunda=(
            argumentos.intervalo_reconciliacion_profunda
        ),
        dias_reconciliacion_profunda=(
            argumentos.dias_reconciliacion_profunda
        ),
    )


if __name__ == "__main__":
    main()
