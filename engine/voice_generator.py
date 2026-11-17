import json, pathlib, subprocess, shutil, sys, wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
story = json.loads((ROOT/"output/story.json").read_text(encoding="utf-8"))
cfg = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
if not shutil.which("espeak-ng"):
    raise SystemExit("espeak-ng is not installed.")
# Verify that Hindi voice exists; do not silently create English narration.
voices = subprocess.run(["espeak-ng", "--voices=hi"], capture_output=True, text=True)
if "hi" not in voices.stdout.lower():
    raise SystemExit("Hindi eSpeak NG voice not found on this runner. Check espeak-ng-data / voice availability.")
(ROOT/"output/audio").mkdir(parents=True, exist_ok=True)
(ROOT/"output/scripts").mkdir(parents=True, exist_ok=True)
for scene in story["scenes"]:
    i = scene["number"]
    text = scene["narration"]
    (ROOT/f"output/scripts/scene_{i:02d}.txt").write_text(text, encoding="utf-8")
    wav = ROOT/f"output/audio/scene_{i:02d}.wav"
    cmd = [
        "espeak-ng", "-v", cfg["voice"]["voice"],
        "-s", str(cfg["voice"]["words_per_minute"]),
        "-p", str(cfg["voice"]["pitch"]),
        "-a", str(cfg["voice"]["amplitude"]),
        "-w", str(wav), text
    ]
    subprocess.run(cmd, check=True)
print("Hindi narration WAV files created.")
