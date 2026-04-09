from app import create_app
from migrate_db import migrate

app = create_app()

if __name__ == "__main__":
    migrate()
    app.run(host="0.0.0.0", port=5000, debug=True)
