from flask_homework import db


# create task model with title, user_id, description and one-to-many relationship with goals
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    goals = db.relationship('Goal', backref='task', lazy=True)

    def __init__(self, title, user_id, description):
        self.title = title
        self.user_id = user_id
        self.description = description

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'description': self.description, 'goals': [goal.to_dict() for goal in self.goals]}