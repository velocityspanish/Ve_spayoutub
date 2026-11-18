"""
Twitter/X Upload Script
Uploads videos to Twitter/X using Twitter API (Free Tier Compatible!)
"""

import os
import sys
import time
import tweepy
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

load_dotenv()


def upload_to_twitter(video_path, caption):
    api_key = os.getenv('TWITTER_API_KEY', '').strip()
    api_secret = os.getenv('TWITTER_API_SECRET', '').strip()
    access_token = os.getenv('TWITTER_ACCESS_TOKEN', '').strip()
    access_secret = os.getenv('TWITTER_ACCESS_SECRET', '').strip()

    if not all([api_key, api_secret, access_token, access_secret]):
        raise ValueError("Missing Twitter credentials in .env")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[twitter] Video: {file_size_mb:.2f} MB")

    try:
        print("[twitter] Authenticating with API v1.1 (media upload)...")
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api_v1 = tweepy.API(auth)

        print("[twitter] Authenticating with API v2 (posting)...")
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        print("[twitter] Uploading video (chunked)...")
        media = api_v1.media_upload(
            filename=str(video_path_obj),
            media_category='tweet_video',
            chunked=True
        )
        print(f"[twitter] Video uploaded! Media ID: {media.media_id}")

        print("[twitter] Waiting for video processing (5s)...")
        time.sleep(5)

        tweet_text = caption[:280]
        response = client.create_tweet(
            text=tweet_text,
            media_ids=[media.media_id]
        )

        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
        print(f"[twitter] Posted! URL: {tweet_url}")

        return {'id': tweet_id, 'url': tweet_url, 'platform': 'twitter'}

    except tweepy.errors.Unauthorized as e:
        print(f"[twitter] Authentication failed: {e}")
        raise
    except tweepy.errors.Forbidden as e:
        print(f"[twitter] Permission denied: {e}")
        raise
    except tweepy.errors.TooManyRequests as e:
        print(f"[twitter] Rate limit exceeded: {e}")
        raise
    except Exception as e:
        print(f"[twitter] Unexpected error: {e}")
        raise


if __name__ == '__main__':
    video_file = Path('final_video.mp4')
    if video_file.exists():
        upload_to_twitter(video_file, "Test Upload #LanguageLearning")
    else:
        print("No test video found.")
