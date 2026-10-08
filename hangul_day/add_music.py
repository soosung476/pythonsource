"""Suno 등에서 만든 음악으로 영상의 배경음악을 바꾼다(영상은 다시 렌더링하지 않는다).

    python3 add_music.py suno_song.mp3                  # 곡의 처음 30초를 사용
    python3 add_music.py suno_song.mp3 --start 42.5     # 42.5초 지점부터 30초
    python3 add_music.py suno_song.mp3 --out 내영상.mp4

음량은 -14 LUFS(유튜브·인스타그램 기준)로 맞추고, 끝부분 1.7초는 페이드아웃한다.
영상은 96 BPM(1마디 = 2.5초)에 맞춰 장면이 바뀌므로, Suno 곡도 96 BPM이면
마디의 첫 박을 --start 로 맞췄을 때 장면 전환과 박자가 잘 맞는다.
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


def shape_filter(start: float) -> str:
    """음악을 30초로 자르고(짧으면 무음으로 채움) 앞뒤를 부드럽게 만든다."""
    fade_in = 0.25 if start > 0 else 0.02
    return (f"aresample=48000,apad,atrim=0:{DUR},asetpts=N/SR/TB,"
            f"afade=t=in:st=0:d={fade_in},afade=t=out:st={DUR - 1.7}:d=1.7")


def measure(music: Path, start: float) -> dict:
    """loudnorm 1차 측정."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-ss", str(start), "-i", str(music),
           "-af", shape_filter(start) + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True, check=True).stderr
    return json.loads(re.findall(r"\{[^{}]*\}", err)[-1])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("music", type=Path, help="음악 파일(mp3, wav, m4a 등)")
    ap.add_argument("--start", type=float, default=0.0, help="곡에서 사용할 시작 지점(초)")
    ap.add_argument("--video", type=Path, default=VIDEO)
    ap.add_argument("--out", type=Path, default=ROOT / "output" / "hangul_day_2026_suno.mp4")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg가 필요합니다.", file=sys.stderr)
        return 1
    for f in (args.music, args.video):
        if not f.exists():
            print(f"파일이 없습니다: {f}", file=sys.stderr)
            return 1

    m = measure(args.music, args.start)
    loudnorm = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                f"offset={m['target_offset']}:linear=true")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(args.video), "-ss", str(args.start), "-i", str(args.music),
           "-filter_complex", f"[1:a]{shape_filter(args.start)},{loudnorm},aresample=48000[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
           "-t", str(DUR), "-movflags", "+faststart", str(args.out)]
    subprocess.run(cmd, check=True)
    print(f"완성: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
