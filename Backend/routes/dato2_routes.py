# routes_dato2.py
from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from extensions import db
from models import Dato2

dato2_bp = Blueprint("dato2_bp", __name__)


@dato2_bp.route("/dato2", methods=["GET"])
def get_dato2():
    data = db.session.execute(db.select(Dato2).order_by(Dato2.id)).scalars()
    return jsonify([item.to_dict() for item in data])


@dato2_bp.route("/dato2", methods=["POST"])
def add_dato2_api():
    data = request.json
    try:
        new_item = Dato2(nombre=data["nombre"])
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except (TypeError, KeyError) as e:
        return jsonify({"error": f"Datos incompletos o incorrectos: {e}"}), 400


@dato2_bp.route("/dato2/<int:item_id>", methods=["PUT", "DELETE"])
def manage_dato2(item_id):
    item = db.session.get(Dato2, item_id)
    if not item:
        return jsonify({"error": f"Dato2 con ID {item_id} no encontrado"}), 404

    if request.method == "PUT":
        data = request.json
        try:
            item.nombre = data.get("nombre", item.nombre).strip()
            db.session.commit()
            return jsonify(item.to_dict()), 200
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Error al actualizar Dato2: {e}"}), 400

    elif request.method == "DELETE":
        try:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"message": f"Dato2 con ID {item_id} eliminado"}), 204
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Error al eliminar Dato2: {e}"}), 500
