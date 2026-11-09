import assert from 'node:assert/strict';
import {tracks} from '../racer/tracks.mjs';
import {normalizeProgress,loadProgress,saveProgress,applyResult,SAVE_KEY} from '../racer/progress.mjs';
const values=new Map([['bulletDashSave','{"coins":987,"highScore":321}'],['foodFightLocalCatalogueV1','{"items":[]}']]);
const storage={getItem:key=>values.get(key)||null,setItem:(key,value)=>values.set(key,value)};
const original=JSON.stringify([...values]);let progress=loadProgress(storage);
assert.equal(progress.unlocked,1);assert.equal(JSON.stringify([...values]),original,'initialization must not write or clear storage');
for(const track of tracks){progress=applyResult(progress,track,{track:track.id,time:track.silver+1});assert.equal(progress.unlocked,Math.min(12,track.id+1));assert.equal(progress.medals[track.id],'Bronze')}
assert.equal(progress.completed.length,12);const best=progress.bestTimes[1];
progress=applyResult(progress,tracks[0],{track:1,time:best+50});assert.equal(progress.bestTimes[1],best);
progress=applyResult(progress,tracks[0],{track:1,time:tracks[0].gold-1});assert.equal(progress.medals[1],'Gold');
progress=applyResult(progress,tracks[0],{track:1,time:best+100});assert.equal(progress.medals[1],'Gold');
progress.color='#ff6479';assert(saveProgress(progress,storage));assert.equal(loadProgress(storage).color,'#ff6479');
assert.equal(values.get('bulletDashSave'),'{"coins":987,"highScore":321}');assert.equal(values.get('foodFightLocalCatalogueV1'),'{"items":[]}');
values.set(SAVE_KEY,'malformed');const malformed=loadProgress(storage);assert.equal(malformed.unlocked,1);assert.equal(values.get(SAVE_KEY),'malformed');
assert.equal(normalizeProgress({unlocked:-1,completed:['bad'],stats:{distance:-2},color:'invalid'}).stats.distance,0);
assert.equal(saveProgress(progress,{setItem:()=>{throw Error('blocked')}}),false);
console.log('PASS: sequential bronze unlocks, best time/medal retention, color persistence, malformed/blocked saves and Food Fight isolation');
