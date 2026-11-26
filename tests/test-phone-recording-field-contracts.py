"""Offline harness-safety contracts; not physical playback evidence."""
import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PhoneRecordingContracts(unittest.TestCase):
 def read(self,name):
  source=(ROOT/'scripts'/name).read_text(encoding='utf-8');ast.parse(source);return source
 def test_growth_keeps_pairing_pump_and_natural_end(self):
  s=self.read('iphone-growing-recording-field.py')
  self.assertIn('await asyncio.to_thread(C.request',s)
  self.assertIn("if options.natural_completion:",s)
  block=s.split('if options.natural_completion:\n   report',1)[1].split('else:await cancel()',1)[0]
  self.assertNotIn('await cancel()',block)
  self.assertIn("airing['end']",block)
  self.assertIn('v.requestVideoFrameCallback',s)
  self.assertIn("if options.channel:allowed=(options.channel,)",s)
  self.assertIn("if options.channel and not options.natural_completion",s)
 def test_real_startup_is_not_transient_fallback_endlist(self):
  s=self.read('iphone-growing-recording-field.py')
  self.assertIn("h.get('error') and not h.get('running')",s)
  self.assertIn("h.get('fallbackStage',0)>=2",s)
  self.assertIn("not (h.get('activeRecording') and h.get('endList'))",s)
  self.assertLess(s.index("report['startup']=await poll"),s.index('v.src=') if 'v.src=' in s else len(s))
  self.assertIn('except asyncio.TimeoutError:',s)
  self.assertIn('for attempt in range(3)',s)
  self.assertIn("report.setdefault('startupTransitions',[])",s)
  self.assertIn('if len(stages)<16:stages.append(observed)',s)
  self.assertIn("(h.get('stderrTail') or '')[-2000:]",s)
  self.assertIn("report['completionStatus']=h;save()",s)
  self.assertIn("h.get('running') is False and h.get('exitCode') is not None",s)
 def test_exact_reservation_and_deletion_no_replay(self):
  s=self.read('iphone-growing-recording-field.py')
  for token in ('if cancel_intent or not record_intent',"current['files'][0]['path']!=report['ownership']['path']","await sched()!=baseline",'deleteOwnedMediaIntent',"confirm='DELETE'",'recordStatus&airingId='):
   self.assertIn(token,s)
 def test_endlist_is_not_a_process_exit_receipt(self):
  tree=ast.parse(self.read('iphone-growing-recording-field.py'))
  function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='producer_completion_ready')
  namespace={};exec(compile(ast.Module(body=[function],type_ignores=[]),'<isolated readiness contract>','exec'),namespace)
  ready=namespace['producer_completion_ready'];sample=dict(activeRecording=False,endList=True,running=True,exitCode=None)
  self.assertFalse(ready(sample))
  sample['running']=False;self.assertFalse(ready(sample))
  sample['exitCode']=0;self.assertTrue(ready(sample))
  sample['exitCode']=3;self.assertTrue(ready(sample)) # caller records/rejects a real failed exit
  for field in ('activeRecording','endList','running'):
   changed=dict(sample);changed[field]=None;self.assertFalse(ready(changed))
 def test_changeover_uses_production_player_and_observed_clocks(self):
  s=self.read('iphone-recording-changeover-field.py')
  for token in ('playback_revision(ROOT)','media.watch','rawMediaTimeMs','origin+last[\'time\']','Previous producer retained','if previous==hls_id','SageMiniPlayback.prototype.start=s.original'):
   self.assertIn(token,s)
  self.assertNotIn('currentTime=',s)
 def test_prefix_exclusive_bounded_and_never_replays_unknown_copy(self):
  s=self.read('preserve-owned-live-startup.py')
  for token in ("report_path.parent!=active","m['files'][0]['path']!=source",'if not args.observe_existing:', 'bs=18800000 count=1 iflag=fullblock conv=excl', 'size!=18800000'):
   self.assertIn(token,s)
  self.assertNotIn('rm ',s)
 def test_live_handoff_is_core_owned_not_repeated_watch(self):
  s=self.read('iphone-live-handoff-field.py')
  self.assertEqual(s.count("__iphoneGate.api('watchContent'"),1)
  for token in ("choices=('7.1','11.1')","mid!=first_mid","v['source']!=first['source']","info['start']!=report['nextAiring']['start']","after['frames']<v['frames']+40","await guard()","await mcp('media.control'","['scheduled']!=baseline"):
   self.assertIn(token,s)
  self.assertNotIn("channel.tune",s)
 def test_completed_fixture_stop_has_exact_id_path_and_activity_guard(self):
  s=self.read('stop-owned-phone-fixture.py')
  for token in ('choices=(20819,20905,84231,2504)',"get('mediaFileId')!=a.media_id",'/var/media/OpenSageTV_Vibe_Tests/',"activity['recordingCount']","path.open('x'","operation='stop'",'if a.media_id==20819:', 'OpenSageTV_Vibe_Test_DVD/VIDEO_TS','elif a.media_id==2504:',"before.get('dvd') is not True",'/var/media/videos/Aidens_Movies/ALADDIN/VIDEO_TS'):
   self.assertIn(token,s)
 def test_dvd_motion_compares_images_and_restores_borrowed_settings(self):
  s=self.read('iphone-real-dvd-gate.py')
  for token in ('--pixels','decodedPixelWindows','--handoff-mse','explicitSyntheticEngineTrial',"report['playerRestored']",'remotePlaybackRestored',"SageMiniPlayback.prototype.start=s.originalStart",'sameProducer'):
   self.assertIn(token,s)
  self.assertNotIn('userGesture=True',s)
 def test_physical_capture_does_not_fabricate_cfr_frames(self):
  s=self.read('capture-phone-hdmi.py')
  self.assertIn("'-fps_mode','passthrough'",s)
  self.assertIn("'artifacts/active'/a.task",s)
 def test_eof_probe_uses_fresh_poll_after_reconnect_not_stale_resource_timing(self):
  s=self.read('iphone-recording-eof-gate.py')
  self.assertIn('__eofSessionProbe',s)
  self.assertIn("u.searchParams.get('action')==='events'",s)
  self.assertNotIn('performance.getEntriesByType',s)
  self.assertIn('await asyncio.to_thread(C.request',s)
  self.assertIn('Fresh native session not observed; no Watch dispatched',s)
 def test_startup_comparison_is_bounded_and_not_control_replay(self):
  s=self.read('benchmark-web097-live-idr.py')
  for token in ('tests/fixtures/web097-default-hls-command.json','1279502996','format=duration','timeout --signal=TERM --kill-after=3s','recv_stderr_ready','ownedTemporaryOutputRemoved'):
   self.assertIn(token,s)
  self.assertNotIn('media.watch',s)
  self.assertNotIn('killall',s)
 def test_original_cea_is_bounded_real_source_and_one_shot_current_apply(self):
  s=self.read('inventory-original-caption-services.py')
  for token in ('18800000','head -c 20971521','hashlib.sha256(data).hexdigest() != SHA','exportsCaptionPayload=False','serverMutations=False','timeout=60'):
   self.assertIn(token,s)
  self.assertNotIn('media.watch',s)
  s=self.read('iphone-original-cea-field.py')
  self.assertEqual(s.count("mcp,'media.watch'"),1)
  self.assertEqual(s.count("mcp,'media.seek'"),1)
  for token in ("profile(2,active=True)","profile(1,active=True)","v['source']!=first['source']","v['source']!=clear['source']",'if not report[\'cleanup\']',"captionAuthority:'cc1',captions:'708'",'profilesRestored'):
   self.assertIn(token,s)
  self.assertNotIn('currentTime=',s)
  self.assertNotIn('media.clear_watched',s)
if __name__=='__main__':unittest.main()
