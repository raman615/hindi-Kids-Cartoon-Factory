# Hindi Kids Cartoon Factory

A free-first GitHub Actions pipeline that creates Hindi children's story videos using:
- Story templates and scene narration (offline; no paid LLM required)
- Blender procedural 3D scene renders
- eSpeak NG Hindi text-to-speech
- FFmpeg scene motion, subtitles, audio and final MP4 assembly
- YouTube Data API upload (private by default)

## Important limitations

This starter project creates a narrated 3D story video using rendered 3D scenes with slow camera motion (Ken Burns-style zoom/pan). It does **not** yet create full character acting, lip-sync, or generative AI video. Hindi eSpeak NG voice is synthetic/robotic; check its availability in the runner. A 5–8 minute duration depends on narration speed and voice output. Rendering may exceed GitHub Actions free minutes, especially for long/high-resolution renders.

GitHub Actions is scheduled cloud execution, not an always-on server. It runs at 09:00 Asia/Kolkata (03:30 UTC) and stops after the job.

## 1. Create your GitHub repository

Create a repository named `Hindi-Kids-Cartoon-Factory`. For the simplest free scheduled runner usage, a public repository can use standard GitHub-hosted runners without consuming the private-repo included minutes. **Public repositories expose source code**, so never commit credentials, tokens, or private data. If you prefer private, check your account's Actions minutes quota.

Upload the complete project files from this ZIP to the repository root.

## 2. Configure YouTube API

1. Open Google Cloud Console: https://console.cloud.google.com/
2. Create a project and enable **YouTube Data API v3**.
3. Configure the OAuth consent screen. Add your Google account as a test user if the app is in Testing.
4. Create an OAuth Client ID of type **Desktop app**.
5. Generate a refresh token using the instructions below. The OAuth scope must be `https://www.googleapis.com/auth/youtube.upload`.
6. In GitHub repository: Settings -> Secrets and variables -> Actions -> New repository secret. Add:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

Do not put credentials in `config.json` or commit them to Git.

### Generate a refresh token locally

On a computer with Python:
```bash
python -m pip install google-auth-oauthlib
```
Save your downloaded OAuth desktop client JSON as `client_secret.json` in the project folder, then run:
```bash
python engine/get_youtube_token.py
```
Copy the printed refresh token into GitHub secret `YOUTUBE_REFRESH_TOKEN`. Delete `client_secret.json` afterwards. Do not upload it to GitHub.

## 3. Run a test

In GitHub: Actions -> Daily Hindi Kids Cartoon -> Run workflow.
The first run uses a story, renders scenes, builds an MP4, and uploads it as **Private**.
The generated MP4, script and thumbnail are also attached as a workflow artifact (if upload succeeds).

## 4. Schedule

The workflow runs daily at 03:30 UTC = 09:00 India time. GitHub scheduled runs can be delayed during busy periods.

## 5. Customize

- Add stories in `stories/story_bank.json`.
- Edit `config.json` to change video size, frame rate, privacy and duration target.
- The default upload privacy is `private`. After checking quality, change it to `public` in `config.json` if you want automatic public publishing. Made-for-kids is set to true.
- You can disable automatic publishing by removing the YouTube secrets; the workflow will still build the video and save an artifact.

## Safety and kids-content checklist

Review each video before publishing. Avoid frightening scenes, unsafe imitation, dangerous challenges, misleading educational claims, copyrighted characters, copyrighted music, and personal information. Use only original assets/music you have rights to use. Correctly mark child-directed content as Made for Kids where applicable.
