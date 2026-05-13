import subprocess

SECRETS_TO_LOAD = {
    "DISCORD_TOKEN",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
}

secrets = {}

with open(".env") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if key in SECRETS_TO_LOAD:
            secrets[key] = value

for key, value in secrets.items():
    result = subprocess.run(
        ["gcloud.cmd", "secrets", "create", key, "--data-file=-"],
        input=value.encode(),
        capture_output=True,
    )
    if result.returncode == 0:
        print(f"✓ Created: {key}")
    else:
        print(f"✗ Failed: {key} — {result.stderr.decode().strip()}")
