// Development-only controller. It sends ordinary throttle/brake/steering values
// into RaceSession.step; it never sets position, progress, checkpoints or time.
import {sampleAt} from '../racer/tracks.mjs';
import {STEP,clamp,angleDelta} from '../racer/physics.mjs';
import {RaceSession} from '../racer/race.mjs';
export function driverInput(race){
 const car=race.car,track=race.track,speed=Math.hypot(car.vx,car.vz),look=7+speed*.35;
 const target=sampleAt(track,Math.min(track.finish+3,car.s+look)),distance=Math.hypot(target.x-car.x,target.z-car.z);
 const angle=angleDelta(Math.atan2(target.x-car.x,target.z-car.z),car.yaw);
 const turnRate=2.1/(1+speed/35)*Math.min(speed/6,1);
 let curvature=0,previous=sampleAt(track,car.s);
 for(const offset of [5,10,15,20,30]){
  const point=sampleAt(track,car.s+offset),change=Math.abs(angleDelta(Math.atan2(point.tx,point.tz),Math.atan2(previous.tx,previous.tz)));
  curvature=Math.max(curvature,change/Math.max(1,point.s-previous.s));previous=point;
 }
 const desired=Math.min(32,Math.max(12,Math.sqrt(10/Math.max(.004,curvature))));
 const steer=clamp(2*Math.sin(angle)/Math.max(2,distance)*Math.max(speed,4)/Math.max(.4,turnRate)*1.2,-1,1);
 return {throttle:speed<desired?1:0,brake:speed>desired+1?1:0,steer:Math.round(steer*20)/20};
}
export function drive(track){
 const race=new RaceSession(track);race.start();const controls=[],path=[];let ticks=0;
 while(race.mode!=='finished'&&ticks<120*180){
  const input=driverInput(race),last=controls.at(-1);
  if(last&&last[1]===input.throttle&&last[2]===input.brake&&last[3]===input.steer)last[0]++;
  else controls.push([1,input.throttle,input.brake,input.steer]);
  race.step(input,STEP);ticks++;
  if(ticks%60===0||race.mode==='finished')path.push([ticks,...['x','y','z','s'].map(k=>Math.round(race.car[k]*1000)/1000),race.nextCheckpoint]);
 }
 return {race,record:{id:track.id,name:track.name,ticks,time:race.time,checkpoints:race.nextCheckpoint,recoveries:race.recoveries,maxJump:race.car.maxJump,airtime:race.car.airtime,wallHits:race.car.wallHits,controls,path}};
}
