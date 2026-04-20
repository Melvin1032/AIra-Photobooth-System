"""Test QR code generation and display."""

import sys
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.qr_server import QRCodeServer

def test_qr_generation():
    """Test QR code generation with a sample photo."""
    print("=" * 60)
    print("QR CODE GENERATION TEST")
    print("=" * 60)
    
    # Initialize QR server
    qr_server = QRCodeServer()
    
    if not qr_server.base_url:
        print("\n❌ ERROR: QR server failed to start!")
        print("Check if port 8080 is available.")
        return
    
    print(f"\n✓ Server running at: {qr_server.base_url}")
    
    # Find a test photo
    test_photo = Path("events/raw/capture_20260420_213225.jpg")
    
    # Try to find any photo in events/raw
    if not test_photo.exists():
        raw_dir = Path("events/raw")
        if raw_dir.exists():
            photos = list(raw_dir.glob("*.jpg"))
            if photos:
                test_photo = photos[0]
                print(f"\n✓ Using test photo: {test_photo.name}")
            else:
                print("\n❌ No test photos found in events/raw/")
                print("Please take a photo first, then test again.")
                return
        else:
            print("\n❌ events/raw/ directory not found!")
            return
    
    # Generate QR code
    print(f"\nGenerating QR code for: {test_photo.name}")
    qr_image = qr_server.generate_qr_code(str(test_photo), size=300)
    
    if qr_image:
        print(f"\n✓ QR code generated successfully!")
        print(f"✓ Size: {qr_image.size[0]}x{qr_image.size[1]} pixels")
        
        # Save QR code for inspection
        qr_output = Path("test_qr_code.png")
        qr_image.save(qr_output)
        print(f"✓ QR code saved to: {qr_output}")
        print(f"\nYou can now:")
        print(f"  1. Open {qr_output} and try scanning it with your phone")
        print(f"  2. Check if the URL in the QR code is accessible:")
        print(f"     {qr_server.base_url}/{test_photo.name}")
        print(f"\nIf the QR code scans successfully, your phone should show:")
        print(f"  - A download page with your photo")
        print(f"  - A 'Download Photo' button")
    else:
        print("\n❌ Failed to generate QR code!")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    # Cleanup
    qr_server.stop()

if __name__ == "__main__":
    test_qr_generation()
