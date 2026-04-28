# fix-ytdl-cover-art

Script to automate cropping of landscape cover art (yt music cover art problem) to square via center crop.




## Scripts

### `fix_cover.py` — embedded audio art

Fixes non-square artwork embedded in audio file tags. Drop it into a music folder and run it. Recurses into all subfolders.

Supported formats:

| Format | Extension |
|--------|-----------|
| MP3 | `.mp3` |
| FLAC | `.flac` |
| AAC/M4A | `.m4a` |
| Ogg Opus | `.opus` |
| Ogg Vorbis | `.ogg` |



## Requirements

Python 3.10+


## Warning ⚠⚠

- All artwork is re-saved as JPEG regardless of the original format (PNG covers included).
- The script modifies files in-place (without conformation). Back up your library first if needed.


## Usage

1. Copy the relevant script into your target folder.
2. Run it:

```bash
python fix_cover.py
```
**Example output:**

```
Processing: some_album_track.flac
  Saved: some_album_track.flac
Processing: other_track.opus
  Already square, skipping.
Done.
```


## How it works

- Reads embedded cover art (or opens image files directly).
- Skips anything already square.
- Center-crops landscape images to the largest possible square, equal amounts removed from both sides. No stretching or padding.
- Re-encodes and writes back.
- Audio data is never modified.


