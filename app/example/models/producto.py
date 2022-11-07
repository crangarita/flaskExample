from app.db import db, BaseModelMixin
from datetime import datetime


class Producto(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)
    descripcion = db.Column(db.String)
    categoria_id = db.Column(db.Integer)

