from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
print("\nREFRESH TOKEN (copy to GitHub secret YOUTUBE_REFRESH_TOKEN):\n")
print(creds.refresh_token)
