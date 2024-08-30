from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(
        timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_done': self.is_done,
            'created_at': self.created_at,
            'completed_at': self.completed_at
        }


db.create_all()


@app.route("/health")
def health():
    return jsonify({'message': 'live'})


@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        new_task = Task(title=data['title'],
                        description=data.get('description'))
        db.session.add(new_task)
        db.session.commit()
        return make_response(jsonify({'message': 'task created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'error creating task: {str(e)}'}), 500)


@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()
        return make_response(jsonify([task.json() for task in tasks]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error getting tasks: {str(e)}'}), 500)


@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    try:
        task = Task.query.filter_by(id=id).first()
        if task:
            return make_response(jsonify({'task': task.json()}), 200)
        return make_response(jsonify({'message': 'task not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'error getting task: {str(e)}'}), 500)


@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    try:
        task = Task.query.filter_by(id=id).first()
        if task:
            data = request.get_json()
            task.title = data['title']
            task.description = data.get('description', task.description)
            if 'is_done' in data:
                task.is_done = data['is_done']
                if task.is_done:
                    task.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            return make_response(jsonify({'message': 'task updated'}), 200)
        return make_response(jsonify({'message': 'task not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'error updating task: {str(e)}'}), 500)


@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    try:
        task = Task.query.filter_by(id=id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            return make_response(jsonify({'message': 'task deleted'}), 200)
        return make_response(jsonify({'message': 'task not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'error deleting task: {str(e)}'}), 500)


@app.route('/tasks/completed', methods=['GET'])
def get_completed_tasks():
    try:
        completed_tasks = Task.query.filter_by(is_done=True).all()
        return make_response(jsonify([task.json() for task in completed_tasks]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error getting completed tasks: {str(e)}'}), 500)


if __name__ == '__main__':
    app.run(debug=True)
