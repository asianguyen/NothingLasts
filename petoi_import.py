# -*- coding: UTF-8 -*-
import sys
from pathlib import Path

PETOI_SUBPATH = 'extensions/petoi-robot-thirdex/python/libraries'

SEARCH_PATHS = [
    Path(__file__).parent,                                         # local PetoiRobot/ in this repo
    Path.home() / 'Library/DFScratch' / PETOI_SUBPATH,            # macOS MindPlus
    Path.home() / 'AppData/Roaming/DFScratch' / PETOI_SUBPATH,    # Windows MindPlus
    Path.home() / 'AppData/Local/DFScratch' / PETOI_SUBPATH,
    Path.home() / 'Downloads/PetoiRobot/..',
    Path.home() / 'Desktop/PetoiRobot/..',
]

try:
    import PetoiRobot  
except ModuleNotFoundError:
    sys.modules.pop('PetoiRobot', None) 
    for path in SEARCH_PATHS:
        if path.exists():
            sys.path.insert(0, str(path))
            try:
                import PetoiRobot
                break
            except ModuleNotFoundError:
                sys.modules.pop('PetoiRobot', None)
                sys.path.pop(0)
    else:
        raise ImportError(
            "PetoiRobot not found. Install MindPlus (https://mindplus.cc) "
            "or place the PetoiRobot folder on your Python path."
        )

from PetoiRobot import *
