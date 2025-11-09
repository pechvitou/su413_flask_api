git link: https://github.com/PechVitou/su413_flask_api.git

Project: Flask + Postman + MySQL

=========================================================
**Run Project:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

**Require to run wamp/xamp
=========================================================
**Migrate Database + Seeding:
flask db init
flask migrate -m "Migration"
flask db upgrade
python seed.py

=========================================================
**copy .env to root directory of the project

Use "SU413_Flask.postman_collection.json" to import into postman to test API

**Reminder: Run python seed.py before testing API in postman