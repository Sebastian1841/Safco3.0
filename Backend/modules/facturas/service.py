# modules/facturas/service.py

from sqlalchemy.exc import IntegrityError
from .extractor import FacturaExtractor
from models.factura import Factura
from extensions import db

class FacturaService:

    # ==========================================
    # LISTAR TODAS LAS FACTURAS
    # ==========================================
    @staticmethod
    def listar():
        facturas = Factura.query.order_by(Factura.id.desc()).all()
        return [f.to_dict() for f in facturas]


    # ==========================================
    # PROCESAR Y GUARDAR FACTURA (con validación)
    # ==========================================
    @staticmethod
    def procesar_y_guardar(pdf_file):

        datos = FacturaExtractor.extraer(pdf_file)

        if not datos["numero_factura"]:
            raise ValueError("No se pudo leer el número de factura.")

        # 🚫 VALIDAR DUPLICADOS ANTES DE GUARDAR
        existente = Factura.query.filter_by(
            numero_factura=datos["numero_factura"]
        ).first()

        if existente:
            raise ValueError(f"La factura {datos['numero_factura']} ya está registrada.")

        nueva = Factura(
            numero_factura = datos["numero_factura"],
            producto       = datos["producto"],
            litros         = datos["litros"],
            fecha          = datos["fecha"],
            total          = datos["total"]
        )

        try:
            db.session.add(nueva)
            db.session.commit()
        except IntegrityError:
            # Si falla por UNIQUE en la BD
            db.session.rollback()
            raise ValueError(f"La factura {datos['numero_factura']} ya existe.")

        return nueva


    # ==========================================
    # ELIMINAR UNA FACTURA
    # ==========================================
    @staticmethod
    def eliminar(id):
        factura = Factura.query.get(id)
        if not factura:
            raise ValueError("Factura no encontrada")

        db.session.delete(factura)
        db.session.commit()


    # ==========================================
    # ELIMINAR MÚLTIPLES
    # ==========================================
    @staticmethod
    def eliminar_varias(ids):
        if not ids:
            return

        Factura.query.filter(Factura.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.session.commit()
