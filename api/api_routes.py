import jwt, datetime
from flask import request, jsonify
from flask_homework import app, db

from models.User import User
from models.Task import Task
from models.Goal import Goal

from functools import wraps

from jwt.exceptions import DecodeError, ExpiredSignatureError


TOKEN_EXPIRATION = datetime.timedelta(hours=2)
SECRET_KEY = app.config['SECRET_KEY']


@app.before_request
def before_request():
    if request.path == '/api/login' or request.path == '/api/register':
        return

    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token is missing!'}), 403
    try:
        _ = jwt.decode(token, SECRET_KEY)
    except DecodeError:
        return jsonify({'message': 'Token is invalid!'}), 403
    except ExpiredSignatureError:
        return jsonify({'message': 'Token is expired!'}), 403


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(data['username'], data['email'], data['password'])

    db.session.add(user)
    db.session.commit()

    data = {'username': user.username, 'user_agent': request.user_agent.string,
            'ip_address': request.remote_addr}

    token = jwt.encode(data, SECRET_KEY, algorithm='HS256').decode('')

    return jsonify({'token': token}), 200


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user is None:
        return 'User does not exist', 404

    if user.password == data['password']:
        data = {'username': user.username, 'user_agent': request.user_agent.string,
                'ip_address': request.remote_addr}
        token = jwt.encode(data, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'token': token}), 200

    return 'Wrong password', 401


@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return {'users': [user.username for user in users]}


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return {'tasks': [task.to_dict() for task in tasks]}


@app.route('/api/tasks/<int:user_id>', methods=['GET'])
def get_tasks_by_user(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return {'tasks': [task.to_dict() for task in tasks]}


@app.route('/api/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return 'Task does not exist', 404

    goals = Goal.query.filter_by(task_id=task_id).all()
    return {'task': task.to_dict()}


def create_goal(label, task_id):
    goal = Goal(label, task_id)
    db.session.add(goal)


@app.route('/api/create_task', methods=['POST'])
def create_task():
    data = request.get_json()

    token = request.headers.get('Authorization')
    decoded = jwt.decode(token, SECRET_KEY)
    username = decoded['username']

    user_id = User.query.filter_by(username=username).first().id

    task = Task(data['title'], user_id, data['description'])
    db.session.add(task)
    db.session.commit()

    for goal in data['goals']:
        create_goal(goal, task.id)

    db.session.commit()

    return {'task_id': task.id}, 200


@app.route('/api/update_task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()

    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return 'Task does not exist', 404

    task.title = data['title']
    task.description = data['description']

    db.session.commit()

    return {'task_id': task.id}, 200


@app.route('/api/update_goal', methods=['PUT'])
def update_goal():
    data = request.get_json()

    for goal_id, status in data['goals']:
        goal = Goal.query.filter_by(id=goal_id).first()

        if goal is None:
            continue

        goal.done = bool(status)

    db.session.commit()

    return '', 200