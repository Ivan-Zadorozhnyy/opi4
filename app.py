from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random
import uuid

app = Flask(__name__)

users_data = {"total": 20, "data": []}

for i in range(20):
    user = {
        "userId": str(uuid.uuid4()),
        "nickname": f"User_{i}",
        "firstName": f"FirstName_{i}",
        "lastName": f"LastName_{i}",
        "registrationDate": (
            datetime.now() - timedelta(days=random.randint(0, 365))
        ).isoformat(),
        "lastSeenDate": datetime.now().isoformat()
        if random.choice([True, False])
        else None,
        "isOnline": random.choice([True, False]),
        "onlineTimePerWeek": random.randint(1000, 100000),
    }
    users_data["data"].append(user)


@app.route("/api/stats/user/total", methods=["GET"])
def get_total_time_online():
    user_id = request.args.get("userId")
    user1 = next((u for u in users_data["data"] if u["userId"] == user_id), None)
    if not user1:
        return jsonify({"error": "User not found"}), 404

    days_since_registration = (
        datetime.now() - datetime.fromisoformat(user1["registrationDate"])
    ).days
    total_time = user1["onlineTimePerWeek"] * days_since_registration / 7

    return jsonify({"totalTime": int(total_time)})


@app.route("/api/stats/user/average", methods=["GET"])
def get_average_time_online():
    user_id = request.args.get("userId")
    user2 = next((u for u in users_data["data"] if u["userId"] == user_id), None)

    if not user2:
        return jsonify({"error": "User not found"}), 404

    days_since_registration = (
        datetime.now() - datetime.fromisoformat(user2["registrationDate"])
    ).days
    total_time = user2["onlineTimePerWeek"] * days_since_registration / 7

    daily_average = total_time / days_since_registration
    weekly_average = daily_average * 7

    return jsonify(
        {"dailyAverage": int(daily_average), "weeklyAverage": int(weekly_average)}
    )


@app.route("/api/user/forget", methods=["POST"])
def forget_user():
    user_id = request.args.get("userId")
    user3 = next((u for u in users_data["data"] if u["userId"] == user_id), None)

    if not user3:
        return jsonify({"error": "User not found"}), 404

    users_data["data"].remove(user3)

    return jsonify({"userId": user_id})


@app.route("/api/users/ids", methods=["GET"])
def get_user_ids():
    user_ids = [user4["userId"] for user4 in users_data["data"]]
    return jsonify(user_ids)


if __name__ == "__main__":
    app.run(debug=True)
