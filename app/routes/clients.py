from flask import Blueprint, jsonify, request
from app import db
from app.models import Client, Asset

clients_bp = Blueprint('clients', __name__, url_prefix='/api')


@clients_bp.route('/clients', methods=['GET'])
def list_clients():
    clients = Client.query.order_by(Client.name).all()
    return jsonify({'clients': [c.to_dict() for c in clients]})


@clients_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify(client.to_dict(include_assets=True))


@clients_bp.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    if not data or not data.get('name', '').strip():
        return jsonify({'error': 'Client name is required'}), 400

    client = Client(
        name=data['name'].strip(),
        contact_email=data.get('contact_email'),
        phone=data.get('phone'),
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict()), 201


@clients_bp.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    if 'name' in data:
        client.name = data['name']
    if 'contact_email' in data:
        client.contact_email = data['contact_email']
    if 'phone' in data:
        client.phone = data['phone']

    db.session.commit()
    return jsonify(client.to_dict())


@clients_bp.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)

    has_assets = Asset.query.filter_by(client_id=client.id).first() is not None
    if has_assets:
        return jsonify({'error': 'Cannot delete client with assigned assets'}), 409

    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Client deleted'}), 200
