
from flask import Blueprint, request, jsonify
from modules.facturas.service import FacturaService

factura_bp = Blueprint("facturas", __name__, url_prefix="/facturas")

# ==============================
# LISTAR TODAS LAS FACTURAS
# ==============================
@factura_bp.get("/listar")
def listar_facturas():
    facturas = FacturaService.listar()
    return jsonify(facturas)


# ==============================
# SUBIR FACTURA
# ==============================
@factura_bp.post("/subir")
def subir_factura():
    archivo = request.files.get("archivo")

    if not archivo:
        return jsonify({"error": "No se envió archivo."}), 400
    
    try:
        factura = FacturaService.procesar_y_guardar(archivo)
        return jsonify({"ok": True, "factura": factura.to_dict()}), 201

    except ValueError as e:
        # Errores esperados: duplicados, PDF incompleto, etc.
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # Errores inesperados
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ==============================
# ELIMINAR UNA FACTURA POR ID
# ==============================
@factura_bp.delete("/<int:id>")
def eliminar_factura(id):
    try:
        FacturaService.eliminar(id)
        return jsonify({"ok": True, "msg": "Factura eliminada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# ELIMINAR MÚLTIPLES
# ==============================
@factura_bp.post("/eliminar-multiple")
def eliminar_multiple():
    ids = request.json.get("ids")

    if not ids or not isinstance(ids, list):
        return jsonify({"error": "Debes enviar una lista de IDs"}), 400
    
    try:
        FacturaService.eliminar_varias(ids)
        return jsonify({"ok": True, "msg": "Facturas eliminadas"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
