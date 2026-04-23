from app import create_app
from app.models import db, Post

app = create_app()
with app.app_context():
    posts = Post.query.all()
    for p in posts:
        print(f"ID: {p.id} | Title: {p.title}")
