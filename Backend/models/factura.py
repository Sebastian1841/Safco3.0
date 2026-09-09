from extensions import db

class Factura(db.Model):
    __tablename__ = "facturas"
    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(50), unique=True, nullable=False)
    producto       = db.Column(db.String(200))
    litros         = db.Column(db.Float)
    fecha          = db.Column(db.String(20))
    total          = db.Column(db.Integer)
    proveedor      = db.Column(db.String(100), default="COPEC")  

    def to_dict(self):
        return {
            "id": self.id,
            "numero_factura": self.numero_factura,
            "producto": self.producto,
            "litros": self.litros,
            "fecha": self.fecha,
            "total": self.total,
            "proveedor": self.proveedor  
        }
