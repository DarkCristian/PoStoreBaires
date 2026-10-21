"""Package native Windows ZIP, Linux tar.gz and corresponding source."""
from pathlib import Path
import argparse
import hashlib
import platform
import tarfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def write_zip(target, files):
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for path,name in files:
            info=zipfile.ZipInfo(name,(2026,10,21,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(path.stat().st_mode & 0xFFFF)<<16
            z.writestr(info,path.read_bytes())
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:raise ValueError('Invalid ZIP')

def package(source_only=False,binary_only=False):
    version=(ROOT/'VERSION').read_text().strip()
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    archives=[]
    if not binary_only:
        excluded={'.git','dist','build','.venv','__pycache__'}
        files=[(p,'PoStoreBaires/'+p.relative_to(ROOT).as_posix()) for p in sorted(ROOT.rglob('*'))
               if p.is_file() and not excluded.intersection(p.relative_to(ROOT).parts) and p.suffix!='.pyc']
        source=out/f'PoStoreBaires-{version}-source.zip'
        write_zip(source,files);archives.append(source)
    if not source_only:
        binary=ROOT/'dist/PoStoreBaires'
        system=platform.system()
        if system not in ('Windows','Linux'):raise ValueError('Unsupported platform')
        executable='PoStoreBaires.exe' if system=='Windows' else 'PoStoreBaires'
        if not (binary/executable).is_file():
            raise ValueError('Primero ejecutá python scripts/build.py en el sistema destino.')
        if system=='Windows':
            archive=out/f'PoStoreBaires-{version}-Windows.zip'
            write_zip(archive,[(p,'PoStoreBaires/'+p.relative_to(binary).as_posix())
                               for p in sorted(binary.rglob('*')) if p.is_file()])
        else:
            archive=out/f'PoStoreBaires-{version}-Linux.tar.gz'
            with tarfile.open(archive,'w:gz',dereference=False) as tar:
                tar.add(binary,arcname='PoStoreBaires')
            with tarfile.open(archive) as tar:
                member=tar.getmember('PoStoreBaires/PoStoreBaires')
                if not member.mode & 0o111:raise ValueError('Linux executable permission missing')
        archives.append(archive)
    suffix='source' if source_only else platform.system()
    manifest=out/f'SHA256SUMS-{suffix}.txt'
    manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in archives),encoding='utf-8')
    for p in archives:print('Packaged '+p.name)
    return archives

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--source-only',action='store_true')
    group.add_argument('--binary-only',action='store_true')
    args=parser.parse_args();package(args.source_only,args.binary_only)
