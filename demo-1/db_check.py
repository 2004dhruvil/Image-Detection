import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

load_dotenv()
app = Flask(__name__)
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
db = SQLAlchemy(app)

with app.app_context():
    result = db.session.execute(text('SELECT * FROM scan_history')).fetchall()
    print("Scan History Table:")
    for row in result:
        print(row)
    
    result2 = db.session.execute(text('SELECT * FROM user')).fetchall()
    print("\nUser Table:")
    for row in result2:
        print(row)
