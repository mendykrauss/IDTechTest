"""
Seed the database with realistic sample data for development and testing.
Run this after setting up the database: python seed.py
"""
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import Client, Asset, AssetStatusAudit

app = create_app('development')


def seed():
    with app.app_context():
        db.create_all()

        # Clear existing data
        AssetStatusAudit.query.delete()
        Asset.query.delete()
        Client.query.delete()
        db.session.commit()

        now = datetime.now(timezone.utc)

        # --- Clients ---
        clients = [
            Client(
                name='Pinnacle Healthcare Group',
                contact_email='it@pinnaclehealthcare.com',
                phone='(555) 210-4400',
            ),
            Client(
                name='Summit Realty Partners',
                contact_email='support@summitrp.com',
                phone='(555) 348-7700',
            ),
            Client(
                name='BlueSky Manufacturing',
                contact_email='helpdesk@blueskymnfg.com',
                phone='(555) 481-2200',
            ),
            Client(
                name='Riverside Law Offices',
                contact_email='admin@riversidelaw.com',
                phone='(555) 623-9900',
            ),
            Client(
                name='TechStart Solutions',
                contact_email='ops@techstart.io',
                phone='(555) 760-5500',
            ),
        ]
        for c in clients:
            db.session.add(c)
        db.session.flush()  # Assign IDs

        pinnacle, summit, bluesky, riverside, techstart = clients

        # --- Assets ---
        assets = [
            # Pinnacle Healthcare Group
            Asset(
                name='HP ProBook 450 G9',
                asset_type='workstation',
                serial_number='PHG-WS-001',
                status='active',
                client_id=pinnacle.id,
                assigned_to='Dr. Sarah Chen',
                last_seen=now - timedelta(hours=2),
                notes='Primary workstation in Exam Room 3',
            ),
            Asset(
                name='HP ProBook 450 G8',
                asset_type='workstation',
                serial_number='PHG-WS-002',
                status='inactive',
                client_id=pinnacle.id,
                assigned_to='Dr. Marcus Webb',
                last_seen=now - timedelta(days=90),
                notes='On loan — not currently in use',
            ),
            Asset(
                name='Dell PowerEdge R740',
                asset_type='server',
                serial_number='PHG-SRV-001',
                status='active',
                client_id=pinnacle.id,
                assigned_to=None,
                last_seen=now - timedelta(minutes=15),
                notes='Primary file and application server',
            ),
            Asset(
                name='Cisco Catalyst 2960-X',
                asset_type='network',
                serial_number='PHG-NET-001',
                status='active',
                client_id=pinnacle.id,
                assigned_to=None,
                last_seen=now - timedelta(minutes=5),
                notes='Core switch — server closet',
            ),
            Asset(
                name='HP LaserJet Enterprise M507',
                asset_type='peripheral',
                serial_number='PHG-PRN-001',
                status='active',
                client_id=pinnacle.id,
                assigned_to=None,
                last_seen=now - timedelta(days=45),
                notes='Reception area printer',
            ),
            Asset(
                name='Lenovo ThinkCentre M720q',
                asset_type='workstation',
                serial_number='PHG-WS-003',
                status='retired',
                client_id=pinnacle.id,
                assigned_to=None,
                last_seen=None,  # intentional — triggers Bug 5
                notes='Decommissioned; awaiting secure wipe and disposal',
            ),

            # Summit Realty Partners
            Asset(
                name='MacBook Pro 14-inch (M3)',
                asset_type='workstation',
                serial_number='SRP-WS-001',
                status='active',
                client_id=summit.id,
                assigned_to='Jennifer Park',
                last_seen=now - timedelta(hours=1),
                notes='Sales Director laptop',
            ),
            Asset(
                name='Dell OptiPlex 7090',
                asset_type='workstation',
                serial_number='SRP-WS-002',
                status='inactive',
                client_id=summit.id,
                assigned_to=None,
                last_seen=None,  # intentional — triggers Bug 5
                notes='Former front desk machine; pending reassignment',
            ),
            Asset(
                name='Synology NAS DS920+',
                asset_type='server',
                serial_number='SRP-NAS-001',
                status='active',
                client_id=summit.id,
                assigned_to=None,
                last_seen=now - timedelta(hours=3),
                notes='Network attached storage — listing documents and contracts',
            ),
            Asset(
                name='Ubiquiti UniFi 24-Port Switch',
                asset_type='network',
                serial_number='SRP-NET-001',
                status='active',
                client_id=summit.id,
                assigned_to=None,
                last_seen=now - timedelta(minutes=10),
                notes='Main office switch',
            ),
            Asset(
                name='Canon imageRUNNER 1643i',
                asset_type='peripheral',
                serial_number='SRP-PRN-001',
                status='inactive',
                client_id=summit.id,
                assigned_to=None,
                last_seen=now - timedelta(days=30),
                notes='Paper jam issue; awaiting service call',
            ),

            # BlueSky Manufacturing
            Asset(
                name='Dell Latitude 5540',
                asset_type='workstation',
                serial_number='BSM-WS-001',
                status='active',
                client_id=bluesky.id,
                assigned_to='Tom Ramirez',
                last_seen=now - timedelta(hours=4),
                notes='Floor supervisor laptop',
            ),
            Asset(
                name='Dell Latitude 5530',
                asset_type='workstation',
                serial_number='BSM-WS-002',
                status='active',
                client_id=bluesky.id,
                assigned_to='Anna Kowalski',
                last_seen=now - timedelta(days=1),
                notes='Quality control workstation',
            ),
            Asset(
                name='HPE ProLiant DL380 Gen10',
                asset_type='server',
                serial_number='BSM-SRV-001',
                status='active',
                client_id=bluesky.id,
                assigned_to=None,
                last_seen=now - timedelta(minutes=30),
                notes='ERP application server',
            ),
            Asset(
                name='Cisco ASA 5506-X',
                asset_type='network',
                serial_number='BSM-FW-001',
                status='inactive',
                client_id=bluesky.id,
                assigned_to=None,
                last_seen=None,  # intentional — triggers Bug 5
                notes='Old firewall — replaced by Meraki MX; being held for parts',
            ),
            Asset(
                name='Zebra ZT410 Label Printer',
                asset_type='peripheral',
                serial_number='BSM-PRN-001',
                status='active',
                client_id=bluesky.id,
                assigned_to=None,
                last_seen=now - timedelta(hours=6),
                notes='Shipping and receiving department',
            ),

            # Riverside Law Offices
            Asset(
                name='Microsoft Surface Pro 9',
                asset_type='workstation',
                serial_number='RLO-WS-001',
                status='active',
                client_id=riverside.id,
                assigned_to='Patricia Nguyen, Esq.',
                last_seen=now - timedelta(hours=2),
                notes='Senior partner tablet/laptop',
            ),
            Asset(
                name='Synology DiskStation DS418j',
                asset_type='server',
                serial_number='RLO-NAS-001',
                status='retired',
                client_id=riverside.id,
                assigned_to=None,
                last_seen=None,  # intentional — triggers Bug 5
                notes='End-of-life NAS; case files migrated to SharePoint',
            ),
            Asset(
                name='HP OfficeJet Pro 9015e',
                asset_type='peripheral',
                serial_number='RLO-PRN-001',
                status='active',
                client_id=riverside.id,
                assigned_to=None,
                last_seen=now - timedelta(days=3),
                notes='Conference room multifunction printer',
            ),

            # TechStart Solutions
            Asset(
                name='MacBook Air 15-inch (M2)',
                asset_type='workstation',
                serial_number='TSS-WS-001',
                status='active',
                client_id=techstart.id,
                assigned_to='Raj Patel',
                last_seen=now - timedelta(hours=1),
                notes='Lead developer machine',
            ),
            Asset(
                name='Mac Mini M2 Pro',
                asset_type='server',
                serial_number='TSS-SRV-001',
                status='active',
                client_id=techstart.id,
                assigned_to=None,
                last_seen=now - timedelta(minutes=20),
                notes='CI/CD build server',
            ),
            Asset(
                name='Netgear ProSAFE GS748T',
                asset_type='network',
                serial_number='TSS-NET-001',
                status='active',
                client_id=techstart.id,
                assigned_to=None,
                last_seen=now - timedelta(hours=1),
                notes='Office core switch',
            ),
        ]

        for a in assets:
            db.session.add(a)

        db.session.commit()
        print(f'Seeded {len(clients)} clients and {len(assets)} assets.')


if __name__ == '__main__':
    seed()
