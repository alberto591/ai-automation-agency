import os
import sys
import time

import requests

GITHUB_REPO = "alberto591/ai-automation-agency"
DEFAULT_BRANCH = "master"


def check_status(interval=15, timeout=300):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GITHUB_TOKEN environment variable is required.")
        return False

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}

    print(f"🔍 Monitoring CI/CD status for {GITHUB_REPO} ({DEFAULT_BRANCH})...")

    start_time = time.time()

    while True:
        try:
            # 1. Get the latest commit SHA for the branch
            url_branch = f"https://api.github.com/repos/{GITHUB_REPO}/branches/{DEFAULT_BRANCH}"
            r_branch = requests.get(url_branch, headers=headers)
            r_branch.raise_for_status()
            latest_sha = r_branch.json()["commit"]["sha"]

            # 2. Get Check Runs for this SHA
            url_checks = (
                f"https://api.github.com/repos/{GITHUB_REPO}/commits/{latest_sha}/check-runs"
            )
            r_checks = requests.get(url_checks, headers=headers)
            r_checks.raise_for_status()
            data = r_checks.json()

            check_runs = data.get("check_runs", [])
            total_count = data.get("total_count", 0)

            print(f"\n--- Status for commit {latest_sha[:7]} at {time.strftime('%H:%M:%S')} ---")

            if total_count == 0:
                print("⏳ No checks reported yet...")
            else:
                pending = False
                failed = False

                for run in check_runs:
                    name = run["name"]
                    status = run["status"]  # queued, in_progress, completed
                    conclusion = run[
                        "conclusion"
                    ]  # success, failure, neutral, cancelled, skipped, ...

                    # Formatting output
                    icon = "⚪"
                    if status == "queued":
                        icon = "zzz"
                    elif status == "in_progress":
                        icon = "🔄"
                    elif conclusion == "success":
                        icon = "✅"
                    elif conclusion == "failure":
                        icon = "❌"
                    elif conclusion == "skipped":
                        icon = "⏭️"

                    print(f"{icon} {name}: {status}" + (f" ({conclusion})" if conclusion else ""))

                    if status in ["queued", "in_progress"]:
                        pending = True
                    elif conclusion == "failure":
                        failed = True

                if failed:
                    print("\n❌ Deployment Failed! One or more checks failed.")
                    return False

                if not pending and not failed:
                    print("\n✅ All Checks Passed! Deployment Successful.")
                    return True

        except Exception as e:
            print(f"⚠️ Error querying GitHub API: {str(e)}")

        if time.time() - start_time > timeout:
            print("\n⚠️ Monitoring timed out.")
            return False

        time.sleep(interval)


if __name__ == "__main__":
    success = check_status()
    if not success:
        sys.exit(1)
