#!/usr/bin/env python3
"""
Year Review Bot - Main runner
Just run: python bot.py
"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("""
╔════════════════════════════════════════════════╗
║   Year Review Bot + Mini App                  ║
╚════════════════════════════════════════════════╝

Starting...
""")

try:
    subprocess.run([sys.executable, 'bot.py'])
except KeyboardInterrupt:
    print("\n\nStopped")
    sys.exit(0)
        sys.exit(0)
