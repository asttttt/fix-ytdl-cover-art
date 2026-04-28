import os
from pathlib import Path
from io import BytesIO
from PIL import Image
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
import base64

# Scans the folder this script is placed in (and all subfolders)
MUSIC_DIR = Path(__file__).parent


def center_square_crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def process_image_bytes(data: bytes) -> bytes | None:
    img = Image.open(BytesIO(data)).convert("RGB")
    w, h = img.size
    if w == h:
        print("  Already square, skipping.")
        return None
    cropped = center_square_crop(img)
    out = BytesIO()
    cropped.save(out, format="JPEG", quality=90)
    return out.getvalue()


def handle_mp3(path: Path):
    try:
        tags = ID3(path)
        apic_keys = [k for k in tags.keys() if k.startswith("APIC")]
        if not apic_keys:
            return
        for key in apic_keys:
            apic = tags[key]
            new_data = process_image_bytes(apic.data)
            if new_data:
                apic.data = new_data
                apic.mime = "image/jpeg"
        tags.save(path)
        print(f"  Saved: {path.name}")
    except Exception as e:
        print(f"  Error: {e}")


def handle_flac(path: Path):
    try:
        audio = FLAC(path)
        if not audio.pictures:
            return
        for pic in audio.pictures:
            new_data = process_image_bytes(pic.data)
            if new_data:
                pic.data = new_data
                pic.mime = "image/jpeg"
                pic.width = pic.height = 0
        audio.save()
        print(f"  Saved: {path.name}")
    except Exception as e:
        print(f"  Error: {e}")


def handle_m4a(path: Path):
    try:
        audio = MP4(path)
        covers = audio.tags.get("covr")
        if not covers:
            return
        new_covers = []
        changed = False
        for cover in covers:
            new_data = process_image_bytes(bytes(cover))
            if new_data:
                new_covers.append(MP4Cover(new_data, imageformat=MP4Cover.FORMAT_JPEG))
                changed = True
            else:
                new_covers.append(cover)
        if changed:
            audio["covr"] = new_covers
            audio.save()
            print(f"  Saved: {path.name}")
    except Exception as e:
        print(f"  Error: {e}")


def handle_ogg_opus(path: Path):
    """Ogg Opus/Vorbis store cover art as base64 METADATA_BLOCK_PICTURE."""
    try:
        audio = OggOpus(path) if path.suffix.lower() == ".opus" else OggVorbis(path)
        pics = audio.get("metadata_block_picture", [])
        if not pics:
            return
        new_pics = []
        changed = False
        for b64 in pics:
            raw = base64.b64decode(b64)
            pic = Picture(raw)
            new_data = process_image_bytes(pic.data)
            if new_data:
                pic.data = new_data
                pic.mime = "image/jpeg"
                pic.width = pic.height = pic.depth = pic.colors = 0
                new_pics.append(base64.b64encode(pic.write()).decode("ascii"))
                changed = True
            else:
                new_pics.append(b64)
        if changed:
            audio["metadata_block_picture"] = new_pics
            audio.save()
            print(f"  Saved: {path.name}")
    except Exception as e:
        print(f"  Error: {e}")


HANDLERS = {
    ".mp3": handle_mp3,
    ".flac": handle_flac,
    ".m4a": handle_m4a,
    ".opus": handle_ogg_opus,
    ".ogg": handle_ogg_opus,
}

if __name__ == "__main__":
    for f in Path(MUSIC_DIR).rglob("*"):
        if f.suffix.lower() in HANDLERS:
            print(f"Processing: {f.name}")
            HANDLERS[f.suffix.lower()](f)
    print("Done.")
