"""
generate_sample_images.py - Synthetic Vehicle Image Generator for ANPR & OCR Testing
=====================================================================================
Smart ANPR Vehicle Verification System

This script creates realistic, synthetic test vehicle images with authentic Indian
registration plates for testing the YOLO/CV detector and EasyOCR pipelines.
"""

from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.core.config import Config


def draw_indian_plate(
    plate_text: str,
    bg_color=(255, 255, 255),
    text_color=(0, 0, 0),
    width=370,
    height=85
) -> Image.Image:
    """
    Renders an authentic High Security Registration Plate (HSRP) style Indian plate:
    - High-contrast white or yellow background
    - Black border
    - Blue 'IND' strip on the left
    - Bold registration characters
    """
    plate = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(plate)

    # Black outer border
    draw.rectangle([(2, 2), (width - 3, height - 3)], outline=(0, 0, 0), width=4)

    # Blue 'IND' strip on left (Standard HSRP)
    stripe_w = 42
    draw.rectangle([(5, 5), (stripe_w, height - 5)], fill=(0, 56, 168))
    # 'IND' text vertically centered
    draw.text((10, height // 2 - 8), "IND", fill=(255, 255, 255))

    # Try to load a clean sans-serif system font, or fallback to default
    font = None
    for font_name in ("Arial.ttf", "Helvetica.ttf", "DejaVuSans-Bold.ttf", "SFNS.ttf"):
        try:
            font = ImageFont.truetype(font_name, 36)
            break
        except Exception:
            continue

    # Center plate characters within the remaining width
    rem_w = width - stripe_w
    if font:
        bbox = font.getbbox(plate_text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = stripe_w + max(10, (rem_w - text_w) // 2)
        text_y = (height - text_h) // 2 - 2
        draw.text((text_x, text_y), plate_text, fill=text_color, font=font)
    else:
        draw.text((stripe_w + 20, height // 2 - 10), plate_text, fill=text_color)

    return plate


def create_vehicle_scene(
    plate_text: Optional[str] = None,
    plate_bg_color=(255, 255, 255),
    car_color=(35, 45, 60),
    canvas_w=800,
    canvas_h=600
) -> Image.Image:
    """
    Creates a vehicle rear/bumper scene with an embedded license plate.
    """
    # Background: Highway pavement and daylight scene
    img = Image.new("RGB", (canvas_w, canvas_h), color=(140, 150, 160))
    draw = ImageDraw.Draw(img)

    # Road surface (lower half)
    draw.rectangle([(0, 380), (canvas_w, canvas_h)], fill=(65, 70, 75))

    # Road lane marking (center dashed white line)
    draw.rectangle([(canvas_w // 2 - 8, 480), (canvas_w // 2 + 8, canvas_h)], fill=(230, 230, 230))

    # Vehicle body silhouette (Rear bumper & trunk)
    car_box = [(120, 160), (canvas_w - 120, 480)]
    draw.rounded_rectangle(car_box, radius=35, fill=car_color, outline=(20, 25, 30), width=3)

    # Tail lights
    draw.rounded_rectangle([(140, 240), (220, 290)], radius=12, fill=(220, 20, 30))
    draw.rounded_rectangle([(canvas_w - 220, 240), (canvas_w - 140, 290)], radius=12, fill=(220, 20, 30))

    # Rear windshield (upper half of vehicle)
    draw.rounded_rectangle([(180, 180), (canvas_w - 180, 270)], radius=15, fill=(25, 35, 45))

    # Trunk handle / groove
    draw.line([(260, 320), (canvas_w - 260, 320)], fill=(20, 25, 30), width=3)

    # Bumper recess for number plate
    plate_recess = [(220, 350), (canvas_w - 220, 460)]
    draw.rounded_rectangle(plate_recess, radius=10, fill=(15, 20, 25))

    # If license plate is requested, embed the rendered plate inside the recess
    if plate_text:
        plate_w = 340
        plate_h = 80
        plate_img = draw_indian_plate(plate_text, bg_color=plate_bg_color, width=plate_w, height=plate_h)

        plate_x = (canvas_w - plate_w) // 2
        plate_y = 365
        img.paste(plate_img, (plate_x, plate_y))

    return img


def generate_all_samples():
    """Generate all test images into backend/app/static/samples/."""
    samples_dir = Path(Config.SAMPLES_DIR)
    samples_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("🎨 Generating ANPR Sample Test Images...")
    print(f"📁 Destination: {samples_dir}")
    print("=" * 65)

    # 1. Car with DL01AB1234 (White private plate)
    car1 = create_vehicle_scene(plate_text="DL 01 AB 1234", plate_bg_color=(255, 255, 255), car_color=(40, 60, 100))
    car1_path = samples_dir / "sample_car_DL01AB1234.jpg"
    car1.save(car1_path, quality=95)
    print(f"  ✅ Created: {car1_path.name} (Vehicle with white plate DL 01 AB 1234)")

    # 2. Commercial Vehicle with MH12DE5678 (Yellow commercial plate)
    car2 = create_vehicle_scene(plate_text="MH 12 DE 5678", plate_bg_color=(255, 215, 0), car_color=(120, 40, 40))
    car2_path = samples_dir / "sample_commercial_MH12DE5678.jpg"
    car2.save(car2_path, quality=95)
    print(f"  ✅ Created: {car2_path.name} (Commercial vehicle with yellow plate MH 12 DE 5678)")

    # 3. Vehicle without number plate (for empty plate testing)
    car_no_plate = create_vehicle_scene(plate_text=None, car_color=(50, 50, 50))
    car_no_plate_path = samples_dir / "sample_vehicle_no_plate.jpg"
    car_no_plate.save(car_no_plate_path, quality=95)
    print(f"  ✅ Created: {car_no_plate_path.name} (Vehicle with empty recess - no plate text)")

    # 4. Plain road scenery without any vehicle or plate (for zero-detection testing)
    plain_road = Image.new("RGB", (800, 600), color=(120, 130, 140))
    draw_road = ImageDraw.Draw(plain_road)
    draw_road.rectangle([(0, 300), (800, 600)], fill=(50, 55, 60))
    road_path = samples_dir / "sample_road_no_plate.jpg"
    plain_road.save(road_path, quality=95)
    print(f"  ✅ Created: {road_path.name} (Plain road without plate for negative detection)")

    # 5. Standalone cropped plate for direct OCR accuracy testing
    standalone_crop = draw_indian_plate("DL 01 AB 1234", bg_color=(255, 255, 255), width=380, height=90)
    crop_path = samples_dir / "sample_cropped_plate_DL01AB1234.jpg"
    standalone_crop.save(crop_path, quality=95)
    print(f"  ✅ Created: {crop_path.name} (Standalone high-res plate crop)")

    # 5. Invalid non-image file
    invalid_path = samples_dir / "sample_invalid.txt"
    with open(invalid_path, "w") as f:
        f.write("This is a plain text file, not an image.")
    print(f"  ✅ Created: {invalid_path.name} (Non-image file for validation testing)")

    print("=" * 65)
    print("🎉 All sample images successfully generated.")
    print("=" * 65)


if __name__ == "__main__":
    generate_all_samples()
