"""Publish a prerelease only after all verified assets have been uploaded."""
from pathlib import Path
import subprocess
import os
from release import verify
ROOT=Path(__file__).resolve().parents[1]

if __name__=='__main__':
    assets=verify()
    tag='v'+(ROOT/'VERSION').read_text().strip()
    # Refuse to silently replace an existing release. If upload fails, the draft
    # stays unpublished for inspection; rerunning requires resolving that draft.
    target = ['--target', os.environ['GITHUB_SHA']] if os.environ.get('GITHUB_SHA') else ['--verify-tag']
    subprocess.run(['gh','release','create',tag]+target+['--draft','--prerelease',
                    '--title',f'PoStoreBaires {tag[1:]} — Windows y Linux',
                    '--notes-file',str(ROOT/'docs/RELEASE-beta-1.0.md')],check=True)
    subprocess.run(['gh','release','upload',tag]+[str(p) for p in assets],check=True)
    subprocess.run(['gh','release','edit',tag,'--draft=false','--prerelease'],check=True)
    print('Prerelease published with all verified packages.')
