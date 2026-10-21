"""Verify all three release packages and assemble one checksum manifest."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]

def verify(out=None):
    out=Path(out) if out is not None else ROOT/'dist'
    version=(ROOT/'VERSION').read_text().strip()
    required={
      'Windows':f'PoStoreBaires-{version}-Windows.zip',
      'Linux':f'PoStoreBaires-{version}-Linux.tar.gz',
      'source':f'PoStoreBaires-{version}-source.zip',
    }
    lines=[]
    for system,name in required.items():
        path=out/name
        manifest=out/f'SHA256SUMS-{system}.txt'
        if not path.is_file() or not manifest.is_file():raise ValueError(f'Missing {system} artifact or checksum')
        entries={}
        for line in manifest.read_text().splitlines():
            digest,filename=line.split('  ',1)
            if filename in entries:raise ValueError('Duplicate checksum entry')
            entries[filename]=digest
        if name not in entries:raise ValueError(f'Missing checksum for {name}')
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if entries[name]!=digest:raise ValueError(f'Checksum mismatch: {name}')
        lines.append(f'{digest}  {name}\n')
    (out/'SHA256SUMS.txt').write_text(''.join(lines),encoding='utf-8')
    print('Windows, Linux and source checksums verified.')
    return [out/name for name in required.values()]+[out/'SHA256SUMS.txt']

if __name__=='__main__':verify()
