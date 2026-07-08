from app import db
from models import User, Location, Asset_Category, Asset
from datetime import date


def seed_database():
    if User.query.count() > 0:
        return

    locations = [
        Location(office_name='The Shard', address='32 London Bridge Street, SE1 9SG', city='London', country='UK', contact_phone='+441111111111'),
        Location(office_name='Tokyo Tower', address='4-2-8 Minato Ward, 105-0011', city='Tokyo', country='Japan', contact_phone='+81222222222'),
        Location(office_name='Taj Mahal Palace', address='Tajganj, Uttar Pradesh, 282001', city='Agra', country='India', contact_phone='+91333333333'),
        Location(office_name='Empire State', address='350 Fifth Avenue, NY 10118', city='New York', country='USA', contact_phone='+15555555555'),
        Location(office_name='Sydney Opera House', address='Bennelong Point, NSW 2000', city='Sydney', country='Australia', contact_phone='+61555555555'),
        Location(office_name='Karaiskakis Stadium', address='Karaoli Dimitriou & Sofianopoulou, 185 47', city='Piraeus', country='Greece', contact_phone='+306666666666'),
        Location(office_name='Lotte World Tower', address='300 Olympic-ro, Songpa-gu', city='Seoul', country='South Korea', contact_phone='+82777777777'),
        Location(office_name='Nymphenburg Palace', address='Schloss Nymphenburg 1, 80638', city='Munich', country='Germany', contact_phone='+498888888888'),
        Location(office_name='Louvre', address='99 Rue de Rivoli, 75001', city='Paris', country='France', contact_phone='+339999999999'),
        Location(office_name='Colosseum', address='Piazza del Colosseo, 1, 00184', city='Rome', country='Italy', contact_phone='+390000000000'),
    ]

    for location in locations:
        db.session.add(location)

    categories = [
        Asset_Category(name='Laptops', description='Portable computers issued to employees for daily work'),
        Asset_Category(name='Desktops', description='Fixed workstation computers for office use'),
        Asset_Category(name='Monitors', description='External display screens for workstations'),
        Asset_Category(name='Printers', description='Network and local printing devices'),
        Asset_Category(name='Docking Stations', description='USB-C and Thunderbolt docking stations for laptop connectivity'),
        Asset_Category(name='Mobile Phones', description='Company-issued smartphones'),
        Asset_Category(name='Headsets', description='Audio headsets for calls and video conferencing'),
        Asset_Category(name='Webcams', description='External cameras for video conferencing'),
        Asset_Category(name='Keyboards', description='External keyboards for workstations'),
        Asset_Category(name='Office Furniture', description='Desks, chairs, and ergonomic equipment'),
    ]

    for category in categories:
        db.session.add(category)

    db.session.commit()

    users = [
        User(username='admin', email='admin@company.com', role='admin', department='IT', location_id=1),
        User(username='mike.tyson', email='mike.tyson@company.com', role='regular', department='Engineering', location_id=1),
        User(username='albert.einstein', email='albert.einstein@company.com', role='regular', department='Marketing', location_id=2),
        User(username='liam.nelson', email='liam.nelson@company.com', role='regular', department='Sales', location_id=3),
        User(username='ann.hathaway', email='ann.hathaway@company.com', role='admin', department='IT', location_id=2),
        User(username='peter.parker', email='peter.parker@company.com', role='regular', department='HR', location_id=4),
        User(username='bruce.banner', email='bruce.banner@company.com', role='regular', department='Finance', location_id=5),
        User(username='bruce.wayne', email='bruce.wayne@company.com', role='regular', department='Operations', location_id=6),
        User(username='barry.allen', email='barry.allen@company.com', role='regular', department='Legal', location_id=7),
        User(username='wade.wilson', email='wade.wilson@company.com', role='regular', department='Support', location_id=8),
    ]

    for user in users:
        user.set_password('P@ssw0rd123')
        db.session.add(user)

    db.session.commit()

    assets = [
        Asset(
            asset_tag='LPT-001', name='MacBook Pro 16" M3', description='16-inch MacBook Pro with M3 Pro chip, 36GB RAM, 512GB SSD',
            serial_number='C02ZN1LPMD6T', purchase_date=date(2023, 1, 15), purchase_price=2499.00,
            status='In Use', assigned_to_user_id=2, category_id=1, location_id=1, warranty_expiry=date(2026, 1, 15)
        ),
        Asset(
            asset_tag='DKT-001', name='Dell OptiPlex 7010', description='Dell OptiPlex 7010 Tower, Intel i7-13700, 32GB RAM, 512GB SSD',
            serial_number='DKTP7010X923', purchase_date=date(2023, 2, 20), purchase_price=1149.00,
            status='Available', category_id=2, location_id=2, warranty_expiry=date(2026, 2, 20)
        ),
        Asset(
            asset_tag='MON-001', name='Dell UltraSharp U2723QE 27"', description='27-inch 4K USB-C hub monitor, IPS Black panel',
            serial_number='CN0HYR7F742', purchase_date=date(2023, 3, 10), purchase_price=579.99,
            status='In Use', assigned_to_user_id=3, category_id=3, location_id=2, warranty_expiry=date(2026, 3, 10)
        ),
        Asset(
            asset_tag='PRN-001', name='HP LaserJet Pro MFP 4101fdw', description='Multifunction laser printer with duplex, fax, and wireless',
            serial_number='VNB3K47291', purchase_date=date(2023, 4, 5), purchase_price=449.99,
            status='Available', category_id=4, location_id=1, warranty_expiry=date(2025, 4, 5)
        ),
        Asset(
            asset_tag='DCK-001', name='CalDigit TS4 Thunderbolt 4 Dock', description='18-port Thunderbolt 4 docking station, 98W charging',
            serial_number='CD4TS22A0587', purchase_date=date(2023, 5, 12), purchase_price=379.99,
            status='In Use', assigned_to_user_id=2, category_id=5, location_id=1, warranty_expiry=date(2025, 5, 12)
        ),
        Asset(
            asset_tag='MOB-001', name='iPhone 15 Pro 256GB', description='Company mobile phone, Space Black, 256GB storage',
            serial_number='F2LZK4HXGR', purchase_date=date(2023, 6, 18), purchase_price=1199.00,
            status='In Use', assigned_to_user_id=4, category_id=6, location_id=3, warranty_expiry=date(2025, 6, 18)
        ),
        Asset(
            asset_tag='HST-001', name='Jabra Evolve2 85', description='Wireless ANC headset with charging stand, UC certified',
            serial_number='JBR85UC0341', purchase_date=date(2023, 7, 1), purchase_price=379.99,
            status='Available', category_id=7, location_id=1, warranty_expiry=date(2025, 7, 1)
        ),
        Asset(
            asset_tag='WBC-001', name='Logitech Brio 4K', description='4K ultra HD webcam with HDR and Windows Hello support',
            serial_number='2218LZ04KP', purchase_date=date(2023, 8, 25), purchase_price=169.99,
            status='In Use', assigned_to_user_id=5, category_id=8, location_id=2, warranty_expiry=date(2025, 8, 25)
        ),
        Asset(
            asset_tag='KBD-001', name='Logitech MX Keys S', description='Wireless illuminated keyboard with smart backlighting',
            serial_number='2105MXK0892', purchase_date=date(2023, 9, 14), purchase_price=109.99,
            status='Available', category_id=9, location_id=4, warranty_expiry=date(2025, 9, 14)
        ),
        Asset(
            asset_tag='FRN-001', name='Herman Miller Aeron Chair', description='Size C, fully loaded, graphite frame, PostureFit SL',
            serial_number='AER-2023-04821', purchase_date=date(2023, 10, 30), purchase_price=1449.00,
            status='In Use', assigned_to_user_id=6, category_id=10, location_id=5, warranty_expiry=date(2035, 10, 30)
        ),
    ]

    for asset in assets:
        db.session.add(asset)

    db.session.commit()
    print("Seed data loaded successfully.")
