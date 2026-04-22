from datetime import datetime, timezone
from app import db


class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    assets = db.relationship('Asset', backref='client', lazy=True)

    def to_dict(self, include_assets=False):
        data = {
            'id': self.id,
            'name': self.name,
            'contact_email': self.contact_email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'asset_count': len(self.assets),
        }
        if include_assets:
            data['assets'] = [a.to_dict() for a in self.assets]
        return data


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False, default='active')
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    assigned_to = db.Column(db.String(200))
    last_seen = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    audit_logs = db.relationship(
        'AssetStatusAudit',
        backref='asset',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'asset_type': self.asset_type,
            'serial_number': self.serial_number,
            'status': self.status,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'assigned_to': self.assigned_to,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }


class AssetStatusAudit(db.Model):
    __tablename__ = 'asset_status_audits'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    previous_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    requester_ip = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'requester_ip': self.requester_ip,
            'timestamp': self.created_at.isoformat(),
        }
