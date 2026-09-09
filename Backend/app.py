# app.py
from flask import Flask
from flask_cors import CORS
from os import environ

from extensions import db



def create_app():
    app = Flask(__name__)
    CORS(app)

    # Permitir que Flask muestre excepciones reales
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Configuración de PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar DB
    db.init_app(app)

    # Registrar modelos y crear tablas
    with app.app_context():
        from models import (
            Dato1,
            Dato2,
            RegistroLitro,
            LitrosControl,
            CargaCombustible,
            Factura              # 👈 agregar Factura aquí
        )
        db.create_all()
        print("📦 Tablas creadas correctamente")

    # Registrar Blueprints
    from routes.dato1_routes import dato1_bp
    from routes.dato2_routes import dato2_bp
    from routes.routes_litros_control import litros_control_bp
    from routes.routes_datos import datos_bp
    from routes.routes_cargas_combustible import cargas_bp
    from routes.factura_routes import factura_bp

    app.register_blueprint(dato1_bp)
    app.register_blueprint(dato2_bp)
    app.register_blueprint(litros_control_bp)
    app.register_blueprint(datos_bp)
    app.register_blueprint(cargas_bp)
    app.register_blueprint(factura_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
