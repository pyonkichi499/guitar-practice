"""songs/<曲名>/sources.toml に書かれた URL から練習用の音源をダウンロードする。"""

import argparse
import logging
import shutil
import sys
import tomllib
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

logger = logging.getLogger(__name__)

SONGS_DIR = Path(__file__).resolve().parent.parent / "songs"

# m4a は YouTube が配信している AAC をそのまま保存する。mp3 / wav は ffmpeg で変換する。
NATIVE_FORMAT = "m4a"
CONVERTED_FORMATS = ("mp3", "wav")


def load_sources(song_dir: Path) -> list[dict[str, str]]:
    sources_file = song_dir / "sources.toml"
    if not sources_file.is_file():
        raise FileNotFoundError(f"{sources_file} がありません")

    with sources_file.open("rb") as f:
        sources = tomllib.load(f).get("sources", [])

    for source in sources:
        if not source.get("name") or not source.get("url"):
            raise ValueError(f"{sources_file}: name と url は必須です: {source}")
    return sources


def build_options(media_dir: Path, name: str, audio_format: str) -> dict:
    options = {
        "format": "bestaudio[ext=m4a]",
        "outtmpl": str(media_dir / f"{name}.%(ext)s"),
        "noplaylist": True,
    }
    if audio_format in CONVERTED_FORMATS:
        options["format"] = "bestaudio"
        options["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": audio_format}
        ]
    return options


def download(song: str, audio_format: str, force: bool) -> int:
    song_dir = SONGS_DIR / song
    sources = load_sources(song_dir)
    if not sources:
        logger.warning("%s に URL が登録されていません", song_dir / "sources.toml")
        return 0

    media_dir = song_dir / "media"
    media_dir.mkdir(exist_ok=True)

    failures = 0
    for source in sources:
        name, url = source["name"], source["url"]
        target = media_dir / f"{name}.{audio_format}"
        if target.exists() and not force:
            logger.info("スキップ（取得済み）: %s", target)
            continue

        logger.info("ダウンロード: %s <- %s", target, url)
        try:
            with YoutubeDL(build_options(media_dir, name, audio_format)) as ydl:
                ydl.download([url])
        except DownloadError:
            # 原因は yt-dlp 自身がエラー出力済み
            logger.error("ダウンロードに失敗しました: %s", url)
            failures += 1
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "song", help="songs/ 以下の曲ディレクトリ名（例: diamond-happy）"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=(NATIVE_FORMAT, *CONVERTED_FORMATS),
        default=NATIVE_FORMAT,
        help="保存する音源の形式（既定: %(default)s）",
    )
    parser.add_argument(
        "--force", action="store_true", help="取得済みでも再ダウンロードする"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.format in CONVERTED_FORMATS and shutil.which("ffmpeg") is None:
        logger.error("%s への変換には ffmpeg が必要です", args.format)
        return 1

    try:
        failures = download(args.song, args.format, args.force)
    except (FileNotFoundError, ValueError, tomllib.TOMLDecodeError) as e:
        logger.error("%s", e)
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
