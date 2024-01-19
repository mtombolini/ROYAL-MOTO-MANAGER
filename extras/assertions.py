from models.user import Role
from routes.api_routes import api_blueprint

from flask import jsonify

@api_blueprint.route('/get_superadmin_role_id')
def get_superadmin_id_role(session):
    return jsonify(
        superadmin_role_id=session.query(Role).filter_by(description="superadministrador").first().id_role,
    )