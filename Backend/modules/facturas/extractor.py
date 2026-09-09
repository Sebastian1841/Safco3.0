import re
import pdfplumber


class FacturaExtractor:

    @staticmethod
    def _normalizar_texto(texto):
        return (
            texto.upper()
            .replace("Á", "A")
            .replace("É", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ú", "U")
            .replace("Ñ", "N")
        )

    @staticmethod
    def _monto_a_int(valor):
        if valor is None:
            return None

        valor = str(valor).strip().replace("$", "").replace(" ", "")

        # Si viene con decimales chilenos: 105.882,00 -> 105.882
        if "," in valor:
            valor = valor.split(",")[0]

        valor = re.sub(r"[^0-9]", "", valor)
        if not valor:
            return None

        return int(valor)

    @staticmethod
    def _numero_a_float(valor):
        if valor is None:
            return None

        valor = str(valor).strip().replace(" ", "")

        # Formato chileno: 1.234,56 -> 1234.56
        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")

        try:
            return float(valor)
        except ValueError:
            return None

    @staticmethod
    def _formatear_fecha(fecha_raw):
        if not fecha_raw:
            return None

        fecha_raw = fecha_raw.strip().upper()

        # Formato ya numérico: 22-05-2026
        match = re.match(r"^([0-9]{2})-([0-9]{2})-([0-9]{4})$", fecha_raw)
        if match:
            dia, mes, anio = match.groups()
            return f"{dia}-{mes}-{anio}"

        # Formato con mes texto: 05-NOV-2025
        match = re.match(r"^([0-9]{2})-([A-ZÁÉÍÓÚ]{3})-([0-9]{4})$", fecha_raw)
        if match:
            dia, mes_texto, anio = match.groups()
            mes_texto = (
                mes_texto.replace("Á", "A")
                .replace("É", "E")
                .replace("Í", "I")
                .replace("Ó", "O")
                .replace("Ú", "U")
            )

            MESES = {
                "ENE": "01", "FEB": "02", "MAR": "03", "ABR": "04",
                "MAY": "05", "JUN": "06", "JUL": "07", "AGO": "08",
                "SEP": "09", "OCT": "10", "NOV": "11", "DIC": "12",
            }

            mes_num = MESES.get(mes_texto, "01")
            return f"{dia}-{mes_num}-{anio}"

        return None

    @staticmethod
    def extraer(pdf_file):
        data = {
            "numero_factura": None,
            "producto": None,
            "litros": None,
            "fecha": None,
            "total": None,
            "proveedor": None,
            "tipo": "FACTURA",
        }

        # --- Leer PDF ---
        texto = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                contenido = page.extract_text()
                if contenido:
                    texto += contenido + " "

        texto = " ".join(texto.split())  # limpiar espacios

        # ----------------------------------------------------
        # DETECTAR TIPO DOCUMENTO
        # ----------------------------------------------------
        texto_normalizado = FacturaExtractor._normalizar_texto(texto)

        if "NOTA DE CREDITO" in texto_normalizado:
            data["tipo"] = "NOTA DE CREDITO"
            data["producto"] = "NOTA DE CREDITO"
        elif "FACTURA ELECTRONICA" in texto_normalizado:
            data["tipo"] = "FACTURA"

        # ----------------------------------------------------
        # NUMERO FACTURA / DOCUMENTO
        # ----------------------------------------------------
        patrones_numero = [
            r"FACTURA\s+N[º°]\s*:?\s*([0-9]{6,12})",
            r"FACTURA\s+NUMERO\s*:?\s*([0-9]{6,12})",
            r"N[º°]\s*:?\s*([0-9]{6,12})",
        ]

        for patron in patrones_numero:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                data["numero_factura"] = match.group(1)
                break

        # ----------------------------------------------------
        # PROVEEDOR
        # ----------------------------------------------------
        match = re.search(r"COPEC", texto, re.IGNORECASE)
        if match:
            data["proveedor"] = "COPEC"

        if "ESMAX DISTRIBUCION SPA" in texto_normalizado or "ESMAX" in texto_normalizado:
            data["proveedor"] = "ESMAX"

        # ----------------------------------------------------
        # NUEVO FORMATO: ESMAX DISTRIBUCION SPA
        # ----------------------------------------------------
        if data["proveedor"] == "ESMAX":

            # Fecha Esmax: FECHA EMISIÓN: 22-05-2026
            match = re.search(
                r"FECHA\s+EMISI[OÓ]N\s*:?\s*([0-9]{2}-[0-9]{2}-[0-9]{4})",
                texto,
                re.IGNORECASE,
            )
            if match:
                data["fecha"] = FacturaExtractor._formatear_fecha(match.group(1))

            # Producto + cantidad + unidad.
            # Ejemplo:
            # 0004002541 DIESEL B NO ADITIVADO - GRANEL (...) 20 M3 $ 1.097.736
            match = re.search(
                r"C[oó]d\s+Producto.*?\b[0-9]{6,12}\s+(.+?)\s+([0-9]+(?:[\.,][0-9]+)?)\s*(M3|M³|L|LT|LTS)\s+\$",
                texto,
                re.IGNORECASE,
            )

            if match:
                producto = " ".join(match.group(1).split()).strip()
                cantidad = FacturaExtractor._numero_a_float(match.group(2))
                unidad = match.group(3).upper().replace("³", "3")

                if producto:
                    data["producto"] = producto.upper()

                if cantidad is not None:
                    if unidad == "M3":
                        data["litros"] = cantidad * 1000
                    else:
                        data["litros"] = cantidad

            # Total Esmax: TOTAL $ 29.672.882
            match = re.search(
                r"\bTOTAL\s*\$\s*([0-9]{1,3}(?:\.[0-9]{3})+)",
                texto,
                re.IGNORECASE,
            )
            if match:
                data["total"] = FacturaExtractor._monto_a_int(match.group(1))

            # Respaldo Esmax: TOTAL FACTURA : 29.672.882
            if data["total"] is None:
                match = re.search(
                    r"TOTAL\s+FACTURA\s*:?\s*([0-9]{1,3}(?:\.[0-9]{3})+)",
                    texto,
                    re.IGNORECASE,
                )
                if match:
                    data["total"] = FacturaExtractor._monto_a_int(match.group(1))

        # ----------------------------------------------------
        # PRODUCTO - detectar el texto ANTES de los litros
        # Mantiene lógica original COPEC / facturas con litros en L
        # ----------------------------------------------------

        # Buscar patrón de litros
        litros_match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*L", texto)

        if litros_match and not data["producto"]:
            idx = litros_match.start()

            # Tomamos 80-120 caracteres antes del match para buscar el producto
            bloque = texto[max(0, idx - 120):idx]

            # Quitamos palabras basura típicas del encabezado
            bloque = re.sub(r"\b(IE|PTOTAL|U|SUBTOTAL)\b", "", bloque, flags=re.IGNORECASE)

            # Limpiamos dobles espacios
            bloque = " ".join(bloque.split())

            # Extraemos solo letras/números típicos del producto
            match = re.search(r"([A-Z0-9\sº°\-]+)$", bloque, re.IGNORECASE)

            if match:
                data["producto"] = match.group(1).strip().upper()

        # ----------------------------------------------------
        # PRODUCTO PARA NOTA DE CRÉDITO SIN LITROS
        # ----------------------------------------------------
        if data["tipo"] == "NOTA DE CREDITO" and not litros_match:
            match = re.search(
                r"PRODUCTO\s+SUBTOTAL\s+(.+?)\s+BASE\s+AFECTA\s+TOTAL",
                texto,
                re.IGNORECASE,
            )

            if match:
                producto_nc = re.sub(
                    r"\s+[0-9]{1,3}(?:\.[0-9]{3})+\s*$",
                    "",
                    match.group(1),
                ).strip()

                if producto_nc:
                    data["producto"] = producto_nc.upper()
            else:
                data["producto"] = "NOTA DE CREDITO"

        # ----------------------------------------------------
        # LITROS FACTURAS CON UNIDAD L
        # ----------------------------------------------------
        if data["litros"] is None:
            match = re.search(r"(\d{1,3}\.\d{3},\d{2})\s*L", texto)
            if match:
                litros = match.group(1).replace(".", "").replace(",", ".")
                data["litros"] = float(litros)

        # ----------------------------------------------------
        # FECHA
        # Soporta:
        # 05-NOV-2025 -> 05-11-2025
        # 22-05-2026  -> 22-05-2026
        # ----------------------------------------------------
        if data["fecha"] is None:
            match = re.search(r"\b([0-9]{2}-[A-ZÁÉÍÓÚ]{3}-[0-9]{4})\b", texto, re.IGNORECASE)
            if match:
                data["fecha"] = FacturaExtractor._formatear_fecha(match.group(1))

        if data["fecha"] is None:
            match = re.search(r"\b([0-9]{2}-[0-9]{2}-[0-9]{4})\b", texto)
            if match:
                data["fecha"] = FacturaExtractor._formatear_fecha(match.group(1))

        # ----------------------------------------------------
        # TOTAL NOTA DE CRÉDITO
        # COPEC: después de BASE AFECTA TOTAL vienen:
        # 1) BASE AFECTA
        # 2) IVA
        # 3) TOTAL FINAL
        # ----------------------------------------------------
        if data["tipo"] == "NOTA DE CREDITO":

            pos = texto_normalizado.find("BASE AFECTA TOTAL")

            if pos != -1:
                segmento = texto[pos:]

                numeros = re.findall(
                    r"\b([0-9]{1,3}(?:\.[0-9]{3})+)\b",
                    segmento,
                )

                if len(numeros) >= 3:
                    total_real = numeros[2]
                    data["total"] = -abs(int(total_real.replace(".", "")))

            # Respaldo si no encuentra BASE AFECTA TOTAL
            if data["total"] is None:
                segmento = texto[texto_normalizado.find("IVA"):] if texto_normalizado.find("IVA") != -1 else texto

                numeros = re.findall(
                    r"\b([0-9]{1,3}(?:\.[0-9]{3})+)\b",
                    segmento,
                )

                if len(numeros) >= 2:
                    total_real = numeros[1]
                    data["total"] = -abs(int(total_real.replace(".", "")))
        else:
            # ----------------------------------------------------
            # TOTAL FACTURA NORMAL
            # Mantiene tu lógica original: tomar el séptimo número
            # Solo se aplica si todavía no se encontró total con formato nuevo
            # ----------------------------------------------------
            if data["total"] is None:
                pos = texto.find("TOTAL")
                if pos != -1:
                    segmento = texto[pos:]  # texto desde TOTAL en adelante

                    # Buscar montos grandes
                    numeros = re.findall(r"\b([0-9]{1,3}(?:\.[0-9]{3})+)\b", segmento)

                    # Tomar el séptimo número si existe (tu lógica original)
                    if len(numeros) >= 7:
                        total_real = numeros[6]
                        data["total"] = int(total_real.replace(".", ""))

        return data
