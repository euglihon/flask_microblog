from app import create_app, db
from app.models import User, Post, Message, Notification

app = create_app()

# оболочка для автомат. импортирования во flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Message': Message, 'Notification': Notification}


if __name__ == '__main__':
	app.run(debug=True)
