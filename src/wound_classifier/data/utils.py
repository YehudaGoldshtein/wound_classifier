"""Image processing utilities for wound data pipeline."""

from pathlib import Path
from typing import Optional

from PIL import Image


# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def is_valid_image(path: Path) -> bool:
    """Check if a file is a valid image.

    Args:
        path: Path to the file

    Returns:
        True if the file is a valid, readable image
    """
    if not path.exists():
        return False

    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        return False

    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def get_image_info(path: Path) -> tuple[int, int, str]:
    """Get image dimensions and format.

    Args:
        path: Path to the image file

    Returns:
        Tuple of (width, height, format)

    Raises:
        ValueError: If file is not a valid image
    """
    try:
        with Image.open(path) as img:
            return img.width, img.height, img.format or "UNKNOWN"
    except Exception as e:
        raise ValueError(f"Cannot read image {path}: {e}")


def resize_image(
    src: Path,
    dst: Path,
    target_size: tuple[int, int],
    keep_aspect: bool = True,
    fill_color: tuple[int, int, int] = (0, 0, 0)
) -> tuple[int, int]:
    """Resize an image to target dimensions.

    Args:
        src: Source image path
        dst: Destination path
        target_size: Target (width, height)
        keep_aspect: If True, maintain aspect ratio and pad
        fill_color: RGB color for padding when keeping aspect ratio

    Returns:
        Tuple of (new_width, new_height)

    Raises:
        ValueError: If source is not a valid image
    """
    try:
        with Image.open(src) as img:
            # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
            if img.mode != "RGB":
                img = img.convert("RGB")

            if keep_aspect:
                # Calculate scaling to fit within target while maintaining aspect
                img_ratio = img.width / img.height
                target_ratio = target_size[0] / target_size[1]

                if img_ratio > target_ratio:
                    # Image is wider - fit to width
                    new_width = target_size[0]
                    new_height = int(target_size[0] / img_ratio)
                else:
                    # Image is taller - fit to height
                    new_height = target_size[1]
                    new_width = int(target_size[1] * img_ratio)

                # Resize the image
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create new image with padding
                result = Image.new("RGB", target_size, fill_color)
                paste_x = (target_size[0] - new_width) // 2
                paste_y = (target_size[1] - new_height) // 2
                result.paste(img_resized, (paste_x, paste_y))
            else:
                # Simple resize without maintaining aspect ratio
                result = img.resize(target_size, Image.Resampling.LANCZOS)

            # Ensure destination directory exists
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Save as JPEG for consistency
            result.save(dst, "JPEG", quality=95)

            return target_size

    except Exception as e:
        raise ValueError(f"Cannot process image {src}: {e}")


def copy_image(src: Path, dst: Path, convert_to_jpg: bool = True) -> tuple[int, int]:
    """Copy an image, optionally converting to JPEG.

    Args:
        src: Source image path
        dst: Destination path
        convert_to_jpg: If True, convert to JPEG format

    Returns:
        Tuple of (width, height)
    """
    try:
        with Image.open(src) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Ensure destination directory exists
            dst.parent.mkdir(parents=True, exist_ok=True)

            if convert_to_jpg:
                # Ensure .jpg extension
                dst = dst.with_suffix(".jpg")
                img.save(dst, "JPEG", quality=95)
            else:
                img.save(dst)

            return img.width, img.height

    except Exception as e:
        raise ValueError(f"Cannot copy image {src}: {e}")


def list_images(directory: Path, recursive: bool = True) -> list[Path]:
    """List all image files in a directory.

    Args:
        directory: Directory to search
        recursive: If True, search subdirectories

    Returns:
        List of image file paths (deduplicated)
    """
    if not directory.exists():
        return []

    images = set()  # Use set to avoid duplicates on case-insensitive filesystems
    pattern = "**/*" if recursive else "*"

    for ext in IMAGE_EXTENSIONS:
        images.update(directory.glob(f"{pattern}{ext}"))
        images.update(directory.glob(f"{pattern}{ext.upper()}"))

    return sorted(images)
