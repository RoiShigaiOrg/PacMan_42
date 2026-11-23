from Game.PacMan import PacMan
from pathlib import Path
import sys

try:
    PacMan(Path(".config.json")).run()
except (Exception, KeyboardInterrupt) as e:
    print(e)
    sys.exit()
