from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from extensions import db
from models import Dato1

dato1_bp = Blueprint("dato1_bp", __name__)


# === GET all ===
@dato1_bp.route("/dato1", methods=["GET"])
def get_all():
    data = db.session.execute(db.select(Dato1).order_by(Dato1.id)).scalars()
    return jsonify([i.to_dict() for i in data])


# === POST ===
@dato1_bp.route("/dato1", methods=["POST"])
def create():
    try:
        new = Dato1(nombre=request.json["nombre"])
        db.session.add(new)
        db.session.commit()
        return jsonify(new.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# === PUT & DELETE ===
@dato1_bp.route("/dato1/<int:item_id>", methods=["PUT", "DELETE"])
def manage_dato1(item_id):
    item = db.session.get(Dato1, item_id)
    if not item:
        return jsonify({"error": f"Dato1 con ID {item_id} no encontrado"}), 404

    if request.method == "PUT":
        data = request.json
        try:
            item.nombre = data.get("nombre", item.nombre).strip()
            db.session.commit()
            return jsonify(item.to_dict()), 200
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Error al actualizar Dato1: {e}"}), 400

    elif request.method == "DELETE":
        try:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"message": f"Dato1 con ID {item_id} eliminado"}), 204
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Error al eliminar Dato1: {e}"}), 500
