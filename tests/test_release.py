import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release',ROOT/'scripts/release.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)

class ReleaseGate(unittest.TestCase):
    def files(self,folder):
        version=(ROOT/'VERSION').read_text().strip()
        names={'Windows':f'PoStoreBaires-{version}-Windows.zip','Linux':f'PoStoreBaires-{version}-Linux.tar.gz','source':f'PoStoreBaires-{version}-source.zip'}
        for kind,name in names.items():
            data=(kind+' artifact').encode()
            (folder/name).write_bytes(data)
            (folder/f'SHA256SUMS-{kind}.txt').write_text(hashlib.sha256(data).hexdigest()+'  '+name+'\n')
        return names

    def test_all_platforms_required(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);names=self.files(folder)
            (folder/names['Linux']).unlink()
            with self.assertRaises(ValueError):release.verify(folder)
            self.assertFalse((folder/'SHA256SUMS.txt').exists())

    def test_corrupt_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);names=self.files(folder)
            (folder/names['Windows']).write_bytes(b'changed')
            with self.assertRaises(ValueError):release.verify(folder)
            self.assertFalse((folder/'SHA256SUMS.txt').exists())

    def test_complete_release_checksums(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);self.files(folder)
            files=release.verify(folder)
            self.assertEqual(len(files),4)
            self.assertEqual(len((folder/'SHA256SUMS.txt').read_text().splitlines()),3)

if __name__=='__main__':unittest.main()
