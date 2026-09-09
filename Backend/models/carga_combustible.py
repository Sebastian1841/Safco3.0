from extensions import db
from datetime import date, time

class CargaCombustible(db.Model):
    __tablename__ = "cargas_combustible"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    dispositivo_id = db.Column(db.Integer, nullable=False)
    litros_total = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "hora": self.hora.strftime("%H:%M"),
            "dispositivo_id": self.dispositivo_id,
            "litros_total": self.litros_total,
        }
