import os, pathlib, json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

ROOT=pathlib.Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
secrets=["YOUTUBE_CLIENT_ID","YOUTUBE_CLIENT_SECRET","YOUTUBE_REFRESH_TOKEN"]
if not all(os.environ.get(k) for k in secrets):
    print("YouTube secrets missing; skipping upload. MP4 will be available as workflow artifact.")
    sys.exit(0)

creds=Credentials(
    token=None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)
youtube=build("youtube","v3",credentials=creds)
title=(ROOT/"output/title.txt").read_text(encoding="utf-8").strip()
description=(ROOT/"output/description.txt").read_text(encoding="utf-8")
tags=cfg["youtube"].get("default_tags",[])
body={
 "snippet":{
   "title":title[:100],
   "description":description[:5000],
   "tags":tags,
   "categoryId":cfg["youtube"].get("category_id","1"),
   "defaultLanguage":"hi",
   "defaultAudioLanguage":"hi"
 },
 "status":{
   "privacyStatus":cfg["youtube"].get("privacy_status","private"),
   "selfDeclaredMadeForKids":bool(cfg["youtube"].get("made_for_kids",True))
 }
}
media=MediaFileUpload(str(ROOT/"output/hindi_kids_story.mp4"),mimetype="video/mp4",chunksize=8*1024*1024,resumable=True)
try:
    req=youtube.videos().insert(part="snippet,status",body=body,media_body=media)
    response=None
    while response is None:
        status,response=req.next_chunk()
        if status: print(f"Upload progress: {int(status.progress()*100)}%")
    print("Uploaded video ID:",response.get("id"))
    print("Privacy:",body["status"]["privacyStatus"])
except HttpError as e:
    print("YouTube API upload failed:",e)
    raise
