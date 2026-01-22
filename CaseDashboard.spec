# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ui', 'ui')],
    hiddenimports=['ui.launcher', 'ui.dashboard', 'ui.panels', 'ui.widgets', 'ui.widgets.calendar_widget', 'ui.widgets.weather_widget', 'ui.widgets.habit_tracker_widget', 'ui.widgets.motivational_quote_widget', 'ui.widgets.system_stats_widget', 'ui.widgets.countdown_widget', 'ui.widgets.sticky_notes_widget', 'ui.widgets.media_controls_widget', 'ui.widgets.focus_music_widget', 'ui.widgets.github_notifications_widget'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CaseDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
