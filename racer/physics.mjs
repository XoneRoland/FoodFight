import { sampleAt,nearestRoad } from './tracks.mjs';
export const STEP=1/120, CAR_HALF_WIDTH=1.1, MAX_SPEED=42;
export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export function angleDelta(a,b){return Math.atan2(Math.sin(a-b),Math.cos(a-b))}
export function createCar(track,s=6){
 const p=sampleAt(track,s);
 return {x:p.x,y:p.y+.65,z:p.z,yaw:Math.atan2(p.tx,p.tz),pitch:0,vx:0,vz:0,vy:0,grounded:true,s,offTime:0,invalidTime:0,distance:0,airtime:0,maxJump:0,wallHits:0};
}
export function updateCar(car,track,input,dt){
 const before={x:car.x,z:car.z,s:car.s};
 let fx=Math.sin(car.yaw),fz=Math.cos(car.yaw),rx=fz,rz=-fx;
 let forward=car.vx*fx+car.vz*fz,side=car.vx*rx+car.vz*rz;
 const throttle=clamp(input.throttle||0,0,1),brake=clamp(input.brake||0,0,1),steer=clamp(input.steer||0,-1,1);
 forward+=(throttle*(forward<-.5?30:17)-brake*(forward>1?30:10))*dt;
 forward-=Math.sign(forward)*Math.min(Math.abs(forward),(.45+Math.abs(forward)*.045+forward*forward*.0018)*dt);
 if(!throttle&&!brake)forward*=Math.exp(-.13*dt);
 forward=clamp(forward,-10,MAX_SPEED);
 const turnRate=2.1/(1+Math.abs(forward)/35)*Math.min(Math.abs(forward)/6,1);
 car.yaw+=steer*turnRate*dt*Math.sign(forward)*(car.grounded?1:.35);
 const worldX=fx*forward+rx*side,worldZ=fz*forward+rz*side;
 fx=Math.sin(car.yaw);fz=Math.cos(car.yaw);rx=fz;rz=-fx;
 forward=worldX*fx+worldZ*fz;side=worldX*rx+worldZ*rz;
 side*=Math.exp(-(Math.abs(forward)>24&&Math.abs(steer)>.3?5.5:10)*dt);
 car.vx=fx*forward+rx*side;car.vz=fz*forward+rz*side;
 car.x+=car.vx*dt;car.z+=car.vz*dt;
 let road=nearestRoad(track,car.x,car.z,car.s),onRoad=road&&road.distance<=track.width/2;
 if(road&&Math.abs(road.lateral)>track.width/2-CAR_HALF_WIDTH&&Math.abs(road.lateral)<track.width/2+4&&car.y<road.y+2.2&&car.y>road.y-.5){
  const sideSign=Math.sign(road.lateral),edge=track.width/2-CAR_HALF_WIDTH;
  car.x=road.x+road.nx*edge*sideSign;car.z=road.z+road.nz*edge*sideSign;
  const outward=(car.vx*road.nx+car.vz*road.nz)*sideSign;
  if(outward>0){car.vx-=road.nx*sideSign*outward*1.1;car.vz-=road.nz*sideSign*outward*1.1;car.vx*=.87;car.vz*=.87;car.wallHits++}
  road=nearestRoad(track,car.x,car.z,car.s);onRoad=true;
 }
 const support=onRoad?road.y+.65:-Infinity;
 if(car.grounded&&onRoad){
  const neededVy=(support-car.y)/dt;
  if(car.vy>1&&neededVy<car.vy-22*dt&&Math.abs(forward)>12){car.grounded=false;car.vy-=20*dt;car.y+=car.vy*dt}
  else{car.y=support;car.vy=neededVy}
 }else{
  car.grounded=false;car.vy-=20*dt;car.y+=car.vy*dt;
  if(onRoad&&car.vy<=0&&car.y<=support&&car.y>support-2){car.y=support;car.vy=0;car.grounded=true}
 }
 if(!car.grounded)car.airtime+=dt;
 if(onRoad)car.maxJump=Math.max(car.maxJump,car.y-support);
 car.offTime=onRoad?0:car.offTime+dt;
 const travelled=Math.hypot(car.x-before.x,car.z-before.z);
 if(onRoad&&Math.abs(road.s-car.s)<=Math.max(2,travelled*2+1)&&car.y>=road.y-.4&&car.y<=road.y+14){car.s=road.s;car.invalidTime=0}
 else car.invalidTime+=dt;
 car.distance+=travelled;
 if(car.grounded&&road){const ahead=sampleAt(track,Math.min(track.length,car.s+2)),behind=sampleAt(track,Math.max(0,car.s-2));const pitch=Math.atan2(ahead.y-behind.y,4);car.pitch+=(pitch-car.pitch)*(1-Math.exp(-10*dt))}
 else car.pitch*=Math.exp(-1.5*dt);
 return {road,onRoad,previousS:before.s,recover:car.offTime>1.3||car.invalidTime>1.3||car.y<-18};
}
