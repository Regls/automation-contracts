import asyncio
import sys
from app.listeners.supabase_listener import realtime_listener

if __name__ == "__main__":
    try:
        asyncio.run(realtime_listener())
    except KeyboardInterrupt:
        print("\nApplication interrupted by developer.")
        sys.exit(0)