"""곡을 분석해 영상 흐름에 가장 잘 맞는 30초 구간을 고른다.

영상은 96 BPM(1마디 = 2.5초)에 맞춰 장면이 바뀐다. 곡의 템포와 마디 첫 박을 찾고,
템포가 96 BPM(또는 그 절반·두 배)에 가까우면 음높이를 유지한 채 살짝 늘이거나 줄여서
곡의 마디가 장면 전환과 겹치게 한다. 그런 다음 장면별 에너지 흐름
(조용한 시작 → 12.5초 새벽 → 15~20초 절정 → 20~25초 잔잔 → 25초 타이틀)과
가장 닮은 구간을 고른다.

    python3 fit_music.py 곡1.mp3 곡2.mp3      # 분석 결과만 출력
"""
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import signal

SR = 22050
HOP = 220            # 약 10ms
VIDEO_BPM = 96.0
VIDEO_BAR = 2.5
DUR = 30.0
ACCENTS = (12.5, 25.0)  # 새벽빛, 타이틀
# 영상 장면별 목표 에너지(0~1), 0.5초 간격
_T = np.arange(0, DUR, 0.5)
TEMPLATE = np.interp(_T, [0, 4.5, 5, 9.5, 10, 12.4, 12.5, 15, 19.9, 20, 24.9, 25, 27.5, 30],
                     [.30, .35, .50, .55, .60, .75, .90, .95, 1.0, .55, .60, .95, .90, .55])
ONSET_LAG = (512 + HOP) / SR  # STFT 창 중심과 차분 때문에 어택이 이만큼 일찍 잡힌다


@dataclass
class Fit:
    path: Path
    duration: float     # 원곡 길이(초)
    bpm: float          # 원곡 템포
    tempo: float        # atempo 배율(>1이면 빨라짐)
    first_bar: float    # 늘인 뒤 첫 마디 시작(초)
    start: float        # 늘인 뒤 사용할 구간 시작(초)
    score: float
    detail: str
    others: list        # 다음 후보들 [(점수, 시작, 설명)]


def load(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def onset_envelopes(x: np.ndarray):
    """전체 대역·저음(킥) 대역의 스펙트럼 플럭스와 저음 에너지(dB), 약 10ms 간격."""
    f, _, Z = signal.stft(x, SR, nperseg=1024, noverlap=1024 - HOP, boundary=None)
    A = np.abs(Z)
    mag = np.log1p(100 * A)
    flux = np.maximum(np.diff(mag, axis=1), 0)
    full = flux.sum(axis=0)
    low = flux[f < 180].sum(axis=0)
    low_db = 10 * np.log10((A[f < 180] ** 2).sum(axis=0)[1:] + 1e-10)
    norm = lambda e: (e - e.mean()) / (e.std() + 1e-9)
    return norm(full), norm(low), low_db


def estimate_tempo(env: np.ndarray) -> float:
    fps = SR / HOP
    ac = signal.fftconvolve(env, env[::-1])[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm = 60 * fps / np.maximum(lags, 1)
    ok = (bpm >= 60) & (bpm <= 200)
    # 사람이 느끼는 템포 대역(90~120 BPM 근처)을 약하게 선호
    prior = np.exp(-0.5 * (np.log2(bpm / 105) / 0.9) ** 2)
    score = np.where(ok, ac * prior, -np.inf)
    k = int(np.argmax(score))
    if 1 <= k < len(ac) - 1:
        a, b, c = ac[k - 1], ac[k], ac[k + 1]
        k = k + 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
    return 60 * fps / k


def beat_grid(full: np.ndarray, low: np.ndarray, low_db: np.ndarray, bpm: float):
    """박 위상과 마디 첫 박 위상(초)을 찾는다.

    4/4에서는 킥이 1·3박에 모두 들어가 킥만으로는 첫 박과 셋째 박이 헷갈린다.
    그래서 구간(베이스가 들어오고 빠지는 곳)이 바뀌는 자리가 마디 첫 박이라는 점도 함께 본다.
    """
    fps = SR / HOP
    period = 60 / bpm * fps
    n = len(full)

    def comb(env, phase, step):
        idx = np.round(np.arange(phase, n, step)).astype(int)
        idx = idx[idx < n]
        return env[idx].mean() if len(idx) else -np.inf

    phases = np.arange(0, period, 0.5)
    beat = phases[int(np.argmax([comb(full, p, period) for p in phases]))]
    kick = np.array([comb(low, beat + j * period, 4 * period) + 0.5 * comb(full, beat + j * period, 4 * period)
                     for j in range(4)])
    nb = int((n - beat) // period)
    beat_db = np.array([low_db[int(beat + i * period):int(beat + (i + 1) * period)].mean() for i in range(nb)])

    def change(j):
        # j번째 박에서 마디가 시작한다면, 마디 경계 앞뒤 두 박씩의 저음 에너지 차이.
        # 구간 전환은 드물지만 크므로 평균 대신 제곱평균(RMS)으로 큰 변화를 살린다.
        d = [beat_db[i:i + 2].mean() - beat_db[i - 2:i].mean() for i in range(j, nb - 1, 4) if i >= 2]
        return float(np.sqrt(np.mean(np.square(d)))) if d else 0.0

    chg = np.array([change(j) for j in range(4)])
    z = lambda v: (v - v.mean()) / (v.std() + 1e-9)
    bar = beat + int(np.argmax(z(kick) + z(chg))) * period
    return beat / fps, bar / fps


def stretch_ratio(bpm: float) -> float:
    """원곡 템포를 96 BPM 박자 격자에 맞추는 배율. 차이가 크면 늘이지 않는다(1.0)."""
    for target in (VIDEO_BPM, VIDEO_BPM / 2, VIDEO_BPM * 2):
        r = target / bpm
        if abs(r - 1) <= 0.07:
            return r
    return 1.0


def energy_curve(x: np.ndarray, ratio: float) -> np.ndarray:
    """0.5초 간격 에너지(dB, 늘인 뒤 시간축)."""
    win = int(round(0.5 * SR * ratio))
    n = len(x) // win
    rms = np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms)


def analyze(path: Path) -> Fit:
    x = load(path)
    dur = len(x) / SR
    full, low, low_db = onset_envelopes(x)
    bpm = estimate_tempo(full)
    ratio = stretch_ratio(bpm)
    _, bar0 = beat_grid(full, low, low_db, bpm)
    bar_len = 4 * 60 / (bpm * ratio)         # 늘인 뒤 마디 길이(맞췄으면 2.5초)
    first_bar = ((bar0 + ONSET_LAG) / ratio) % bar_len

    energy = energy_curve(x, ratio)
    fps = SR / HOP
    stretched_dur = dur / ratio
    cands = []
    start = first_bar
    while start + DUR <= stretched_dur + 1.0:
        i0 = int(round(start / 0.5))
        seg = energy[i0:i0 + len(TEMPLATE)]
        if len(seg) == len(TEMPLATE) and seg.max() > -50:
            shape = np.corrcoef(seg, TEMPLATE)[0, 1]
            silent = np.mean(seg < seg.max() - 30)          # 중간에 소리가 끊기는 구간
            acc = []
            for a in ACCENTS:                              # 장면 강세 지점의 어택
                k = int(round((start + a) * ratio * fps))
                acc.append(full[max(0, k - 5):k + 6].max() if k < len(full) else 0)
            # 곡이 영상 끝(28.5~31초)에서 자연스럽게 끝나면 가산점
            ending = 0.15 if start + 28.5 <= stretched_dur <= start + DUR + 1.0 else 0.0
            score = shape + 0.08 * np.mean(acc) - 2 * silent + ending
            cands.append((float(score), start, f"모양 {shape:+.2f}, 강세 {np.mean(acc):+.1f}, 끊김 {silent:.0%}"
                                               + (", 곡의 끝과 맞물림" if ending else "")))
        start += bar_len
    cands.sort(reverse=True)
    best = cands[0] if cands else (-np.inf, 0.0, "후보 없음(곡이 30초보다 짧음)")
    return Fit(path, dur, bpm, ratio, first_bar, best[1], best[0], best[2], cands[1:4])


def choose(paths) -> list[Fit]:
    fits = [analyze(Path(p)) for p in paths]
    return sorted(fits, key=lambda f: f.score, reverse=True)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    for k, f in enumerate(choose(sys.argv[1:])):
        mark = "★" if k == 0 else " "
        print(f"{mark} {f.path.name}: {f.duration:.1f}s, {f.bpm:.1f} BPM, 배율 {f.tempo:.4f}, "
              f"첫 마디 {f.first_bar:.2f}s → 시작 {f.start:.2f}s (점수 {f.score:+.3f}; {f.detail})")
        for sc, st, d in f.others:
            print(f"      다른 후보: 시작 {st:.2f}s (점수 {sc:+.3f}; {d})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
