# movie-rd.html（研究開発部門 ／ Box＋ファイルサーバー編）の作り直し方

- 本編の素材：`_build/rd-body.html`（CSS・シーンのHTML・タイムライン。`@@CSS@@` `@@MARKUP@@` `@@SCRIPT@@` で3つに分かれている）
- 組み立て：`python3 _build/build-rd.py [本編ナレーション.mp3]`
  - `movie-z12.html` からオープニング／クロージングの6ブロックとNeuronロゴを取り出して結合する
  - 引数なしで実行すると、本編の音声は**無音**（長さだけ合わせたMP3）になる
  - ナレーションMP3を渡すと、それを埋め込んで `movie-rd.html` を書き出す
- 本編の長さ：159.2秒（オープニング8秒＋クロージング7秒を足して 2分54秒）

## ナレーション
`_build/narr.json` にシーンごとの「cap（字幕の表示文）」と「read（VOICEVOXに読ませる文）」が入っている。
VOICEVOX 剣崎雌雄（style 21・速度1.0・抑揚0.95）でシーンごとにwavを作り、
各シーンの長さ（d秒）に合わせて先頭に0.6秒の無音を入れてから1本につなぎ、
loudnorm で -16 LUFS、48kHz、MP3 96kbps にして `build-rd.py` に渡す。

## 字幕の時間
`rd-body.html` の `CAPS` 配列（シーンid・開始秒・終了秒・文）。
実際のナレーション音声ができたら、ffmpeg の silencedetect（-38dB, 0.25秒）で
文の切れ目を拾って、この配列の秒数を合わせる。
