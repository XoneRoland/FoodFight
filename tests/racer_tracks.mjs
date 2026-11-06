import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {tracks,validateTrack} from '../racer/tracks.mjs';
import {RaceSession} from '../racer/race.mjs';
import {STEP} from '../racer/physics.mjs';
import {drive} from './racer_driver.mjs';
const records=[];
for(const track of tracks){
 const validation=validateTrack(track);assert(validation.valid,track.name+': '+validation.errors.join(', '));
 const {race,record}=drive(track);
 console.log(track.id,track.name,race.mode,race.time.toFixed(3)+'s','progress',race.car.s.toFixed(1)+'/'+track.finish.toFixed(1),'CP',race.nextCheckpoint+'/'+track.checkpoints.length,'recoveries',race.recoveries,'jump',race.car.maxJump.toFixed(2));
 assert.equal(race.mode,'finished',track.name+' has not been successfully driven');
 assert.equal(race.nextCheckpoint,track.checkpoints.length);assert.equal(race.recoveries,0,track.name+' should be driven without recovery');
 // Replay the exact quantized control stream through an independent session.
 const replay=new RaceSession(track);replay.start();
 for(const [count,throttle,brake,steer] of record.controls)for(let i=0;i<count;i++)replay.step({throttle,brake,steer},STEP);
 assert.equal(replay.mode,'finished');assert(Math.abs(replay.time-record.time)<.001);
 records.push(record);
}
const hash=createHash('sha256');for(const file of ['../racer/physics.mjs','../racer/race.mjs','../racer/tracks.mjs','racer_driver.mjs'])hash.update(await readFile(new URL(file,import.meta.url)));
if(process.argv.includes('--record'))await writeFile(new URL('racer_paths.json',import.meta.url),JSON.stringify({version:1,step:STEP,sourceSha256:hash.digest('hex'),driver:'pure-pursuit-v1',records}));
console.log('PASS: geometry, actual driving and control-stream replay for '+tracks.length+' tracks');
