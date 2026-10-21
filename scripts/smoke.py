"""Run the built executable on its native OS with a bounded timeout."""
from pathlib import Path
import os
import platform
import subprocess
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    name='PoStoreBaires.exe' if platform.system()=='Windows' else 'PoStoreBaires'
    executable=ROOT/'dist/PoStoreBaires'/name
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen')
    subprocess.run([str(executable),'--smoke-test'],env=env,check=True,timeout=60)
    print('Native packaged executable started and exited successfully.')
