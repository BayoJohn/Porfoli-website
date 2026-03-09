import os
import markdown as md
from datetime import datetime, timedelta
from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from app.models import db, Project, Post, Message, Comment, PageView

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.secret_key = "change-this-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
    app.config["ADMIN_PASSWORD"] = "changeme123"

    db.init_app(app)

    def uploads_path(*args):
        return os.path.join(app.root_path, "static/uploads", *args)

    @app.before_request
    def track_visit():
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return
        view = PageView(
            path=request.path,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:300]
        )
        db.session.add(view)
        db.session.commit()

    # ── Public routes ─────────────────────────────────────────────────────────

    @app.route("/")
    def home():
        projects = Project.query.limit(2).all()
        posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
        return render_template("home.html", projects=projects, posts=posts)

    @app.route("/about")
    def about():
        profile_exists = os.path.exists(uploads_path("profile.jpg"))
        return render_template("about.html", profile_exists=profile_exists)

    @app.route("/projects")
    def projects():
        all_projects = Project.query.all()
        return render_template("projects.html", projects=all_projects)

    @app.route("/projects/<int:project_id>", methods=["GET", "POST"])
    def project_detail(project_id):
        project = Project.query.get_or_404(project_id)
        comments = Comment.query.filter_by(project_id=project_id, approved=True).order_by(Comment.created_at.desc()).all()
        if request.method == "POST":
            comment = Comment(
                name=request.form["name"],
                email=request.form["email"],
                body=request.form["body"],
                project_id=project_id,
                approved=True
            )
            db.session.add(comment)
            db.session.commit()
            flash("Comment posted!")
            return redirect(url_for("project_detail", project_id=project_id))
        return render_template("project_detail.html", project=project, comments=comments)

    @app.route("/blog")
    def blog():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("blog.html", posts=posts)

    @app.route("/blog/<int:post_id>", methods=["GET", "POST"])
    def post(post_id):
        post = Post.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_id=post_id, approved=True).order_by(Comment.created_at.desc()).all()
        if request.method == "POST":
            comment = Comment(
                name=request.form["name"],
                email=request.form["email"],
                body=request.form["body"],
                post_id=post_id,
                approved=True
            )
            db.session.add(comment)
            db.session.commit()
            flash("Comment posted!")
            return redirect(url_for("post", post_id=post_id))
        post_body = md.markdown(post.body, extensions=['fenced_code', 'codehilite', 'tables', 'nl2br'])
        return render_template("post.html", post=post, comments=comments, post_body=post_body)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            msg = Message(
                name=request.form["name"],
                email=request.form["email"],
                message=request.form["message"]
            )
            db.session.add(msg)
            db.session.commit()
            flash("Thanks! Your message was sent.")
            return redirect(url_for("contact"))
        return render_template("contact.html")

    # ── Admin helpers ─────────────────────────────────────────────────────────

    def admin_context():
        return dict(
            pending_count=Comment.query.filter_by(approved=False).count(),
            unread_count=Message.query.filter_by(read=False).count(),
            profile_exists=os.path.exists(uploads_path("profile.jpg")),
        )

    # ── Admin auth ────────────────────────────────────────────────────────────

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            if request.form["password"] == app.config["ADMIN_PASSWORD"]:
                session["admin"] = True
                return redirect(url_for("admin_dashboard"))
            flash("Wrong password.")
        return render_template("admin_login.html")

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin", None)
        return redirect(url_for("home"))

    # ── Admin dashboard ───────────────────────────────────────────────────────

    @app.route("/admin")
    def admin_dashboard():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        stats = {
            "posts": Post.query.count(),
            "projects": Project.query.count(),
            "comments": Comment.query.count(),
            "messages": Message.query.count(),
        }

        total_visits = PageView.query.count()
        unique_visitors = db.session.query(PageView.ip).distinct().count()

        from sqlalchemy import func
        top_pages = db.session.query(
            PageView.path,
            func.count(PageView.id).label('count')
        ).group_by(PageView.path).order_by(func.count(PageView.id).desc()).limit(5).all()

        today = datetime.utcnow().date()
        daily_visits = []
        daily_labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = PageView.query.filter(
                db.func.date(PageView.created_at) == day
            ).count()
            daily_visits.append(count)
            daily_labels.append(day.strftime('%b %d'))

        recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
        recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
        recent_messages = Message.query.order_by(Message.id.desc()).limit(5).all()

        return render_template("admin_dashboard.html",
            stats=stats,
            total_visits=total_visits,
            unique_visitors=unique_visitors,
            top_pages=top_pages,
            daily_visits=daily_visits,
            daily_labels=daily_labels,
            recent_posts=recent_posts,
            recent_comments=recent_comments,
            recent_messages=recent_messages,
            **admin_context()
        )

    # ── Admin posts ───────────────────────────────────────────────────────────

    @app.route("/admin/posts")
    def admin_posts():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("admin_posts.html", posts=posts, **admin_context())

    @app.route("/admin/post/new", methods=["GET", "POST"])
    def admin_post_new():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        if request.method == "POST":
            post = Post(title=request.form["title"], body=request.form["body"])
            db.session.add(post)
            db.session.commit()
            flash("Post created!")
            return redirect(url_for("admin_posts"))
        return render_template("admin_post_form.html", post=None, **admin_context())

    @app.route("/admin/post/<int:post_id>/edit", methods=["GET", "POST"])
    def admin_post_edit(post_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        post = Post.query.get_or_404(post_id)
        if request.method == "POST":
            post.title = request.form["title"]
            post.body = request.form["body"]
            db.session.commit()
            flash("Post updated!")
            return redirect(url_for("admin_posts"))
        return render_template("admin_post_form.html", post=post, **admin_context())

    @app.route("/admin/post/<int:post_id>/delete", methods=["POST"])
    def admin_post_delete(post_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.")
        return redirect(url_for("admin_posts"))

    # ── Admin projects ────────────────────────────────────────────────────────

    @app.route("/admin/projects")
    def admin_projects():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        projects = Project.query.all()
        return render_template("admin_projects.html", projects=projects, **admin_context())

    @app.route("/admin/project/new", methods=["GET", "POST"])
    def admin_project_new():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        if request.method == "POST":
            image_filename = None
            if "image" in request.files:
                file = request.files["image"]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(uploads_path(filename))
                    image_filename = filename
            project = Project(
                title=request.form["title"],
                description=request.form["description"],
                url=request.form["url"],
                tech_stack=request.form["tech_stack"],
                image=image_filename
            )
            db.session.add(project)
            db.session.commit()
            flash("Project created!")
            return redirect(url_for("admin_projects"))
        return render_template("admin_project_form.html", project=None, **admin_context())

    @app.route("/admin/project/<int:project_id>/edit", methods=["GET", "POST"])
    def admin_project_edit(project_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        project = Project.query.get_or_404(project_id)
        if request.method == "POST":
            project.title = request.form["title"]
            project.description = request.form["description"]
            project.url = request.form["url"]
            project.tech_stack = request.form["tech_stack"]
            if "image" in request.files:
                file = request.files["image"]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(uploads_path(filename))
                    project.image = filename
            db.session.commit()
            flash("Project updated!")
            return redirect(url_for("admin_projects"))
        return render_template("admin_project_form.html", project=project, **admin_context())

    @app.route("/admin/project/<int:project_id>/delete", methods=["POST"])
    def admin_project_delete(project_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted.")
        return redirect(url_for("admin_projects"))

    # ── Admin comments ────────────────────────────────────────────────────────

    @app.route("/admin/comments")
    def admin_comments():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        pending = Comment.query.filter_by(approved=False).order_by(Comment.created_at.desc()).all()
        approved = Comment.query.filter_by(approved=True).order_by(Comment.created_at.desc()).all()
        return render_template("admin_comments.html", pending=pending, approved=approved, **admin_context())

    @app.route("/admin/comment/<int:comment_id>/approve", methods=["POST"])
    def comment_approve(comment_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        comment = Comment.query.get_or_404(comment_id)
        comment.approved = True
        db.session.commit()
        flash("Comment approved!")
        return redirect(url_for("admin_comments"))

    @app.route("/admin/comment/<int:comment_id>/delete", methods=["POST"])
    def comment_delete(comment_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.")
        return redirect(url_for("admin_comments"))

    # ── Admin messages ────────────────────────────────────────────────────────

    @app.route("/admin/messages")
    def admin_messages():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        messages = Message.query.order_by(Message.id.desc()).all()
        for msg in messages:
            msg.read = True
        db.session.commit()
        return render_template("admin_messages.html", messages=messages, **admin_context())

    @app.route("/admin/message/<int:msg_id>/delete", methods=["POST"])
    def message_delete(msg_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        msg = Message.query.get_or_404(msg_id)
        db.session.delete(msg)
        db.session.commit()
        flash("Message deleted.")
        return redirect(url_for("admin_messages"))

    # ── Admin settings ────────────────────────────────────────────────────────

    @app.route("/admin/settings", methods=["GET", "POST"])
    def admin_settings():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        if request.method == "POST":
            if "profile_photo" in request.files:
                file = request.files["profile_photo"]
                if file and allowed_file(file.filename):
                    file.save(uploads_path("profile.jpg"))
                    flash("Profile photo updated!")
            return redirect(url_for("admin_settings"))
        profile_exists = os.path.exists(uploads_path("profile.jpg"))
        return render_template("admin_settings.html", profile_exists=profile_exists, **admin_context())

    return app