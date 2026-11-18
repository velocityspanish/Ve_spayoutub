"""
Threads Upload - Uses tmpfiles.org for public URL
"""

import os
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def upload_to_threads(video_path, text):
    print("\n" + "=" * 60)
    print("THREADS UPLOAD STARTING")
    print("=" * 60)

    access_token = os.getenv('THREADS_ACCESS_TOKEN')
    user_id = os.getenv('THREADS_USER_ID')

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else ("PLACEHOLDER (***)" if s == "***" else "MISSING")
    print(f"[threads] User ID: {user_id}")
    print(f"[threads] Access Token: {mask(access_token)}")

    if not access_token:
        raise ValueError("THREADS_ACCESS_TOKEN not set")
    if not user_id:
        raise ValueError("THREADS_USER_ID not set")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[threads] Video: {video_path} ({file_size_mb:.2f} MB)")

    text_limited = text[:500] if len(text) > 500 else text
    print(f"[threads] Text: {len(text_limited)} chars")

    try:
        print(f"[threads] Step 1: Uploading to temporary hosting...")
        video_url = None

        try:
            print("[threads] Uploading to file.io...")
            with open(video_path_obj, 'rb') as video_file:
                files = {'file': video_file}
                response = requests.post('https://file.io/?expires=1d', files=files, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    video_url = data.get('link')
                    print(f"[threads] Uploaded to file.io: {video_url}")
        except Exception as e:
            print(f"[threads] file.io failed: {e}")

        if not video_url:
            print("[threads] Trying tmpfiles.org...")
            try:
                with open(video_path_obj, 'rb') as video_file:
                    files = {'file': ('video.mp4', video_file, 'video/mp4')}
                    temp_response = requests.post(
                        'https://tmpfiles.org/api/v1/upload',
                        files=files,
                        timeout=180
                    )
                if temp_response.status_code == 200:
                    temp_data = temp_response.json()
                    temp_url = temp_data.get('data', {}).get('url', '')
                    if temp_url:
                        video_url = temp_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/').replace('http://', 'https://')
                        print(f"[threads] Uploaded to tmpfiles.org: {video_url}")
            except Exception as e:
                print(f"[threads] tmpfiles.org failed: {e}")

        if not video_url:
            raise Exception("All hosting attempts failed")

        print(f"[threads] Step 2: Creating Threads container...")
        api_versions = ['v1.0', 'v18.0']
        container_id = None

        for api_version in api_versions:
            container_url = f"https://graph.threads.net/{api_version}/{user_id}/threads"
            container_params = {
                'media_type': 'VIDEO',
                'video_url': video_url,
                'text': text_limited,
                'access_token': access_token
            }
            container_response = requests.post(container_url, params=container_params, timeout=60)
            if container_response.status_code == 200:
                response_data = container_response.json()
                container_id = response_data.get('id')
                if container_id:
                    print(f"[threads] Container created with API {api_version}: {container_id}")
                    break
            else:
                error_data = container_response.json() if container_response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"[threads] API {api_version} failed: {error_msg}")

        if not container_id:
            raise Exception("Failed to create container with all API versions")

        print(f"[threads] Step 3: Waiting for video processing...")
        max_wait = 120
        waited = 0
        while waited < max_wait:
            status_url = f"https://graph.threads.net/v1.0/{container_id}"
            status_params = {
                'fields': 'status',
                'access_token': access_token
            }
            status_response = requests.get(status_url, params=status_params, timeout=30)
            status_data = status_response.json()
            status = status_data.get('status', 'UNKNOWN')
            print(f"[threads] Status: {status} (waited {waited}s)")
            if status == 'FINISHED':
                print(f"[threads] Video processing complete!")
                break
            elif status == 'ERROR':
                raise Exception(status_data.get('error_message', 'Video processing failed'))
            time.sleep(10)
            waited += 10

        if waited >= max_wait:
            raise Exception("Video processing timed out")

        print(f"[threads] Step 4: Publishing...")
        publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
        publish_params = {
            'creation_id': container_id,
            'access_token': access_token
        }
        publish_response = requests.post(publish_url, params=publish_params, timeout=60)
        if publish_response.status_code != 200:
            error_data = publish_response.json() if publish_response.text else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"Threads Publish Error: {error_msg}")

        thread_id = publish_response.json().get('id')
        print(f"[threads] SUCCESS! Thread ID: {thread_id}")
        print("=" * 60)
        return {'id': thread_id, 'platform': 'threads', 'status': 'success'}

    except Exception as e:
        print(f"[threads] ERROR: {e}")
        print("=" * 60)
        raise


if __name__ == '__main__':
    video_file = Path('final_video.mp4')
    if video_file.exists():
        try:
            result = upload_to_threads(str(video_file), "Test upload")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Failed: {e}")
