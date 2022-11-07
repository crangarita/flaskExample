import os
from flask import Flask, jsonify, request
from app.common.error_handling import ObjectNotFound, AppErrorBaseClass

from app.example.controllers.producto import producto_bp
from app.db import db

version = os.environ.get('API_VERSION', 'v1')
prefix = f"/api/{version}"


def create_app(settings_module):

    app = Flask(__name__)
    app.config.from_object(settings_module)

    db.init_app(app)

    # Deshabilita el modo estricto de acabado de una URL con /
    app.url_map.strict_slashes = False

    # Registra los blueprints

    app.register_blueprint(producto_bp, url_prefix=f'{prefix}/productos')

    register_error_handlers(app)

    return app



def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception_error(e):
        return jsonify({'msg': e.args}), 500

    @app.errorhandler(405)
    def handle_405_error(e):
        return jsonify({'msg': 'Method not allowed'}), 405

    @app.errorhandler(403)
    def handle_403_error(e):
        return jsonify({'msg': 'Forbidden error'}), 403

    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({'msg': 'Not Found error'}), 404

    @app.errorhandler(AppErrorBaseClass)
    def handle_app_base_error(e):
        return jsonify({'msg': str(e)}), 500

    @app.errorhandler(ObjectNotFound)
    def handle_object_not_found_error(e):
        return jsonify({'msg': str(e)}), 404


