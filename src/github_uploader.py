"""Upload episode MP3s to GitHub Releases and return a public download URL.

This module uses the GitHub REST API (no external PyGithub dependency).
Environment variables used:
- `GITHUB_TOKEN`: Personal Access Token with `repo` scope for private repos or `public_repo` for public repos.
- `GITHUB_REPO`: repository in the form `owner/repo` where releases will be created.

Functions:
- upload_release_asset(mp3_path, tag='automated', release_name=None) -> browser_download_url or None
"""
from __future__ import annotations
import os
import requests


def _api_headers(token: str):
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }


def upload_release_asset(mp3_path: str, tag: str = 'automated', release_name: str | None = None) -> str | None:
    """Create or find a release with `tag` and upload `mp3_path` as an asset.

    Returns the public `browser_download_url` for the uploaded asset, or None on failure/when disabled.
    """
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO')
    if not token or not repo:
        return None

    headers = _api_headers(token)
    api_base = 'https://api.github.com'

    # 1) Try to find an existing release by tag
    try:
        resp = requests.get(f'{api_base}/repos/{repo}/releases/tags/{tag}', headers=headers, timeout=30)
        if resp.status_code == 200:
            release = resp.json()
        else:
            # create a new release
            payload = {'tag_name': tag, 'name': release_name or tag, 'draft': False, 'prerelease': False}
            cre = requests.post(f'{api_base}/repos/{repo}/releases', headers=headers, json=payload, timeout=30)
            if cre.status_code not in (201, 200):
                print(f'Release creation error ({cre.status_code}): {cre.text}')
                return None
            release = cre.json()

        release_id = release['id']

        # 2) Upload the asset
        basename = os.path.basename(mp3_path)
        upload_url = f'https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={basename}'
        # Guess content type
        content_type = 'audio/mpeg'
        with open(mp3_path, 'rb') as fh:
            up_headers = headers.copy()
            up_headers.update({'Content-Type': content_type})
            up = requests.post(upload_url, headers=up_headers, data=fh, timeout=120)
            if up.status_code not in (201, 200):
                print(f'Asset upload error ({up.status_code}): {up.text}')
                return None
            asset = up.json()
            return asset.get('browser_download_url')

    except Exception as e:
        print('GitHub upload failed:', e)
        return None


if __name__ == '__main__':
    print('github_uploader module loaded')
