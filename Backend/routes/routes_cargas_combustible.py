# routes/routes_cargas_combustible.py
from flask import Blueprint, jsonify, request
from datetime import date, time
from sqlalchemy import exc
from extensions import db
from models import CargaCombustible

cargas_bp = Blueprint("cargas_bp", __name__)


# ====================================================
# GET: lista de cargas
# ====================================================
@cargas_bp.route("/cargas_combustible", methods=["GET"])
def get_cargas():
    data = db.session.execute(
        db.select(CargaCombustible).order_by(CargaCombustible.fecha.desc())
    ).scalars()
    return jsonify([item.to_dict() for item in data])


# ====================================================
# POST: crear carga (fecha + hora SEPARADAS)
# ====================================================
@cargas_bp.route("/cargas_combustible", methods=["POST"])
def add_carga():
    data = request.json
    try:
        # Ahora recibimos fecha y hora separadas
        fecha_obj = date.fromisoformat(data["fecha"])
        hora_obj = time.fromisoformat(data["hora"])

        nueva = CargaCombustible(
            fecha=fecha_obj,
            hora=hora_obj,
            dispositivo_id=data["dispositivo_id"],
            litros_total=data["litros_total"],
        )

        db.session.add(nueva)
        db.session.commit()
        return jsonify(nueva.to_dict()), 201

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": f"Datos incorrectos: {e}"}), 400

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Error de base de datos: {e}"}), 500


# ====================================================
# PUT / DELETE
# ====================================================
@cargas_bp.route("/cargas_combustible/<int:carga_id>", methods=["PUT", "DELETE"])
def manage_carga(carga_id):
    carga = db.session.get(CargaCombustible, carga_id)
    if not carga:
        return jsonify({"error": f"Carga con ID {carga_id} no encontrada"}), 404

    # -------------------- PUT --------------------
    if request.method == "PUT":
        data = request.json
        try:
            if "fecha" in data:
                carga.fecha = date.fromisoformat(data["fecha"])

            if "hora" in data:
                carga.hora = time.fromisoformat(data["hora"])

            if "dispositivo_id" in data:
                carga.dispositivo_id = data["dispositivo_id"]

            if "litros_total" in data:
                carga.litros_total = data["litros_total"]

            db.session.commit()
            return jsonify(carga.to_dict()), 200

        except (ValueError, TypeError, KeyError, exc.SQLAlchemyError) as e:
            db.session.rollback()
            return jsonify({"error": f"Error al actualizar: {e}"}), 400

    # -------------------- DELETE --------------------
    elif request.method == "DELETE":
        try:
            db.session.delete(carga)
            db.session.commit()
            return jsonify({"message": f"Carga con ID {carga_id} eliminada"}), 204
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Error al eliminar: {e}"}), 500
