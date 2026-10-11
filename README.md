# guitar-practice

ギター練習用の作業リポジトリ。音源のダウンロードスクリプトと、曲ごとの練習メモ・コード譜を管理する。
ダウンロードした音源は Git で追跡しない。

## セットアップ

```sh
uv sync
```

以下は必須ではないが、入れておくことを勧める。

- `ffmpeg`: mp3 / wav への変換に必要。m4a でも、ないと一部のプレイヤーで再生できない DASH 形式のまま保存される
- `deno`: yt-dlp が YouTube の解析に使う JavaScript ランタイム。ないと取得できる形式が減ることがある

## 使い方

1. `songs/<曲名>/sources.toml` に URL を書く

   ```toml
   [[sources]]
   name = "original"
   url = "https://www.youtube.com/watch?v=..."
   ```

2. ダウンロードする

   ```sh
   uv run scripts/download.py diamond-happy            # m4a（無変換）
   uv run scripts/download.py diamond-happy -f wav     # wav に変換
   uv run scripts/download.py diamond-happy --force    # 取得済みでも再取得
   ```

   音源は `songs/<曲名>/media/<name>.<拡張子>` に保存される。

## 構成

```
scripts/download.py        ダウンロードスクリプト
songs/<曲名>/
  sources.toml             ダウンロード対象の URL
  notes.md                 練習メモ
  chords.md                コード譜
  media/                   ダウンロードした音源（Git 追跡外）
```

## 曲を追加する

`songs/` の下にディレクトリを作り、`sources.toml` を置く。
