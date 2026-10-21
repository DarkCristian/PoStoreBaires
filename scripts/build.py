"""Build a native portable folder on the current OS; never cross-compile."""
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys
from importlib import metadata

ROOT = Path(__file__).resolve().parents[1]

def build():
    if platform.system() not in ('Windows', 'Linux'):
        raise SystemExit('Esta beta tiene build preparado para Windows y Linux.')
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
               '--windowed', '--name', 'PoStoreBaires', '--distpath', str(ROOT/'dist'),
               '--workpath', str(ROOT/'build'), '--specpath', str(ROOT/'build'),
               '--paths', str(ROOT), '--hidden-import', 'PySide6.QtSvg',
               '--add-data', str(ROOT/'postorebaires/assets')+os.pathsep+'postorebaires/assets',
               '--exclude-module', 'PySide6.QtWebEngineCore',
               '--exclude-module', 'PySide6.QtWebEngineWidgets',
               '--exclude-module', 'PySide6.QtQml', str(ROOT/'run.py')]
    subprocess.run(command, cwd=ROOT, check=True)
    dest = ROOT/'dist/PoStoreBaires'
    for name in ('LICENSE','README.md','main.md','VERSION','CHANGELOG.md','SECURITY.md','THIRD_PARTY.md'):
        shutil.copy2(ROOT/name, dest/name)
    shutil.copytree(ROOT/'licenses', dest/'licenses', dirs_exist_ok=True)
    notices = dest/'licenses/dependencies'
    notices.mkdir(parents=True, exist_ok=True)
    for name in ('PySide6', 'PySide6-Essentials', 'PySide6-Addons', 'shiboken6', 'pyinstaller'):
        distribution = metadata.distribution(name)
        target = notices/name
        target.mkdir(exist_ok=True)
        (target/'METADATA.txt').write_text(distribution.read_text('METADATA') or '', encoding='utf-8')
        for item in distribution.files or []:
            if 'license' in str(item).lower() or 'copying' in str(item).lower():
                source = Path(distribution.locate_file(item))
                if source.is_file() and '__pycache__' not in source.parts:
                    shutil.copy2(source, target/source.name)
    for candidate in (Path(sys.base_prefix)/'LICENSE.txt',
                      Path(sys.base_prefix)/'lib/python3.12/LICENSE.txt'):
        if candidate.is_file():
            shutil.copy2(candidate, dest/'licenses/Python-LICENSE.txt')
            break
    shutil.copytree(ROOT/'docs', dest/'docs', dirs_exist_ok=True)
    print('Native build completed on '+platform.system()+': '+str(dest))
    return dest

if __name__ == '__main__':
    build()
