#!/usr/bin/env python3
"""
E-Commerce Product Suite Image Grid Stitcher Script
Assembles N (default 10) product suite images into a clean, modern e-commerce product collage card
with title banner, numbered shot badges, and shot descriptions.
Preserves input image aspect ratio (e.g., 2:3, 3:4, 1:1, 9:16, 16:9) without stretching or distortion.
"""

import os
import sys
import json
import argparse
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont


def find_system_cjk_font(font_size: int = 18) -> ImageFont.ImageFont:
    """Find a system CJK font (Windows/Linux/macOS) for PIL rendering."""
    candidate_paths = [
        # Windows
        "C:\\Windows\\Fonts\\msyh.ttc",       # YaHei
        "C:\\Windows\\Fonts\\msyhbd.ttc",     # YaHei Bold
        "C:\\Windows\\Fonts\\simhei.ttf",     # SimHei
        "C:\\Windows\\Fonts\\simsun.ttc",     # SimSun
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        # Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                continue
                
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def calculate_grid_dimensions(num_panels: int, grid_arg: str) -> Tuple[int, int]:
    """Calculate rows and columns based on image count or user argument."""
    if grid_arg and grid_arg != "auto" and "x" in grid_arg:
        parts = grid_arg.lower().split("x")
        try:
            cols = int(parts[0])
            rows = int(parts[1])
            return cols, rows
        except ValueError:
            pass
            
    if num_panels <= 1:
        return 1, 1
    elif num_panels == 2:
        return 2, 1
    elif num_panels == 3:
        return 3, 1
    elif num_panels == 4:
        return 2, 2
    elif num_panels == 5:
        return 5, 1
    elif num_panels == 6:
        return 3, 2
    elif num_panels <= 8:
        return 4, 2
    elif num_panels == 10:
        return 5, 2  # Default 5 columns, 2 rows for 10-shot suite
    else:
        cols = 5
        rows = (num_panels + cols - 1) // cols
        return cols, rows


DEFAULT_SHOT_LABELS = [
    "01. Hero Main",
    "02. USP Callout",
    "03. Lifestyle",
    "04. Craftsmanship",
    "05. Dimensions",
    "06. Model Demo",
    "07. Unboxing",
    "08. Studio Luxury",
    "09. Multi-Angle",
    "10. Promo Banner"
]


def detect_aspect_ratio(image_paths: List[str]) -> Tuple[int, int]:
    """Detect aspect ratio width and height from the first valid input image."""
    for path in image_paths:
        if os.path.exists(path):
            try:
                with Image.open(path) as img:
                    return img.width, img.height
            except Exception:
                continue
    return 600, 600  # Default square if no valid image found


def parse_aspect_ratio_str(aspect_str: str) -> Optional[Tuple[int, int]]:
    """Parse aspect ratio string such as '2:3', '3:4', '16:9', '1:1'."""
    if not aspect_str or aspect_str == "auto":
        return None
    if ":" in aspect_str:
        parts = aspect_str.split(":")
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return None


def create_product_suite_grid(
    image_paths: List[str],
    captions: Optional[List[str]] = None,
    title: str = "E-Commerce Product Suite",
    output_path: str = "product_suite_grid.png",
    grid: str = "auto",
    tile_width: int = 600,
    aspect_ratio: str = "auto",
    tile_size_arg: Optional[str] = None,
    gutter: int = 20,
    banner_height: int = 90,
    bg_color: str = "#0F172A",          # Dark Slate-900
    banner_bg: str = "#1E293B",         # Slate-800
    banner_text_color: str = "#F8FAFC", # Slate-50
    caption_bg: str = "#1E293B",        # Card background
    tile_bg_color: str = "#1E293B",     # Container tile background
    badge_bg: str = "#2563EB",          # Royal Blue badge
    badge_text_color: str = "#FFFFFF",
    caption_text_color: str = "#F1F5F9",
) -> dict:
    """Stitch N product images into a structured e-commerce product suite collage card."""
    if not image_paths:
        return {"code": 1, "status": "error", "message": "No image paths provided"}
        
    num_images = len(image_paths)
    cols, rows = calculate_grid_dimensions(num_images, grid)
    
    # Determine target tile dimensions (preserving aspect ratio)
    tile_w = tile_width
    tile_h = tile_width
    
    if tile_size_arg and "x" in tile_size_arg.lower():
        try:
            parts = tile_size_arg.lower().split("x")
            tile_w = int(parts[0])
            tile_h = int(parts[1])
        except ValueError:
            pass
    else:
        parsed_aspect = parse_aspect_ratio_str(aspect_ratio)
        if parsed_aspect:
            ar_w, ar_h = parsed_aspect
            tile_h = int(tile_w * (ar_h / ar_w))
        else:
            # Auto detect from first valid image
            orig_w, orig_h = detect_aspect_ratio(image_paths)
            tile_h = int(tile_w * (orig_h / orig_w))
            
    # Load fonts
    title_font = find_system_cjk_font(28)
    label_font = find_system_cjk_font(18)
    badge_font = find_system_cjk_font(16)
    
    # Normalize captions
    if not captions or len(captions) == 0:
        captions = DEFAULT_SHOT_LABELS[:num_images]
    while len(captions) < num_images:
        idx = len(captions) + 1
        captions.append(f"{idx:02d}. Product Image {idx}")
        
    caption_box_h = 44
    cell_w = tile_w
    cell_h = tile_h + caption_box_h
    
    canvas_w = (cols * cell_w) + ((cols + 1) * gutter)
    canvas_h = banner_height + (rows * cell_h) + ((rows + 1) * gutter)
    
    # Create main canvas
    canvas = Image.new("RGB", (canvas_w, canvas_h), color=bg_color)
    draw = ImageDraw.Draw(canvas)
    
    # Draw Header Banner
    draw.rectangle([(0, 0), (canvas_w, banner_height)], fill=banner_bg)
    
    # Header title text
    title_text = f"🛍️  {title}"
    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    t_w = t_bbox[2] - t_bbox[0]
    t_h = t_bbox[3] - t_bbox[1]
    draw.text(((canvas_w - t_w) // 2, (banner_height - t_h) // 2), title_text, font=title_font, fill=banner_text_color)
    
    # Accent line below banner
    draw.line([(0, banner_height - 3), (canvas_w, banner_height - 3)], fill="#3B82F6", width=3)
    
    # Place product tiles
    for idx, path in enumerate(image_paths):
        r = idx // cols
        c = idx % cols
        
        x = gutter + c * (cell_w + gutter)
        y = banner_height + gutter + r * (cell_h + gutter)
        
        # Tile container
        tile = Image.new("RGB", (tile_w, tile_h), color=tile_bg_color)
        
        # Load and scale image preserving aspect ratio
        try:
            if os.path.exists(path):
                img = Image.open(path).convert("RGB")
                orig_w, orig_h = img.size
                
                # Proportional contain scaling (no distortion/stretching)
                scale = min(tile_w / orig_w, tile_h / orig_h)
                new_w = max(1, int(orig_w * scale))
                new_h = max(1, int(orig_h * scale))
                
                resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Center inside tile container
                off_x = (tile_w - new_w) // 2
                off_y = (tile_h - new_h) // 2
                tile.paste(resized_img, (off_x, off_y))
            else:
                p_draw = ImageDraw.Draw(tile)
                p_text = f"Image #{idx+1}\nMissing File"
                p_draw.text((tile_w // 4, tile_h // 2), p_text, font=label_font, fill="#94A3B8")
        except Exception as e:
            p_draw = ImageDraw.Draw(tile)
            p_draw.text((20, tile_h // 2), f"Error loading image #{idx+1}", font=label_font, fill="#FCA5A5")
            
        # Paste tile onto canvas
        canvas.paste(tile, (x, y))
        
        # Draw tile border
        draw.rectangle([(x, y), (x + tile_w, y + tile_h)], outline="#475569", width=2)
        
        # Draw Top-Left Badge (Shot number)
        badge_str = f"#{idx+1:02d}"
        b_bbox = draw.textbbox((0, 0), badge_str, font=badge_font)
        b_w = b_bbox[2] - b_bbox[0] + 16
        b_h = b_bbox[3] - b_bbox[1] + 10
        badge_x = x + 8
        badge_y = y + 8
        
        draw.rectangle([(badge_x, badge_y), (badge_x + b_w, badge_y + b_h)], fill=badge_bg)
        draw.text((badge_x + 8, badge_y + 3), badge_str, font=badge_font, fill=badge_text_color)
        
        # Draw Bottom Caption Bar
        cap_y = y + tile_h
        draw.rectangle([(x, cap_y), (x + tile_w, cap_y + caption_box_h)], fill=caption_bg, outline="#334155", width=1)
        
        caption_str = captions[idx]
        cap_bbox = draw.textbbox((0, 0), caption_str, font=label_font)
        cap_w = cap_bbox[2] - cap_bbox[0]
        cap_h = cap_bbox[3] - cap_bbox[1]
        
        cap_text_x = x + max(8, (tile_w - cap_w) // 2)
        cap_text_y = cap_y + (caption_box_h - cap_h) // 2
        draw.text((cap_text_x, cap_text_y), caption_str, font=label_font, fill=caption_text_color)
        
    # Ensure directory exists and save
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    canvas.save(output_path, quality=95)
    
    return {
        "code": 0,
        "status": "success",
        "message": f"Successfully stitched {num_images} product suite images into grid ({cols}x{rows}) maintaining aspect ratio ({tile_w}x{tile_h})",
        "output_path": os.path.abspath(output_path),
        "dimensions": {
            "width": canvas_w,
            "height": canvas_h,
            "cols": cols,
            "rows": rows,
            "tile_width": tile_w,
            "tile_height": tile_h
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Stitch e-commerce product suite images into a grid preview card with aspect ratio preservation.")
    parser.add_argument("images", nargs="+", help="Paths to generated product images (1..N)")
    parser.add_argument("--captions", nargs="*", help="Captions / shot labels for each image in order")
    parser.add_argument("--title", default="E-Commerce Product Suite", help="Title banner header text")
    parser.add_argument("--grid", default="5x2", help="Grid structure (e.g., 5x2, 2x5, auto)")
    parser.add_argument("--tile-width", type=int, default=600, help="Tile container width in pixels (default: 600)")
    parser.add_argument("--aspect-ratio", default="auto", help="Aspect ratio for tiles (e.g., auto, 2:3, 3:4, 1:1, 9:16, 16:9)")
    parser.add_argument("--tile-size", help="Explicit tile dimensions WxH (e.g., 600x900)")
    parser.add_argument("-o", "--output", default="product_suite_grid.png", help="Output PNG filepath")
    
    args = parser.parse_args()
    
    res = create_product_suite_grid(
        image_paths=args.images,
        captions=args.captions,
        title=args.title,
        output_path=args.output,
        grid=args.grid,
        tile_width=args.tile_width,
        aspect_ratio=args.aspect_ratio,
        tile_size_arg=args.tile_size
    )
    
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(res["code"])


if __name__ == "__main__":
    main()
