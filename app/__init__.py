from flask import Flask, render_template, request, flash, redirect, url_for, session
from app.models import db, Project, Post

def create_app():
    app = Flask(__name__)
    app.secret_key = "change-this-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
    app.config["ADMIN_PASSWORD"] = "changeme123"

    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/projects")
    def projects():
        all_projects = Project.query.all()
        return render_template("projects.html", projects=all_projects)

    @app.route("/blog")
    def blog():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("blog.html", posts=posts)

    @app.route("/blog/<int:post_id>")
    def post(post_id):
        post = Post.query.get_or_404(post_id)
        return render_template("post.html", post=post)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            message = request.form["message"]
            print(f"Message from {name} ({email}): {message}")
            flash("Thanks! Your message was sent.")
            return redirect(url_for("contact"))
        return render_template("contact.html")

    @app.route("/admin")
    def admin():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        posts = Post.query.order_by(Post.created_at.desc()).all()
        projects = Project.query.all()
        return render_template("admin.html", posts=posts, projects=projects)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            if request.form["password"] == app.config["ADMIN_PASSWORD"]:
                session["admin"] = True
                return redirect(url_for("admin"))
            flash("Wrong password.")
        return render_template("admin_login.html")

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin", None)
        return redirect(url_for("home"))

    @app.route("/admin/post/new", methods=["GET", "POST"])
    def admin_post_new():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        if request.method == "POST":
            post = Post(title=request.form["title"], body=request.form["body"])
            db.session.add(post)
            db.session.commit()
            flash("Post created!")
            return redirect(url_for("admin"))
        return render_template("admin_post_form.html", post=None)

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
            return redirect(url_for("admin"))
        return render_template("admin_post_form.html", post=post)

    @app.route("/admin/post/<int:post_id>/delete", methods=["POST"])
    def admin_post_delete(post_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.")
        return redirect(url_for("admin"))

    return app