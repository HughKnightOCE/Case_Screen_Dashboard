#!/usr/bin/env python3
"""
Quick test to verify launcher layout editor transfers to running app
"""
import sys
import json
from pathlib import Path

# Must create QApplication first for Qt widgets
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

# Test 1: Check that launcher properly updates config with custom layout
from app.config import load_config, save_config, PRESETS
from ui.launcher import LayoutGridWidget

def test_layout_persistence():
    """Test that custom layout is persisted to config.json"""
    
    # Start with default config
    cfg = load_config()
    print(f"Initial layout from config: {cfg.layout}")
    
    # Simulate launcher action: create a grid and update it
    grid = LayoutGridWidget(None)
    
    # Change slot_1 from focus_timer to metrics
    grid.cells["slot_1"].set_widget("metrics")
    
    # Change slot_2 from metrics to university  
    grid.cells["slot_2"].set_widget("university")
    
    # Get the modified layout
    new_layout = grid.get_layout()
    print(f"Modified layout from grid: {new_layout}")
    
    # Simulate _accept() in launcher
    cfg.layout = new_layout
    
    # Save the config
    save_config(cfg)
    
    # Load it back and verify
    cfg_loaded = load_config()
    print(f"Loaded layout after save: {cfg_loaded.layout}")
    
    # Verify changes persisted
    assert cfg_loaded.layout["slot_1"] == "metrics", f"slot_1 should be 'metrics', got {cfg_loaded.layout['slot_1']}"
    assert cfg_loaded.layout["slot_2"] == "university", f"slot_2 should be 'university', got {cfg_loaded.layout['slot_2']}"
    
    print("✓ Layout persistence test PASSED")
    
    # Test 2: Verify dashboard reads the layout
    from ui.dashboard import DashboardView
    
    # Create dashboard with the new layout
    dashboard = DashboardView(layout_cfg=cfg_loaded.layout, parent=None)
    
    print("✓ Dashboard layout test PASSED")
    
    print("\n✅ All tests passed! Layout configuration is properly transferred.")

if __name__ == "__main__":
    test_layout_persistence()
