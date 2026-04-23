from app import create_app
from app.models import db, Post

app = create_app()
with app.app_context():
    count = Post.query.count()
    print(f"Total posts: {count}")
    p = Post.query.first()
    if p:
        print(f"First post ID: {p.id}")
        print(f"Title: {p.title}")
        print(f"Body: {p.body[:100]}...")
