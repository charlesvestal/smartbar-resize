#!/usr/bin/env python3
import argparse, math, os, sys
from pathlib import Path
from PIL import Image, ImageOps

# Status bar heights for each device (in points, will be scaled appropriately)
STATUS_BAR_HEIGHTS = {
    "ipad": {
        "iPad (12.9)": 40,      # iPad Pro 12.9" - modern iPadOS status bar
        "iPad (11)": 40,        # iPad Pro 11", iPad Air - modern iPadOS status bar
        "iPad (10.5)": 40,      # iPad Pro 10.5" - modern iPadOS status bar
        "iPad (9.7)": 40,       # iPad 9.7", iPad Air 2, etc. - modern iPadOS status bar
    },
    "iphone": {
        "iPhone (6.9)": 54,     # iPhone 16 Pro Max with Dynamic Island
        "iPhone (6.5)": 54,     # iPhone Pro Max models with Dynamic Island
        "iPhone (6.3)": 54,     # iPhone Pro models with Dynamic Island  
        "iPhone (6.1)": 54,     # iPhone models with Dynamic Island
        "iPhone (5.5)": 20,     # iPhone Plus models
        "iPhone (4.7)": 20,     # iPhone 6/7/8 standard
        "iPhone (4.0)": 20,     # iPhone 5/5S/5C/SE (1st gen)
        "iPhone (3.5)": 20,     # iPhone 4/4S
    },
    "mac": {
        "Mac": 0,               # No status bar for Mac screenshots
    },
    "apple_tv": {
        "Apple TV": 0,          # No status bar for Apple TV
    },
    "vision_pro": {
        "Vision Pro": 0,        # No status bar for Vision Pro
    },
    "watch": {
        "Apple Watch": 0,       # No status bar for Watch (uses full screen)
    },
}

# Allowed outputs
TARGETS = {
    "ipad": {
        "iPad (12.9)": {
            "portrait":  [(2064, 2752), (2048, 2732)],
            "landscape": [(2752, 2064), (2732, 2048)],
        },
        "iPad (11)": {
            "portrait":  [(1668, 2420), (1668, 2388), (1640, 2360), (1488, 2266)],
            "landscape": [(2420, 1668), (2388, 1668), (2360, 1640), (2266, 1488)],
        },
        "iPad (10.5)": {
            "portrait":  [(1668, 2224)],
            "landscape": [(2224, 1668)],
        },
        "iPad (9.7)": {
            "portrait":  [(1536, 2048), (1536, 2008), (768, 1024), (768, 1004)],
            "landscape": [(2048, 1536), (2048, 1496), (1024, 768), (1024, 748)],
        },
    },
    "iphone": {
        "iPhone (6.9)": {
            "portrait":  [(1290, 2796), (1320, 2868)],
            "landscape": [(2796, 1290), (2868, 1320)],
        },
        "iPhone (6.5)": {
            "portrait":  [(1284, 2778), (1242, 2688)],
            "landscape": [(2778, 1284), (2688, 1242)],
        },
        "iPhone (6.3)": {
            "portrait":  [(1179, 2556), (1206, 2622)],
            "landscape": [(2556, 1179), (2622, 1206)],
        },
        "iPhone (6.1)": {
            "portrait":  [(1170, 2532), (1125, 2436), (1080, 2340)],
            "landscape": [(2532, 1170), (2436, 1125), (2340, 1080)],
        },
        "iPhone (5.5)": {
            "portrait":  [(1242, 2208)],
            "landscape": [(2208, 1242)],
        },
        "iPhone (4.7)": {
            "portrait":  [(750, 1334)],
            "landscape": [(1334, 750)],
        },
        "iPhone (4.0)": {
            "portrait":  [(640, 1096), (640, 1136)],
            "landscape": [(1096, 640), (1136, 640)],
        },
        "iPhone (3.5)": {
            "portrait":  [(640, 920), (640, 960)],
            "landscape": [(920, 640), (960, 640)],
        },
    },
    "mac": {
        "Mac": {
            "portrait":  [],
            "landscape": [(1280, 800), (1440, 900), (2560, 1600), (2880, 1800)],
        }
    },
    "apple_tv": {
        "Apple TV": {
            "portrait":  [],
            "landscape": [(1920, 1080), (3840, 2160)],
        }
    },
    "vision_pro": {
        "Vision Pro": {
            "portrait":  [],
            "landscape": [(3840, 2160)],
        }
    },
    "watch": {
        "Apple Watch": {
            "portrait":  [(410, 502), (416, 496), (396, 484), (368, 448), (312, 390)],
            "landscape": [],
        }
    },
}

def iter_family_groups(family):
    for group_label, orientations in TARGETS.get(family, {}).items():
        yield group_label, orientations

def all_sizes_for_family(family):
    sizes = []
    for _, orientations in iter_family_groups(family):
        for orien, dims in orientations.items():
            for (w, h) in dims:
                sizes.append((orien, w, h))
    return sizes

def orientation_of(w, h):
    return "portrait" if h >= w else "landscape"

def aspect_ratio(w, h):
    return w / h

def nearest_family_by_aspect(w, h, device_hint="auto", allowed_families=None):
    """Choose iPad vs iPhone by aspect ratio proximity (if auto)."""
    if allowed_families is None:
        allowed_families = TARGETS.keys()
    if device_hint in TARGETS and device_hint in allowed_families:
        return device_hint
    ar = aspect_ratio(w, h)
    fam_scores = {}
    for fam in TARGETS.keys():
        if fam not in allowed_families:
            continue
        fam_ars = []
        for _, orientations in iter_family_groups(fam):
            for orien, dims in orientations.items():
                fam_ars.extend([sw/sh for (sw, sh) in dims])
        if not fam_ars:
            continue
        fam_scores[fam] = min(abs(ar - far) for far in fam_ars)
    return min(fam_scores, key=fam_scores.get)

def pick_target(w, h, device_hint="auto", allowed_families=None):
    fam = nearest_family_by_aspect(w, h, device_hint, allowed_families)
    orien = orientation_of(w, h)

    ar_in = aspect_ratio(w, h)
    best = None
    best_score = math.inf
    best_group = None

    for group_label, orientations in iter_family_groups(fam):
        candidates = orientations.get(orien, [])
        if not candidates:
            # fallback to any orientation in this group
            candidates = [dim for dims in orientations.values() for dim in dims]
        for (tw, th) in candidates:
            ar_out = aspect_ratio(tw, th)
            ar_diff = abs(ar_in - ar_out)
            scale = max(tw / w, th / h)
            score = ar_diff * 10 + abs(scale - 1.0)
            if score < best_score:
                best_score = score
                best = (tw, th)
                best_group = group_label

    tw, th = best
    return tw, th, fam, orien, best_group

def candidate_targets_for(fam, group, source_orien, force_orientation="source"):
    """Return a list of (tw, th) target sizes for the given family+group and orientation selection."""
    orientations = TARGETS.get(fam, {}).get(group, {})
    if force_orientation == "portrait":
        orients = ["portrait"]
    elif force_orientation == "landscape":
        orients = ["landscape"]
    elif force_orientation == "both":
        orients = ["portrait", "landscape"]
    else:  # "source"
        orients = [source_orien]

    sizes = []
    for orien in orients:
        sizes.extend(orientations.get(orien, []))
    return sizes

def _score_match(in_w, in_h, tw, th):
    ar_in = aspect_ratio(in_w, in_h)
    ar_out = aspect_ratio(tw, th)
    ar_diff = abs(ar_in - ar_out)
    scale = max(tw / in_w, th / in_h)
    return ar_diff * 10 + abs(scale - 1.0)

def closest_size_from_list(in_w, in_h, sizes):
    best = None
    best_score = math.inf
    for (tw, th) in sizes:
        s = _score_match(in_w, in_h, tw, th)
        if s < best_score:
            best_score = s
            best = (tw, th)
    return best

def closest_size_for_group(in_w, in_h, fam, group_label, orient):
    orientations = TARGETS.get(fam, {}).get(group_label, {})
    sizes = orientations.get(orient, [])
    if not sizes:
        # fallback to any orientation in group
        sizes = [dim for dims in orientations.values() for dim in dims]
    if not sizes:
        return None
    return closest_size_from_list(in_w, in_h, sizes)

from typing import Tuple

def get_status_bar_height(family: str, group: str, target_w: int, target_h: int) -> int:
    """Get the appropriate status bar height for a device family and group, scaled to target resolution."""
    base_height = STATUS_BAR_HEIGHTS.get(family, {}).get(group, 0)
    if base_height == 0:
        return 0
    
    # Scale status bar height based on resolution
    # Use a reference resolution for scaling - iPhone 6/7/8 (750x1334) or iPad (1536x2048)
    if family == "iphone":
        # Scale based on width (iPhone reference: 375 points = 750 pixels @2x)
        scale_factor = target_w / 750.0
    elif family == "ipad":
        # Scale based on width (iPad reference: 768 points = 1536 pixels @2x) 
        scale_factor = target_w / 1536.0
    else:
        return base_height
    
    return max(1, int(round(base_height * scale_factor)))

def two_slice_resize_horizontal(bar_img: Image.Image, left_cap: int, right_cap: int, target_w: int, target_h: int) -> Image.Image:
    """Resize status bar by positioning left/right caps without stretching, filling middle with solid background."""
    w, h = bar_img.size
    
    # Use 1/3 of source width for each cap (ignore small command line arguments)
    left_cap = w // 3
    right_cap = w // 3
    
    # Ensure caps don't overlap (leave some space in middle)
    if left_cap + right_cap > w * 0.8:  # Leave at least 20% for middle
        left_cap = int(w * 0.35)
        right_cap = int(w * 0.35)

    left_region = bar_img.crop((0, 0, left_cap, h))
    right_region = bar_img.crop((w - right_cap, 0, w, h))

    # Scale parts proportionally to maintain aspect ratio
    scale_factor = target_h / h
    if scale_factor != 1.0:
        new_left_w = int(left_region.width * scale_factor)
        new_right_w = int(right_region.width * scale_factor)
        left_region = left_region.resize((new_left_w, target_h), Image.LANCZOS)
        right_region = right_region.resize((new_right_w, target_h), Image.LANCZOS)

    # Create canvas with solid background (sample from middle of original status bar)
    canvas = Image.new("RGBA", (target_w, target_h))
    
    # Sample background color from the middle of the original status bar
    middle_x = w // 2
    middle_sample = bar_img.crop((middle_x, 0, middle_x + 1, h))
    if target_h != h:
        middle_sample = middle_sample.resize((1, target_h), Image.LANCZOS)
    
    # Fill entire canvas with background color
    for x in range(target_w):
        canvas.paste(middle_sample, (x, 0))
    
    # Paste left cap at original position
    if left_region.width > 0:
        canvas.paste(left_region, (0, 0))
    
    # Paste right cap at the end
    if right_region.width > 0:
        canvas.paste(right_region, (target_w - right_region.width, 0))
    
    return canvas


def compose_cover_with_status_bar(src: Image.Image, target_w: int, target_h: int, sb_src_h: int, sb_target_h: int, left_cap: int, right_cap: int, content_mode: str = "cover") -> Image.Image:
    """Compose an image with a preserved status bar.
    Steps:
      1) Slice top sb_src_h from source as status bar.
      2) Fit the remainder to (target_w, target_h - sb_target_h) using specified content_mode.
      3) 2-slice-resize the status bar to (target_w, sb_target_h) and paste on top.
    """
    w, h = src.size
    sb_src_h = max(1, min(sb_src_h, h - 1))

    bar_strip = src.crop((0, 0, w, sb_src_h))
    content = src.crop((0, sb_src_h, w, h))

    content_target_h = max(1, target_h - sb_target_h)
    
    if content_mode == "contain":
        # Letterbox/pad to exact size
        content_fitted = ImageOps.pad(content, (target_w, content_target_h), method=Image.LANCZOS, color="black", centering=(0.5, 0.5))
    else:  # cover
        # Fill exactly, cropping as needed
        content_fitted = ImageOps.fit(content, (target_w, content_target_h), method=Image.LANCZOS, centering=(0.5, 0.5))

    bar_resized = two_slice_resize_horizontal(bar_strip, left_cap, right_cap, target_w, sb_target_h)

    # Composite
    if content_fitted.mode != "RGBA":
        content_fitted = content_fitted.convert("RGBA")
    if bar_resized.mode != "RGBA":
        bar_resized = bar_resized.convert("RGBA")

    canvas = Image.new("RGBA", (target_w, target_h))
    canvas.paste(bar_resized, (0, 0))
    canvas.paste(content_fitted, (0, sb_target_h))
    return canvas.convert("RGB")

def process_image(path, out_dir, mode, device_hint, quality, format_override, allowed_families, smartbar_orientations=None):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # honor device orientation
    w, h = img.size

    tw, th, fam, orien, group = pick_target(w, h, device_hint, allowed_families=allowed_families)

    # Determine which targets to produce
    jobs = []  # list of tuples (GROUP_LABEL, TW, TH)
    if getattr(args_namespace, "each_group", False):
        # One output per model group, optionally per orientation
        fam_groups = list(TARGETS.get(fam, {}).keys())
        force_or = getattr(args_namespace, "force_orientation", "source")
        for grp in fam_groups:
            if force_or == "both":
                orients = ["portrait", "landscape"]
            elif force_or in ("portrait", "landscape"):
                orients = [force_or]
            else:  # source
                orients = [orien]
            for orx in orients:
                best_pair = closest_size_for_group(w, h, fam, grp, orx)
                if best_pair:
                    jobs.append((grp, best_pair[0], best_pair[1]))
    else:
        # Original behavior: best group only
        if getattr(args_namespace, "all_sizes", False):
            sizes = candidate_targets_for(
                fam,
                group,
                orien,
                getattr(args_namespace, "force_orientation", "source"),
            )
            seen = set()
            sizes = [(x, y) for (x, y) in sizes if not ((x, y) in seen or seen.add((x, y)))]
            for (TW, TH) in sizes:
                jobs.append((group, TW, TH))
        else:
            jobs = [(group, tw, th)]

    last_out = None
    for (group_label, TW, TH) in jobs:
        # Determine current target orientation
        target_orien = orientation_of(TW, TH)
        
        # Check if we should use smartbar for this orientation
        use_smartbar = (smartbar_orientations and target_orien in smartbar_orientations)
        
        if mode == "cover" and not use_smartbar:
            # Fill exactly, cropping as needed
            out_img = ImageOps.fit(img, (TW, TH), method=Image.LANCZOS, centering=(0.5, 0.5))
        elif mode == "contain":
            # Letterbox/pad to exact size
            out_img = ImageOps.pad(img, (TW, TH), method=Image.LANCZOS, color=None, centering=(0.5, 0.5))
        elif mode == "stretch":
            # Distort to fit exact size (no aspect ratio preservation)
            out_img = img.resize((TW, TH), Image.LANCZOS)
        elif use_smartbar:
            # Use provided sb_src or derive from device type
            if args_namespace.sb_src is not None:
                sb_src = args_namespace.sb_src
            else:
                # Use device-appropriate status bar height scaled to source resolution
                sb_src = get_status_bar_height(fam, group_label, w, h)
                if sb_src == 0:
                    raise ValueError(f"No status bar defined for {fam} {group_label}. Use --sb-src to specify manually.")
            
            # Use provided sb_target or derive from device type  
            if args_namespace.sb_target is not None:
                sb_target = int(args_namespace.sb_target)
            else:
                # Use device-appropriate status bar height for target resolution
                sb_target = get_status_bar_height(fam, group_label, TW, TH)
                if sb_target == 0:
                    sb_target = sb_src  # fallback to source height
                    
            out_img = compose_cover_with_status_bar(
                img,
                TW,
                TH,
                sb_src_h=sb_src,
                sb_target_h=sb_target,
                left_cap=int(args_namespace.sb_left),
                right_cap=int(args_namespace.sb_right),
                content_mode=args_namespace.smartbar_mode,
            )
        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Build filename
        suffix = f"_{fam}_{TW}x{TH}"
        stem = Path(path).stem
        ext = (format_override or Path(path).suffix.lstrip(".") or "png").lower()
        # Normalize to jpg/png; HEIC etc. become JPG by default
        if ext in ("heic", "heif", "tif", "tiff", "bmp", "webp"):
            ext = "jpg"
        out_name = f"{stem}{suffix}.{ext}"
        fam_dir = Path(out_dir) / fam / group_label
        fam_dir.mkdir(parents=True, exist_ok=True)
        out_path = fam_dir / out_name

        save_kwargs = {}
        if ext in ("jpg", "jpeg"):
            save_kwargs.update({"quality": quality, "optimize": True, "progressive": True})
        out_img.save(out_path, **save_kwargs)
        last_out = out_path

    # Return info about the last-produced file
    return last_out, fam, orien, (TW, TH)

def iter_paths(input_path):
    p = Path(input_path)
    exts = {".png", ".jpg", ".jpeg", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp"}
    if p.is_file():
        if p.suffix.lower() in exts:
            yield p
        return
    for fp in p.rglob("*"):
        if fp.is_file() and fp.suffix.lower() in exts:
            yield fp

def main():
    ap = argparse.ArgumentParser(
        description="Resize device screenshots to the closest or all allowed sizes by family and model group (cover/contain/stretch/cover_smartbar). Supports per-group output via --each-group."
    )
    ap.add_argument("input", nargs="+", help="Input file(s) or directory(ies)")
    ap.add_argument("-o", "--output", default="resized", help="Output directory (default: ./resized)")
    ap.add_argument("--device", choices=["auto", "ipad", "iphone"], default="auto",
                    help="Force device family or auto-detect by aspect ratio (default: auto)")
    ap.add_argument("--mode", choices=["cover", "contain", "stretch", "cover_smartbar"], default="cover",
                    help="cover: fill target (crop if needed); contain: letterbox; stretch: distort to fit; cover_smartbar: cover but preserve status bar by 2-slice (default: cover)")
    ap.add_argument("--quality", type=int, default=92, help="JPEG quality (default: 92)")
    ap.add_argument("--format", choices=["jpg", "png"], help="Force output format (optional)")
    ap.add_argument("--families", default="iphone,ipad",
                    help=f"Comma-separated list of families to consider (choices: {','.join(TARGETS.keys())}; default: iphone,ipad)")
    ap.add_argument("--all-sizes", action="store_true",
                    help="Generate outputs for ALL target sizes in the matched family/group instead of only the closest one")
    ap.add_argument("--force-orientation", choices=["source", "portrait", "landscape", "both"], default="source",
                    help="Which orientation set(s) to use within the group: use the source image orientation, force portrait, force landscape, or both")
    ap.add_argument("--each-group", action="store_true",
                    help="Generate one output per model group (e.g., iPad (12.9), iPad (11), etc.). With --force-orientation both, produces one portrait and one landscape per group.")
    ap.add_argument("--smartbar", choices=["portrait", "landscape", "both"], default=None,
                    help="Enable smart status bar handling for specific orientation(s): portrait, landscape, or both")
    ap.add_argument("--smartbar-mode", choices=["cover", "contain"], default="cover",
                    help="How to resize content below status bar: cover (crop to fill) or contain (letterbox)")
    ap.add_argument("--sb-src", type=int, default=None,
                    help="Source status bar height in pixels (optional; uses device-appropriate height if not specified)")
    ap.add_argument("--sb-target", type=int, default=None,
                    help="Override target status bar height in pixels (optional; otherwise uses device-appropriate scaled height)")
    ap.add_argument("--sb-left", type=int, default=200,
                    help="Left cap width for 2-slice status bar (pixels)")
    ap.add_argument("--sb-right", type=int, default=200,
                    help="Right cap width for 2-slice status bar (pixels)")
    args = ap.parse_args()

    # Store smartbar orientation preference for later use
    smartbar_orientations = set()
    if args.smartbar:
        if args.smartbar == "both":
            smartbar_orientations = {"portrait", "landscape"}
        else:
            smartbar_orientations = {args.smartbar}

    global args_namespace
    args_namespace = args

    selected_families = [f.strip() for f in args.families.split(",") if f.strip()]
    invalid_families = [f for f in selected_families if f not in TARGETS]
    if invalid_families:
        print(f"Error: Invalid families specified: {', '.join(invalid_families)}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    for input_path in args.input:
        for p in iter_paths(input_path):
            try:
                out_path, fam, orien, size = process_image(
                    p, out_dir, args.mode, args.device, args.quality, args.format, allowed_families=selected_families, smartbar_orientations=smartbar_orientations
                )
                processed += 1
                print(f"✓ {p.name} → {out_path.name} ({fam}, {orien}, {size[0]}x{size[1]})")
            except Exception as e:
                print(f"✗ {p}: {e}", file=sys.stderr)

    if processed == 0:
        print("No matching images found.", file=sys.stderr)

if __name__ == "__main__":
    main()