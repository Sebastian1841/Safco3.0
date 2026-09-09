from config import db

class LitrosControl(db.Model):
    __tablename__ = "litros_controles"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    dispositivo = db.Column(db.Integer, nullable=False)
    litros_inicio = db.Column(db.Float, nullable=False)
    litros_final = db.Column(db.Float, nullable=False)
    diferencia_manual = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "dispositivo": self.dispositivo,
            "litros_inicio": self.litros_inicio,
            "litros_final": self.litros_final,
            "diferencia_manual": self.diferencia_manual,
        }
