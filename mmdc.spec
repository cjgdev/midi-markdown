# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MIDI Markdown compiler.

This configuration creates a onedir distribution for optimal startup performance.
Based on research findings: onedir mode provides 3x faster startup than onefile.

Build with: pyinstaller mmdc.spec
"""

from PyInstaller.utils.hooks import copy_metadata, collect_data_files
import os
import sys

# Get the absolute path to the project root
project_root = os.path.abspath('.')
src_dir = os.path.join(project_root, 'src')

# Add source directory to path for imports
sys.path.insert(0, src_dir)

# Import version from package
from midi_markdown import __version__

block_cipher = None

# Collect metadata for packages that need it
datas = []
datas += copy_metadata('rich')  # Rich needs metadata for version detection
datas += copy_metadata('typer')  # Typer may need metadata
datas += copy_metadata('mido')   # MIDI library metadata

# Include the Lark grammar file (critical - parser won't work without it)
datas += [(os.path.join(src_dir, 'midi_markdown', 'parser', 'mmd.lark'),
           'midi_markdown/parser')]

# Optionally include device libraries as bundled resources
# Uncomment to bundle device libraries with the executable
# datas += [(os.path.join(project_root, 'devices'), 'devices')]

# Optionally include example files
# Uncomment to bundle examples with the executable
# datas += [(os.path.join(project_root, 'examples'), 'examples')]

# Hidden imports required by dependencies
hiddenimports = [
    # Typer/Click shell completion support
    'shellingham.posix',
    'shellingham.nt',

    # Python-rtmidi platform-specific modules
    'rtmidi',
    'rtmidi.midiconstants',

    # Lark parser internals (may be auto-detected, but explicit is safer)
    'lark',
    'lark.parsers',
    'lark.lexer',

    # Rich terminal detection
    'pygments',
    'pygments.lexers',
    'pygments.formatters',

    # YAML frontmatter parsing
    'yaml',

    # Ensure all midi_markdown submodules are included
    'midi_markdown.cli',
    'midi_markdown.cli.main',
    'midi_markdown.cli.commands',
    'midi_markdown.parser',
    'midi_markdown.midi',
    'midi_markdown.alias',
    'midi_markdown.expansion',
    'midi_markdown.utils',
    'midi_markdown.utils.validation',
]

# Analysis configuration
a = Analysis(
    [os.path.join(src_dir, 'midi_markdown', '__main__.py')],  # Entry point
    pathex=[src_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        '_tkinter',
        'tk',
        'tcl',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Onedir mode - binaries separate from exe
    name='mmdc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression for smaller size
    console=True,  # CLI tool MUST use console mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file when available
)

# Collect all files into the distribution directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mmdc',
)

# macOS-specific: Create .app bundle
# Uncomment for macOS builds
# app = BUNDLE(
#     coll,
#     name='mmdc.app',
#     icon=None,  # TODO: Add .icns icon
#     bundle_identifier='com.midimarkdown.mmdc',
#     version=__version__,
#     info_plist={
#         'CFBundleName': 'MIDI Markdown Compiler',
#         'CFBundleDisplayName': 'mmdc',
#         'CFBundleVersion': __version__,
#         'CFBundleShortVersionString': __version__,
#         'NSHumanReadableCopyright': 'MIT License',
#         'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra
#         'NSHighResolutionCapable': True,
#     },
# )
