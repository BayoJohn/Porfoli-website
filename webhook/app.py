import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ARGOCD_SERVER = os.environ.get("ARGOCD_SERVER", "argocd-server.argocd.svc.cluster.local")
ARGOCD_TOKEN = os.environ.get("ARGOCD_TOKEN", "")
ARGOCD_APP = os.environ.get("ARGOCD_APP", "portfolio")


def get_argocd_headers():
    return {
        "Authorization": f"Bearer {ARGOCD_TOKEN}",
        "Content-Type": "application/json"
    }


def trigger_rollback():
    url = f"https://{ARGOCD_SERVER}/api/v1/applications/{ARGOCD_APP}/rollback"
    try:
        history_url = f"https://{ARGOCD_SERVER}/api/v1/applications/{ARGOCD_APP}"
        resp = requests.get(history_url, headers=get_argocd_headers(), verify=False, timeout=10)
        app_data = resp.json()
        history = app_data.get("status", {}).get("history", [])
        if len(history) < 2:
            print("Not enough history to rollback")
            return False
        last_good_id = history[-2]["id"]
        print(f"Rolling back to deployment ID: {last_good_id}")
        rollback_resp = requests.post(
            url,
            headers=get_argocd_headers(),
            json={"id": last_good_id, "dryRun": False, "prune": False},
            verify=False,
            timeout=10
        )
        print(f"Rollback response: {rollback_resp.status_code} {rollback_resp.text}")
        return rollback_resp.status_code == 200
    except Exception as e:
        print(f"Rollback error: {e}")
        return False


@app.route("/healthz")
def health():
    return jsonify({"status": "ok"})


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    print(f"Received alert: {json.dumps(data, indent=2)}")
    alerts = data.get("alerts", [])
    firing_alerts = [a for a in alerts if a.get("status") == "firing"]
    rollback_triggers = ["KubePodCrashLooping", "KubeContainerWaiting"]

    for alert in firing_alerts:
        alert_name = alert.get("labels", {}).get("alertname", "")
        namespace = alert.get("labels", {}).get("namespace", "")
        if alert_name in rollback_triggers and namespace == "portfolio":
            print(f"Triggering rollback for alert: {alert_name} in {namespace}")
            success = trigger_rollback()
            return jsonify({
                "action": "rollback",
                "alert": alert_name,
                "success": success
            })

    return jsonify({"action": "none", "reason": "no matching alerts"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
