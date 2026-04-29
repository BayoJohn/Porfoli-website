from app import create_app
from app.models import db, Project

app = create_app()
with app.app_context():
    p1 = Project.query.get(1)
    if p1:
        p1.image = 'dark_hero_image.png'
    p2 = Project.query.get(2)
    if p2:
        p2.image = 'kites-in-air-oq.jpg'
    db.session.commit()
    print("Images updated.")
