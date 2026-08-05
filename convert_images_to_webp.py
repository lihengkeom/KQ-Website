from pathlib import Path
from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def convert_image(source_path: Path, quality: int = 85) -> Path:
    output_path = source_path.with_suffix(".webp")

    if output_path.exists() and output_path.stat().st_mtime >= source_path.stat().st_mtime:
        return output_path

    with Image.open(source_path) as img:
        img = img.convert("RGBA") if img.mode in ("P", "LA") else img.convert("RGB")
        img.save(output_path, format="WEBP", quality=quality, method=6)

    return output_path


def main(root: Path, quality: int = 85) -> int:
    images = [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not images:
        print("No PNG/JPG files found to convert.")
        return 0

    print(f"Found {len(images)} image(s) to convert.")
    for source_path in sorted(images):
        try:
            output_path = convert_image(source_path, quality)
            print(f"Converted: {source_path.relative_to(root)} -> {output_path.relative_to(root)}")
        except Exception as exc:
            print(f"Failed: {source_path.relative_to(root)} ({exc})")

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert PNG/JPG images to WebP in the current workspace.")
    parser.add_argument("root", nargs="?", default=".", help="Root folder to scan for images.")
    parser.add_argument("--quality", type=int, default=85, help="Quality for WebP output (0-100).")
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise SystemExit(f"Root path does not exist or is not a directory: {root_path}")

    try:
        import PIL
    except ImportError:
        raise SystemExit("Pillow is required. Install it with: pip install pillow")

    raise SystemExit(main(root_path, args.quality))
