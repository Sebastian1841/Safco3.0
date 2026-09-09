from config import db
from sqlalchemy import UniqueConstraint
from utils.timezone import CHILE_TZ
from datetime import timezone

class RegistroLitro(db.Model):
    __tablename__ = "registros_litros"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    litros = db.Column(db.Float)
    ibutton = db.Column(db.String(50))
    dispositivo_id = db.Column(db.Integer, nullable=False)
    dato1_id = db.Column(db.Integer, db.ForeignKey("dato1_referencias.id", ondelete="SET NULL"))
    dato2_id = db.Column(db.Integer, db.ForeignKey("dato2_referencias.id", ondelete="SET NULL"))

    __table_args__ = (UniqueConstraint("fecha", "dispositivo_id", name="uq_fecha_dispositivo"),)

    def to_dict(self):
        aware_utc = self.fecha.replace(tzinfo=timezone.utc)
        local_time = aware_utc.astimezone(CHILE_TZ)

        return {
            "id": self.id,
            "fecha": local_time.isoformat(),
            "litros": self.litros,
            "ibutton": self.ibutton,
            "dispositivo_id": self.dispositivo_id,
            "dato1_id": self.dato1_id,
            "dato2_id": self.dato2_id,
        }
