#!/usr/bin/env bash
# Render the thesis explainer video with Manim Community.
#   ./render.sh [quality]  quality: l (480p15) | m (720p30) | h (1080p60, default)
#   GGP_REPO=/path/to/generalized_geometry_projection GGP_PYTHON=<python of its FEniCS env> ./render.sh
#   recomputes the Lagrangian (GGP) run if data/ggp_repo_GP.npz is missing
set -euo pipefail
cd "$(dirname "$0")"
Q="${1:-h}"
PY="${PYTHON:-python}"
MANIM="${MANIM:-manim}"
[ -f data/simp.npz ] || "$PY" topopt_data.py
if [ ! -f data/ggp_repo_GP.npz ]; then
  : "${GGP_REPO:?set GGP_REPO to a clone of https://github.com/SimoneConiglio/generalized_geometry_projection}"
  ${GGP_PYTHON:-python} run_ggp_repo.py "$GGP_REPO"   # e.g. GGP_PYTHON="micromamba run -n ggp python"
fi
SCENES="S1_Intro S2_TipClearance S3_FEM S4_SIMP S5_Stress S6_GGP S7_Application S8_Conclusion"
for s in $SCENES; do "$MANIM" -q"$Q" scenes.py "$s"; done   # sequential: Tex cache is shared
case "$Q" in l) RES=480p15;; m) RES=720p30;; *) RES=1080p60;; esac
DIR="media/videos/scenes/$RES/"
: > list.txt
for s in $SCENES; do echo "file '${DIR}${s}.mp4'" >> list.txt; done
ffmpeg -y -v error -f concat -safe 0 -i list.txt -c copy thesis_explainer.mp4
rm list.txt
echo "Done -> video/thesis_explainer.mp4"
