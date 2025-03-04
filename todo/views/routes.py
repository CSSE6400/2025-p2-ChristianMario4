from flask import Blueprint, jsonify
from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():

    # Get the "completed" and "window" query parameter
    completed_filter = request.args.get('completed', default=None)
    window_value = request.args.get('window', default = None, type=int)

    if window_value is not None:
        cutoff_date = datetime.utcnow() + timedelta(days=window_value)
    todos = Todo.query.all()
    result = []
    for todo in todos:

        # completed filter handling
        if (completed_filter is not None) and ((str(todo.completed).lower()) != completed_filter.lower()):
            continue

        # window filter handling
        if window_value is not None and todo.deadline_at and todo.deadline_at > cutoff_date:
            continue

        result.append(todo.to_dict())

    return jsonify(result)


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST'])
def create_todo():
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
        )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    allowed_keys = ['title', 'description', 'completed', 'deadline_at']

    if todo.title is None:
        return jsonify({'error': 'Title cannot be null'}), 400
    
    # Check for invalid values
    provided_keys = request.json.keys()

    for key in provided_keys:
        if key not in allowed_keys:
            return jsonify({'error': 'Forbidden key attempted to be added'}), 400
        
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    todo.title = request.json.get('title', todo.title)
    if todo.title is None:
        return jsonify({'error': 'Title cannot be null'}), 404
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)

    allowed_keys = ['title', 'description', 'completed', 'deadline_at']
    # Check for invalid values
    provided_keys = request.json.keys()
    for key in provided_keys:
        if key not in allowed_keys:
            return jsonify({'error': 'Forbidden key attempted to be added'}), 400
    
    db.session.commit()
    
    return jsonify(todo.to_dict())


@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200

