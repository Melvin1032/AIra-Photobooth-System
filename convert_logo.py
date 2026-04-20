"""
Convert PNG logo to ICO format for Windows application icon
"""
from PIL import Image
from pathlib import Path

def convert_logo():
    """Convert MAIN-LOGO.png to .ico format with maximum HD quality"""
    
    logo_path = Path("assets/MAIN-LOGO.png")
    if not logo_path.exists():
        print(f"❌ Logo not found: {logo_path}")
        return False
    
    print(f"✓ Found logo: {logo_path}")
    
    # Open the image
    img = Image.open(logo_path)
    
    # Convert to RGBA if needed (preserves transparency)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    print(f"  Original size: {img.size}")
    print(f"  Mode: {img.mode}")
    
    # Create ICO with ALL standard Windows icon sizes for maximum quality
    # Windows will automatically pick the best size for each context
    icon_sizes = [
        (16, 16),    # Taskbar small, File explorer list
        (24, 24),    # Taskbar medium
        (32, 32),    # Desktop icon, Start menu
        (40, 40),    # Taskbar large
        (48, 48),    # File explorer large icons
        (64, 64),    # Extra large
        (72, 72),    # Windows 10/11 medium
        (96, 96),    # Windows 10/11 large
        (128, 128),  # Very large (HiDPI)
        (256, 256),  # Maximum size (4K displays)
    ]
    
    # Resize for each size using highest quality algorithm
    icons = []
    for size in icon_sizes:
        # Use LANCZOS for highest quality downsampling
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
        print(f"  ✓ Created {size[0]}x{size[1]} icon (HD quality)")
    
    # Save as ICO with all sizes embedded
    output_path = Path("assets/app_icon.ico")
    
    # Use iconbitmap method for better quality multi-resolution ICO
    try:
        import io
        icon_images = []
        for icon in icons:
            buffer = io.BytesIO()
            icon.save(buffer, format='PNG')
            icon_images.append(buffer.getvalue())
        
        # Write ICO file manually for maximum quality
        with open(output_path, 'wb') as f:
            # ICO header
            f.write(b'\x00\x00')  # Reserved
            f.write(b'\x01\x00')  # ICO type (1 = icon)
            f.write(len(icons).to_bytes(2, 'little'))  # Number of images
            
            # Calculate offset (header + directory entries)
            offset = 6 + (len(icons) * 16)
            
            # Write directory entries
            for i, icon in enumerate(icons):
                width = icon.size[0] if icon.size[0] < 256 else 0
                height = icon.size[1] if icon.size[1] < 256 else 0
                f.write(bytes([width]))  # Width
                f.write(bytes([height]))  # Height
                f.write(b'\x00')  # Color palette
                f.write(b'\x00')  # Reserved
                f.write(b'\x01\x00')  # Color planes
                f.write(b'\x20\x00')  # Bits per pixel (32)
                png_data = icon_images[i]
                f.write(len(png_data).to_bytes(4, 'little'))  # Size
                f.write(offset.to_bytes(4, 'little'))  # Offset
                offset += len(png_data)
            
            # Write PNG data
            for png_data in icon_images:
                f.write(png_data)
        
        print(f"  ✓ Used high-quality multi-resolution ICO format")
    except Exception as e:
        print(f"  ⚠️  Fallback to standard ICO: {e}")
        icons[0].save(
            output_path,
            format='ICO',
            sizes=[(icon.size[0], icon.size[1]) for icon in icons]
        )
    
    file_size_kb = output_path.stat().st_size / 1024
    print(f"\n✅ HD Icon created: {output_path}")
    print(f"   Size: {file_size_kb:.1f} KB")
    print(f"   Resolutions: {len(icon_sizes)} sizes (16px to 256px)")
    print(f"   Quality: Maximum (LANCZOS resampling + PNG compression)")
    
    return True

if __name__ == "__main__":
    convert_logo()
