from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.example.models.producto import Producto
from app.example.schemas.producto_schema import ProductoSchema

from app import ObjectNotFound

producto_bp = Blueprint('producto_bp', __name__)

producto_schema = ProductoSchema()

@producto_bp.route('', methods=['GET'])
def get_productos():
    productos = Producto.get_all()
    result = producto_schema.dump(productos, many=True)
    return jsonify(result)
