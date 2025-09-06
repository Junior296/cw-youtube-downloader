import yt_dlp
import shutil
import os

def get_streams(video_url):
    # Copy cookie file to /tmp so yt-dlp can safely read/write
    cookie_src = "/etc/secrets/yt.txt"
    cookie_tmp = "/tmp/yt.txt"
    
    if os.path.exists(cookie_src):
        shutil.copy(cookie_src, cookie_tmp)
        cookiefile = cookie_tmp
    else:
        cookiefile = None  # fallback if no cookies needed

    ydl_opts = {
        "quiet": True,
        "cookiefile": cookiefile,
        "cachedir": False,       # no cache writing
        "simulate": True,        # only extract info
        "noprogress": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "writethumbnail": False,
        "writesubtitles": False,
        "nopart": True,          # don't create .part files
        "nooverwrites": True,
        "update": False,
        "rm_cache_dir": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as yt:
        info = yt.extract_info(video_url, download=False)
        formats = info.get('formats', [])
        title = info.get("title", "video").replace("/", "_")

        audios, muxed = [], []
        videos = {}

        for f in formats:
            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            height = f.get("height")
            ext = f.get("ext")

            if f.get("protocol") == "m3u8":  # skip HLS
                continue

            # Video-only
            if vcodec != "none" and acodec == "none":
                if height and (height not in videos or (f.get("tbr") or 0) > (videos[height].get("tbr") or 0)) and ext == "mp4":
                    videos[height] = {
                        "quality": height,
                        "ext": ext,
                        "size": f.get("filesize_approx"),
                        "url": f.get("url")
                    }

            # Audio-only
            elif vcodec == "none" and acodec != "none":
                if int(f.get("abr") or 0) > 100 and ext == "m4a":
                    audios.append({
                        "quality": height,
                        "ext": ext,
                        "size": f.get("filesize_approx"),
                        "url": f.get("url")
                    })

            # Muxed
            elif vcodec != "none" and acodec != "none":
                muxed.append({
                    "quality": height,
                    "ext": ext,
                    "size": f.get("filesize_approx"),
                    "url": f.get("url")
                })

    return title, audios, muxed, list(videos.values())
