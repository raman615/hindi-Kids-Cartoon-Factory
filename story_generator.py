import json, random, datetime, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
bank = json.loads((ROOT/"stories/story_bank.json").read_text(encoding="utf-8"))
today = datetime.date.today()
stories = bank["stories"]
# Rotate deterministically by date; no external AI API is needed.
story = stories[today.toordinal() % len(stories)]
scenes = story["scenes"]
if len(scenes) != 8:
    raise SystemExit("Each story must contain exactly 8 scene paragraphs.")
out = {
    "date": today.isoformat(),
    "id": story["id"],
    "title": story["title"],
    "lesson": story["lesson"],
    "characters": story["characters"],
    "scenes": [{"number": i+1, "narration": p[0]} for i,p in enumerate(scenes)]
}
(ROOT/"output").mkdir(exist_ok=True)
(ROOT/"output/story.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT/"output/title.txt").write_text(story["title"], encoding="utf-8")
(ROOT/"output/description.txt").write_text(
    f'{story["title"]}\n\nआज की हिंदी बच्चों की कहानी।\n\nसीख: {story["lesson"]}\n\n#HindiKidsStory #HindiCartoon #MoralStory',
    encoding="utf-8")
print("Selected story:", story["title"])
print("Narration words:", sum(len(x["narration"].split()) for x in out["scenes"]))
