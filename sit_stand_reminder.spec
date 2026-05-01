# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

ttkbootstrap_datas, ttkbootstrap_binaries, ttkbootstrap_hiddenimports = collect_all("ttkbootstrap")

a = Analysis(
    ["launch.py"],
    pathex=[],
    binaries=ttkbootstrap_binaries,
    datas=[("images/*.png", "images"), ("audio/*.wav", "audio")] + ttkbootstrap_datas,
    hiddenimports=["PIL", "PIL.Image", "PIL.ImageTk"] + ttkbootstrap_hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="sit_stand_reminder",
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
