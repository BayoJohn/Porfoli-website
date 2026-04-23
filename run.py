from app import create_app
from migrate_db import migrate

app = create_app()

if __name__ == "__main__":
    import os
    migrate()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
