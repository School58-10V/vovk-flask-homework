from flask_homework import db


# create goal model with label, done, task_id and many-to-one relationship with tasks
class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(80), nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    def __init__(self, label, task_id):
        self.label = label
        self.done = False
        self.task_id = task_id

    def __repr__(self):
        return f'<Goal {self.label}, Status {self.done}>'

    def to_dict(self):
        return {'id': self.id, 'label': self.label, 'done': self.done}