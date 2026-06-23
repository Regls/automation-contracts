import asyncio
import sys
from app.listeners.supabase_listener import realtime_listener

async def main():
    print("🚀 [APP] Starting contract automation...")

    await realtime_listener()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 [APP]Application interrupted by developer.")
        sys.exit(0)