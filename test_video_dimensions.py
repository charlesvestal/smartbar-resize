#!/usr/bin/env python3
"""Test video dimensions are correct"""

# Import the functions from our script
import sys
sys.path.append('.')

try:
    from resize_screenshots import VIDEO_TARGETS, pick_target
    
    def test_iphone_6_9_video():
        """Test iPhone 6.9 video targeting"""
        # Simulate a 1920x886 landscape video input
        tw, th, fam, orien, group = pick_target(1920, 886, "iphone", ["iphone"], use_video_targets=True)
        
        print(f"Input: 1920x886 landscape video")
        print(f"Target: {tw}x{th} ({fam}, {orien}, {group})")
        
        # Should target iPhone 6.9" landscape: 1920x886
        assert tw == 1920 and th == 886, f"Expected 1920x886, got {tw}x{th}"
        assert fam == "iphone", f"Expected iphone, got {fam}"
        assert orien == "landscape", f"Expected landscape, got {orien}"
        assert "6.9" in group, f"Expected iPhone 6.9, got {group}"
        
        print("✓ iPhone 6.9 landscape video targeting works correctly")
        
    def test_iphone_portrait_video():
        """Test iPhone portrait video targeting"""  
        # Simulate a 886x1920 portrait video input
        tw, th, fam, orien, group = pick_target(886, 1920, "iphone", ["iphone"], use_video_targets=True)
        
        print(f"\nInput: 886x1920 portrait video")
        print(f"Target: {tw}x{th} ({fam}, {orien}, {group})")
        
        # Should target iPhone portrait: 886x1920
        assert tw == 886 and th == 1920, f"Expected 886x1920, got {tw}x{th}"
        assert fam == "iphone", f"Expected iphone, got {fam}"
        assert orien == "portrait", f"Expected portrait, got {orien}"
        
        print("✓ iPhone portrait video targeting works correctly")
        
    def test_ipad_video():
        """Test iPad video targeting"""
        # Simulate a 1600x1200 landscape video input
        tw, th, fam, orien, group = pick_target(1600, 1200, "ipad", ["ipad"], use_video_targets=True)
        
        print(f"\nInput: 1600x1200 landscape video")
        print(f"Target: {tw}x{th} ({fam}, {orien}, {group})")
        
        # Should target iPad landscape: 1600x1200
        assert tw == 1600 and th == 1200, f"Expected 1600x1200, got {tw}x{th}"
        assert fam == "ipad", f"Expected ipad, got {fam}"
        assert orien == "landscape", f"Expected landscape, got {orien}"
        
        print("✓ iPad landscape video targeting works correctly")
        
    def test_video_vs_screenshot_dimensions():
        """Test that video and screenshot dimensions are different"""
        # Same input dimensions, different targets
        screenshot_target = pick_target(1920, 886, "iphone", ["iphone"], use_video_targets=False)
        video_target = pick_target(1920, 886, "iphone", ["iphone"], use_video_targets=True)
        
        print(f"\nSame input (1920x886):")
        print(f"Screenshot target: {screenshot_target[0]}x{screenshot_target[1]}")
        print(f"Video target: {video_target[0]}x{video_target[1]}")
        
        # They should be different
        assert screenshot_target[:2] != video_target[:2], "Screenshot and video targets should be different"
        print("✓ Video and screenshot dimensions are properly separated")
        
    # Run tests
    test_iphone_6_9_video()
    test_iphone_portrait_video() 
    test_ipad_video()
    test_video_vs_screenshot_dimensions()
    
    print("\n✅ All video dimension tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)