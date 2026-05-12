# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PyQt6.sip',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        'PIL',
        'PIL.Image',
        'pptx',
        'pptx.util',
        'pptx.dml.color',
        'pptx.enum.text',
        'pptx.enum.shapes',
        'reportlab',
        'reportlab.lib.pagesizes',
        'reportlab.pdfgen.canvas',
        'pandas',
        'pandas.core',
        'sqlite3',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'lxml',
        'lxml.etree',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_qt5agg',
        'mplcursors',
        'httpx',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
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
    [],
    exclude_binaries=True,
    name='AuditarContabilidade',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo_auditar.png',
)

# Criar pasta do app (mais estável que .exe único para PyQt6)
app_folder = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AuditarContabilidade'
)
