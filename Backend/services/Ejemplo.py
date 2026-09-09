#!/usr/bin/env python3

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests


logger = logging.getLogger(__name__)


class GPSGateError(RuntimeError):
    """Error controlado al consultar o procesar GpsGate."""


class ThingsBoardSimple:
    """
    Mantiene exactamente el nombre y la interfaz del servicio anterior,
    pero ahora obtiene toda la información directamente desde GpsGate.
    """

    # ============================================================
    # COMPATIBILIDAD CON EL SERVICIO ANTERIOR
    # ============================================================

    TIMEOUT = 30
    RETRYABLE_STATUS = {429, 500, 502, 503, 504}
    MAX_RETRIES = 2
    RETRY_SLEEP = 1.0

    # UUID antiguos de ThingsBoard.
    # Se mantienen para no romper archivos que los utilizan.
    DISPOSITIVO1_ANTIGUO = "52906fe0-a5d5-11f0-9dd9-bb6adf6472c1"
    DISPOSITIVO2_ANTIGUO = "39dd8c70-6cb0-11f0-9c9f-ebe52b51bbe5"

    # IDs reales en GpsGate.
    GPSGATE_USER_ID_CODIGO1 = 4552
    GPSGATE_USER_ID_CODIGO2 = 4201

    TOKEN_PREDETERMINADO = (
        "v2:MDAwMDAwMjYyNTpiZTQ4YTA0MDYyYmM5YzhlYjhhMg=="
    )

    GPSGATE_API_ROOT = (
        "https://www.sinergygroupchile.cl/"
        "comGpsGate/api/v.1/applications/3"
    )

    MIN_LITROS_CODIGO1 = 3.0
    MIN_LITROS_CODIGO2 = 3.0
    MAX_DIAS_CONSULTA = 366

    CONFIGURACION_DISPOSITIVOS = {
        "codigo1": {
            "dispositivo_legacy": DISPOSITIVO1_ANTIGUO,
            "user_id": GPSGATE_USER_ID_CODIGO1,
            "username": "SAFCO2",
            "nombre": "FLUJOMETRO SAFCO FIJO",
            "modo": "ciclos",
        },
        "codigo2": {
            "dispositivo_legacy": DISPOSITIVO2_ANTIGUO,
            "user_id": GPSGATE_USER_ID_CODIGO2,
            "username": "SAFCO",
            "nombre": "SAFCO FLUJOMETRO",
            "modo": "ciclos",
        },
    }

    def __init__(
        self,
        token: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        # --------------------------------------------------------
        # Atributos antiguos conservados
        # --------------------------------------------------------

        # Se conserva por compatibilidad, aunque ya no se consulta.
        self.url = "https://sinergychile.cl"

        # Ya no se necesitan usuario ni contraseña de ThingsBoard.
        self.usuario = ""
        self.password = ""

        # Se mantienen los UUID antiguos para que otros archivos
        # sigan reconociendo exactamente los mismos dispositivos.
        self.dispositivo1 = self.DISPOSITIVO1_ANTIGUO
        self.dispositivo2 = self.DISPOSITIVO2_ANTIGUO

        # Se mantienen exactamente los nombres antiguos.
        self.variables_codigo1 = [
            "Litros_total",
            "iButton_total",
        ]

        self.variables_codigo2 = [
            "litrosFTotal",
            "iButton",
        ]

        # --------------------------------------------------------
        # Configuración actual GpsGate
        # --------------------------------------------------------

        self.token = (
            token
            or os.getenv("GPSGATE_TOKEN")
            or self.TOKEN_PREDETERMINADO
        ).strip()

        if not self.token:
            raise ValueError(
                "No se configuró el token de GpsGate."
            )

        self.gpsgate_api_root = self.GPSGATE_API_ROOT

        self.session = session or requests.Session()
        self._session_propia = session is None

        try:
            self.chile_tz = ZoneInfo(
                "America/Santiago"
            )

        except ZoneInfoNotFoundError:
            self._log(
                "tzdata no encontrado. "
                "Se utilizará UTC-3 fijo."
            )

            self.chile_tz = timezone(
                timedelta(hours=-3)
            )

    # ============================================================
    # LOGS
    # ============================================================

    def _log(
        self,
        mensaje: str,
    ) -> None:
        print(
            f"[GPSGATE] {mensaje}"
        )

    def _error(
        self,
        mensaje: str,
    ) -> None:
        print(
            f"[GPSGATE][ERROR] {mensaje}"
        )

    # ============================================================
    # COMPATIBILIDAD DE AUTENTICACIÓN
    # ============================================================

    def _login(
        self,
    ) -> bool:
        """
        Método conservado para compatibilidad.

        GpsGate usa un token fijo en el header Authorization,
        por lo que no necesita hacer login.
        """

        return bool(
            self.token
        )

    # ============================================================
    # CICLO DE VIDA
    # ============================================================

    def cerrar(
        self,
    ) -> None:
        if self._session_propia:
            self.session.close()

    def __enter__(
        self,
    ):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.cerrar()

    # ============================================================
    # FECHAS
    # ============================================================

    def _fecha_a_timestamp(
        self,
        fecha_str: str,
    ) -> int:
        """
        Método antiguo conservado.

        Convierte YYYY-MM-DD a epoch en milisegundos.
        """

        fecha = datetime.strptime(
            fecha_str,
            "%Y-%m-%d",
        )

        return int(
            fecha.timestamp() * 1000
        )

    def _validar_fecha(
        self,
        fecha: str,
    ) -> datetime:
        try:
            return datetime.strptime(
                fecha,
                "%Y-%m-%d",
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                f"Fecha inválida: {fecha!r}. "
                "El formato requerido es YYYY-MM-DD."
            ) from error

    def _validar_rango(
        self,
        fecha_inicio: str,
        fecha_fin: str,
    ) -> tuple[datetime, datetime]:

        inicio = self._validar_fecha(
            fecha_inicio
        )

        fin = self._validar_fecha(
            fecha_fin
        )

        if fin < inicio:
            raise ValueError(
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        cantidad_dias = (
            fin - inicio
        ).days + 1

        if (
            cantidad_dias
            > self.MAX_DIAS_CONSULTA
        ):
            raise ValueError(
                f"El rango máximo permitido es de "
                f"{self.MAX_DIAS_CONSULTA} días."
            )

        return inicio, fin

    def _iterar_fechas(
        self,
        fecha_inicio: str,
        fecha_fin: str,
    ) -> Iterator[str]:

        inicio, fin = (
            self._validar_rango(
                fecha_inicio,
                fecha_fin,
            )
        )

        fecha_actual = inicio

        while fecha_actual <= fin:
            yield fecha_actual.strftime(
                "%Y-%m-%d"
            )

            fecha_actual += timedelta(
                days=1
            )

    def _parsear_fecha_utc(
        self,
        fecha_str: Optional[str],
    ) -> Optional[datetime]:

        if not fecha_str:
            return None

        try:
            fecha = datetime.fromisoformat(
                str(
                    fecha_str
                ).replace(
                    "Z",
                    "+00:00",
                )
            )

            if fecha.tzinfo is None:
                fecha = fecha.replace(
                    tzinfo=timezone.utc
                )

            return fecha.astimezone(
                timezone.utc
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    def _obtener_fecha_track(
        self,
        track: Dict[str, Any],
    ) -> Optional[datetime]:

        fecha_str = (
            track.get("utc")
            or track.get("serverUtc")
            or track.get("timestamp")
            or track.get("timeStamp")
        )

        return self._parsear_fecha_utc(
            fecha_str
        )

    def _obtener_epoch_ms(
        self,
        track: Dict[str, Any],
    ) -> Optional[int]:

        fecha = self._obtener_fecha_track(
            track
        )

        if fecha is None:
            return None

        return int(
            fecha.timestamp() * 1000
        )

    # ============================================================
    # VARIABLES DE TELEMETRÍA
    # ============================================================

    @staticmethod
    def _normalizar_nombre(
        valor: Any,
    ) -> str:

        return "".join(
            caracter.lower()
            for caracter in str(valor)
            if caracter.isalnum()
        )

    def _obtener_variable(
        self,
        variables: Any,
        *nombres: str,
    ) -> Any:

        if not isinstance(
            variables,
            dict,
        ):
            return None

        variables_normalizadas = {
            self._normalizar_nombre(
                nombre
            ): valor
            for nombre, valor
            in variables.items()
        }

        for nombre in nombres:
            nombre_normalizado = (
                self._normalizar_nombre(
                    nombre
                )
            )

            if (
                nombre_normalizado
                in variables_normalizadas
            ):
                return (
                    variables_normalizadas[
                        nombre_normalizado
                    ]
                )

        return None

    @staticmethod
    def _convertir_float(
        valor: Any,
    ) -> Optional[float]:

        if valor is None:
            return None

        if isinstance(
            valor,
            bool,
        ):
            return float(
                valor
            )

        if isinstance(
            valor,
            (int, float),
        ):
            return float(
                valor
            )

        try:
            return float(
                str(
                    valor
                ).strip().replace(
                    ",",
                    ".",
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    def _obtener_litros(
        self,
        track: Dict[str, Any],
    ) -> Optional[float]:

        variables = (
            track.get("variables")
            or {}
        )

        valor = self._obtener_variable(
            variables,
            "LitrosF",
            "litrosF",
            "litros_f",
            "litrosFTotal",
            "Litros_total",
        )

        return self._convertir_float(
            valor
        )

    def _obtener_ibutton(
        self,
        track: Dict[str, Any],
    ) -> Optional[str]:

        variables = (
            track.get("variables")
            or {}
        )

        valor = self._obtener_variable(
            variables,
            "IButton",
            "iButton",
            "iButton_total",
            "DriverID",
            "DriverId",
        )

        if valor is None:
            return None

        return str(
            valor
        )

    # ============================================================
    # RESOLUCIÓN DE DISPOSITIVOS
    # ============================================================

    def _resolver_codigo_dispositivo(
        self,
        dispositivo: Any,
    ) -> str:
        """
        Acepta cualquiera de estas formas:

        - UUID antiguo de ThingsBoard.
        - User ID de GpsGate.
        - codigo1 / codigo2.
        """

        valor = str(
            dispositivo
        ).strip()

        equivalencias_codigo1 = {
            "codigo1",
            str(
                self.dispositivo1
            ),
            str(
                self.GPSGATE_USER_ID_CODIGO1
            ),
        }

        equivalencias_codigo2 = {
            "codigo2",
            str(
                self.dispositivo2
            ),
            str(
                self.GPSGATE_USER_ID_CODIGO2
            ),
        }

        if valor in equivalencias_codigo1:
            return "codigo1"

        if valor in equivalencias_codigo2:
            return "codigo2"

        raise ValueError(
            f"Dispositivo no reconocido: "
            f"{dispositivo}"
        )

    # ============================================================
    # API GPSGATE
    # ============================================================

    def _consultar_tracks_dia(
        self,
        user_id: int,
        fecha: str,
    ) -> List[Dict[str, Any]]:

        url = (
            f"{self.gpsgate_api_root}/"
            f"users/{user_id}/tracks"
        )

        ultimo_error: Optional[str] = None

        for intento in range(
            self.MAX_RETRIES + 1
        ):
            try:
                respuesta = (
                    self.session.get(
                        url,
                        params={
                            "Date": fecha,
                        },
                        headers={
                            "Authorization": (
                                self.token
                            ),
                            "Accept": (
                                "application/json"
                            ),
                        },
                        timeout=self.TIMEOUT,
                    )
                )

            except (
                requests.RequestException
            ) as error:

                ultimo_error = (
                    "Error de conexión "
                    f"con GpsGate: {error}"
                )

                self._error(
                    ultimo_error
                )

                if (
                    intento
                    < self.MAX_RETRIES
                ):
                    time.sleep(
                        self.RETRY_SLEEP
                    )

                    continue

                raise GPSGateError(
                    ultimo_error
                ) from error

            if (
                respuesta.status_code
                == 200
            ):
                try:
                    payload = (
                        respuesta.json()
                    )

                except ValueError as error:
                    raise GPSGateError(
                        "GpsGate respondió HTTP 200, "
                        "pero no entregó JSON válido."
                    ) from error

                tracks = (
                    self._extraer_lista_tracks(
                        payload
                    )
                )

                self._log(
                    f"Usuario {user_id}, "
                    f"fecha {fecha}: "
                    f"{len(tracks)} tracks."
                )

                return tracks

            if (
                respuesta.status_code
                in (401, 403)
            ):
                raise GPSGateError(
                    "El token de GpsGate es inválido "
                    "o no tiene permisos suficientes. "
                    f"Status={respuesta.status_code}"
                )

            if (
                respuesta.status_code
                in self.RETRYABLE_STATUS
            ):
                ultimo_error = (
                    "GpsGate respondió "
                    f"{respuesta.status_code} "
                    f"en intento {intento + 1}/"
                    f"{self.MAX_RETRIES + 1}."
                )

                self._error(
                    ultimo_error
                )

                if (
                    intento
                    < self.MAX_RETRIES
                ):
                    time.sleep(
                        self.RETRY_SLEEP
                    )

                    continue

                raise GPSGateError(
                    ultimo_error
                )

            raise GPSGateError(
                "Respuesta inesperada de GpsGate: "
                f"{respuesta.status_code}. "
                f"Body={respuesta.text[:300]}"
            )

        raise GPSGateError(
            ultimo_error
            or (
                "Error desconocido "
                "consultando GpsGate."
            )
        )

    @staticmethod
    def _extraer_lista_tracks(
        payload: Any,
    ) -> List[Dict[str, Any]]:

        if isinstance(
            payload,
            list,
        ):
            return [
                track
                for track in payload
                if isinstance(
                    track,
                    dict,
                )
            ]

        if isinstance(
            payload,
            dict,
        ):
            for clave in (
                "tracks",
                "items",
                "data",
                "result",
            ):
                contenido = payload.get(
                    clave
                )

                if isinstance(
                    contenido,
                    list,
                ):
                    return [
                        track
                        for track in contenido
                        if isinstance(
                            track,
                            dict,
                        )
                    ]

        raise GPSGateError(
            "GpsGate no entregó una lista "
            "de tracks reconocible."
        )

    def obtener_tracks(
        self,
        user_id: int,
        fecha_inicio: str,
        fecha_fin: str,
    ) -> List[Dict[str, Any]]:

        tracks_totales: List[
            Dict[str, Any]
        ] = []

        for fecha in self._iterar_fechas(
            fecha_inicio,
            fecha_fin,
        ):
            tracks_dia = (
                self._consultar_tracks_dia(
                    user_id=user_id,
                    fecha=fecha,
                )
            )

            tracks_totales.extend(
                tracks_dia
            )

        tracks_totales.sort(
            key=lambda track: (
                self._obtener_epoch_ms(
                    track
                )
                or 0
            )
        )

        return tracks_totales

    # ============================================================
    # CÓDIGO 1 — CICLOS SUMADOS
    # ============================================================

    def _procesar_codigo1(
        self,
        tracks: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:

        litros_totales: List[
            Dict[str, Any]
        ] = []

        ibuttons_totales: List[
            Dict[str, Any]
        ] = []

        en_ciclo = False
        suma_actual = 0.0

        ultimo_punto: Optional[
            Dict[str, Any]
        ] = None

        for track in tracks:
            litros = self._obtener_litros(
                track
            )

            if litros is None:
                continue

            if litros > 0:
                if not en_ciclo:
                    en_ciclo = True
                    suma_actual = 0.0

                suma_actual += litros
                ultimo_punto = track
                continue

            if not en_ciclo:
                continue

            if (
                ultimo_punto is not None
                and suma_actual
                >= self.MIN_LITROS_CODIGO1
            ):
                epoch_ms = (
                    self._obtener_epoch_ms(
                        ultimo_punto
                    )
                )

                if epoch_ms is not None:
                    ibutton = (
                        self._obtener_ibutton(
                            ultimo_punto
                        )
                    )

                    litros_totales.append({
                        "ts": epoch_ms,
                        "value": round(
                            suma_actual,
                            6,
                        ),
                    })

                    ibuttons_totales.append({
                        "ts": epoch_ms,
                        "value": (
                            ibutton or ""
                        ),
                    })

            en_ciclo = False
            suma_actual = 0.0
            ultimo_punto = None

        return {
            "Litros_total": (
                litros_totales
            ),
            "iButton_total": (
                ibuttons_totales
            ),
        }

    # ============================================================
    # CÓDIGO 2 — CICLOS SUMADOS
    # ============================================================

    def _procesar_codigo2(
        self,
        tracks: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:

        litros_totales: List[
            Dict[str, Any]
        ] = []

        ibuttons_totales: List[
            Dict[str, Any]
        ] = []

        en_ciclo = False
        suma_actual = 0.0

        ultimo_punto: Optional[
            Dict[str, Any]
        ] = None

        for track in tracks:
            litros = self._obtener_litros(
                track
            )

            if litros is None:
                continue

            # Un valor positivo pertenece a una carga.
            if litros > 0:
                if not en_ciclo:
                    en_ciclo = True
                    suma_actual = 0.0

                suma_actual += litros
                ultimo_punto = track
                continue

            # Si llega 0 sin existir una carga abierta,
            # simplemente se ignora.
            if not en_ciclo:
                continue

            # El 0 marca el final de la carga.
            if (
                ultimo_punto is not None
                and suma_actual
                >= self.MIN_LITROS_CODIGO2
            ):
                epoch_ms = (
                    self._obtener_epoch_ms(
                        ultimo_punto
                    )
                )

                if epoch_ms is not None:
                    ibutton = (
                        self._obtener_ibutton(
                            ultimo_punto
                        )
                    )

                    litros_totales.append({
                        "ts": epoch_ms,
                        "value": round(
                            suma_actual,
                            6,
                        ),
                    })

                    ibuttons_totales.append({
                        "ts": epoch_ms,
                        "value": (
                            ibutton or ""
                        ),
                    })

            en_ciclo = False
            suma_actual = 0.0
            ultimo_punto = None

        return {
            # Se mantienen estos nombres para compatibilidad
            # con gpsgate_sync_service.py y el resto del sistema.
            "litrosFTotal": (
                litros_totales
            ),
            "iButton": (
                ibuttons_totales
            ),
        }

    # ============================================================
    # MÉTODO ANTIGUO CONSERVADO
    # ============================================================

    def obtener_datos(
        self,
        dispositivo: Any,
        variables: List[str],
        fecha_inicio: str,
        fecha_fin: str,
        fallback_empty: bool = True,
    ) -> Dict[str, Any]:
        """
        Conserva exactamente la firma del método antiguo.

        El argumento variables se mantiene por compatibilidad,
        aunque la extracción ahora se realiza desde GpsGate.
        """

        del variables

        try:
            codigo = (
                self._resolver_codigo_dispositivo(
                    dispositivo
                )
            )

            configuracion = (
                self.CONFIGURACION_DISPOSITIVOS[
                    codigo
                ]
            )

            tracks = self.obtener_tracks(
                user_id=(
                    configuracion["user_id"]
                ),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )

            if codigo == "codigo1":
                return (
                    self._procesar_codigo1(
                        tracks
                    )
                )

            return self._procesar_codigo2(
                tracks
            )

        except Exception as error:
            self._error(
                "obtener_datos() falló: "
                f"{error}"
            )

            if fallback_empty:
                return {}

            raise

    # ============================================================
    # CONSULTA PRINCIPAL ANTIGUA CONSERVADA
    # ============================================================

    def consultar_por_fechas(
        self,
        fecha_inicio: str,
        fecha_fin: str,
    ) -> Dict[str, Any]:
        """
        Devuelve exactamente la misma estructura que el servicio
        anterior de ThingsBoard.
        """

        self._log(
            f"Consultando del {fecha_inicio} "
            f"al {fecha_fin}"
        )

        datos1 = self.obtener_datos(
            self.dispositivo1,
            self.variables_codigo1,
            fecha_inicio,
            fecha_fin,
            fallback_empty=True,
        )

        datos2 = self.obtener_datos(
            self.dispositivo2,
            self.variables_codigo2,
            fecha_inicio,
            fecha_fin,
            fallback_empty=True,
        )

        return {
            "codigo1": datos1,
            "codigo2": datos2,
        }

    # ============================================================
    # LISTADO DE DISPOSITIVOS
    # ============================================================

    def listar_dispositivos(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Entrega ambos dispositivos manteniendo también los UUID
        antiguos para compatibilidad con el frontend/backend.
        """

        return [
            {
                "id": self.dispositivo1,
                "deviceId": (
                    self.dispositivo1
                ),
                "gpsGateUserId": (
                    self.GPSGATE_USER_ID_CODIGO1
                ),
                "codigo": "codigo1",
                "username": "SAFCO2",
                "name": (
                    "FLUJOMETRO SAFCO FIJO"
                ),
                "nombre": (
                    "FLUJOMETRO SAFCO FIJO"
                ),
                "modo": "ciclos",
                "activo": True,
            },
            {
                "id": self.dispositivo2,
                "deviceId": (
                    self.dispositivo2
                ),
                "gpsGateUserId": (
                    self.GPSGATE_USER_ID_CODIGO2
                ),
                "codigo": "codigo2",
                "username": "SAFCO",
                "name": (
                    "SAFCO FLUJOMETRO"
                ),
                "nombre": (
                    "SAFCO FLUJOMETRO"
                ),
                "modo": "ciclos",
                "activo": True,
            },
        ]

    # ============================================================
    # RESULTADOS EN CONSOLA
    # ============================================================

    def mostrar_resultados(
        self,
        datos: Dict[str, Any],
    ) -> None:

        datos_codigo1 = (
            datos.get("codigo1")
            or {}
        )

        litros_codigo1 = (
            datos_codigo1.get(
                "Litros_total",
                [],
            )
        )

        ibuttons_codigo1 = (
            datos_codigo1.get(
                "iButton_total",
                [],
            )
        )

        if litros_codigo1:
            print(
                "\n🔹 CÓDIGO 1 - "
                "LITROS TOTALES"
            )

            print(
                "   Registros encontrados: "
                f"{len(litros_codigo1)}"
            )

            for indice in range(
                min(
                    3,
                    len(litros_codigo1),
                )
            ):
                registro = (
                    litros_codigo1[
                        indice
                    ]
                )

                fecha = (
                    datetime.fromtimestamp(
                        registro["ts"] / 1000,
                        tz=timezone.utc,
                    ).astimezone(
                        self.chile_tz
                    )
                )

                ibutton = (
                    ibuttons_codigo1[
                        indice
                    ]["value"]
                    if indice
                    < len(
                        ibuttons_codigo1
                    )
                    else "N/A"
                )

                print(
                    f"   {fecha} "
                    "- Litros: "
                    f"{registro['value']} "
                    "- iButton: "
                    f"{ibutton}"
                )

        else:
            print(
                "\n🔹 CÓDIGO 1 - SIN DATOS "
                "(o fallo GpsGate)"
            )

        datos_codigo2 = (
            datos.get("codigo2")
            or {}
        )

        litros_codigo2 = (
            datos_codigo2.get(
                "litrosFTotal",
                [],
            )
        )

        ibuttons_codigo2 = (
            datos_codigo2.get(
                "iButton",
                [],
            )
        )

        if litros_codigo2:
            print(
                "\n🔹 CÓDIGO 2 - "
                "LITROS TOTALES"
            )

            print(
                "   Registros encontrados: "
                f"{len(litros_codigo2)}"
            )

            for indice in range(
                min(
                    3,
                    len(litros_codigo2),
                )
            ):
                registro = (
                    litros_codigo2[
                        indice
                    ]
                )

                fecha = (
                    datetime.fromtimestamp(
                        registro["ts"] / 1000,
                        tz=timezone.utc,
                    ).astimezone(
                        self.chile_tz
                    )
                )

                ibutton = (
                    ibuttons_codigo2[
                        indice
                    ]["value"]
                    if indice
                    < len(
                        ibuttons_codigo2
                    )
                    else "N/A"
                )

                print(
                    f"   {fecha} "
                    "- Litros: "
                    f"{registro['value']} "
                    "- iButton: "
                    f"{ibutton}"
                )

        else:
            print(
                "\n🔹 CÓDIGO 2 - SIN DATOS "
                "(o fallo GpsGate)"
            )


# ============================================================
# ALIAS NUEVO
# ============================================================

# Los archivos antiguos pueden seguir importando:
#
# from services.Ejemplo import ThingsBoardSimple
#
# Y los nuevos también pueden utilizar:
#
# from services.Ejemplo import GPSGateSimple

GPSGateSimple = ThingsBoardSimple