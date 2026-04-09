# StackedByBayo — Personal Portfolio & Blog

A full-stack personal portfolio and blog built with Python/Flask, deployed to a self-hosted Kubernetes cluster on Oracle Cloud via a complete GitOps CI/CD pipeline.

**Live:** [129.146.31.124](http://129.146.31.124)

---

## What This Is

This is not a template. Every line of infrastructure was built from scratch as part of a self-taught DevOps learning journey. The site itself is a Flask web app — but the real project is the pipeline that deploys it.

---

## Tech Stack

### Application
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask |
| Database | SQLite + SQLAlchemy |
| Frontend | Jinja2, Tailwind CSS |
| Rich Text | EasyMDE (Markdown editor) |
| WSGI | Gunicorn |

### Infrastructure
| Layer | Technology |
|-------|-----------|
| Cloud | Oracle Cloud (Always Free Tier) |
| Orchestration | Kubernetes (k3s) |
| Ingress | Traefik |
| Container Registry | Harbor (self-hosted) |
| Security Scanning | Trivy |
| GitOps | ArgoCD |
| CI/CD | Drone CI |
| Source Control | Gitea (self-hosted) |
| VPN | WireGuard |
| Monitoring | Prometheus + Grafana + Alertmanager |
| Alerts | Slack webhooks |

---

## CI/CD Pipeline

Every `git push` to the main branch triggers a fully automated pipeline:
```
git push
    │
    ▼
Gitea (self-hosted Git)
    │
    ▼
Drone CI (build triggered via webhook)
    │  • Clones repo
    │  • Builds Docker image
    │  • Pushes to Harbor registry
    │
    ▼
Trivy (security scan)
    │  • Scans image for vulnerabilities
    │  • Blocks on critical CVEs
    │
    ▼
Drone CI (updates k8s manifest)
    │  • Updates image tag in deployment.yaml
    │  • Commits back to Gitea
    │
    ▼
ArgoCD (detects manifest change)
    │  • Auto-syncs Kubernetes cluster
    │  • Rolling update — zero downtime
    │
    ▼
Kubernetes (k3s on Oracle Cloud)
    │  • 3 replicas running
    │  • Traefik handles ingress
    └─ Live 🚀
```

Zero manual steps after `git push`.

---

## Infrastructure Architecture
```
Local Machine (Ubuntu)
├── Gitea          — Self-hosted Git server
├── Drone CI       — CI/CD runner
├── Harbor         — Private Docker registry
└── WireGuard      — VPN tunnel to Oracle Cloud

Oracle Cloud Server (Always Free)
├── k3s            — Lightweight Kubernetes
├── Traefik        — Ingress controller
├── ArgoCD         — GitOps operator
├── Prometheus     — Metrics collection
├── Grafana        — Dashboards
└── Alertmanager   — Slack alerts
```

---

## Project Structure
```
my-portfolio/
├── app/
│   ├── __init__.py        # App factory + all routes
│   ├── models.py          # SQLAlchemy models
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── blog.html
│   │   ├── post.html
│   │   ├── projects.html
│   │   ├── about.html
│   │   └── contact.html
│   └── static/
│       └── uploads/       # Project images, profile photo
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml    # 3 replicas, image updated by CI
│   ├── service.yaml       # LoadBalancer on port 80
│   └── ingress.yaml       # Traefik ingress
├── Dockerfile
├── .drone.yml             # CI/CD pipeline definition
├── update-manifest.sh     # Updates k8s image tag after build
├── requirements.txt
├── run.py
└── README.md
```

---

## Running Locally
```bash
# Clone the repo
git clone https://github.com/BayoJohn/my-portfolio.git
cd my-portfolio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

App runs at `http://localhost:5000`

---

## Features

- **Blog** — Write and publish posts via admin panel with Markdown support
- **Projects** — Showcase projects with images, descriptions and tech tags
- **Contact** — Contact form with visitor logging
- **Analytics** — Visitor IP tracking (X-Forwarded-For aware behind Traefik)
- **Admin** — Password-protected admin dashboard

---

## Testing

The application includes a `pytest` suite for automated testing.

**Important Note on Database Tests**: 
The test database is set up using SQLAlchemy's `db.create_all()` which creates a fresh, perfectly matching in-memory database schema based on the current state of `models.py`. 
Because of this, the test suite **cannot detect schema mismatch errors** against your stateful production database. For example, if you add a new column to a model but forget to run a database migration on the live server, your tests will still pass because they run against a freshly built schema, not the outdated production schema. 

To prevent these live mismatch errors, the application is configured to automatically run `migrate()` from `migrate_db.py` whenever the entrypoint (`run.py`) spins up.

---

## Monitoring

The cluster is monitored with the kube-prometheus-stack:

- **Grafana** — Dashboards for pod health, CPU, memory
- **Prometheus** — Scrapes metrics from all cluster components
- **Alertmanager** — Sends Slack alerts for:
  - Site downtime
  - Pod crash looping
  - High CPU/memory usage
  - Pipeline failures

---

## Blog Posts

All infrastructure decisions are documented publicly on the blog:

1. How I Automated My Way Out of a Broken CI/CD Pipeline
2. How I Deployed My Portfolio to Kubernetes at Midnight
3. How I Added Slack Alerting to My Kubernetes Homelab
4. How I Completed My GitOps Pipeline with ArgoCD
5. Why My Analytics Were Lying to Me (And How Kubernetes Was to Blame)
6. How I Deployed a Second Site to My Kubernetes Cluster at 5am

---

## Author

**Omobayonle Ogundele (Bayo)**
DevOps Engineer — Lagos, Nigeria 🇳🇬

- GitHub: [@BayoJohn](https://github.com/BayoJohn)
- LinkedIn: [bayo123](https://www.linkedin.com/in/bayo123)
- Twitter: [@BayoJohnMoses](https://twitter.com/BayoJohnMoses)
- Email: ogundelebayo8@gmail.com

---

*Built from scratch. Deployed to production. Documented publicly.*
