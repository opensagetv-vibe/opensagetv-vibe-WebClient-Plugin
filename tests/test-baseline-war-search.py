"""Archive scan functionality/safety, not rollback or live deployment proof."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec=importlib.util.spec_from_file_location('scan',Path(__file__).resolve().parents[1]/'scripts/find-baseline-war.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)


class SearchTests(unittest.TestCase):
    def result(self):return dict(archivesInspected=0,wars=[],matches=[],skipped=[])
    def archive(self,entries):
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,'w') as archive:
            for name,data in entries.items():archive.writestr(name,data)
        return buffer.getvalue()

    def test_war_in_nested_installer_is_hashed_not_named(self):
        data=b'canonical fake test war';nested=self.archive({'jetty/webapps/anonymous.war':data})
        outer=self.archive({'dist/local-plugin/installer.zip':nested,'ignored.txt':b'none'})
        result=self.result();S.inspect_zip(io.BytesIO(outer),'outer.zip',result)
        self.assertEqual(result['archivesInspected'],2)
        self.assertEqual(len(result['wars']),1)
        self.assertEqual(result['wars'][0]['sha256'],S.hashlib.sha256(data).hexdigest())
        self.assertEqual(result['skipped'],[])
        self.assertEqual(result['matches'],[])

    def test_candidate_names_cannot_fabricate_exact_match(self):
        result=self.result();S.record_war(b'not original','original-3.2.4.war',result)
        self.assertEqual(result['matches'],[])

    def test_actual_bytes_determine_a_positive_match(self):
        data=b'exact test fixture';digest=S.hashlib.sha256(data).hexdigest()
        result=self.result()
        with patch.object(S,'EXPECTED',digest):S.record_war(data,'no-version-name.war',result)
        self.assertEqual(result['matches'][0]['sha256'],digest)

    def test_large_zip_metadata_keeps_expanded_member_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'large.zip'
            source.write_bytes(self.archive({'nested/original.war':b'bounded fixture'}))
            with patch.object(S,'MAX_ARCHIVE',1):
                bounded=self.result();S.inspect_file(source,root,bounded)
                self.assertEqual(bounded['skipped'][0]['reason'],'archive-size-bound')
                metadata=self.result();S.inspect_file(source,root,metadata,large_zip_metadata=True)
                self.assertEqual(len(metadata['wars']),1)
                self.assertEqual(metadata['skipped'],[])

    def test_expansion_and_depth_bounds_are_explicit(self):
        result=self.result()
        S.inspect_zip(io.BytesIO(self.archive({'a.war':b'12345'})),'outer.zip',result,budget=[4])
        self.assertEqual(result['wars'],[])
        self.assertEqual(result['skipped'][0]['reason'],'expanded-byte-bound')
        result=self.result()
        S.inspect_zip(io.BytesIO(self.archive({'nested.zip':b'zip'})),'outer.zip',result,depth=2)
        self.assertEqual(result['skipped'][0]['reason'],'nested-depth-bound')

    def test_invalid_archive_is_not_absence_proof(self):
        result=self.result();S.inspect_zip(io.BytesIO(b'not zip'),'invalid.zip',result)
        self.assertEqual(result['skipped'][0]['reason'],'archive-unreadable')

    def test_explicit_member_override_does_not_remove_total_expansion_bound(self):
        archive=self.archive({'nested.zip':self.archive({'original.war':b'original'})})
        result=self.result()
        with patch.object(S,'MAX_MEMBER',1):
            S.inspect_zip(io.BytesIO(archive),'outer.zip',result,max_member=1024)
        self.assertEqual(len(result['wars']),1)
        result=self.result()
        S.inspect_zip(io.BytesIO(archive),'outer.zip',result,budget=[2],max_member=1024)
        self.assertEqual(result['wars'],[])
        self.assertEqual(result['skipped'][0]['reason'],'expanded-byte-bound')
        with self.assertRaises(ValueError):
            S.inspect_zip(io.BytesIO(archive),'outer.zip',self.result(),max_member=129*1024*1024)

    def test_file_outside_root_is_not_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);outside=root.parent/'outside.war'
            with self.assertRaises(ValueError):S.inspect_file(outside,root,self.result())


if __name__=='__main__':unittest.main()
