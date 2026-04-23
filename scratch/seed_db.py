from app import create_app
from app.models import db, Post, Project
from datetime import datetime

app = create_app()
with app.app_context():
    # Only seed if empty
    if Post.query.count() == 0:
        p1 = Post(
            title="How I Deployed a Second Site to My Kubernetes Cluster at 5am (And Everything That Went Wrong)",
            body="""It was 5am. The house was quiet, except for the hum of my server. I decided it was time. Time to deploy the second site to my cluster.

I had been putting it off for weeks. "It's just another ingress rule," I told myself. "Just another helm chart."

I was wrong.

It started with a simple YAML error. A missing quote. Then, a namespace conflict. By 3am, I was deep in the Traefik logs, wondering why my CORS policy was suddenly blocking everything.

This was a Django project I had built last year. It was supposed to be simple. But Kubernetes has a way of making simple things complex when you're tired.

Anyway, after three hours of debugging, I finally saw it. The green light. The site was live.

Key takeaways:
1. Always check your indentation.
2. Don't deploy at 5am.
3. GitOps saves lives (or at least sanity).
""",
            created_at=datetime.utcnow()
        )
        db.session.add(p1)
        
        # Add a few more for the sidebar
        p2 = Post(title="How I Automated My Way Out of a Broken CI/CD Pipeline", body="...", created_at=datetime.utcnow())
        p3 = Post(title="How I Added Slack Alerting to My Kubernetes Homelab", body="...", created_at=datetime.utcnow())
        db.session.add(p2)
        db.session.add(p3)
        
        db.session.commit()
        print("✅ Database seeded with sample posts.")
    else:
        print("✓ Database already has posts. Skipping seed.")
