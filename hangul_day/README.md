# 제580돌 한글날 홍보 모션그래픽 (30초)

2026년 10월 9일 한글날(훈민정음 반포 580돌)을 알리는 30초짜리 모션그래픽 영상입니다.

- 완성 영상: [`output/hangul_day_2026.mp4`](output/hangul_day_2026.mp4) — 1920×1080, 60fps, H.264 + AAC, 약 17MB
- 썸네일: [`output/hangul_day_2026_thumbnail.jpg`](output/hangul_day_2026_thumbnail.jpg)
- 배경음악: Suno로 만든 「Spring Festival Plucks」 (아래 「음악」 참고)

## 구성 (96 BPM, 1마디 = 2.5초)

| 시간 | 장면 | 화면 문구 |
|---|---|---|
| 0–5초 | 천지인: 점(ㆍ)·가로획(ㅡ)·세로획(ㅣ)이 나타나고, 하늘의 점이 땅·사람의 획에 붙으며 모음 열 개가 태어남 | 하늘 · 땅 · 사람을 본떠 모음을 만들고, |
| 5–10초 | 발음 기관을 본뜬 기본 자음 ㄱㄴㅁㅅㅇ → 획을 더해 ㅋ ㄷㅌ ㅂㅍ ㅈㅊ ㅎ (가획) | 소리 내는 모양을 본떠 자음을 만들었습니다 / 소리가 세지면 획을 더했습니다 |
| 10–15초 | 자모가 날아와 ‘한글’로 모이고, 새벽빛이 번지며 밤에서 한지로 전환 | 자음과 모음이 모여 한 글자를 이룹니다 / 訓民正音 · 백성을 가르치는 바른 소리 |
| 15–20초 | 11,172자의 글자 벽, 숫자 세기, 사랑·하늘·노래 같은 낱말이 떠오름 | 스물네 개의 자모로 11,172개의 글자를 만들 수 있습니다 |
| 20–25초 | 『훈민정음』 서문 | 사람마다 하여금 쉬이 익혀 날로 씀에 편안케 하고자 할 따름이니라 |
| 25–30초 | 타이틀, 도장, 오방색 자모 장식 | 제580돌 한글날 · 2026. 10. 9. · 백성을 위한 글자에서, 세계가 배우는 글자로 |

모음의 색은 삼태극의 천지인 색(하늘=빨강, 땅=파랑, 사람=노랑)을 따랐고,
가획 장면에서 새로 더한 획은 금색으로 표시했습니다.

## 음악

영상에는 아래 프롬프트로 Suno에서 만든 「Spring Festival Plucks」 두 버전 중 첫 번째 곡이 들어 있습니다.

- 곡 분석: 97.0 BPM으로 곡 전체에서 템포가 일정(박 위치 흔들림 ±4ms). 두 번째 버전(98.2 BPM)은
  템포가 조금씩 흔들리고 장면 흐름과도 덜 맞았습니다.
- 템포: 음높이는 그대로 두고 0.9896배(97 → 96 BPM)로 1% 늦춰서, 곡의 마디가 장면 전환(2.5초 간격)과 겹칩니다.
- 구간: 곡의 2.95초(두 번째 마디)부터 30초. 조용한 도입부가 밤 장면에 깔리고, 곡에 베이스가 들어오는
  지점이 ‘한글날’ 타이틀(25초)과 맞물리고, 가장 큰 박은 마지막 마디가 시작하는 27.5초에 옵니다.
  마지막 1.7초는 페이드아웃, 음량은 -14 LUFS.

Suno 곡을 넣기 전에는 `music.py`로 합성한 국악 퓨전풍 임시 음악(가야금·장구·대금풍 선율, 96 BPM)을 썼고,
지금도 그대로 다시 만들 수 있습니다.

### Suno에서 곡 만들기 (Custom 모드)

**Title**

```
한글, 빛이 되다
```

**Style of Music**

```
Korean traditional fusion, gayageum plucks, daegeum flute, janggu percussion, warm cinematic strings, uplifting, hopeful, festive, bright, 96 BPM, D major pentatonic, instrumental, short promo
```

**Lyrics** (Instrumental을 켜고 구조 태그만 넣기)

```
[Intro: soft gayageum harmonics, warm strings]
[Build: janggu rhythm enters, rising gayageum arpeggios]
[Drop: full ensemble, festive and bright]
[Break: solo daegeum melody, calm and emotional]
[Final Chorus: triumphant, full ensemble]
[Big Finish]
[End]
```

**Exclude Styles**

```
vocals, EDM, heavy metal, distortion
```

화면에 글자가 많아서 노래보다 연주곡이 잘 어울립니다. 생성된 곡에서 30초를 고를 때는
조용히 시작해 점점 커지는 구간을 고르면 장면(밤 → 새벽 → 타이틀) 흐름과 잘 맞습니다.

### 영상의 음악 바꾸기

Suno에서 받은 두 곡을 함께 넣으면 자동으로 비교해서 고릅니다.

```bash
python3 add_music.py 곡1.mp3 곡2.mp3 --auto      # 곡·구간·템포 자동 선택
python3 add_music.py suno_song.mp3 --start 42.5  # 직접 지정: 42.5초 지점부터 30초
```

`--auto`는 `fit_music.py`로 곡의 템포와 마디 첫 박을 찾고, 96 BPM에 가까우면(±7%) 음높이를 유지한 채
속도를 맞춰 곡의 마디가 장면 전환(2.5초 간격)과 겹치게 합니다. 그다음 장면별 흐름(조용한 시작 →
12.5초 새벽빛 → 15~20초 절정 → 20~25초 서문 → 25초 타이틀)과 에너지 모양이 가장 닮은 30초를 고릅니다.

`output/hangul_day_2026_suno.mp4`가 만들어집니다. 영상은 다시 렌더링하지 않고 그대로 복사하며,
음악은 -14 LUFS로 맞추고 마지막 1.7초를 페이드아웃합니다(ffmpeg 필요). 지금 영상과 같은 설정은 다음과 같습니다.

```bash
python3 add_music.py Spring_Festival_Plucks.mp4 --start 2.9469 --tempo 0.989635
```

## 직접 렌더링하기

필요한 것: Python 3.10+, ffmpeg, `pip install playwright numpy scipy pillow`, Chromium
(`python3 -m playwright install chromium` 또는 `CHROMIUM_PATH` 환경 변수로 지정).

```bash
python3 fetch_fonts.py          # Google Fonts에서 Noto Serif KR · Noto Sans KR 받기 (fonts/)
python3 music.py                # 임시 음악 → output/music_placeholder.wav
python3 render.py --audio output/music_placeholder.wav --out output/hangul_day_2026.mp4
python3 add_music.py Spring_Festival_Plucks.mp4 --start 2.9469 --tempo 0.989635   # Suno 곡 입히기

python3 render.py --still 12.8 27.5   # 특정 시점 정지 화면(PNG)
python3 render.py --sheet             # 2초 간격 콘택트 시트
```

브라우저에서 바로 보려면 `hangul_day` 폴더에서 `python3 -m http.server` 를 실행한 뒤
`http://localhost:8000/scene/index.html?play` 를 열면 됩니다(`#12.5` 처럼 시간을 붙이면 그 장면만 표시).

## 파일

| 파일 | 내용 |
|---|---|
| `scene/main.js` | 애니메이션 전체. `renderFrame(t)`가 t초의 화면을 캔버스에 그림 |
| `scene/index.html` | 캔버스와 폰트 정의 |
| `render.py` | 헤드리스 Chromium으로 프레임을 받아 ffmpeg로 인코딩 |
| `music.py` | 임시 배경음악 합성(Suno 곡을 넣기 전 버전) |
| `add_music.py` | 음악만 교체 |
| `fit_music.py` | 곡의 템포·마디 분석, 영상에 맞는 30초 구간 고르기 |
| `fetch_fonts.py` | 폰트 내려받기 |

폰트: Noto Serif KR, Noto Sans KR (SIL Open Font License 1.1, Google Fonts).
