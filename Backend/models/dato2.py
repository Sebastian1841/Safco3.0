from config import db

class Dato2(db.Model):
    __tablename__ = "dato2_referencias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}
