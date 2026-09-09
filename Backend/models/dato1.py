from config import db

class Dato1(db.Model):
    __tablename__ = "dato1_referencias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}
