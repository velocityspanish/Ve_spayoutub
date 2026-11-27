"""
YouTube Shorts uploader (refresh token from GitHub Secrets).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime

load_dotenv()


def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()

    print(f"[youtube] Client ID: {'set' if client_id else 'MISSING'}")
    print(f"[youtube] Client Secret: {'set' if client_secret else 'MISSING'}")
    print(f"[youtube] Refresh Token: {'set' if refresh_token else 'MISSING'}")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing credentials! Set these environment variables:\n"
            "  - YOUTUBE_CLIENT_ID\n"
            "  - YOUTUBE_CLIENT_SECRET\n"
            "  - YOUTUBE_REFRESH_TOKEN"
        )

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    try:
        creds.refresh(Request())
    except Exception as e:
        if "invalid_grant" in str(e).lower():
            print("\n[youtube] AUTH ERROR: Refresh token has EXPIRED or been REVOKED.")
            print("SOLUTION: Generate a NEW refresh token.")
            print("   1. Go to Google Cloud Console.")
            print("   2. Ensure OAuth Consent Screen is in 'Production' or add yourself as a test user.")
            print("   3. Run a local script to get a new refresh token.")
        raise

    return build('youtube', 'v3', credentials=creds)


def generate_video_metadata(category: str, num_phrases: int, phrases: list = None):
    import config

    lang = config.LANGUAGE["name"]
    label = "Mandarin" if lang == "Chinese" else lang
    brand = config.BRAND
    handle = config.HANDLE

    title_variants = [
        f"{num_phrases} {label} Phrases for {category} (Sound Natural)",
        f"Can You Say These {num_phrases} {label} Phrases?",
        f"{num_phrases} {label} Phrases Locals Actually Use",
    ]
    title = title_variants[(len(category) + num_phrases) % len(title_variants)]

    description_lines = [
        f"Can you say these {num_phrases} {label} phrases?",
        "",
        f"Today's topic: {category}",
        "",
        f"Listen, repeat, and use one today. {brand}",
        "",
    ]

    if phrases:
        for i, phrase in enumerate(phrases[:5], 1):
            description_lines.append(f"{i}. {phrase['english']}")
            description_lines.append(f"   {phrase.get('native', '')}")
            transliteration = phrase.get('transliteration') or ''
            if transliteration:
                description_lines.append(f"   [{transliteration}]")
            description_lines.append("")

    description_lines.extend([
        "Which phrase are you trying first? Comment below.",
        f"Follow {handle} for daily {label} lessons.",
        "",
        " ".join(config.HASHTAGS[:8]),
        f"#Shorts #Learn{label.replace(' ', '')} #{category.replace(' ', '')}",
    ])
    description = "\n".join(description_lines)

    extra = {
        "Chinese": ["mandarin", "hsk", "chinese phrases", "learn mandarin", "mandarin chinese"],
        "Japanese": ["japanese phrases", "jlpt", "learn japanese", "japanese shorts"],
        "Korean": ["korean phrases", "topik", "learn korean", "korean shorts"],
        "German": ["german phrases", "learn german", "german shorts", "deutsch lernen"],
        "Russian": ["russian phrases", "learn russian", "russian shorts"],
        "Spanish": ["spanish phrases", "learn spanish", "spanish shorts"],
    }.get(lang, [])

    tags = [
        f"learn {label.lower()}",
        f"{label.lower()} lessons",
        f"{label.lower()} for beginners",
        f"{label.lower()} phrases",
        f"{label.lower()} shorts",
        "language learning",
        "language shorts",
        f"speak {label.lower()}",
        category.lower(),
        "education",
        f"daily {label.lower()}",
        brand.lower(),
    ] + extra
    tags = list(dict.fromkeys(tags))
    return title, description, tags


def upload_to_youtube(video_path, title, description, tags=None, category_id='27'):
    if tags is None:
        tags = ['education', 'language learning']
    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }

    if '#Shorts' not in body['snippet']['description']:
        body['snippet']['description'] += '\n\n#Shorts'

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True,
        mimetype='video/mp4'
    )

    print(f"[youtube] Uploading: {title}")
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] Progress: {int(status.progress() * 100)}%")

    print(f"[youtube] Uploaded! Video ID: {response['id']}")
    print(f"[youtube] URL: https://youtube.com/shorts/{response['id']}")

    return response


def main():
    video_file = Path('final_video.mp4')
    if not video_file.exists():
        print("[youtube] No video found at final_video.mp4")
        return

    import config
    title = f"Learn {config.LANGUAGE['name']} Daily"
    description = "#shorts #language #education"
    tags = ['education', 'language learning']

    try:
        upload_to_youtube(
            video_path=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id='22'
        )
    except Exception as e:
        print(f"[youtube] Upload failed: {e}")
        raise


if __name__ == '__main__':
    main()
