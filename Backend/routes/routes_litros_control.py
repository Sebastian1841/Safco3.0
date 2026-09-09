# routes_litros_control.py
from flask import Blueprint, jsonify, request
from datetime import date
from sqlalchemy import exc
from extensions import db
from models import LitrosControl

litros_control_bp = Blueprint("litros_control_bp", __name__)


@litros_control_bp.route("/litros_control", methods=["GET"])
def get_litros_control():
    data = db.session.execute(
        db.select(LitrosControl).order_by(LitrosControl.fecha.desc())
    ).scalars()
    return jsonify([item.to_dict() for item in data])


@litros_control_bp.route("/litros_control", methods=["POST"])
def add_litros_control_api():
    data = request.json
    try:
        diferencia = data["litros_final"] - data["litros_inicio"]
        fecha_obj = date.fromisoformat(data["fecha"])
        new_control = LitrosControl(
            fecha=fecha_obj,
            dispositivo=data["dispositivo"],
            litros_inicio=data["litros_inicio"],
            litros_final=data["litros_final"],
            diferencia_manual=diferencia,
        )
        db.session.add(new_control)
        db.session.commit()
        return jsonify(new_control.to_dict()), 201
    except (TypeError, KeyError, ValueError) as e:
        return jsonify({"error": f"Datos incorrectos: {e}"}), 400


@litros_control_bp.route("/litros_control/<int:control_id>", methods=["PUT", "DELETE"])
def manage_litros_control(control_id):
    control = db.session.get(LitrosControl, control_id)
    if not control:
        return jsonify({"error": f"Control con ID {control_id} no encontrado"}), 404

    if request.method == "PUT":
        data = request.json
        try:
            control.fecha = date.fromisoformat(data.get("fecha", control.fecha.isoformat()))
            control.dispositivo = data.get("dispositivo", control.dispositivo)
            control.litros_inicio = data.get("litros_inicio", control.litros_inicio)
            control.litros_final = data.get("litros_final", control.litros_final)
            control.diferencia_manual = control.litros_final - control.litros_inicio
            db.session.commit()
            return jsonify(control.to_dict()), 200
        except (TypeError, KeyError, ValueError, exc.SQLAlchemyError) as e:
            db.session.rollback()
            return jsonify({"error": f"Error al actualizar: {e}"}), 400

    elif request.method == "DELETE":
        try:
            db.session.delete(control)
            db.session.commit()
            return jsonify({"message": f"Control con ID {control_id} eliminado"}), 204
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Error al eliminar: {e}"}), 500
