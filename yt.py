import yt_dlp

def get_streams(video_url):
    ydl_opts = {
        'quiet': True,
        'cookiefile': "/etc/secrets/yt.txt"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as yt:
        info = yt.extract_info(video_url, download=False)
        formats = info['formats']
        title = info.get("title", "video").replace("/", "_")

        audios, muxed = [], []
        videos = {}

        for f in formats:
            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            height = f.get("height")
            ext = f.get("ext")

            # Skip HLS playlists
            if f.get("protocol") == "m3u8":
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
                    audio = {
                        "quality": height,
                        "ext": ext,
                        "size": f.get("filesize_approx"),
                        "url": f.get("url")
                    }
                    audios.append(audio)

            # Muxed (video+audio)
            elif vcodec != "none" and acodec != "none":
                mixed = {
                    "quality": height,
                    "ext": ext,
                    "size": f.get("filesize_approx"),
                    "url": f.get("url")
                }
                muxed.append(mixed)

    return title, audios, muxed, list(videos.values())
