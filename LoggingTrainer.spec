from pathlib import Path


project_dir = Path.cwd()

a = Analysis(
    [str(project_dir / "run_trainer.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[(str(project_dir / "assets" / "audio"), "assets/audio")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["kokoro", "numpy", "soundfile", "torch"],
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
    name="LoggingTrainer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
