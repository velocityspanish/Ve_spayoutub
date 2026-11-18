"""
Facebook Reels Upload

Facebook Graph API for uploading Reels to Facebook Page.
"""

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

from cover_frame import extract_cover_frame

load_dotenv()


def _set_reel_cover(video_id, access_token, video_path):
    cover = extract_cover_frame(video_path)
    if not cover:
        print("[facebook] No cover frame available, keeping default")
        return
    endpoints = ("https://graph-video.facebook.com/v21.0", "https://graph.facebook.com/v21.0")
    for attempt in range(8):
        for base in endpoints:
            try:
                with open(cover, 'rb') as fh:
                    res = requests.post(
                        f"{base}/{video_id}/thumbnails",
                        data={'access_token': access_token, 'is_preferred': 'true'},
                        files={'source': ('cover.jpg', fh, 'image/jpeg')},
                        timeout=(15, 120),
                    )
                if res.status_code == 200:
                    print(f"[facebook] Cover set to phrase frame: {cover.name}")
                    return
                body = res.json() if res.text else {}
                err = body.get('error', {}) if isinstance(body, dict) else {}
                print(f"[facebook] Cover attempt {attempt + 1} ({base.split('/')[2]}): "
                      f"{res.status_code} - {str(err or res.text)[:160]}")
                if err.get('code') in (100, 190, 200):
                    print("[facebook] Cover endpoint rejected the request, keeping default")
                    return
            except Exception as exc:
                print(f"[facebook] Cover attempt {attempt + 1} error: {exc}")
        time.sleep(15)
    print("[facebook] Could not set custom cover; reel keeps the default frame")


def _post_pinned_comment(video_id, description, access_token, page_id):
    import time
    print(f"[facebook] Posting description as pinned comment...")
    max_retries = 5
    comment_id = None
    for attempt in range(max_retries):
        try:
            comment_url = f"https://graph.facebook.com/v21.0/{video_id}/comments"
            comment_data = {
                'access_token': access_token,
                'message': description
            }
            res_comment = requests.post(comment_url, data=comment_data, timeout=30)
            if res_comment.status_code == 200:
                resp = res_comment.json()
                comment_id = resp.get('id')
                if comment_id:
                    print(f"[facebook] Comment posted! ID: {comment_id}")
                    break
                else:
                    print(f"[facebook] Comment response missing ID: {resp}")
            elif res_comment.status_code == 404 and attempt < max_retries - 1:
                wait = (attempt + 1) * 10
                print(f"[facebook] Video not ready for comments yet, retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"[facebook] Comment post failed: {res_comment.status_code} - {res_comment.text[:200]}")
                break
        except Exception as e:
            print(f"[facebook] Comment post error: {e}")
            break
    if comment_id:
        try:
            pin_url = f"https://graph.facebook.com/v21.0/{comment_id}"
            pin_data = {
                'access_token': access_token,
                'is_pinned': 'true'
            }
            res_pin = requests.post(pin_url, data=pin_data, timeout=15)
            if res_pin.status_code == 200:
                print(f"[facebook] Comment pinned to top!")
            else:
                print(f"[facebook] Pin attempt: {res_pin.status_code} - {res_pin.text[:200]}")
        except Exception as e:
            print(f"[facebook] Pin attempt error: {e}")


def upload_to_facebook(video_path, description, title="Velocity lesson"):
    print("\n" + "=" * 60)
    print("FACEBOOK UPLOAD STARTING")
    print("=" * 60)

    access_token = (os.getenv('FACEBOOK_ACCESS_TOKEN') or os.getenv('FB_ACCESS_TOKEN')
                    or os.getenv('FB_PAGE_ACCESS_TOKEN'))
    page_id = os.getenv('FACEBOOK_PAGE_ID') or os.getenv('FB_PAGE_ID')

    print(f"[facebook] Page ID: {'set' if page_id else 'MISSING'}")
    print(f"[facebook] Access Token: {'set' if access_token else 'MISSING'}")

    if not access_token:
        raise ValueError("FACEBOOK_ACCESS_TOKEN not set in environment variables")
    if not page_id:
        raise ValueError("FACEBOOK_PAGE_ID not set in environment variables")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[facebook] Video: {video_path} ({file_size_mb:.2f} MB)")

    try:
        file_size = video_path_obj.stat().st_size

        print(f"[facebook] Step 1: Initiating upload session...")
        start_url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"
        start_data = {
            'access_token': access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        res_start = requests.post(start_url, data=start_data, timeout=30)
        if res_start.status_code != 200:
            raise Exception(f"Start Phase Failed: {res_start.text}")

        start_json = res_start.json()
        video_id = start_json.get('video_id')
        upload_url = start_json.get('upload_url')
        if not video_id:
            raise Exception(f"No video_id returned. Response: {start_json}")

        print(f"[facebook] Step 2: Transferring file...")
        headers = {
            'Authorization': f'OAuth {access_token}',
            'offset': '0',
            'file_size': str(file_size)
        }
        with open(video_path, 'rb') as f:
            res_transfer = requests.post(upload_url, headers=headers, data=f, timeout=600)
        if res_transfer.status_code != 200:
            raise Exception(f"Transfer Phase Failed: {res_transfer.text}")

        print(f"[facebook] Step 3: Publishing Reel...")
        finish_url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"
        finish_data = {
            'access_token': access_token,
            'upload_phase': 'finish',
            'video_id': video_id,
            'description': description,
            'video_state': 'PUBLISHED'
        }
        res_finish = requests.post(finish_url, data=finish_data, timeout=60)

        if res_finish.status_code == 200 and res_finish.json().get('success'):
            print(f"[facebook] SUCCESS! Reel uploaded! Video ID: {video_id}")
            try:
                _set_reel_cover(video_id, access_token, video_path)
            except Exception as exc:
                print(f"[facebook] Cover setup skipped: {exc}")
            _post_pinned_comment(video_id, description, access_token, page_id)
            return {
                'id': video_id,
                'platform': 'facebook',
                'status': 'success',
                'url': f"https://facebook.com/{video_id}"
            }
        else:
            raise Exception(f"Finish Phase Failed: {res_finish.text}")

    except requests.exceptions.Timeout:
        raise Exception("Upload timed out (video too large or slow connection)")
    except Exception as e:
        print(f"[facebook] ERROR: {e}")
        raise


def upload_to_facebook_story(video_path):
    print("\n" + "=" * 60)
    print("FACEBOOK STORY UPLOAD STARTING")
    print("=" * 60)

    access_token = (os.getenv('FACEBOOK_ACCESS_TOKEN') or os.getenv('FB_ACCESS_TOKEN')
                    or os.getenv('FB_PAGE_ACCESS_TOKEN'))
    page_id = os.getenv('FACEBOOK_PAGE_ID') or os.getenv('FB_PAGE_ID')
    if not access_token or not page_id:
        raise ValueError("Missing FACEBOOK_ACCESS_TOKEN or FACEBOOK_PAGE_ID")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    url = f"https://graph.facebook.com/v21.0/{page_id}/video_stories"
    try:
        file_size = video_path_obj.stat().st_size
        print(f"[facebook] Step 1: Initiating upload session...")
        start_url = f"https://graph.facebook.com/v21.0/{page_id}/video_stories"
        start_data = {
            'access_token': access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        res_start = requests.post(start_url, data=start_data, timeout=30)
        if res_start.status_code != 200:
            raise Exception(f"Start Phase Failed: {res_start.text}")

        start_json = res_start.json()
        upload_session_id = start_json.get('upload_session_id')
        video_id = start_json.get('video_id')
        upload_url = start_json.get('upload_url')

        if upload_url:
            print(f"[facebook] Step 2: Transferring file via upload_url...")
            headers = {
                'Authorization': f'OAuth {access_token}',
                'offset': '0',
                'file_size': str(file_size)
            }
            with open(video_path, 'rb') as f:
                res_transfer = requests.post(upload_url, headers=headers, data=f, timeout=600)
            if res_transfer.status_code != 200:
                raise Exception(f"Transfer Phase Failed: {res_transfer.text}")
            print(f"[facebook] Step 3: Finishing upload...")
            finish_url = f"https://graph.facebook.com/v21.0/{page_id}/video_stories"
            finish_data = {
                'access_token': access_token,
                'upload_phase': 'finish',
                'video_id': video_id
            }
            if upload_session_id:
                finish_data['upload_session_id'] = upload_session_id
            res_finish = requests.post(finish_url, data=finish_data, timeout=60)
            if res_finish.status_code == 200 or res_finish.json().get('success'):
                print(f"[facebook] SUCCESS! Story uploaded! Video ID: {video_id}")
                return {'id': video_id, 'platform': 'facebook_story', 'status': 'success'}
            else:
                raise Exception(f"Finish Phase Failed: {res_finish.text}")
        elif upload_session_id:
            print(f"[facebook] Step 2: Transferring file...")
            transfer_url = f"https://graph.facebook.com/v21.0/{page_id}/video_stories"
            with open(video_path, 'rb') as f:
                files = {'video_file_chunk': f}
                transfer_data = {
                    'access_token': access_token,
                    'upload_phase': 'transfer',
                    'start_offset': 0,
                    'upload_session_id': upload_session_id
                }
                res_transfer = requests.post(transfer_url, data=transfer_data, files=files, timeout=600)
            if res_transfer.status_code != 200:
                raise Exception(f"Transfer Phase Failed: {res_transfer.text}")
            print(f"[facebook] Step 3: Finishing upload...")
            finish_url = f"https://graph.facebook.com/v21.0/{page_id}/video_stories"
            finish_data = {
                'access_token': access_token,
                'upload_phase': 'finish',
                'upload_session_id': upload_session_id,
                'title': 'Story Upload'
            }
            res_finish = requests.post(finish_url, data=finish_data, timeout=60)
            if res_finish.status_code == 200 or res_finish.json().get('success'):
                print(f"[facebook] SUCCESS! Story uploaded! Video ID: {video_id}")
                return {'id': video_id, 'platform': 'facebook_story', 'status': 'success'}
            else:
                raise Exception(f"Finish Phase Failed: {res_finish.text}")
        else:
            raise Exception(f"No upload_session_id or upload_url returned. Response: {start_json}")
    except Exception as e:
        print(f"[facebook] ERROR: {e}")
        raise


if __name__ == '__main__':
    from pathlib import Path
    video_file = Path('final_video.mp4')
    if video_file.exists():
        try:
            upload_to_facebook_story(video_file)
        except Exception as e:
            print(f"Test failed: {e}")
