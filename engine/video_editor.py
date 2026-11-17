import json, pathlib, subprocess, shutil, wave, re, math, sys
from PIL import Image, ImageDraw, ImageFont

ROOT=pathlib.Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
story=json.loads((ROOT/"output/story.json").read_text(encoding="utf-8"))
out=ROOT/"output"
W,H=cfg["video"]["width"],cfg["video"]["height"]
FPS=cfg["video"]["fps"]

def run(cmd):
    subprocess.run(cmd, check=True)

def wav_duration(path):
    with wave.open(str(path),"rb") as w:
        return w.getnframes()/float(w.getframerate())

def make_srt(text, duration, path):
    # One readable caption block per scene, split into short lines.
    words=text.split()
    chunks=[]
    current=[]
    for word in words:
        current.append(word)
        if len(current)>=9:
            chunks.append(" ".join(current)); current=[]
    if current: chunks.append(" ".join(current))
    per=max(2.0, duration/max(1,len(chunks)))
    def stamp(s):
        ms=int(s*1000); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; sec=ms//1000; ms%=1000
        return f"{h:02}:{m:02}:{sec:02},{ms:03}"
    lines=[]
    for i,c in enumerate(chunks):
        start=i*per; end=min(duration,(i+1)*per)
        if end<=start: continue
        lines += [str(i+1), f"{stamp(start)} --> {stamp(end)}", c, ""]
    path.write_text("\n".join(lines),encoding="utf-8")

def main():
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg missing")
    (out/"segments").mkdir(exist_ok=True)
    segment_paths=[]
    total=0
    for item in story["scenes"]:
        i=item["number"]
        img=ROOT/f"output/scenes/scene_{i:02d}.png"
        wav=ROOT/f"output/audio/scene_{i:02d}.wav"
        if not img.exists() or not wav.exists():
            raise SystemExit(f"Missing scene image/audio for scene {i}")
        dur=wav_duration(wav)
        total+=dur
        srt=ROOT/f"output/segments/scene_{i:02d}.srt"
        make_srt(item["narration"],dur,srt)
        # scale/crop and gentle zoompan. Burn Hindi captions using available system fonts.
        seg=ROOT/f"output/segments/scene_{i:02d}.mp4"
        vf=(f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},zoompan=z='min(zoom+0.00035,1.06)':d=1:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
            f"subtitles={srt.as_posix()}:force_style='FontName=Noto Sans Devanagari,FontSize=25,"
            f"PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=2,"
            f"Shadow=1,Alignment=2,MarginV=35'")
        run(["ffmpeg","-y","-loop","1","-i",str(img),"-i",str(wav),
             "-vf",vf,"-t",f"{dur:.3f}","-r",str(FPS),"-c:v","libx264",
             "-preset","ultrafast","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",
             "-shortest",str(seg)])
        segment_paths.append(seg)
    concat=out/"segments/concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in segment_paths),encoding="utf-8")
    final=out/"hindi_kids_story.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(final)])
    # Simple thumbnail from first scene with title overlay.
    im=Image.open(ROOT/"output/scenes/scene_01.png").convert("RGB").resize((1280,720))
    draw=ImageDraw.Draw(im)
    font_path="/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
    try: font=ImageFont.truetype(font_path,64)
    except: font=ImageFont.load_default()
    title=story["title"]
    draw.rounded_rectangle((35,35,1245,160),radius=25,fill=(20,30,40))
    draw.text((65,55),title,font=font,fill=(255,240,100),stroke_width=2,stroke_fill=(30,20,10))
    im.save(out/"thumbnail.jpg",quality=90)
    minutes=total/60
    print(f"Rendered narration duration: {minutes:.2f} minutes")
    if minutes < cfg["video"]["min_minutes"] or minutes > cfg["video"]["max_minutes"]:
        print("WARNING: narration duration is outside configured target. Expand story paragraphs or adjust TTS speed.")
    print("Video:",final)

if __name__=="__main__":
    main()
