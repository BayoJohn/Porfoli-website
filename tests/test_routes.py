import pytest
from app import create_app
from app.models import db


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "ADMIN_PASSWORD": "testpassword"
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client):
    client.post("/admin/login", data={"password": "testpassword"})
    return client


# ── Public routes ──────────────────────────────────────────────────────────

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about_page_loads(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_projects_page_loads(client):
    response = client.get("/projects")
    assert response.status_code == 200


def test_blog_page_loads(client):
    response = client.get("/blog")
    assert response.status_code == 200


def test_contact_page_loads(client):
    response = client.get("/contact")
    assert response.status_code == 200


def test_contact_form_submission(client):
    response = client.post("/contact", data={
        "name": "Test User",
        "email": "test@test.com",
        "message": "Hello from test"
    })
    assert response.status_code == 302


def test_404_page(client):
    response = client.get("/nonexistent-page")
    assert response.status_code == 404


# ── Visitor tracking ───────────────────────────────────────────────────────

def test_visitor_ip_is_tracked(client, app):
    client.get("/")
    with app.app_context():
        from app.models import PageView
        views = PageView.query.all()
        assert len(views) >= 1


def test_admin_routes_not_tracked(client, app):
    client.get("/admin/login")
    with app.app_context():
        from app.models import PageView
        views = PageView.query.filter_by(path="/admin/login").all()
        assert len(views) == 0


# ── Admin auth ─────────────────────────────────────────────────────────────

def test_admin_login_wrong_password(client):
    response = client.post("/admin/login", data={"password": "wrongpassword"})
    assert response.status_code == 200


def test_admin_login_correct_password(client):
    response = client.post("/admin/login", data={"password": "testpassword"})
    assert response.status_code == 302


def test_admin_dashboard_requires_login(client):
    response = client.get("/admin")
    assert response.status_code == 302


def test_admin_dashboard_accessible_when_logged_in(admin_client):
    response = admin_client.get("/admin")
    assert response.status_code == 200


def test_admin_logout(admin_client):
    response = admin_client.get("/admin/logout")
    assert response.status_code == 302
    response = admin_client.get("/admin")
    assert response.status_code == 302


# ── Admin posts ────────────────────────────────────────────────────────────

def test_admin_create_post(admin_client, app):
    response = admin_client.post("/admin/post/new", data={
        "title": "Test Post",
        "body": "This is a test post body"
    })
    assert response.status_code == 302
    with app.app_context():
        from app.models import Post
        post = Post.query.filter_by(title="Test Post").first()
        assert post is not None


def test_admin_delete_post(admin_client, app):
    with app.app_context():
        from app.models import Post
        post = Post(title="To Delete", body="body")
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    response = admin_client.post(f"/admin/post/{post_id}/delete")
    assert response.status_code == 302
    with app.app_context():
        from app.models import Post
        assert Post.query.get(post_id) is None


# ── Admin projects ─────────────────────────────────────────────────────────

def test_admin_create_project(admin_client, app):
    response = admin_client.post("/admin/project/new", data={
        "title": "Test Project",
        "description": "A test project",
        "url": "https://github.com/test",
        "tech_stack": "Python, Flask"
    })
    assert response.status_code == 302
    with app.app_context():
        from app.models import Project
        project = Project.query.filter_by(title="Test Project").first()
        assert project is not None
