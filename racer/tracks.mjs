// Original point-to-point courses. Coordinates are [x, z, height].
export const definitions=[
 {id:1,name:'First Gear',difficulty:'Beginner',width:21,points:[[0,0],[0,80],[22,155],[85,210],[105,290],[80,370],[80,440]],theme:'coast',ramps:[]},
 {id:2,name:'Coastal Sprint',difficulty:'Easy',width:20,points:[[0,0],[0,75],[65,130],[150,140],[220,200],[210,280],[140,340],[90,410],[110,480]],theme:'coast',ramps:[]},
 {id:3,name:'Desert Dash',difficulty:'Easy',width:19,points:[[0,0],[0,140],[-55,230],[-140,260],[-225,320],[-200,420],[-100,470],[-75,580]],theme:'desert',ramps:[]}
];
export const themes={
 coast:{sky:'#94d9ef',ground:'#6cae83',road:'#3b4862',edge:'#eff4ff',accent:'#52e1ff'},
 desert:{sky:'#f3c797',ground:'#c59064',road:'#4f4650',edge:'#ffe7bd',accent:'#ffbf66'},
 forest:{sky:'#b2d8d8',ground:'#487660',road:'#39444b',edge:'#c8eee0',accent:'#7cf1bc'},
 sunset:{sky:'#d692b1',ground:'#796278',road:'#44425b',edge:'#ffd6b5',accent:'#ffa082'},
 canyon:{sky:'#d6bdd6',ground:'#946b60',road:'#4c485e',edge:'#f0d6b7',accent:'#ffc578'},
 skyline:{sky:'#a3c9ef',ground:'#7382aa',road:'#424b70',edge:'#d0e8ff',accent:'#86e8ff'},
 mountain:{sky:'#bedee9',ground:'#718b8e',road:'#3a4855',edge:'#eef5ed',accent:'#ffdf8e'},
 neon:{sky:'#111630',ground:'#1d2541',road:'#303a59',edge:'#bda1ff',accent:'#63f0ee'}
};
const mix=(a,b,t)=>a+(b-a)*t;
function spline(a,b,c,d,t){return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)}
export function buildTrack(def){
 const points=def.points.map(p=>({x:p[0],z:p[1],y:p[2]||0})),samples=[];
 for(let i=0;i<points.length-1;i++){
  const a=points[Math.max(0,i-1)],b=points[i],c=points[i+1],d=points[Math.min(points.length-1,i+2)];
  const steps=Math.max(10,Math.ceil(Math.hypot(c.x-b.x,c.z-b.z)/1.7));
  for(let j=0;j<steps;j++){const t=j/steps;samples.push({x:spline(a.x,b.x,c.x,d.x,t),z:spline(a.z,b.z,c.z,d.z,t),y:spline(a.y,b.y,c.y,d.y,t)})}
 }
 samples.push({...points.at(-1)});
 let length=0;
 for(let i=0;i<samples.length;i++){if(i)length+=Math.hypot(samples[i].x-samples[i-1].x,samples[i].z-samples[i-1].z);samples[i].s=length}
 for(const p of samples)for(const ramp of def.ramps||[]){
  const start=length*ramp.at,up=ramp.up||12,top=ramp.top||3,down=ramp.down||20,u=p.s-start;
  if(u>=0&&u<=up+top+down)p.y+=u<up?ramp.height*u/up:u<up+top?ramp.height:ramp.height*(1-(u-up-top)/down);
 }
 for(let i=0;i<samples.length;i++){
  const a=samples[Math.max(0,i-1)],b=samples[Math.min(samples.length-1,i+1)],n=Math.hypot(b.x-a.x,b.z-a.z)||1;
  samples[i].tx=(b.x-a.x)/n;samples[i].tz=(b.z-a.z)/n;samples[i].nx=samples[i].tz;samples[i].nz=-samples[i].tx;
 }
 const finish=length-8,count=Math.max(3,Math.min(7,Math.floor(length/110)));
 const checkpoints=Array.from({length:count},(_,i)=>10+(finish-20)*(i+1)/(count+1));
 return {...def,samples,length,finish,checkpoints,theme:themes[def.theme],gold:Math.round(length/(def.targetSpeed||24)+8),silver:Math.round(length/(def.targetSpeed||24)*1.5+15)};
}
export function sampleAt(track,s){
 const points=track.samples;s=Math.max(0,Math.min(track.length,s));let low=0,high=points.length-1;
 while(high-low>1){const mid=(low+high)>>1;if(points[mid].s<s)low=mid;else high=mid}
 const a=points[low],b=points[high],t=(s-a.s)/(b.s-a.s||1);
 const tx=mix(a.tx,b.tx,t),tz=mix(a.tz,b.tz,t),n=Math.hypot(tx,tz)||1;
 return {x:mix(a.x,b.x,t),y:mix(a.y,b.y,t),z:mix(a.z,b.z,t),tx:tx/n,tz:tz/n,nx:tz/n,nz:-tx/n,s};
}
export function nearestRoad(track,x,z,nearS){
 let best=null,bestD=Infinity;
 for(let i=0;i<track.samples.length-1;i++){
  const a=track.samples[i],b=track.samples[i+1];if(Number.isFinite(nearS)&&(b.s<nearS-65||a.s>nearS+65))continue;
  const dx=b.x-a.x,dz=b.z-a.z,l2=dx*dx+dz*dz,t=Math.max(0,Math.min(1,((x-a.x)*dx+(z-a.z)*dz)/(l2||1)));
  const qx=a.x+t*dx,qz=a.z+t*dz,d2=(x-qx)**2+(z-qz)**2;
  if(d2<bestD){const n=Math.sqrt(l2)||1;bestD=d2;best={x:qx,z:qz,y:mix(a.y,b.y,t),s:mix(a.s,b.s,t),tx:dx/n,tz:dz/n,nx:dz/n,nz:-dx/n,lateral:(x-qx)*dz/n-(z-qz)*dx/n,distance:Math.sqrt(d2)}}
 }
 return best;
}
export function validateTrack(track){
 const errors=[];if(track.width<9)errors.push('Road too narrow for the 2.2m car');
 if(track.samples.length<10||track.finish<60)errors.push('Route too short');
 for(let i=1;i<track.samples.length;i++){
  const a=track.samples[i-1],b=track.samples[i],distance=Math.hypot(b.x-a.x,b.z-a.z);
  if(![b.x,b.y,b.z,b.s].every(Number.isFinite)||distance>3.5||distance<.001)errors.push('Discontinuous road at '+i);
  if(Math.abs(b.y-a.y)/distance>.7)errors.push('Excessive road grade at '+i);
 }
 if(track.checkpoints.some((s,i)=>s<=6||s>=track.finish||(i&&s<=track.checkpoints[i-1])))errors.push('Invalid checkpoint order');
 for(const r of track.ramps||[]){if(r.at*track.length+(r.up||12)+(r.top||3)+(r.down||20)+25>track.finish)errors.push('Ramp lacks landing runout')}
 const start=sampleAt(track,6),finish=sampleAt(track,track.finish);
 if(!nearestRoad(track,start.x,start.z,6)||!nearestRoad(track,finish.x,finish.z,track.finish))errors.push('Invalid start or finish');
 return {valid:errors.length===0,errors:[...new Set(errors)],length:track.length,width:track.width,checkpoints:track.checkpoints.length,requiredGaps:0};
}
export const tracks=definitions.map(buildTrack);
