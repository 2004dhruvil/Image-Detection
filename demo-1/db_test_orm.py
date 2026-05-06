from app import app, db, ScanHistory, User

with app.app_context():
    scan = ScanHistory.query.first()
    if scan:
        print(f"Scan ID: {scan.id}")
        print(f"User ID from scan: {scan.user_id}")
        if scan.user:
            print(f"User retrieved via relationship: {scan.user.username}")
        else:
            print("scan.user is None")
    else:
        print("No scans found")
