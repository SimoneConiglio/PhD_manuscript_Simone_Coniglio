# Narrated thesis explainer

A ~12-minute narrated, 3Blue1Brown-style explainer of the thesis, made with the
[paper-to-explainer-video](https://github.com/SimoneConiglio/video-explaination-skill) skill
(Manim + Kokoro voice).

| file | contents |
|---|---|
| `script.md` | the reviewed script: scenes, narration, a source for every number |
| `video.py` | the 17 Manim scenes; toy examples (ring, springs, two bars) are computed here |
| `explainer.py` | the skill's library (`Narrated` scenes, spoken-text rewriting) |
| `precompute.py` | SIMP runs with/without filter, and the single-bar projection vs beam theory |
| `synth.py` | synthesizes every sentence once before parallel renders |
| `data/` | replayed runs: SIMP (`simp*.npz`), GGP framework short cantilever (`ggp_repo_GP.npz`), `bar_hc.npz` |
| `assets/` | figures from the manuscript, trimmed |
| `thesis_explainer_narrated.mp4` | the assembled video (English) |
| `thesis_explainer_narrated_fr.mp4` | the same video in French (`VIDEO_LANG=fr-fr VIDEO_VOICE=ff_siwis`) |
| `i18n.py`, `narration_fr.json` | French on-screen text and narration (every string must have a translation) |
| `kid.py` | the thesis told to a three-year-old, English or French (~1.5 min) |
| `thesis_for_kids_en.mp4`, `thesis_for_kids_fr.mp4` | the children's versions (voices `af_heart`, `ff_siwis`) |

## Rebuild
```bash
SKILL=/path/to/video-explaination-skill/paper-to-explainer-video
bash $SKILL/scripts/setup.sh .venv voice
.venv/bin/python precompute.py /path/to/GGP-Python        # optional: data/ is committed
export VIDEO_VOICE_DIR=$PWD/voice
.venv/bin/python synth.py                 # or: synth.py kid ; and VIDEO_LANG=fr-fr VIDEO_VOICE=ff_siwis for French
bash $SKILL/scripts/render.sh .venv video.py out qh     # or kid.py
bash $SKILL/scripts/assemble.sh out qh thesis_explainer_narrated.mp4
```
`data/ggp_repo_GP.npz` comes from `../video/run_ggp_repo.py` (generalized_geometry_projection
framework, `short_cantilever` preset).
