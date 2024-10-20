from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from datetime import datetime
import uuid
import os

application = Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@miso-devops-db.clkg7wpaxqmo.us-east-1.rds.amazonaws.com/miso_devops_db')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['JWT_SECRET_KEY'] = 'miso-devops-password'

db = SQLAlchemy(application)
ma = Marshmallow(application)
api = Api(application)
jwt = JWTManager(application)

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    app_uuid = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255))
    ip_address = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlacklistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blacklist

blacklist_schema = BlacklistSchema()

@application.route('/', methods=['GET'])
def health_check():
    return make_response(jsonify({"status": "healthy"}), 200)

@application.route('/version', methods=['GET'])
def version():
    return make_response(jsonify({"version": "1.0.0"}), 200)

@application.route('/get-token', methods=['POST'])
def get_token():
    return jsonify(access_token=create_access_token(identity='test'))

class BlacklistResource(Resource):
    @jwt_required()
    def post(self):
        email = request.json.get('email')
        app_uuid = request.json.get('app_uuid')
        blocked_reason = request.json.get('blocked_reason', '')
        ip_address = request.remote_addr

        if not email or not app_uuid:
            return {'message': 'Email y app_uuid son requeridos'}, 400

        try:
            uuid.UUID(app_uuid)
        except ValueError:
            return {'message': 'app_uuid debe ser un UUID válido'}, 400

        if len(blocked_reason) > 255:
            return {'message': 'La razón de bloqueo no puede exceder 255 caracteres'}, 400

        existing_email = Blacklist.query.filter_by(email=email).first()
        if existing_email:
            return {'message': 'El email ya está en la lista negra'}, 409

        new_blacklist = Blacklist(email=email, app_uuid=app_uuid, blocked_reason=blocked_reason, ip_address=ip_address)
        db.session.add(new_blacklist)
        db.session.commit()

        return {'message': 'Email agregado a la lista negra exitosamente'}, 201

class BlacklistCheckResource(Resource):
    @jwt_required()
    def get(self, email):
        blacklist_entry = Blacklist.query.filter_by(email=email).first()
        if blacklist_entry:
            return {
                'is_blacklisted': True,
                'reason': blacklist_entry.blocked_reason
            }
        return {'is_blacklisted': False}

@application.route('/clear-blacklist', methods=['DELETE'])
@jwt_required()
def clear_blacklist():
    db.session.query(Blacklist).delete()
    db.session.commit()
    return {'message': 'Lista negra limpiada exitosamente'}, 200

api.add_resource(BlacklistResource, '/blacklists')
api.add_resource(BlacklistCheckResource, '/blacklists/<string:email>')


with application.app_context():
    print("Creando tablas...")
    db.create_all()
    print("Tablas creadas exitosamente")

if __name__ == '__main__':
    application.run(debug=True)
