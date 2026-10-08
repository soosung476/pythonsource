"""한글날 모션그래픽 렌더러.

scene/index.html 의 renderFrame(t)를 헤드리스 크로미움에서 프레임마다 호출해
PNG를 받아 ffmpeg로 H.264 영상을 만든다.

    python3 render.py                          # output/hangul_day_video.mp4 (무음)
    python3 render.py --audio output/music.wav --out output/hangul_day_2026.mp4
    python3 render.py --still 1.5 12.8 27      # 특정 시점 정지 화면(PNG)
    python3 render.py --sheet                  # 2초 간격 콘택트 시트(PNG)

먼저 python3 fetch_fonts.py 로 폰트를 받아 두어야 한다.
"""
import argparse
import asyncio
import base64
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent
SCENE = ROOT / "scene" / "index.html"
W, H = 1920, 1080


def find_chromium(explicit: str | None) -> str | None:
    """Playwright 기본 브라우저 대신 쓸 크로미움 실행 파일(없으면 None → 기본값)."""
    for cand in (explicit, os.environ.get("CHROMIUM_PATH"), "/opt/pw-browsers/chromium"):
        if cand and Path(cand).exists():
            return cand
    return None


async def open_pages(pw, n: int, chromium: str | None):
    browser = await pw.chromium.launch(
        executable_path=chromium,
        args=["--allow-file-access-from-files", "--force-color-profile=srgb"],
    )
    pages = []
    for _ in range(n):
        context = await browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=1)
        page = await context.new_page()
        page.on("pageerror", lambda e: print("page error:", e, file=sys.stderr))
        await page.goto(SCENE.as_uri())
        await page.evaluate("window.ready")
        pages.append(page)
    return browser, pages


async def grab(page, t: float) -> bytes:
    data_url = await page.evaluate("t => window.renderFrame(t)", t)
    return base64.b64decode(data_url.split(",", 1)[1])


async def render_stills(times, out_dir: Path, chromium):
    out_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser, (page,) = await open_pages(pw, 1, chromium)
        paths = []
        for t in times:
            path = out_dir / f"still_{t:06.2f}.png"
            path.write_bytes(await grab(page, t))
            paths.append(path)
            print(path)
        await browser.close()
    return paths


async def render_sheet(out: Path, chromium, start=0.5, step=2.0, cols=4):
    from PIL import Image

    times = [start + i * step for i in range(int((30 - start) / step) + 1)]
    async with async_playwright() as pw:
        browser, (page,) = await open_pages(pw, 1, chromium)
        tw, th = W // cols, H // cols
        rows = -(-len(times) // cols)
        sheet = Image.new("RGB", (tw * cols, th * rows), "black")
        for i, t in enumerate(times):
            img = Image.open(io.BytesIO(await grab(page, t))).convert("RGB").resize((tw, th), Image.LANCZOS)
            sheet.paste(img, ((i % cols) * tw, (i // cols) * th))
        await browser.close()
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out, "times:", ", ".join(f"{t:.1f}" for t in times))


async def render_video(out: Path, fps: int, duration: float, workers: int, audio: Path | None, chromium, crf: int):
    total = round(fps * duration)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-",
    ]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += [
        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
        "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-tune", "animation",
        "-profile:v", "high", "-level:v", "4.2",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
    ]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-map", "0:v", "-map", "1:a", "-shortest"]
    cmd += ["-movflags", "+faststart", str(out)]
    out.parent.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    async with async_playwright() as pw:
        browser, pages = await open_pages(pw, workers, chromium)
        done: dict[int, bytes] = {}
        cond = asyncio.Condition()

        async def worker(k: int, page):
            for i in range(k, total, workers):
                png = await grab(page, i / fps)
                async with cond:
                    # 인코더보다 너무 앞서 나가지 않게 기다린다(메모리 제한)
                    await cond.wait_for(lambda: i - next_frame < workers * 6)
                    done[i] = png
                    cond.notify_all()

        next_frame = 0

        async def writer():
            nonlocal next_frame
            loop = asyncio.get_running_loop()
            while next_frame < total:
                async with cond:
                    await cond.wait_for(lambda: next_frame in done)
                    png = done.pop(next_frame)
                await loop.run_in_executor(None, ff.stdin.write, png)
                async with cond:
                    next_frame += 1
                    cond.notify_all()
                if next_frame % fps == 0:
                    print(f"\r{next_frame}/{total} frames", end="", flush=True)
            print()

        await asyncio.gather(writer(), *(worker(k, p) for k, p in enumerate(pages)))
        await browser.close()

    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "output" / "hangul_day_video.mp4")
    ap.add_argument("--audio", type=Path, help="함께 넣을 음악 파일")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--duration", type=float, default=30.0)
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("--still", type=float, nargs="+", help="이 시점들의 정지 화면만 PNG로 저장")
    ap.add_argument("--sheet", action="store_true", help="2초 간격 콘택트 시트 저장")
    ap.add_argument("--stills-dir", type=Path, default=ROOT / "output" / "stills")
    ap.add_argument("--chromium", help="크로미움 실행 파일 경로")
    args = ap.parse_args()

    if not (ROOT / "fonts" / "NotoSerifKR-900.ttf").exists():
        print("폰트가 없습니다. 먼저 `python3 fetch_fonts.py`를 실행하세요.", file=sys.stderr)
        return 1
    if not shutil.which("ffmpeg") and not (args.still or args.sheet):
        print("ffmpeg가 필요합니다.", file=sys.stderr)
        return 1

    chromium = find_chromium(args.chromium)
    if args.still:
        asyncio.run(render_stills(args.still, args.stills_dir, chromium))
    elif args.sheet:
        asyncio.run(render_sheet(args.stills_dir / "sheet.png", chromium))
    else:
        asyncio.run(render_video(args.out, args.fps, args.duration, args.workers, args.audio, chromium, args.crf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
