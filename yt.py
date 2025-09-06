import yt_dlp


def get_streams(video_url):
    ydl_opts = {
        "quiet": True,
        "cookiefile": "/etc/secrets/yt.txt",
        "cachedir": False,
        "noprogress": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "simulate": True,
        "writethumbnail": False,
        "writesubtitles": False,
        "nopart": True,
        "nooverwrites": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as yt:
            info = yt.extract_info(video_url, download=False)
            formats = info.get('formats') or []
            title = info.get("title", "video").replace("/", "_")

            audios, muxed = [], []
            videos = {}

            for f in formats:
                vcodec = f.get("vcodec")
                acodec = f.get("acodec")
                height = f.get("height")
                ext = f.get("ext")

                if f.get("protocol") == "m3u8":
                    continue

                if vcodec != "none" and acodec == "none":
                    if height and (height not in videos or (f.get("tbr") or 0) > (videos[height].get("tbr") or 0)) and ext == "mp4":
                        videos[height] = {
                            "quality": height,
                            "ext": ext,
                            "size": f.get("filesize_approx"),
                            "url": f.get("url")
                        }

                elif vcodec == "none" and acodec != "none":
                    if int(f.get("abr") or 0) > 100 and ext == "m4a":
                        audios.append({
                            "quality": height,
                            "ext": ext,
                            "size": f.get("filesize_approx"),
                            "url": f.get("url")
                        })

                elif vcodec != "none" and acodec != "none":
                    muxed.append({
                        "quality": height,
                        "ext": ext,
                        "size": f.get("filesize_approx"),
                        "url": f.get("url")
                    })

        return title, audios, muxed, list(videos.values())

    except Exception as e:
        return None, [], [], [], str(e)
