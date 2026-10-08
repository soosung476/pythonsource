"""Suno 등에서 만든 음악으로 영상의 배경음악을 바꾼다(영상은 다시 렌더링하지 않는다).

    python3 add_music.py 곡1.mp3 곡2.mp3 --auto        # 두 곡을 분석해 더 잘 맞는 곡·구간·템포를 골라 넣기
    python3 add_music.py suno_song.mp3                  # 곡의 처음 30초를 그대로 사용
    python3 add_music.py suno_song.mp3 --start 42.5     # 42.5초 지점부터 30초
    python3 add_music.py suno_song.mp3 --out 내영상.mp4

--auto 는 fit_music.py로 곡의 템포와 마디 첫 박을 찾고, 96 BPM에 가까우면 음높이를 유지한 채
속도를 살짝 맞춰 곡의 마디가 장면 전환(2.5초 간격)과 겹치게 한 뒤, 장면 흐름과 가장 닮은
30초 구간을 고른다. 음량은 -14 LUFS(유튜브·인스타그램 기준)로 맞추고, 끝 1.7초는 페이드아웃한다.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VIDEO = ROOT / "output" / "hangul_day_2026.mp4"
DUR = 30.0


def shape_filter(start: float, tempo: float = 1.0) -> str:
    """(필요하면 템포를 맞춘 뒤) 30초를 잘라내고, 모자라면 무음으로 채우고, 앞뒤를 부드럽게 만든다."""
    fade_in = 0.25 if start > 0 else 0.02
    stretch = f"atempo={tempo:.5f}," if abs(tempo - 1) > 1e-4 else ""
    return (f"aresample=48000,{stretch}atrim=start={start:.4f},asetpts=N/SR/TB,apad,atrim=0:{DUR},"
            f"afade=t=in:st=0:d={fade_in},afade=t=out:st={DUR - 1.7}:d=1.7")


def measure(music: Path, chain: str) -> dict:
    """loudnorm 1차 측정."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(music),
           "-af", chain + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, check=True).stderr
    return json.loads(re.findall(r"\{[^{}]*\}", err)[-1])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("music", type=Path, nargs="+", help="음악 파일(mp3, wav, m4a 등). --auto면 여러 개 가능")
    ap.add_argument("--auto", action="store_true", help="곡·시작 지점·템포를 자동으로 고르기")
    ap.add_argument("--start", type=float, default=0.0, help="곡에서 사용할 시작 지점(초)")
    ap.add_argument("--tempo", type=float, default=1.0, help="속도 배율(음높이 유지, 예: 1.02)")
    ap.add_argument("--video", type=Path, default=VIDEO)
    ap.add_argument("--out", type=Path, default=ROOT / "output" / "hangul_day_2026_suno.mp4")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg가 필요합니다.", file=sys.stderr)
        return 1
    for f in (*args.music, args.video):
        if not f.exists():
            print(f"파일이 없습니다: {f}", file=sys.stderr)
            return 1
    if len(args.music) > 1 and not args.auto:
        print("여러 곡을 비교하려면 --auto를 붙이세요.", file=sys.stderr)
        return 1

    music, start, tempo = args.music[0], args.start, args.tempo
    if args.auto:
        import fit_music

        fits = fit_music.choose(args.music)
        for k, f in enumerate(fits):
            print(f"{'★' if k == 0 else ' '} {f.path.name}: {f.bpm:.1f} BPM → 배율 {f.tempo:.4f}, "
                  f"시작 {f.start:.2f}s (점수 {f.score:+.3f}; {f.detail})")
        best = fits[0]
        music, start, tempo = best.path, best.start, best.tempo

    chain = shape_filter(start, tempo)
    m = measure(music, chain)
    loudnorm = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                f"offset={m['target_offset']}:linear=true")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(args.video), "-i", str(music),
           "-filter_complex", f"[1:a]{chain},{loudnorm},aresample=48000[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
           "-t", str(DUR), "-movflags", "+faststart", str(args.out)]
    subprocess.run(cmd, check=True)
    print(f"완성: {args.out}  (곡 {music.name}, 시작 {start:.2f}s, 배율 {tempo:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
