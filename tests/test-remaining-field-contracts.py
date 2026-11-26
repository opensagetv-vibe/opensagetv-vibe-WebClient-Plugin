"""Offline safety contracts for remaining original-source field runners."""
import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FieldContracts(unittest.TestCase):
    def test_host_profile_smoke_is_focused_and_decoded(self):
        source=(ROOT/'tests/stock-long-recording-field.py').read_text(encoding='utf-8')
        for token in ('--profile-smoke','[(a.profile_start,20)] if a.profile_smoke',"last['height']!=480",
                      "'WEB-104' if a.profile_smoke",'if a.profile_smoke and (a.elapsed_soak_seconds or a.only_soak)'):
            self.assertIn(token,source)
    def test_long_source_does_not_watch_or_mutate_original_metadata(self):
        source=(ROOT/'tests/stock-long-recording-field.py').read_text(encoding='utf-8')
        tree=ast.parse(source)
        constants={n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
        self.assertFalse({'media.watch','media.seek','media.clear_watched','channel.tune'} & constants)
        self.assertIn("keys=('watched','watchedCompletely','serverResumeSeconds')",source)
        self.assertIn("if any(before.get(k)!=after.get(k) for k in keys)",source)
    def test_long_field_uses_real_document_runtime_and_media(self):
        source=(ROOT/'tests/stock-long-recording-field.py').read_text(encoding='utf-8')
        self.assertNotIn('context.route(',source)
        self.assertIn("'/SageTVWebPlayer/index.html'",source)
        self.assertIn('vendor/hlsjs/hls.min.js',source)
        self.assertIn("C.request(cfg,path,dict(action=action,**values)",source)
        for event in ('timeupdate','playing','canplay','ended'):
            self.assertIn("addEventListener('"+event+"'",source)
    def test_inventory_is_read_only_and_requires_complete_stable_total(self):
        tree=ast.parse((ROOT/'scripts/inventory-long-recordings.py').read_text(encoding='utf-8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='request']
        self.assertTrue(calls)
        self.assertTrue(all(len(n.args)==2 and not n.keywords for n in calls))
        source=ast.unparse(tree)
        self.assertIn('expected == final == len(rows)',source)
    def test_sustained_mode_is_one_bounded_offset_without_replaying_matrix(self):
        source=(ROOT/'tests/stock-long-recording-field.py').read_text(encoding='utf-8')
        self.assertIn("if not 20<=a.soak_seconds<=600",source)
        self.assertIn("[(18000,a.soak_seconds)] if a.only_soak",source)
        self.assertIn("'resourceSamples'",source)
        self.assertIn('next_resource=time.monotonic()+30',source)
        self.assertIn('originalWatchStateUnchanged',source)
    def test_strict_audio_observes_public_dom_and_actual_plan_field(self):
        source=(ROOT/'tests/stock-audio-fallback-field.py').read_text(encoding='utf-8')
        self.assertNotIn('page.evaluate("lastError',source)
        self.assertIn("getElementById('osdMessage')",source)
        self.assertIn("effective.get('audioStreamIndex')",source)
        self.assertIn("state.get('active') is not None",source)
    def test_elapsed_soak_is_explicit_bounded_owned_and_checkpointed(self):
        source=(ROOT/'tests/stock-long-recording-field.py').read_text(encoding='utf-8')
        for token in ('choices=(7200,10800)',"if a.elapsed_soak_seconds:p.error('Multi-hour testing removed",'[(0,a.elapsed_soak_seconds)]',"free<10*1024**3","free<2*1024**3","if owned and not stop_intent:","elapsedPlaybackSeconds",'def save():'):
            self.assertIn(token,source)
        self.assertEqual(source.count("stop_intent=True;report['ownedStopIntent']=True;save()"),2)
        self.assertNotIn('safeToRestart',source)
        self.assertIn('from playback_activity import observe_activity',source)
    def test_disk_pressure_uses_private_networkless_bounded_mount(self):
        source=(ROOT/'scripts/verify-hls-disk-pressure.py').read_text(encoding='utf-8')
        for token in ("'--network','none'","'--pull','never'","'--read-only'","'--cap-drop','ALL'",'size=192m','--memory','512m',"data['Image']!=report.get('devImage')",'ownedSandboxRetired'):
            self.assertIn(token,source)
        self.assertNotIn('commission-mobile',source)
    def test_elapsed_profile_is_explicit_verified_and_stall_bounded(self):
        source=(ROOT/'tests/stock-long-recording-field.py').read_text(encoding='utf-8')
        for token in ('stream_profileSchemaVersion=8','stream_videoKbps=1000',"stream_resolution='480'",
                      "effective.get('videoTargetKbps')!=1000",'time.monotonic()-last_progress>45'):
            self.assertIn(token,source)
    def test_phone_profile_is_focused_and_stop_is_one_shot(self):
        source=(ROOT/'scripts/iphone-long-source-field.py').read_text(encoding='utf-8')
        for token in ('--profile-smoke',"'WEB-104' if options.profile_smoke",'stream_videoKbps=1000',
                      "effective.get('videoTargetKbps')!=1000","last['height']!=480",'if owned and not stop_intent:',
                      'stop_intent=True\n            if not (await asyncio.to_thread'):
            self.assertIn(token,source)
    def test_mpeg2_copy_comparison_is_owned_and_exports_verified_report(self):
        source=(ROOT/'tests/stock-copy-recovery-field.py').read_text(encoding='utf-8')
        for token in ('567424984',"baseline!={'mediaId':84394,'path':expected}","info.get('recording')","'MPEG2-Video'",'saveDiagnosticsToServer:false','page.expect_download','hashes.sha256',"serverSaveRequested=False"):
            self.assertIn(token,source)
        self.assertNotIn('media.clear_watched',source)
        self.assertIn("v['time']>0 and v['width']==0 and v['frames']==0",source)
        self.assertIn("'Copied video was not decoded:' in v['notice']",source)
if __name__=='__main__':unittest.main()
