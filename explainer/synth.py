"""Synthesize every narration sentence of video.py once, before parallel renders.

    VIDEO_VOICE_DIR=/path/to/voice python synth.py [module]     # module: video (default) or kid

Runs each scene's construct() with animations disabled, records what narrate() would
say, prints it as it will be spoken, and fills the voice cache.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib

import explainer
from manim import Scene

video = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "video")

said = []
explainer.Narrated.narrate = lambda self, m: said.append(getattr(video, 'narr', lambda x: x)(m)) or 0.0
Scene.play = lambda self, *a, **k: None
Scene.wait = lambda self, *a, **k: None
for name in video.SCENES:
    start = len(said)
    getattr(video, name)().construct()
    print(f"## {name}: {len(said) - start} sentences")
    for m in said[start:]:
        print("  >", explainer.spoken(m))
if os.environ.get("VIDEO_VOICE_DIR"):
    total = 0.0
    for m in said:
        total += explainer.speech(explainer.spoken(m))[1]
    print(f"{len(said)} sentences, {total / 60:.1f} min of narration")
