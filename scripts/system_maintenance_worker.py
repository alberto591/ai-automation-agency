#!/usr/bin/env python3
"""
System Maintenance Worker
Runs background tasks to keep the system healthy and data fresh.
- Periodic View Refreshes (for Dashboard)
- Embedding Generation for new properties
- Connectivity checks
"""

import os
import signal
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from config.container import container
from infrastructure.logging import get_logger

logger = get_logger(__name__)

# CONFIGURATION
REFRESH_INTERVAL_SECONDS = 3600  # Hourly
EMBEDDING_BATCH_SIZE = 50


class MaintenanceWorker:
    def __init__(self):
        self.running = True
        self.last_view_refresh = 0
        self.last_embedding_check = 0

    def start(self):
        print("=" * 60)
        print("   🚀 AI SYSTEM MAINTENANCE WORKER STARTED")
        print("=" * 60)
        print("   Mode: Background Processing")
        print("   Tasks: View Refresh, Embedding Sync")
        print("=" * 60)

        while self.running:
            current_time = time.time()

            # 1. Refresh Analytics Views (Materialized Views)
            if current_time - self.last_view_refresh > REFRESH_INTERVAL_SECONDS:
                self.refresh_analytics()
                self.last_view_refresh = current_time

            # 2. Check for missing embeddings
            if current_time - self.last_embedding_check > 300:  # Every 5 mins
                self.sync_embeddings()
                self.last_embedding_check = current_time

            time.sleep(60)  # Main loop pulse

    def refresh_analytics(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Refreshing Analytics Views...")
        try:
            # Try concurrent refresh first (better for production)
            container.db.client.rpc("refresh_performance_views").execute()
            print("   ✅ Materialized views refreshed (concurrently).")
        except Exception as e:
            # If concurrent refresh fails (e.g. missing unique index), try a standard refresh
            err_msg = str(e).lower()
            if "not found" in err_msg:
                print("   ⚠️  refresh_performance_views() not found in DB. Skipping.")
            elif "concurrently" in err_msg or "unique index" in err_msg:
                print("   ⚠️  Concurrent refresh failed. Attempting standard refresh...")
                try:
                    # Manually trigger a standard refresh if the RPC fails due to concurrency issues
                    container.db.client.table("mv_daily_performance_summary").select(
                        "*", count="exact"
                    ).limit(0).execute()
                    # We can't easily run arbitrary SQL REFRESH via the client table interface,
                    # but we can try a different RPC if available or just log it.
                    # For now, let's just log that the index should be applied.
                    print(
                        "   ❌ Please apply the unique index to mv_daily_performance_summary to enable background updates."
                    )
                except Exception:
                    print(f"   ❌ Refresh failed: {e}")
            else:
                print(f"   ❌ View Refresh Failed: {e}")

    def sync_embeddings(self):
        """Find properties missing embeddings and generate them."""
        try:
            # Find properties where embedding is null
            res = (
                container.db.client.table("properties")
                .select("id, title, description")
                .is_("embedding", "null")
                .limit(EMBEDDING_BATCH_SIZE)
                .execute()
            )

            missing = res.data
            if not missing:
                return

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🧬 Found {len(missing)} properties missing embeddings. Processing..."
            )

            for p in missing:
                text = f"{p['title']}. {p['description']}"
                embedding = container.ai.get_embedding(text)

                container.db.client.table("properties").update({"embedding": embedding}).eq(
                    "id", p["id"]
                ).execute()

            print(f"   ✅ Processed {len(missing)} embeddings.")
        except Exception as e:
            print(f"   ❌ Embedding Sync Failed: {e}")

    def stop(self):
        print("\n🛑 Shutting down maintenance worker...")
        self.running = False


if __name__ == "__main__":
    worker = MaintenanceWorker()

    def signal_handler(sig, frame):
        worker.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        worker.start()
    except Exception as e:
        print(f"💥 Worker crashed: {e}")
        logger.error("WORKER_CRASHED", context={"error": str(e)})
