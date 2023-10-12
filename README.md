# Project setup
1. Create a Python virtual environment and activate it:
```
python3 -m venv .venv
source .venv/bin/activate
```
2. Install dependencies:
```
python3 -m pip install -r requirements.txt
```
3. Apply migrations:
```
python3 manage.py migrate
```
4. Load fixtures:
```
python3 manage.py loaddata initial
```
5. Run the server:
```
python3 manage.py runserver
```

Users and their tokens have to be created manually via the admin panel.

# Endpoints
POST `/images/` - upload an image

GET `/images/` - list user's images

POST `/images/links/` - create an expiring link to an image

GET `/images/links/{link_id}` - retrieve an image or its thumbnail