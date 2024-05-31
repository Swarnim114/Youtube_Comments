from youtube_comment_downloader import YoutubeCommentDownloader
import concurrent.futures

def fetch_comments(video_id, start_idx, end_idx):
    downloader = YoutubeCommentDownloader()
    comments = []
    retry_attempts = 3

    for attempt in range(retry_attempts):
        try:
            for idx, comment in enumerate(downloader.get_comments(video_id)):
                if idx >= start_idx and idx < end_idx:
                    comments.append(comment['text'])
                elif idx >= end_idx:
                    break
            return comments
        except Exception as e:
            if attempt < retry_attempts - 1:
                continue
            else:
                print(f"Failed to fetch comments from {start_idx} to {end_idx} after {retry_attempts} attempts. Error: {e}")
                return []

    return comments

def scrape_youtube_comments(video_url):
    video_id = video_url.split('v=')[-1]  # Extract video ID from URL
    downloader = YoutubeCommentDownloader()

    # Determine the total number of comments
    total_comments = sum(1 for _ in downloader.get_comments(video_id))

    # Divide the workload
    num_workers = 20  # Increase the number of concurrent workers for better performance
    batch_size = total_comments // num_workers

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(num_workers):
            start_idx = i * batch_size
            end_idx = (i + 1) * batch_size if i != num_workers - 1 else total_comments
            futures.append(executor.submit(fetch_comments, video_id, start_idx, end_idx))

        comments = []
        for future in concurrent.futures.as_completed(futures):
            comments.extend(future.result())

    return comments

def save_comments(comments):
    if comments:
        with open("comments.txt", "w", encoding="utf-8") as file:
            for i, comment in enumerate(comments):
                file.write(f"{i + 1}: {comment}\n")
        print("Comments have been saved to comments.txt")
    else:
        print("No comments found or failed to scrape comments.")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    comments = scrape_youtube_comments(video_url)
    save_comments(comments)
