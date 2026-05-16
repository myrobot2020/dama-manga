import os
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# --- Configuration ---
# Root directory where your extracted PNG panels are stored
INPUT_ROOT = Path("data/raw/manga/panels")
# Destination for the mobile-optimized WebP assets
OUTPUT_ROOT = Path("data/manga/mobile")
# Max dimension (width or height) to ensure efficiency on mobile devices
MAX_DIMENSION = 1200
# WebP quality (80 is standard for high-quality mobile assets)
WEBP_QUALITY = 80
# Encoding method 6 is slowest but provides the best compression
WEBP_METHOD = 6

def optimize_image(input_path: Path, output_path: Path):
    """Resize image and convert to WebP for mobile optimization."""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB for best WebP compatibility
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")

            # Downscale if larger than MAX_DIMENSION
            width, height = img.size
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                if width > height:
                    new_width = MAX_DIMENSION
                    new_height = int(height * (MAX_DIMENSION / width))
                else:
                    new_height = MAX_DIMENSION
                    new_width = int(width * (MAX_DIMENSION / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create destination folder
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as WebP
            img.save(output_path, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
            return True
    except Exception as e:
        print(f"\n❌ Error processing {input_path.name}: {e}")
        return False

def main():
    print(f"🚀 Starting Mobile Asset Optimization...")
    print(f"   Settings: Max Dim={MAX_DIMENSION}px, WebP Quality={WEBP_QUALITY}")

    # Find all 'image panels' subdirectories
    image_panel_dirs = list(INPUT_ROOT.glob("**/image panels"))

    if not image_panel_dirs:
        print("❌ No 'image panels' directories found. Verify the INPUT_ROOT.")
        # Try a broader search if the structured one fails
        image_panel_dirs = [INPUT_ROOT]
        print(f"   Falling back to searching all of {INPUT_ROOT}...")

    # Collect all PNG files
    all_images = []
    for d in image_panel_dirs:
        all_images.extend(list(d.glob("**/*.png")))

    if not all_images:
        print("❌ No .png files were found in the search paths.")
        return

    print(f"📦 Found {len(all_images)} panels to optimize.")

    success_count = 0
    for img_path in tqdm(all_images, desc="Optimizing", unit="img"):
        # Extract volume folder name (e.g., buddha_v01)
        volume_name = "unknown"
        for part in img_path.parts:
            if part.startswith("buddha_v"):
                volume_name = part
                break

        # Target: data/manga/mobile/buddha_vXX/filename.webp
        output_path = OUTPUT_ROOT / volume_name / (img_path.stem + ".webp")

        # Avoid re-processing if it already exists
        if output_path.exists():
            success_count += 1
            continue

        if optimize_image(img_path, output_path):
            success_count += 1

    print(f"\n✨ Done! Optimized {success_count}/{len(all_images)} images.")
    print(f"   Assets saved to: {OUTPUT_ROOT.absolute()}")

if __name__ == "__main__":
    main()
