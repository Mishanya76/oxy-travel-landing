"""Download selected photos from the OXY.TRAVEL VK community and convert them to WebP."""
from __future__ import annotations

import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

PHOTOS = {
    # Wall posts of https://vk.ru/oxy.samara
    "hero-egypt": "https://sun9-4.userapi.com/s/v1/ig2/edxjhAffY5u828jzdksYLcgdtpH91XrwZ8F4o3UU3Q_crslwfWys1Y4oPcnb42MkygWjhjJf9eTNmlqKI7ucRCdw.jpg?quality=95&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720,1440x810,1600x900&from=bu&cs=1600x0",
    "egypt-sahl": "https://sun9-87.userapi.com/s/v1/ig2/QeLa1ZKqN_TFNu9j2AbY-0moXcZihdtHWRAiUCR7tAM9rFim9YPgvlh_Zi-LPQ0sshQfhVvkW_zHdNnzQ1VyXsbm.jpg?quality=95&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720,1440x810,1600x900&from=bu&cs=1600x0",
    "turkey-kemer": "https://sun9-45.userapi.com/s/v1/ig2/sQzOKyE2nWefwJ1b2S09_o6yWtUKMwCT87mcrsIPyhlOLEpS1HHlD4lgNaSktU84AkimqqgUAXMSmOa157xDW1BR.jpg?quality=95&as=32x27,48x40,72x60,108x90,160x133,240x200,360x300,480x400,540x450,640x533,720x600,1080x900,1280x1067,1296x1080&from=bu&cs=1296x0",
    "turkey-side": "https://sun9-6.userapi.com/s/v1/ig2/tI-2AfCuctUrTU1KAQDyMp5Zj-YCsakoaGdQnNt5prklM7DTnA0HServhQwWWO6ezNPDUT82EAqqsCM77zdJ6k4t.jpg?quality=95&as=32x20,48x30,72x45,108x67,160x100,240x150,360x225,480x300,540x337,640x400,720x450,1024x640&from=bu&cs=1024x0",
    "russia-samara": "https://sun9-77.vkuserphoto.ru/s/v1/ig1/3SselMBx3ssscQT2hAXmGvhwCqxXsKJvTG9104-g0ZmEeNWXmTzeAt_2wkrAwPipD-b-d1D6.jpg?quality=96&as=32x16,48x24,72x36,108x54,160x80,240x120,360x180,480x240,540x270,640x320,720x360,1080x540,1200x600&from=bu&cs=1200x0",
    "phuket-offer": "https://sun9-7.vkuserphoto.ru/s/v1/ig2/IZd4li_W545gi5UM4moRnkLIUaS7tvm11hjMsaT2hAlp9UdfsvExR0I0T4spUuw9w3SUxy_7xPYZkUhOZP4mEamb.jpg?quality=96&as=32x23,48x34,72x51,108x77,160x114,240x170,360x256,480x341,540x383,548x389&from=bu&cs=548x0",
    # Albums of the community: "Наши туристы в Тае", "Кипр", "Кос"
    "thailand-1": "https://sun9-15.vkuserphoto.ru/s/v1/ig2/qJbJy7fsFIX9K65igITJ3pBhqdh3vTkTywZ4B3M42yqPKmVHdsI3ouPIyaH1ErhF_HbPpPegN3hUDWG_E6-H0zEg.jpg?quality=96&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720&from=bu&cs=1280x0",
    "thailand-2": "https://sun9-82.vkuserphoto.ru/s/v1/ig2/i9MLG1syQxsbqQgXqQ5xTqQrz9r4ZM8m0Z7eW3blazFCXgz7HzWflaqwiPvRZdevu4_3iLVhHl7jqEif2nzK1UaK.jpg?quality=96&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720&from=bu&cs=1280x0",
    "thailand-3": "https://sun9-63.vkuserphoto.ru/s/v1/ig2/8e5goLJjFPZfz7Y9BwU_hbTTjShtsR19ozQLDTW96RQNfszt3CC6vtKXysWPGNU7O-ZmjkA4JRYsw9yq-Xf_-2Zr.jpg?quality=96&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720&from=bu&cs=1280x0",
    "thailand-4": "https://sun9-2.vkuserphoto.ru/s/v1/ig2/i_KTLRxR-lP3jZU5-T5yf98qjFHQmdYQ6UGJtaphfSbnqJCjTHZl_r9wzfYe-kvw729THwTSP8tKG4SAUOQWjsui.jpg?quality=96&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720&from=bu&cs=1280x0",
    "thailand-5": "https://sun9-50.vkuserphoto.ru/s/v1/ig2/gBPbcvWXfefdNsmKUFH_8fmvVVAPoxUNtSNA4tgMxWFgD1I-nzfhc89WcJ-I3im-URy2grpKgdX-gkthT1WFQd8s.jpg?quality=96&as=32x18,48x27,72x40,108x61,160x90,240x135,360x202,480x270,540x304,640x360,720x405,1080x607,1280x720&from=bu&cs=1280x0",
    "cyprus-1": "https://sun9-70.vkuserphoto.ru/s/v1/ig2/zS7vNl6ve-p1PUuv633WwLHn-aRa9lSLkJi1n5-Z8Emd1ju-E3j4Xvrm3xsBRQ4wFFxFdppGXGZNiO8f4xUkjGP2.jpg?quality=96&as=32x24,48x36,72x54,108x81,160x120,240x180,360x270,480x360,540x405,640x480,720x540,1080x810,1280x960&from=bu&cs=1280x0",
    "cyprus-2": "https://sun9-47.vkuserphoto.ru/s/v1/ig2/1zm1bYF13BPuk7XjeSMPdTKqGgxoLf4eaSnHHMaIKP3PaIRBHhTjzy_IuKdeiZCDlJwt6JmVxcPUQrxhfyKPHOhk.jpg?quality=96&as=32x24,48x36,72x54,108x81,160x120,240x180,360x270,480x360,540x405,640x480,720x540,1080x810,1280x960&from=bu&cs=1280x0",
    "kos-1": "https://sun9-48.vkuserphoto.ru/s/v1/ig2/AddubRzOJdL0hHfA1YERShOE_a5yCpMuehMLAZyVwazQe6ShNBKfqGQqtNhhSABttHbtlm7jfZ8hw2ywaKQ1iA2M.jpg?quality=96&as=32x21,48x32,72x48,108x72,160x107,240x160,360x240,480x320,540x360,640x426,720x480,1080x720,1280x853&from=bu&cs=1280x0",
}

manifest = {}
for name, url in PHOTOS.items():
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
            "Referer": "https://vk.ru/oxy.samara",
        },
    )
    with urlopen(request, timeout=30) as response:
        data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")
    image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    target = OUT / f"{name}.webp"
    image.save(target, "WEBP", quality=82, method=6)
    manifest[name] = {
        "file": target.name,
        "source": url,
        "size": list(image.size),
        "bytes": target.stat().st_size,
    }
    print(f"{name}: {image.size} -> {target.stat().st_size // 1024} KB")

(OUT / "sources.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)
