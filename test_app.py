import pytest
from app import app, db, Workshop


@pytest.fixture
def client():
    # Configurar la app para modo testing (BD temporal en memoria)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_get_workshops_empty(client):
    """Debe retornar lista vacía al inicio."""
    response = client.get('/api/workshops')
    assert response.status_code == 200
    assert response.json == []


def test_create_workshop(client):
    """Debe permitir crear un taller vía POST."""
    new_data = {
        "name": "Python 101",
        "description": "Intro a Python",
        "date": "2023-12-01",
        "time": "10:00",
        "location": "Lab 1",
        "category": "Tecnología"
    }
    response = client.post('/api/workshops', json=new_data)
    assert response.status_code == 201
    assert response.json['name'] == "Python 101"


def test_delete_workshop(client):
    """Debe permitir borrar un taller."""
    # 1. Crear
    client.post('/api/workshops', json={
        "name": "To Delete", "date": "2023-01-01", "time": "09:00",
        "location": "X", "category": "Test"
    })
    # 2. Borrar (ID será 1)
    response = client.delete('/api/workshops/1')
    assert response.status_code == 200