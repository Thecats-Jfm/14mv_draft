# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['mv_draft/__main__.py'],
             pathex=['E:\workarea for vsc\14mv_draft'], # 替换为你的项目根目录的绝对路径
             binaries=[],
             datas=[('img/*', 'img')], # 包含img目录下所有文件
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='14mvd', # 你可以自定义这个名称，确保它与你的应用相关
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True, # 如果你的应用不需要控制台窗口，可以设置为False
          disable_windowed_traceback=False,
          argv_emulation=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)
