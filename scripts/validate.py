"""Validate Python source without executing the user interface."""
from pathlib import Path
import ast
import wave
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
assert (root/'VERSION').read_text().strip()=='1.0.0-beta.1'
assert 'GNU GENERAL PUBLIC LICENSE' in (root/'LICENSE').read_text()
for folder in ('postorebaires','scripts','tests'):
    for p in (root/folder).rglob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
for p in (root/'postorebaires/assets').glob('*.svg'):ET.parse(p)
for name in ('scan','cash'):
    with wave.open(str(root/'postorebaires/assets'/f'{name}.wav')) as audio:
        assert audio.getnchannels()==1 and audio.getnframes()>0
for name in ('README.md','main.md','SECURITY.md','THIRD_PARTY.md','licenses/LGPL-3.0.txt','Compilar-Windows.cmd'):
    assert (root/name).is_file()
print('Python sources, version, licenses and assets validated.')
