import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 깃허브 시크릿에서 디스코드 웹후크 URL을 가져옵니다.
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TARGET_URL = "https://www.polyteru-store.com/schedule"
BASE_URL = "https://www.polyteru-store.com"
LAST_POST_FILE = "last_post.txt"

def get_latest_post():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 아임웹 게시판 내 게시글 태그 탐색
        post_link_tag = soup.select_one("a[href*='/schedule?bmode=view']") or soup.select_one(".board_list a") or soup.select_one("a[href*='idx=']")
        
        if post_link_tag:
            title = post_link_tag.get_text(strip=True)
            rel_url = post_link_tag.get("href", "")
            full_url = urllib.parse.urljoin(BASE_URL, rel_url)
            return {"title": title, "url": full_url}
    except Exception as e:
        print(f"크롤링 에러: {e}")
    return None

def send_discord_alarm(title, url):
    if not DISCORD_WEBHOOK_URL:
        print("디스코드 웹후크 URL이 설정되지 않았습니다.")
        return

    payload = {
        "username": "폴리테루 발매 알리미",
        "embeds": [{
            "title": "🚨 POLYTERU 새로운 일정 등록!",
            "description": f"**{title}**\n\n[▶ 일정 바로가기]({url})",
            "color": 0x000000,
            "footer": {"text": "Polyteru Schedule Notifier"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def main():
    post = get_latest_post()
    if not post:
        print("게시글을 가져오지 못했습니다.")
        return

    last_title = ""
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    # 기존 최신글과 다르면 알림 전송
    if post["title"] != last_title:
        print(f"새로운 게시글 발견: {post['title']}")
        send_discord_alarm(post["title"], post["url"])
        
        # 최신 게시글 제목 업데이트
        with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
            f.write(post["title"])
    else:
        print("새로운 일정이 없습니다.")

if __name__ == "__main__":
    main()
