import os
import csv
import re
import time
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import googleapiclient.discovery
from config.settings import Config

# CONSTANTS
MIN_VIEWS, MIN_COMMENTS, VIDS_PER_CHANNEL, API_RETRY_DELAY = 100, 1, 1000, 2

COMMENT_CSV_HEADERS = [
    "Video ID", "Video Title", "Comment ID", "Parent ID",
    "Author", "Published At", "Like Count", "Comment"
]

# UTILS
def build_youtube_client(): return googleapiclient.discovery.build("youtube", "v3", developerKey=Config.YOUTUBE_API_KEY)

def _api_call_with_retry(fn, *args, retry_delay: int = API_RETRY_DELAY, **kwargs):
    delay = retry_delay
    while True:
        try:
            return fn(*args, **kwargs).execute()
        except Exception as e:
            print(f"API error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2

            if delay > 10:
                print("Failed to process request. Breaking.")
                break

def compile_title_pattern(keyword: str) -> re.Pattern: return re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)

def _extract_handle_from_url(url: str) -> str | None:
    path = urlparse(url).path.strip("/")
    if path.startswith("@"):
        return path[1:]
    parts = path.split("/")
    if parts[0] in ("c", "user") and len(parts) > 1:
        return parts[1]
    return parts[0] if parts[0] else None

def resolve_channel_id(yt, url: str):
    handle = _extract_handle_from_url(url)
    if not handle:
        print(f"Could not extract handle from URL: {url}")
        return None

    resp = _api_call_with_retry(yt.channels().list, part="id", forHandle=handle)
    if resp and resp.get("items"):
        return resp["items"][0]["id"]

    # Fallback: search by handle name
    resp = _api_call_with_retry(
        yt.search().list, part="snippet", q=handle, type="channel", maxResults=1
    )
    if resp and resp.get("items"):
        return resp["items"][0]["snippet"]["channelId"]

    print(f"Could not resolve channel ID for URL: {url}")
    return None

def search_videos_in_channel(
    yt, channel_id: str, keyword: str, max_results: int = VIDS_PER_CHANNEL
):
    resp = _api_call_with_retry(
        yt.search().list,
        part="snippet",
        channelId=channel_id,
        type="video",
        q=keyword,
        order="date",
        maxResults=max_results,
    )
    if not resp:
        return []

    pattern = compile_title_pattern(keyword)
    return [
        (item["id"]["videoId"], item["snippet"]["title"])
        for item in resp.get("items", [])
        if item["id"].get("videoId") and pattern.search(item["snippet"].get("title", ""))
    ]

def search_videos_globally(
    yt,
    query: str,
    title_patterns: list[re.Pattern],
    published_after: str,
    published_before: str,
    max_videos: int | None = None,
):
    matched, page_token, total_checked = [], None, 0

    while True:
        if max_videos is not None and len(matched) >= max_videos:
            print(f"Reached max_videos={max_videos}, stopping search.")
            break

        resp = _api_call_with_retry(
            yt.search().list,
            part="snippet",
            q=query,
            type="video",
            maxResults=50,
            pageToken=page_token,
            publishedAfter=published_after,
            publishedBefore=published_before,
            order="relevance",
        )
        if not resp:
            break

        for item in resp.get("items", []):
            total_checked += 1
            vid = item["id"].get("videoId")
            title = item["snippet"].get("title", "")
            if vid and all(p.search(title) for p in title_patterns):
                matched.append((vid, title))
                print(f"[matched] {vid} - {title}")
                if max_videos is not None and len(matched) >= max_videos:
                    break

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    print(f"Global search complete. Checked ~{total_checked} results, found {len(matched)} videos.")
    return matched

def filter_videos_by_stats(
    yt,
    videos,
    min_views: int = MIN_VIEWS,
    min_comments: int = MIN_COMMENTS,
):
    kept = []
    ids = [vid for vid, _ in videos]

    for i in range(0, len(ids), 50):
        batch_ids = ids[i : i + 50]
        resp = _api_call_with_retry(
            yt.videos().list, part="statistics,snippet", id=",".join(batch_ids)
        )
        if not resp:
            continue

        for item in resp.get("items", []):
            vid_id = item["id"]
            title = item.get("snippet", {}).get("title", "")
            view_count = int(item.get("statistics", {}).get("viewCount", 0))
            comment_count = int(item.get("statistics", {}).get("commentCount", 0))

            if view_count >= min_views and comment_count >= min_comments:
                kept.append((vid_id, title))
            else:
                print(f"[filtered-out] {vid_id} (views={view_count}, comments={comment_count})")

    return kept

def _build_rfc3339_window(
    timeframe_days: int | None
) -> tuple[str, str]:
    if timeframe_days is None:
        raise ValueError("timeframe_days must be provided.")
    
    start_dt = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
    start_date_rfc3339 = start_dt.isoformat(timespec="seconds").replace("+00:00", "Z")
    end_dt = datetime.now(timezone.utc)
    end_date_rfc3339 = end_dt.isoformat(timespec="seconds").replace("+00:00", "Z")
    return start_date_rfc3339, end_date_rfc3339

def _collect_videos_from_channels(yt, keywords: list[str]) -> list[tuple[str, str]]:
    channel_ids = [resolve_channel_id(yt, url) for url in Config.CHANNELS]
    channel_ids = [cid for cid in channel_ids if cid]

    seen, collected = set(), []

    for keyword in keywords:
        print(f"Searching channel videos for keyword: '{keyword}'")
        candidates = []

        for cid in channel_ids:
            candidates.extend(search_videos_in_channel(yt, cid, keyword))

        new_candidates = [(vid, title) for vid, title in candidates if vid not in seen]
        if not new_candidates:
            print(f"No new videos found for keyword '{keyword}'.")
            continue

        filtered = filter_videos_by_stats(yt, new_candidates)
        print(
            f"{len(filtered)}/{len(new_candidates)} videos passed thresholds "
            f"for keyword '{keyword}'."
        )

        for vid_id, title in filtered:
            seen.add(vid_id)
            collected.append((vid_id, title))

    return collected

def _collect_videos_globally(
    yt,
    query: str,
    title_keywords: list[str],
    timeframe_days: int | None = 365,
    min_views: int = MIN_VIEWS,
    min_comments: int = MIN_COMMENTS,
    max_videos: int | None = None,
) -> list[tuple[str, str]]:
    published_after, published_before = _build_rfc3339_window(timeframe_days)
    print(
        f"Searching globally for '{query}' between "
        f"{published_after} and {published_before}..."
    )

    title_patterns = [compile_title_pattern(kw) for kw in title_keywords]
    matched = search_videos_globally(yt, query, title_patterns, published_after, published_before, max_videos)

    if not matched:
        print("No matching videos found.")
        return []

    filtered = filter_videos_by_stats(yt, matched, min_views, min_comments)
    print(
        f"{len(filtered)} videos remain after filtering "
        f"(min_views={min_views}, min_comments={min_comments})."
    )
    return filtered

def fetch_all_comments_raw(yt, video_id: str) -> list[dict]:
    """Fetches native JSON dicts from YouTube API."""
    raw_threads = []
    page_token = None

    while True:
        resp = _api_call_with_retry(
            yt.commentThreads().list,
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token,
            textFormat="plainText",
            order="relevance",
        )
        if not resp:
            break

        # Iterate through threads to paginate replies if they exist
        for item in resp.get("items", []):
            top_id = item["snippet"]["topLevelComment"]["id"]
            
            # Pull paginated replies as a raw nested list inside the dict
            if item["snippet"].get("totalReplyCount", 0) > 0:
                all_replies = []
                r_page_token = None
                while True:
                    r_resp = _api_call_with_retry(
                        yt.comments().list,
                        part="snippet",
                        parentId=top_id,
                        maxResults=100,
                        pageToken=r_page_token,
                        textFormat="plainText",
                    )
                    if not r_resp:
                        break
                    all_replies.extend(r_resp.get("items", []))
                    r_page_token = r_resp.get("nextPageToken")
                    if not r_page_token:
                        break
                item["fetched_replies"] = all_replies

            raw_threads.append(item)

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return raw_threads

def write_comments_to_json(output_path: str, videos: list[tuple[str, str]], yt) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    all_raw_data = {}
    for video_id, title in videos:
        print(f"Fetching raw comments for video {video_id} | {title} ...")
        raw_data = fetch_all_comments_raw(yt, video_id)

        if not raw_data:
            print(f"No comments fetched for {video_id}.")
            continue

        all_raw_data[video_id] = {
            "video_title": title,
            "raw_threads": raw_data
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_raw_data, f, indent=2)

    print(f"JSON saved to {output_path}")

def extract_youtube_comments(keywords: list[str] | None = Config.KEYWORDS) -> None:
    if keywords is None:
        print("Must provide keywords")
        return

    yt = build_youtube_client()

    channel_videos = _collect_videos_from_channels(yt, keywords)
    channel_output = os.path.join(Config.RAW_DATA_DIR, "yt_comments", "matched_comments.json")
    write_comments_to_json(channel_output, channel_videos, yt)

    global_videos = _collect_videos_globally(
        yt,
        query="Pakistan Solar",
        title_keywords=["Pakistan", "Solar"],
        timeframe_days=365,
    )
    global_output = os.path.join(Config.RAW_DATA_DIR, "yt_comments", "global_pakistan_solar_comments.json")
    write_comments_to_json(global_output, global_videos, yt)