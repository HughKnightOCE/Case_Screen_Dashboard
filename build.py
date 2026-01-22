#!/usr/bin/env python3
"""
Build script for Case Screen Dashboard using PyInstaller.
"""

import subprocess
import sys
import shutil
import os
from pathlib import Path

def build():
    try:
        # Clean previous build
        dist_dir = Path("dist")
        if dist_dir.exists():
            try:
                shutil.rmtree(dist_dir)
            except PermissionError:
                print("Error: Cannot remove dist directory. Please close any running instances of CaseDashboard.exe and try again.")
                sys.exit(1)
        
        # Ensure the ui package and widget modules are included in the build
        hidden = [
            'ui.launcher', 'ui.dashboard', 'ui.panels', 'ui.widgets',
            'ui.widgets.calendar_widget', 'ui.widgets.weather_widget',
            'ui.widgets.habit_tracker_widget', 'ui.widgets.motivational_quote_widget',
            'ui.widgets.system_stats_widget', 'ui.widgets.countdown_widget',
            'ui.widgets.sticky_notes_widget', 'ui.widgets.media_controls_widget',
            'ui.widgets.focus_music_widget', 'ui.widgets.github_notifications_widget'
        ]

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "CaseDashboard",
        ]

        # Add ui package as data
        cmd.extend(["--add-data", f"ui{os.pathsep}ui"])

        # If an icon exists at assets/icon.ico, embed it into the EXE
        icon_path = Path("assets") / "icon.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

        for h in hidden:
            cmd.extend(["--hidden-import", h])

        cmd.append("main.py")
        subprocess.run(cmd, check=True)
        print("Build successful. Executable in dist/ directory.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()