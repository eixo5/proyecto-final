import pytest
import jwt
import datetime
from app import app, db, Workshop, User, bcrypt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def admin_headers(client):
    with app.app_context():
        hashed_pw = bcrypt.generate_password_hash('pass123').decode('utf-8')
        admin_user = User(username='admin_test', password=hashed_pw, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

        user_id = admin_user.id

    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def test_get_workshops_public(client):
    response = client.get('/api/workshops')
    assert response.status_code == 200
    assert response.json == []


def test_create_workshop_authorized(client, admin_headers):
    new_data = {
        "name": "Python 101",
        "description": "Intro a Python",
        "date": "2023-12-01",
        "time": "10:00",
        "location": "Lab 1",
        "category": "Tecnología"
    }
    # Pasamos 'headers=admin_headers'
    response = client.post('/api/workshops', json=new_data, headers=admin_headers)

    assert response.status_code == 201
    assert response.json['name'] == "Python 101"


def test_create_workshop_unauthorized(client):
    new_data = {
        "name": "Hacker Workshop",
        "date": "2023-12-01",
        "time": "10:00",
        "location": "Lab X",
        "category": "Hacking"
    }
    # Sin headers
    response = client.post('/api/workshops', json=new_data)

    # Esperamos 401 (Unauthorized)
    assert response.status_code == 401


def test_delete_workshop_authorized(client, admin_headers):
    client.post('/api/workshops', json={
        "name": "To Delete", "date": "2023-01-01", "time": "09:00",
        "location": "X", "category": "Test"
    }, headers=admin_headers)

    response = client.delete('/api/workshops/1', headers=admin_headers)
    assert response.status_code == 200


def test_register_student_public(client, admin_headers):
    client.post('/api/workshops', json={
        "name": "Clase Abierta",
        "date": "2023-01-01",
        "time": "09:00",
        "location": "Aula Magna",
        "category": "General"
    }, headers=admin_headers)

    student_data = {"student_name": "Juan Perez"}
    response = client.post('/api/workshops/1/register', json=student_data)

    assert response.status_code == 201
    assert "registrado exitosamente" in response.json['message']
