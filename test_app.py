import pytest
from app import app, db, Task

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'message': 'live'}


def test_create_task(client):
    response = client.post('/tasks', json={
        'title': 'Test Task',
        'description': 'This is a test task'
    })
    assert response.status_code == 201
    assert response.json == {'message': 'task created'}

    tasks = Task.query.all()
    assert len(tasks) == 1
    assert tasks[0].title == 'Test Task'
    assert tasks[0].description == 'This is a test task'


def test_get_tasks(client):
    response = client.get('/tasks')
    assert response.status_code == 200
    assert len(response.json) == 0


def test_update_task(client):
    task = Task(title='Old Task', description='Old description')
    db.session.add(task)
    db.session.commit()

    response = client.put(f'/tasks/{task.id}', json={
        'title': 'Updated Task',
        'description': 'Updated description',
        'is_done': True
    })
    assert response.status_code == 200
    assert response.json == {'message': 'task updated'}

    updated_task = Task.query.get(task.id)
    assert updated_task.title == 'Updated Task'
    assert updated_task.description == 'Updated description'
    assert updated_task.is_done is True


def test_delete_task(client):
    task = Task(title='Task to delete', description='Description')
    db.session.add(task)
    db.session.commit()

    response = client.delete(f'/tasks/{task.id}')
    assert response.status_code == 200
    assert response.json == {'message': 'task deleted'}

    deleted_task = Task.query.get(task.id)
    assert deleted_task is None
