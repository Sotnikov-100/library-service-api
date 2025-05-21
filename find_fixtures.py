import json

FIXTURE_PATH = "fixtures/fixtures_users.json"
DEFAULT_DATE_JOINED = "2024-01-01T12:00:00Z"

with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for obj in data:
    if obj["model"] == "users.user":
        fields = obj["fields"]
        if "date_joined" not in fields or fields["date_joined"] is None:
            fields["date_joined"] = DEFAULT_DATE_JOINED

with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ 'date_joined' додано до всіх користувачів.")
