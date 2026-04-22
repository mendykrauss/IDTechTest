import csv
from io import StringIO

from flask import Blueprint, Response, jsonify, request
from app import db
from app.models import Asset

assets_bp = Blueprint('assets', __name__, url_prefix='/api')

PER_PAGE = 10


def _build_filtered_assets_query():
    search = request.args.get('search', '').strip()
    asset_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    query = Asset.query

    if search:
        query = query.filter(Asset.name.ilike(f'%{search}%'))

    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)

    if status:
        query = query.filter(Asset.status == status)

    return query


@assets_bp.route('/assets', methods=['GET'])
def list_assets():
    page = max(1, request.args.get('page', 1, type=int))
    query = _build_filtered_assets_query()

    total = query.count()

    offset = (page - 1) * PER_PAGE
    assets = query.order_by(Asset.name).offset(offset).limit(PER_PAGE).all()

    return jsonify({
        'assets': [a.to_dict() for a in assets],
        'total': total,
        'page': page,
        'per_page': PER_PAGE,
        'pages': max(1, (total + PER_PAGE - 1) // PER_PAGE),
    })


@assets_bp.route('/assets/export', methods=['GET'])
def export_assets_csv():
    assets = _build_filtered_assets_query().order_by(Asset.name).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id',
        'name',
        'asset_type',
        'status',
        'client_id',
        'client_name',
        'serial_number',
        'assigned_to',
        'last_seen',
        'notes',
        'created_at',
    ])

    for asset in assets:
        writer.writerow([
            asset.id,
            asset.name,
            asset.asset_type,
            asset.status,
            asset.client_id,
            asset.client.name if asset.client else '',
            asset.serial_number or '',
            asset.assigned_to or '',
            asset.last_seen.isoformat() if asset.last_seen else '',
            asset.notes or '',
            asset.created_at.isoformat() if asset.created_at else '',
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=assets.csv',
        },
    )


@assets_bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return jsonify(asset.to_dict())


@assets_bp.route('/assets', methods=['POST'])
def create_asset():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    missing_fields = []
    field_labels = {
        'name': 'Name',
        'asset_type': 'Type',
        'client_id': 'Client',
    }
    for field in ('name', 'asset_type', 'client_id'):
        value = data.get(field)
        if value is None:
            missing_fields.append(field)
            continue
        if isinstance(value, str) and not value.strip():
            missing_fields.append(field)
    if missing_fields:
        missing_labels = [field_labels[field] for field in missing_fields]
        return jsonify({
            'error': f"Missing required field(s): {', '.join(missing_labels)}"
        }), 400

    name = data['name']
    asset_type = data['asset_type']
    client_id = data['client_id']

    asset = Asset(
        name=name,
        asset_type=asset_type,
        client_id=client_id,
        serial_number=data.get('serial_number'),
        assigned_to=data.get('assigned_to'),
        notes=data.get('notes'),
        status=data.get('status', 'active'),
    )
    db.session.add(asset)
    db.session.commit()
    return jsonify(asset.to_dict()), 201


@assets_bp.route('/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    if 'name' in data:
        asset.name = data['name']
    if 'asset_type' in data:
        asset.asset_type = data['asset_type']
    if 'serial_number' in data:
        asset.serial_number = data['serial_number']
    if 'assigned_to' in data:
        asset.assigned_to = data['assigned_to']
    if 'notes' in data:
        asset.notes = data['notes']
    if 'client_id' in data:
        asset.client_id = data['client_id']

    db.session.commit()
    return jsonify(asset.to_dict())


@assets_bp.route('/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Asset deleted'}), 200


@assets_bp.route('/assets/<int:asset_id>/toggle', methods=['POST'])
def toggle_asset_status(asset_id):
    asset = Asset.query.get_or_404(asset_id)

    if asset.status == 'active':
        asset.status = 'inactive'
    elif asset.status == 'inactive':
        asset.status = 'active'
    # retired assets cannot be toggled further

    db.session.commit()
    return jsonify(asset.to_dict())


@assets_bp.route('/assets/<int:asset_id>/decommission', methods=['POST'])
def decommission_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if asset.status == 'retired':
        return jsonify({'error': 'Asset is already retired'}), 400
    asset.status = 'retired'
    db.session.commit()
    return jsonify(asset.to_dict())
