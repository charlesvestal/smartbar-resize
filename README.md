# Smartbar Resize

A Python utility for intelligently resizing device screenshots and videos to App Store Connect specifications while preserving status bars with proper proportions.

## Features

- **Smart Status Bar Preservation**: Maintains authentic status bar appearance using 2-slice horizontal resizing
- **Video + Image Support**: Process both screenshots and app preview videos with correct App Store Connect dimensions
- **Orientation-Specific Control**: Apply status bar handling only to portrait, landscape, or both orientations  
- **Multiple Content Modes**: Choose between cover (crop to fill) or contain (letterbox) for content below status bar
- **Multi-Device Support**: Generate outputs for all iOS device sizes automatically
- **Flexible Input**: Process individual files, directories, or use glob patterns
- **Device Family Detection**: Automatically detect iPad vs iPhone based on aspect ratio
- **Video Quality Control**: Configurable codec and quality settings for video output

## Installation

Requires Python 3.6+, PIL/Pillow, and FFmpeg:

```bash
pip install Pillow

# Install FFmpeg (for video processing)
# macOS: brew install ffmpeg
# Ubuntu/Debian: apt install ffmpeg
# Windows: Download from https://ffmpeg.org/
```

## Quick Start

### Basic Usage

```bash
# Resize all images in a directory for iPad
python resize_screenshots.py screenshots/ --device ipad --families ipad --each-group

# iPhone with status bar only on portrait orientation  
python resize_screenshots.py screenshots/ --device iphone --families iphone --each-group --smartbar portrait

# iPad with status bar on both orientations, letterboxed content
python resize_screenshots.py screenshots/ --device ipad --families ipad --each-group --smartbar both --smartbar-mode contain

# Process videos for iPhone app previews (uses App Store Connect video dimensions)
python resize_screenshots.py videos/*.mp4 --device iphone --families iphone --each-group --mode contain

# Mixed images and videos with custom video quality
python resize_screenshots.py content/ --families iphone,ipad --each-group --video-codec libx265 --video-crf 28
```

### Target Specific Files

```bash
# Only process files containing "menu" in filename
python resize_screenshots.py screenshots/*menu* --device ipad --families ipad --each-group --mode stretch

# Multiple patterns
python resize_screenshots.py screenshots/*menu* screenshots/*settings* --device ipad --each-group
```

## Command Line Options

### Core Options
- `input` - Input file(s) or directory(ies). Supports glob patterns.
- `--device {auto,ipad,iphone}` - Force device family or auto-detect (default: auto)
- `--families FAMILIES` - Comma-separated device families to generate (default: iphone,ipad)
- `--each-group` - Generate outputs for every device model group
- `-o, --output OUTPUT` - Output directory (default: ./resized)

### Resize Modes
- `--mode {cover,contain,stretch}` - Base resize mode:
  - `cover`: Fill target exactly, cropping as needed (default)
  - `contain`: Letterbox/pad to exact size
  - `stretch`: Distort to fit exact size

### Smart Status Bar Options
- `--smartbar {portrait,landscape,both}` - Enable smart status bar for specific orientations
- `--smartbar-mode {cover,contain}` - How to resize content below status bar (default: cover)
- `--sb-src SB_SRC` - Override source status bar height in pixels
- `--sb-target SB_TARGET` - Override target status bar height in pixels
- `--sb-left SB_LEFT` - Left cap width for status bar (default: 200)
- `--sb-right SB_RIGHT` - Right cap width for status bar (default: 200)

### Advanced Options
- `--all-sizes` - Generate ALL target sizes in matched family/group instead of closest match
- `--force-orientation {source,portrait,landscape,both}` - Override orientation detection
- `--quality QUALITY` - JPEG quality (default: 92)
- `--format {jpg,png}` - Force output format

### Video Options
- `--video-codec CODEC` - Video codec for output (default: libx264)
- `--video-crf CRF` - Video CRF quality 0-51, lower is better (default: 18 for App Store Connect)
- `--app-store-optimize` - Use App Store Connect optimized settings (H.264 High Profile, 30fps max)

## Examples

### App Store Screenshots

```bash
# iPhone App Store screenshots (status bar on portrait only)
python resize_screenshots.py iphone_screenshots/ \
  --device iphone --families iphone --each-group \
  --smartbar portrait --smartbar-mode contain

# iPad App Store screenshots (status bar on both orientations)
python resize_screenshots.py ipad_screenshots/ \
  --device ipad --families ipad --each-group \
  --smartbar both --smartbar-mode contain
```

### Marketing Materials

```bash
# Simple resize without status bar processing
python resize_screenshots.py marketing/ \
  --families iphone,ipad --each-group --mode contain

# Stretch specific promotional images
python resize_screenshots.py promo/*hero* --mode stretch --each-group
```

## Visual Examples

### Before and After Comparison

#### iPad Landscape with Smart Status Bar

**Before** (Source: iPad landscape screenshot)

<img src="https://raw.githubusercontent.com/charlesvestal/smartbar-resize/main/examples/input/source_ipad_landscape.png" height="400" alt="iPad Source">

**After** (Resized to iPad 11" with preserved status bar)

<img src="https://raw.githubusercontent.com/charlesvestal/smartbar-resize/main/examples/output/ipad/iPad%20(11)/source_ipad_landscape_ipad_2388x1668.png" height="400" alt="iPad Output">

**What Changed:**
- Status bar "Screens 6:16 AM Fri Aug 29" text preserved without stretching
- Status bar icons (WiFi, VPN, 82%, battery) maintain proper proportions
- Content area resized to fit target resolution while preserving aspect ratio
- Overall image resized from source dimensions to iPad 11" specifications (2388x1668)

#### iPhone Portrait with Smart Status Bar

**Before** (Source: iPhone portrait screenshot)

<img src="https://raw.githubusercontent.com/charlesvestal/smartbar-resize/main/examples/input/source_iphone_portrait.png" height="400" alt="iPhone Source">

**After** (Resized to iPhone 6.9" with preserved status bar)

<img src="https://raw.githubusercontent.com/charlesvestal/smartbar-resize/main/examples/output/iphone/iPhone%20(6.9)/source_iphone_portrait_iphone_1320x2868.png" height="400" alt="iPhone Output">

**What Changed:**
- Status bar "15:41" and status icons preserved at correct proportions
- Content area below status bar resized to target dimensions
- No stretching or distortion of UI elements in status bar
- Resized to iPhone 6.9" specifications (1320x2868)

## Video vs Screenshot Dimensions

The utility automatically uses different target dimensions for videos vs screenshots:

### App Preview Videos (when processing .mp4, .mov, etc.)
- **iPhone 6.9"**: 886×1920 (portrait), 1920×886 (landscape) 
- **iPhone 6.5"/6.3"/6.1"**: 886×1920 (portrait), 1920×886 (landscape)
- **iPhone 5.5"/4.0"**: 1080×1920 (portrait), 1920×1080 (landscape)
- **iPhone 4.7"**: 750×1334 (portrait), 1334×750 (landscape)
- **iPad 13"/12.9"/11"/10.5"**: 1200×1600 (portrait), 1600×1200 (landscape)
- **iPad 9.7"**: 900×1200 (portrait), 1200×900 (landscape)

### Screenshots (when processing .png, .jpg, etc.)
- Uses full App Store Connect screenshot specifications
- Much higher resolution than videos (e.g. iPhone 6.9" screenshots are 1290×2796)

## App Store Connect Compliance

The utility automatically validates and enforces App Store Connect requirements for videos:

### Automatic Validation
- **Framerate**: Automatically limits to 30fps maximum (reduces higher framerates)
- **Duration**: Warns if video is shorter than 15s or longer than 30s
- **File Size**: Warns if source video exceeds 500MB limit
- **Dimensions**: Uses exact App Store Connect app preview dimensions

### Optimization Options
```bash
# Use App Store Connect optimized settings
python resize_screenshots.py videos/ --app-store-optimize --families iphone --each-group

# Custom high-quality settings  
python resize_screenshots.py videos/ --video-codec libx264 --video-crf 15 --families ipad
```

## How Smart Status Bar Works

1. **Status Bar Extraction**: The top portion of the source image is identified as the status bar
2. **2-Slice Resizing**: Status bar is divided into left and right caps (preserving text/icons) with middle filled
3. **Content Processing**: The remaining image content is resized using the specified mode (cover/contain)
4. **Composition**: Status bar and content are recombined at target resolution

This approach ensures:
- Status bar text remains crisp and properly proportioned
- Device-specific status bar heights are automatically applied
- Content aspect ratios are preserved or letterboxed as desired

## Supported Devices

### iPhone
- iPhone (6.9") - 16 Pro Max series
- iPhone (6.5") - Pro Max series with Dynamic Island  
- iPhone (6.3") - Pro series with Dynamic Island
- iPhone (6.1") - Standard series with Dynamic Island/Face ID
- iPhone (5.5") - Plus series
- iPhone (4.7") - Standard series (6/7/8)
- iPhone (4.0") - SE/5 series
- iPhone (3.5") - 4/4S series

### iPad
- iPad (12.9") - Pro 12.9" series
- iPad (11") - Pro 11"/Air series
- iPad (10.5") - Pro 10.5" series  
- iPad (9.7") - Standard/Air series

### Other Platforms
- Mac, Apple TV, Vision Pro, Apple Watch (basic resize support)

## Output Structure

```
resized/
├── iphone/
│   ├── iPhone (6.1)/
│   │   ├── screenshot1_iphone_1170x2532.png
│   │   └── screenshot2_iphone_2532x1170.png
│   └── iPhone (6.5)/
│       ├── screenshot1_iphone_1284x2778.png
│       └── screenshot2_iphone_2778x1284.png
└── ipad/
    ├── iPad (11)/
    │   ├── screenshot1_ipad_1668x2388.png
    │   └── screenshot2_ipad_2388x1668.png
    └── iPad (12.9)/
        ├── screenshot1_ipad_2048x2732.png
        └── screenshot2_ipad_2732x2048.png
```

## License

MIT License - Feel free to use and modify for your projects.