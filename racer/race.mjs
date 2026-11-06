import {createCar,updateCar} from './physics.mjs';
export function formatTime(seconds){const ms=Math.max(0,Math.round(seconds*1000));return String(Math.floor(ms/60000)).padStart(2,'0')+':'+String(Math.floor(ms/1000)%60).padStart(2,'0')+'.'+String(ms%1000).padStart(3,'0')}
export function medalFor(track,time){return time<=track.gold?'Gold':time<=track.silver?'Silver':'Bronze'}
export class RaceSession{
 constructor(track){this.track=track;this.mode='menu';this.car=createCar(track);this.time=0;this.nextCheckpoint=0;this.recoveries=0;this.result=null;this.remaining=3;this.lastCheckpoint=6;this.goTime=0}
 start(){this.car=createCar(this.track);this.mode='countdown';this.time=0;this.remaining=3;this.nextCheckpoint=0;this.lastCheckpoint=6;this.recoveries=0;this.result=null;this.goTime=0}
 pause(){if(!['racing','countdown'].includes(this.mode))return;this.previousMode=this.mode;this.mode='paused'}
 resume(){if(this.mode==='paused')this.mode=this.previousMode}
 recover(){
  if(this.mode!=='racing')return;
  const old=this.car;this.car=createCar(this.track,this.lastCheckpoint+.5);
  for(const key of ['distance','airtime','maxJump','wallHits'])this.car[key]=old[key];
  this.time+=3;this.recoveries++;
 }
 step(input,dt){
  if(this.mode==='countdown'){
   this.remaining-=dt;if(this.remaining<=0){this.mode='racing';this.goTime=.75}return;
  }
  if(this.mode!=='racing')return;
  this.goTime=Math.max(0,this.goTime-dt);this.time+=dt;
  const movement=updateCar(this.car,this.track,input,dt);
  if(movement.recover){this.recover();return}
  const valid=movement.onRoad&&Math.abs(this.car.y-(movement.road.y+.65))<4;
  if(!valid)return;
  const next=this.track.checkpoints[this.nextCheckpoint];
  if(next!==undefined&&movement.previousS<next&&this.car.s>=next){this.lastCheckpoint=next;this.nextCheckpoint++}
  if(this.nextCheckpoint===this.track.checkpoints.length&&movement.previousS<this.track.finish&&this.car.s>=this.track.finish){
   this.mode='finished';this.car.vx=0;this.car.vz=0;
   this.result={track:this.track.id,time:this.time,medal:medalFor(this.track,this.time),recoveries:this.recoveries};
  }
 }
}
