from marshmallow import fields

from app.ext import ma


class ProductoSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    nombre = fields.String()
    descripcion = fields.String()
    categoria_id = fields.Integer()
