from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask('TO-DO Tracker')
app.config.from_object('config')
CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# with app.app_context():
#     db.create_all()