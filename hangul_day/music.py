"""한글날 영상용 임시 배경음악(30초, 96 BPM, D 장조 5음계)을 합성한다.

Suno로 만든 곡이 준비되기 전까지 쓰는 국악 퓨전풍 트랙이다.
가야금(카플러스-스트롱 현 합성 + 농현), 장구(덩·덕·쿵), 대금풍 관악기, 현악 패드,
북·심벌 효과음을 영상의 장면 전환 시점에 맞춰 배치했다.

    python3 music.py                 # output/music_placeholder.wav
"""
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
DUR = 30.0
BEAT = 60 / 96
S16 = BEAT / 4
S8 = BEAT / 2
BAR = BEAT * 4
TAIL = 4.0
OUT = Path(__file__).resolve().parent / "output" / "music_placeholder.wav"

rng = np.random.default_rng(1446)
NOTE_IDX = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}


def hz(name: str) -> float:
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE_IDX[pitch] + 12 * (octave - 4)) / 12)


def tt(n: int) -> np.ndarray:
    return np.arange(n) / SR


# ---------------------------------------------------------------- 필터
def lowpass(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "low", fs=SR, output="sos"), x)


def highpass(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "high", fs=SR, output="sos"), x)


def bandpass(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


# ---------------------------------------------------------------- 믹서
# 악기군별 음량. 각 악기군의 K-가중 라우드니스(BS.1770)를 재서 목표값에 맞춘 값이다
# (python3 music.py --stems 로 다시 잴 수 있다).
STEM_GAIN = {
    "gayageum": 0.74, "pad": 0.53, "bass": 0.28, "drums": 0.35,
    "fx": 0.41, "bells": 0.50, "flute": 0.68,
}
STEM_TARGET = {  # LUFS
    "gayageum": -20, "pad": -25, "bass": -25, "drums": -22,
    "fx": -27, "bells": -27, "flute": -21,
}


class Mixer:
    def __init__(self):
        n = int((DUR + TAIL) * SR)
        self.stems = {k: np.zeros((n, 2)) for k in STEM_GAIN}
        self.send = np.zeros((n, 2))

    def add(self, stem, t, x, gain=1.0, pan=0.0, send=0.0):
        i = int(round(t * SR))
        if x.ndim == 1:
            a = (pan + 1) * np.pi / 4
            x = np.stack([x * np.cos(a), x * np.sin(a)], axis=1) * np.sqrt(2)
        buf = self.stems[stem]
        end = min(i + len(x), len(buf))
        if end <= i:
            return
        seg = x[: end - i] * gain * STEM_GAIN[stem]
        buf[i:end] += seg
        if send:
            self.send[i:end] += seg * send


def k_weight(x):
    """ITU-R BS.1770 K-가중 필터(48 kHz)."""
    x = signal.lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285],
                       [1.0, -1.69065929318241, 0.73248077421585], x, axis=0)
    return signal.lfilter([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], x, axis=0)


def lufs(x):
    """게이트를 적용한 통합 라우드니스(LUFS)."""
    y = k_weight(x)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = np.array([np.sum(np.mean(y[i:i + blk] ** 2, axis=0)) for i in range(0, len(y) - blk, hop)])
    lk = -0.691 + 10 * np.log10(ms + 1e-20)
    ms = ms[lk > -70]
    if not len(ms):
        return -np.inf
    rel = -0.691 + 10 * np.log10(np.mean(ms)) - 10
    ms = ms[-0.691 + 10 * np.log10(ms) > rel]
    return -0.691 + 10 * np.log10(np.mean(ms))


# ---------------------------------------------------------------- 악기
def gayageum(freq, dur=2.6, vel=1.0, bend=0.0, vib=0.0, bright=0.38, seed=0):
    """카플러스-스트롱 현 합성. bend: 시작 음높이(센트, 꺾는 소리), vib: 농현 깊이(센트)."""
    n = int(dur * SR)
    r = np.random.default_rng(seed)
    period = SR / freq
    nd = int(np.floor(period - 0.6))
    d = period - 0.5 - nd
    c = (1 - d) / (1 + d)
    t60 = np.interp(freq, [100, 300, 1000], [3.4, 2.4, 1.1])
    g = 10 ** (-3 / (t60 * freq))
    exc = r.uniform(-1, 1, nd)
    exc = signal.lfilter([bright], [1, -(1 - bright)], exc)
    exc -= np.roll(exc, max(1, int(nd * 0.13)))  # 뜯는 위치 → 비음 섞인 음색
    x = np.zeros(n)
    x[:nd] = exc
    a = np.zeros(nd + 3)
    a[0], a[1] = 1.0, c
    a[nd] -= 0.5 * g * c
    a[nd + 1] -= 0.5 * g * (1 + c)
    a[nd + 2] -= 0.5 * g
    y = signal.lfilter([1.0, c], a, x)
    if bend or vib:
        tm = tt(n + SR)
        cents = bend * np.exp(-tm / 0.05)
        cents += vib * np.sin(2 * np.pi * 5.3 * tm) * np.clip((tm - 0.22) / 0.35, 0, 1)
        rate = 2 ** (cents / 1200)
        pos = np.cumsum(rate) - rate[0]
        pos = pos[pos < n - 2]
        i = pos.astype(int)
        f = pos - i
        y = y[i] * (1 - f) + y[i + 1] * f
    # 손가락으로 뜯는 부드러운 어택, 몸통 울림, 날카로운 고역 정리
    y *= 1 - np.exp(-tt(len(y)) / 0.0015)
    y = 0.8 * y + 0.35 * bandpass(y, 180, 420) + 0.15 * bandpass(y, 900, 1600)
    y = lowpass(y, 7500)
    y = y / (np.max(np.abs(y)) + 1e-9)
    return vel * y * 0.6


def bell(freq, dur=2.2, vel=1.0, ratio=3.5, index=1.6):
    tm = tt(int(dur * SR))
    mod = index * np.exp(-tm * 5) * np.sin(2 * np.pi * freq * ratio * tm)
    y = np.sin(2 * np.pi * freq * tm + mod) * np.exp(-tm * 2.6)
    y += 0.25 * np.sin(2 * np.pi * freq * 2.76 * tm) * np.exp(-tm * 6)
    return vel * y * (1 - np.exp(-tm * 900)) * 0.3


def pad(notes, dur, attack=0.6, release=1.2, cutoff=1900, vel=1.0):
    n = int((dur + release) * SR)
    tm = tt(n)
    out = np.zeros((n, 2))
    for k, name in enumerate(notes):
        f0 = hz(name)
        for v, det in enumerate((-8, 0, 8)):
            f = f0 * 2 ** (det / 1200)
            ph = rng.uniform(0, 2 * np.pi)
            y = np.zeros(n)
            for h in range(1, 40):
                if h * f > cutoff * 2.2:
                    break
                y += np.sin(2 * np.pi * h * f * tm + ph * h) / h
            pan = np.clip((v - 1) * 0.55 + (k - len(notes) / 2) * 0.08, -0.9, 0.9)
            a = (pan + 1) * np.pi / 4
            out[:, 0] += y * np.cos(a)
            out[:, 1] += y * np.sin(a)
    out = signal.sosfilt(signal.butter(2, cutoff, "low", fs=SR, output="sos"), out, axis=0)
    env = np.clip(tm / attack, 0, 1) ** 2
    env *= np.clip((dur + release - tm) / release, 0, 1) ** 1.5
    env *= 1 + 0.06 * np.sin(2 * np.pi * 0.35 * tm)
    return vel * out * env[:, None] / (len(notes) * 3) * 0.55


def bass(freq, dur, vel=1.0):
    tm = tt(int((dur + 0.08) * SR))
    y = np.sin(2 * np.pi * freq * tm) + 0.25 * np.sin(4 * np.pi * freq * tm)
    env = np.minimum(np.clip(tm / 0.006, 0, 1), np.clip((dur + 0.08 - tm) / 0.08, 0, 1))
    env *= 0.75 + 0.25 * np.exp(-tm * 6)
    return vel * np.tanh(1.4 * y) * env * 0.42


def deok(vel=1.0):
    """장구 채편(높은 '덕')."""
    tm = tt(int(0.3 * SR))
    noise = bandpass(rng.uniform(-1, 1, len(tm)), 1400, 5200) * np.exp(-tm * 55)
    f = 430 + 240 * np.exp(-tm * 60)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm * 30)
    return vel * (0.75 * noise + 0.55 * tone) * 0.55


def kung(vel=1.0):
    """장구 궁편(낮은 '쿵')."""
    tm = tt(int(0.7 * SR))
    f = 92 + 70 * np.exp(-tm * 22)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm * 6.5)
    thump = lowpass(rng.uniform(-1, 1, len(tm)), 380) * np.exp(-tm * 38)
    return vel * (tone + 0.9 * thump) * 0.62


def buk(vel=1.0):
    """큰북: 장면이 바뀌는 큰 박자."""
    tm = tt(int(2.0 * SR))
    f = 52 + 75 * np.exp(-tm * 16)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm * 2.6)
    skin = bandpass(rng.uniform(-1, 1, len(tm)), 120, 700) * np.exp(-tm * 9)
    return vel * np.tanh(1.5 * (tone + 0.45 * skin)) * 0.75


def kick(vel=1.0):
    tm = tt(int(0.45 * SR))
    f = 46 + 110 * np.exp(-tm * 38)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm * 9)
    return vel * np.tanh(1.8 * y) * 0.6


def crash(vel=1.0, dur=2.6):
    tm = tt(int(dur * SR))
    y = highpass(rng.uniform(-1, 1, len(tm)), 4200) * np.exp(-tm * 2.0)
    for f in (3150, 4870, 6230, 8110):
        y += 0.06 * np.sin(2 * np.pi * f * tm + rng.uniform(0, 6)) * np.exp(-tm * 3)
    y = lowpass(y, 11000)
    return vel * y * (1 - np.exp(-tm * 400)) * 0.32


def swell(dur, vel=1.0):
    """역재생 심벌 같은 상승음(장면 전환 직전)."""
    n = int(dur * SR)
    tm = tt(n)
    u = tm / dur
    hi = highpass(rng.uniform(-1, 1, n), 3000)
    lo = bandpass(rng.uniform(-1, 1, n), 500, 2500)
    y = (lo * (1 - u) + hi * u) * u ** 2.2
    return vel * y * 0.35


def whoosh(dur, vel=1.0):
    n = int(dur * SR)
    tm = tt(n)
    u = tm / dur
    lo = bandpass(rng.uniform(-1, 1, n), 250, 900)
    hi = bandpass(rng.uniform(-1, 1, n), 1500, 4500)
    env = np.sin(np.pi * u) ** 1.6
    y = (lo * (1 - u) + hi * u) * env
    return vel * np.stack([y * (1 - 0.6 * u), y * (0.4 + 0.6 * u)], axis=1) * 0.5


def flute(phrase, vel=1.0):
    """대금풍 선율: [(시작 박, 길이 박, 음이름)]. 이음줄로 이어 부르고 음 머리를 살짝 끌어 올린다."""
    t0 = phrase[0][0] * BEAT
    t1 = (phrase[-1][0] + phrase[-1][1]) * BEAT
    n = int((t1 - t0 + 0.6) * SR)
    tm = tt(n)
    f = np.zeros(n)
    cents = np.zeros(n)
    for k, (b, length, name) in enumerate(phrase):
        s = int((b * BEAT - t0) * SR)
        f[s:] = hz(name)
        local = tm[s:] - tm[s]
        cents[s:] = -45 * np.exp(-local / 0.07)  # 음 머리 끌어올림
        cents[s:] += 22 * np.sin(2 * np.pi * 5.0 * local) * np.clip((local - 0.28) / 0.4, 0, 1)
    f = signal.sosfilt(signal.butter(1, 18, "low", fs=SR, output="sos"), f)  # 음 사이를 매끄럽게
    f[: int(0.02 * SR)] = hz(phrase[0][2])
    ph = 2 * np.pi * np.cumsum(f * 2 ** (cents / 1200)) / SR
    tone = np.sin(ph) + 0.38 * np.sin(2 * ph) + 0.16 * np.sin(3 * ph) + 0.07 * np.sin(4 * ph)
    tone = np.tanh(1.3 * tone)  # 청 울림 같은 거친 배음
    breath = bandpass(rng.uniform(-1, 1, n), 1200, 6000) * 0.07
    end = t1 - t0
    env = np.clip(tm / 0.09, 0, 1) * np.clip((end + 0.25 - tm) / 0.35, 0, 1)
    env *= 0.85 + 0.15 * np.sin(np.pi * np.clip(tm / end, 0, 1))
    return vel * (tone + breath) * env * 0.16


# ---------------------------------------------------------------- 곡 구성
def build():
    mx = Mixer()
    stem = {"v": "fx"}

    def put(t, x, g=1.0, pan=0.0, send=0.3, to=None):
        mx.add(to or stem["v"], t, x, g, pan, send)

    def pluck(t, name, vel=0.8, pan=-0.15, send=0.35, **kw):
        put(t, gayageum(hz(name), vel=vel, seed=int(t * 1000), **kw), 1.0, pan, send, to="gayageum")

    def chime(t, name, vel=0.6, pan=0.3, send=0.6):
        put(t, bell(hz(name), vel=vel), 1.0, pan, send, to="bells")

    # 화성 진행 (마디 = 2.5초)
    chords = [
        (0.0, 5.0, ["D3", "A3", "E4", "F#4"]),            # 1–2마디  D(add9)
        (5.0, 2.5, ["B2", "F#3", "A3", "D4"]),            # 3       Bm7
        (7.5, 1.25, ["G2", "D3", "B3", "D4"]),            # 4       G
        (8.75, 1.25, ["A2", "E3", "A3", "C#4"]),          #         A
        (10.0, 1.25, ["B2", "F#3", "B3", "D4"]),          # 5       Bm
        (11.25, 1.25, ["A2", "E3", "A3", "C#4"]),         #         A
        (12.5, 2.5, ["D3", "A3", "D4", "F#4", "A4"]),     # 6       D (새벽)
        (15.0, 1.25, ["D3", "A3", "D4", "F#4"]),          # 7       D
        (16.25, 1.25, ["A2", "E3", "A3", "C#4"]),         #         A
        (17.5, 1.25, ["B2", "F#3", "B3", "D4"]),          # 8       Bm
        (18.75, 1.25, ["G2", "D3", "B3", "D4"]),          #         G
        (20.0, 1.25, ["G2", "D3", "B3", "F#4"]),          # 9       Gmaj7
        (21.25, 1.25, ["A2", "E3", "A3", "C#4"]),         #         A
        (22.5, 1.25, ["E3", "B3", "D4", "G4"]),           # 10      Em7
        (23.75, 1.25, ["A2", "E3", "G3", "C#4"]),         #         A7
        (25.0, 1.25, ["D3", "A3", "D4", "F#4", "A4"]),    # 11      D (타이틀)
        (26.25, 1.25, ["G2", "D3", "B3", "D4", "G4"]),    #         G (도장)
        (27.5, 2.5, ["D3", "A3", "D4", "F#4", "A4", "E5"]),  # 12  D(add9) 마무리
    ]
    for start, length, notes in chords:
        vel = 0.75 if start < 5 else 1.0
        att = 1.6 if start == 0 else 0.25
        put(start, pad(notes, length, attack=att, release=1.4 if start >= 27.5 else 0.5, vel=vel), 0.9, 0, 0.45, to="pad")

    # 베이스(3–8, 11마디). 8분음표로 근음을 짚는다.
    roots = {5.0: "B1", 7.5: "G1", 8.75: "A1", 10.0: "B1", 11.25: "A1", 12.5: "D2", 15.0: "D2", 16.25: "A1",
             17.5: "B1", 18.75: "G1", 25.0: "D2", 26.25: "G1"}
    for start, name in roots.items():
        span = 1.25 if start not in (5.0, 12.5) else 2.5
        steps = int(round(span / S8))
        for k in range(steps):
            accent = 1.0 if k % 2 == 0 else 0.7
            put(start + k * S8, bass(hz(name), S8 * 0.9, accent), 1.0, 0, 0, to="bass")
    put(27.5, bass(hz("D2"), 2.3, 1.0), 1.0, 0, 0, to="bass")

    # 장구 장단(4/4 퓨전): (16분 칸, 소리, 세기)
    groove = [(0, "deong", 1.0), (3, "deok", 0.45), (4, "deok", 0.85), (6, "kung", 0.8), (8, "kung", 0.65),
              (10, "deok", 0.55), (11, "deok", 0.35), (12, "deok", 0.9), (14, "kung", 0.6), (15, "deok", 0.4)]

    def janggu_bar(t0, gain=1.0, light=False):
        for step, kind, v in groove:
            if light and kind == "deok" and v < 0.5:
                continue
            t = t0 + step * S16
            if kind in ("deong", "kung"):
                put(t, kung(v), gain, -0.2, 0.12, to="drums")
            if kind in ("deong", "deok"):
                put(t, deok(v), gain, 0.25, 0.12, to="drums")

    def roll(t0, t1, gain=0.8, crescendo=True):
        """'더러러러' 굴리기."""
        n = int((t1 - t0) / (S16 / 2))
        for k in range(n):
            u = k / max(1, n - 1)
            put(t0 + k * S16 / 2, deok(0.25 + 0.6 * (u if crescendo else 1 - u)), gain, 0.25, 0.15, to="drums")

    for bar_t in (5.0, 7.5):
        janggu_bar(bar_t, 0.8, light=True)
    for bar_t in (10.0, 15.0, 17.5, 25.0):
        janggu_bar(bar_t, 1.0)
    janggu_bar(12.5, 0.6, light=True)
    for b in range(8):  # 7–8마디 킥
        put(15.0 + b * BEAT, kick(0.9 if b % 2 == 0 else 0.6), 1.0, 0, 0, to="drums")
    for b in range(4):
        put(25.0 + b * BEAT, kick(0.85 if b % 2 == 0 else 0.55), 1.0, 0, 0, to="drums")

    # ---- 1마디: ㆍ ㅡ ㅣ
    chime(0.625, "A5", 0.75, -0.35)
    pluck(0.625, "A4", 0.8, pan=-0.35)
    pluck(1.25, "D4", 0.85, pan=0.0, vib=30, dur=3.0)
    pluck(1.875, "E5", 0.8, pan=0.35, bend=-200)  # 아래에서 밀어 올리는 소리(사람, 일어섬)
    chime(1.875, "E6", 0.4, 0.35)

    # ---- 2마디: 모음 열 개가 차례로
    run = ["D4", "E4", "F#4", "A4", "B4", "D5", "E5", "F#5", "A5", "B5"]
    for i, name in enumerate(run):
        pluck(2.5 + i * S16, name, 0.5 + 0.035 * i, pan=-0.5 + i * 0.1)
        if i >= 6:
            chime(2.5 + i * S16 + 0.16, name, 0.25, 0.5 - i * 0.05)
    pluck(3.75 + 0.3, "D5", 0.55, vib=35, dur=3.0)
    roll(4.53, 5.0, 0.55)

    # ---- 3마디: 자음 다섯 (Bm7 분산화음)
    for i, name in enumerate(["B3", "D4", "F#4", "A4", "B4"]):
        pluck(5.0 + i * S8, name, 0.8, pan=-0.4 + i * 0.2, bend=-80 if i == 4 else 0, vib=25 if i == 4 else 0)
    pluck(6.875, "A4", 0.5)
    pluck(7.1875, "F#4", 0.45, vib=20)

    # ---- 4마디: 가획 (16분음표 상행)
    for i, name in enumerate(["B4", "D5", "E5", "A5", "B5"]):
        pluck(7.5 + i * S16, name, 0.7, pan=-0.4 + i * 0.2)
        chime(7.5 + i * S16, name, 0.22, 0.4)
    for i, name in enumerate(["E5", "A5", "B5"]):
        pluck(8.75 + i * S16, name, 0.75, pan=-0.2 + i * 0.2)
        chime(8.75 + i * S16, name.replace("5", "6"), 0.22, 0.4)
    roll(9.4, 10.0, 0.6)

    # ---- 5마디: 자모가 날아와 '한글'로
    put(10.12, whoosh(1.25, 0.9), 1.0, 0, 0.3)
    pluck(10.0, "B3", 0.6)
    pluck(10.3125, "F#4", 0.5)
    for i, name in enumerate(["A3", "E4", "A4", "C#5"]):  # 착지 순간의 화음
        pluck(11.25 + i * 0.012, name, 0.6, pan=-0.3 + 0.2 * i, vib=20)
    put(11.25, kung(0.9), 1.0, -0.2, 0.2, to="drums")
    put(11.25, deok(0.8), 1.0, 0.25, 0.2, to="drums")
    put(11.25, crash(0.25, 1.5), 1.0, 0.3, 0.2)
    put(11.0, swell(1.5, 0.9), 1.0, 0, 0.2)
    roll(11.9, 12.5, 0.8)

    # ---- 6마디: 새벽빛 (가장 큰 박)
    put(12.5, buk(1.0), 1.0, 0, 0.2, to="drums")
    put(12.5, crash(0.9), 1.0, 0, 0.25)
    for i, name in enumerate(["B5", "A5", "F#5", "E5", "D5", "B4", "A4", "F#4", "E4", "D4"]):
        pluck(12.5 + i * S16 / 2, name, 0.65 - i * 0.02, pan=0.4 - i * 0.08)
    for i, name in enumerate(["D6", "F#6", "A6"]):
        chime(12.5 + i * 0.03, name, 0.4, -0.4 + 0.4 * i)
    for i, name in enumerate(["A5", "B5", "D6", "E6"]):  # 訓民正音
        chime(13.12 + i * 0.07, name, 0.32, -0.3 + 0.2 * i)
    for k, name in enumerate(["D4", "A4", "F#4", "A4", "D5", "A4", "E5", "A4"]):
        pluck(13.75 + k * S8, name, 0.4, pan=0.1 * ((k % 3) - 1))
    put(14.0, swell(1.0, 0.8), 1.0, 0, 0.2)

    # ---- 7–8마디: 11,172
    put(15.0, crash(0.5), 1.0, -0.2, 0.2)
    count_notes = ["D4", "F#4", "A4", "B4", "D5", "E5", "F#5", "A5", "B5", "D6"]
    steps = int((17.35 - 15.5) / S16)
    for k in range(steps):
        u = k / steps
        name = count_notes[min(len(count_notes) - 1, int(u * len(count_notes)) + (k % 2))]
        pluck(15.5 + k * S16, name, 0.35 + 0.35 * u, pan=0.3 * np.sin(k), send=0.25)
    put(17.5, crash(0.7), 1.0, 0.2, 0.2)
    put(17.5, buk(0.7), 1.0, 0, 0.15, to="drums")
    for i, name in enumerate(["B3", "F#4", "B4", "D5"]):
        pluck(17.5 + i * 0.01, name, 0.7, pan=-0.3 + 0.2 * i, vib=25)
    word_notes = ["D6", "E6", "F#6", "A6", "B6", "A6", "F#6", "E6", "D6", "B5"]
    for k, name in enumerate(word_notes):
        chime(18.12 + k * S16, name, 0.3, -0.6 + 0.13 * k)
        pluck(18.12 + k * S16, name.replace("6", "5"), 0.35, pan=0.6 - 0.13 * k, send=0.3)
    for i, name in enumerate(["B5", "A5", "F#5", "E5", "D5", "B4", "A4", "F#4"]):  # 글자 벽이 무너짐
        pluck(19.65 + i * 0.045, name, 0.45 - i * 0.03, pan=-0.3 + i * 0.08)

    # ---- 9–10마디: 『훈민정음』 서문 (드럼 빠짐, 대금 선율)
    phrase = [(32, 1, "B4"), (33, 1.5, "D5"), (34.5, 0.5, "E5"), (35, 2, "F#5"),
              (37, 0.5, "E5"), (37.5, 0.5, "D5"), (38, 2, "E5")]
    put(32 * BEAT, flute(phrase, 1.0), 1.0, 0.15, 0.5, to="flute")
    for k, name in enumerate(["G3", "D4", "B4", "D4", "A3", "E4", "C#5", "E4",
                              "E3", "B3", "G4", "B3", "A3", "E4", "G4", "E4"]):
        pluck(20.0 + k * S8, name, 0.32, pan=-0.35, send=0.4)
    chime(22.5, "F#6", 0.3, 0.3)
    chime(22.8, "D6", 0.3, 0.4)
    roll(24.4, 25.0, 0.75)
    put(23.6, swell(1.4, 1.0), 1.0, 0, 0.2)

    # ---- 11–12마디: 제580돌 한글날
    put(25.0, buk(1.0), 1.0, 0, 0.2, to="drums")
    put(25.0, crash(1.0), 1.0, 0, 0.25)
    for i, name in enumerate(["D5", "F#5", "A5"]):  # 한 · 글 · 날
        pluck(25.12 + i * 0.12, name, 0.8, pan=-0.3 + 0.3 * i)
        chime(25.12 + i * 0.12, name.replace("5", "6"), 0.3, -0.3 + 0.3 * i)
    chime(25.55, "E6", 0.3, 0.0)
    hook = [(40, 0.5, "D5"), (40.5, 0.5, "E5"), (41, 1, "F#5"), (42, 1, "A5"), (43, 0.5, "B5"), (43.5, 0.5, "A5"), (44, 3.5, "D6")]
    put(40 * BEAT, flute(hook, 0.8), 1.0, 0.2, 0.45, to="flute")
    put(26.25, buk(0.9), 1.0, 0, 0.2, to="drums")
    put(26.25, kung(1.0), 1.0, -0.2, 0.15, to="drums")
    put(26.25, deok(0.9), 1.0, 0.25, 0.15, to="drums")
    for i, name in enumerate(["G3", "D4", "G4", "B4"]):
        pluck(26.25 + i * 0.012, name, 0.7, pan=-0.3 + 0.2 * i)
    put(27.5, crash(0.8, 3.0), 1.0, 0, 0.3)
    put(27.5, kung(0.9), 1.0, -0.2, 0.2, to="drums")
    put(27.5, deok(0.8), 1.0, 0.25, 0.2, to="drums")
    for i, name in enumerate(["D3", "A3", "D4", "F#4", "A4", "D5"]):
        pluck(27.5 + i * 0.02, name, 0.65, pan=-0.5 + 0.2 * i, vib=30 if i == 5 else 0, dur=3.2)
    for i, name in enumerate(["A5", "B5", "D6", "E6", "F#6", "A6"]):  # 빛 줄기
        chime(28.0 + i * 0.09, name, 0.22, -0.5 + 0.2 * i)
    return mx


def reverb_ir(seconds=2.4):
    n = int(seconds * SR)
    tm = tt(n)
    ir = rng.standard_normal((n, 2)) * np.exp(-tm * 6.9 / seconds)[:, None]
    ir = signal.sosfilt(signal.butter(1, 5200, "low", fs=SR, output="sos"), ir, axis=0)
    ir[: int(0.018 * SR)] = 0
    return ir / np.sqrt(np.sum(ir ** 2, axis=0))


def main() -> int:
    mx = build()
    if "--stems" in sys.argv:
        # 악기군별 라우드니스를 재고 목표값에 맞는 STEM_GAIN을 제안한다
        for k, buf in mx.stems.items():
            lk = lufs(buf)
            gain = STEM_GAIN[k] * 10 ** ((STEM_TARGET[k] - lk) / 20)
            print(f"{k:9s} {lk:6.1f} LUFS  target {STEM_TARGET[k]}  -> gain {gain:.3f}")
        return 0
    ir = reverb_ir()
    wet = np.stack([signal.fftconvolve(mx.send[:, ch], ir[:, ch])[: len(mx.send)] for ch in range(2)], axis=1)
    mix = sum(mx.stems.values()) + 0.9 * wet
    mix = highpass(mix.T, 32).T
    n = int(DUR * SR)
    mix = mix[:n]
    fade = np.ones(n)
    fo = int(1.2 * SR)
    fade[-fo:] = np.linspace(1, 0, fo) ** 2
    mix *= fade[:, None]
    # -14 LUFS로 맞추고, 넘치는 봉우리는 부드럽게 눌러 -1 dBFS 아래로
    mix *= 10 ** ((-14 - lufs(mix)) / 20)
    ceiling = 10 ** (-1.6 / 20)  # 샘플 사이 봉우리(true peak)까지 -1 dB 아래로
    over = np.abs(mix) > 0.7 * ceiling
    knee = 0.7 * ceiling
    mix[over] = np.sign(mix[over]) * (knee + (ceiling - knee) * np.tanh((np.abs(mix[over]) - knee) / (ceiling - knee)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(OUT, SR, (mix * 32767).astype(np.int16))
    print(OUT, f"{n / SR:.1f}s, {lufs(mix):.1f} LUFS, peak {20 * np.log10(np.max(np.abs(mix))):.1f} dBFS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
