# -*- coding: utf-8 -*-
import re, base64, subprocess, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z12  = os.path.join(REPO, 'movie-z12.html')
BODY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rd-body.html')
OUT  = os.path.join(REPO, 'movie-rd.html')
NARR = sys.argv[1] if len(sys.argv) > 1 else ''   # 本編ナレーションMP3（未指定なら無音）

z = open(Z12, encoding='utf-8').read()
b = open(BODY, encoding='utf-8').read()

def block(kind, part):
    m = re.search(r'(?:/\*|<!--) ===== NEURON-%s:%s:BEGIN ===== (?:\*/|-->)(.*?)(?:/\*|<!--) ===== NEURON-%s:%s:END ===== (?:\*/|-->)'
                  % (kind, part, kind, part), z, re.S)
    if not m: raise SystemExit('missing block %s:%s' % (kind, part))
    return m.group(0)        # 目印ごとそのまま持ってくる

base_css = z[z.find('<style>')+7 : z.find('</style>')]
# 念のため、z12側のNEURONスタイルは base_css に含まれたまま使う
nlogo = re.search(r'class="nlogo" src="(data:[^"]+)"', z).group(1)
player_js = re.findall(r'<script>(.*?)</script>', z, re.S)[-1]

parts = re.split(r'@@CSS@@|@@MARKUP@@|@@SCRIPT@@', b)
if len(parts) != 4: raise SystemExit('body markers broken: %d' % len(parts))
_, extra_css, markup, timeline = parts
markup = markup.replace('@@NLOGO@@', nlogo)

# 本編の長さ（タイムラインの S から合計する）
secs = [float(x) for x in re.findall(r'd:\s*([0-9.]+)', timeline)]
total = round(sum(secs), 3)

tmp = '/tmp/_rd_body_audio.mp3'
if NARR:
    subprocess.run(['ffmpeg','-y','-i',NARR,'-ar','48000','-b:a','96k',tmp], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    subprocess.run(['ffmpeg','-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono',
                    '-t',str(total),'-b:a','96k',tmp], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
mp3 = base64.b64encode(open(tmp,'rb').read()).decode('ascii')

html = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>エージェント検索デモ 研究開発部門（HTML版）</title>
<style>
%s
%s
</style></head>
<body>
<div id="app"><div id="viewport">
  <div id="stage">
%s
    <div id="cap"></div><div id="mode"></div>
    <div class="disc">※ 登場する企業・製品・文書・人名はすべて架空です</div>
    <div class="brandmark">Brains Technology</div>
    <div id="prog" style="position:absolute;left:0;bottom:0;height:5px;background:var(--teal);width:0;z-index:50;opacity:.85;"></div>
  </div>
%s
%s
</div></div>
<audio id="abgm" preload="auto"></audio>
<div id="ctrl">
  <button id="bPlay">&#9654; 再生</button>
  <button id="bPause">&#8214; 一時停止</button>
  <button id="bLoop">&#8635; 繰り返し再生</button>
  <button id="bCap">字幕</button>
  <button id="bSnd">&#9834; 音声</button>
  <div id="bar"><div id="barBg"></div><div id="barFill"></div><div id="barKnob"></div></div>
  <div id="tm">0:00 / 0:00</div>
</div>
<div id="hint"><span>&#9654; クリックして再生</span></div>
<script type="text/plain" id="d_bgm">%s</script>
<script>window.__still=true;</script>
<script>%s</script>
%s
%s
<script>%s</script>
</body></html>
""" % (base_css, extra_css, markup,
       block('OPENING','MARKUP'), block('CLOSING','MARKUP'),
       mp3, timeline,
       block('OPENING','SCRIPT'), block('CLOSING','SCRIPT'), player_js)

open(OUT,'w',encoding='utf-8').write(html)
print('wrote', OUT, len(html), 'chars  body=%.1fs' % total, 'narration=' + (NARR or 'SILENT'))
