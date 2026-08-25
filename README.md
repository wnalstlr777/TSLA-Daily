# TSLA-Daily

GitHub Pages용 Tesla 뉴스 대시보드입니다.

## 자동 업데이트
`.github/workflows/update_news.yml`이 매일 오전 7:30(Asia/Seoul)에 실행되어
Google News RSS에서 최근 Tesla 뉴스를 수집하고 `news.json`을 갱신합니다.

## 첫 실행
GitHub 저장소의 **Actions → Update Tesla News → Run workflow** 를 한 번 눌러주세요.

그 뒤 사이트를 새로고침하면 최신 기사 카드가 표시됩니다.
