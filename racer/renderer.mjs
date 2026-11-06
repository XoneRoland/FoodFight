import { sampleAt } from './tracks.mjs';
const color=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255);
const sub=(a,b)=>a.map((n,i)=>n-b[i]);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>{const n=Math.hypot(...a)||1;return a.map(v=>v/n)};
const dot=(a,b)=>a.reduce((n,v,i)=>n+v*b[i],0);
function multiply(a,b){const out=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)out[c*4+r]+=a[k*4+r]*b[c*4+k];return out}
function perspective(aspect){const f=1/Math.tan(Math.PI/6),near=.25,far=900;return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0])}
function lookAt(eye,target){const z=norm(sub(eye,target)),x=norm(cross([0,1,0],z)),y=cross(z,x);return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1])}
function model(car){const c=Math.cos(car.yaw),s=Math.sin(car.yaw),p=Math.sin(car.pitch),q=Math.cos(car.pitch);return new Float32Array([c,0,-s,0,-s*p,q,-c*p,0,s*q,p,c*q,0,car.x,car.y,car.z,1])}
const identity=new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
class Geometry{
 constructor(){this.data=[]}
 tri(a,b,c,hex){const n=norm(cross(sub(b,a),sub(c,a))),rgb=typeof hex==='string'?color(hex):hex;for(const p of [a,b,c])this.data.push(...p,...n,...rgb)}
 quad(a,b,c,d,hex){this.tri(a,b,c,hex);this.tri(a,c,d,hex)}
 box(x,y,z,w,h,d,hex){const a=x-w/2,b=x+w/2,c=y-h/2,e=y+h/2,f=z-d/2,g=z+d/2;this.quad([a,c,f],[a,e,f],[b,e,f],[b,c,f],hex);this.quad([a,c,g],[b,c,g],[b,e,g],[a,e,g],hex);this.quad([a,e,f],[a,e,g],[b,e,g],[b,e,f],hex);this.quad([a,c,f],[b,c,f],[b,c,g],[a,c,g],hex);this.quad([a,c,f],[a,c,g],[a,e,g],[a,e,f],hex);this.quad([b,c,f],[b,e,f],[b,e,g],[b,c,g],hex)}
 cone(x,y,z,r,h,hex,sides=5){for(let i=0;i<sides;i++){const a=i*2*Math.PI/sides,b=(i+1)*2*Math.PI/sides;this.tri([x+Math.cos(a)*r,y,z+Math.sin(a)*r],[x,y+h,z],[x+Math.cos(b)*r,y,z+Math.sin(b)*r],hex)}}
 wheel(x,y,z){const n=8,r=.48,w=.35;for(let i=0;i<n;i++){const a=i*2*Math.PI/n,b=(i+1)*2*Math.PI/n,p=[Math.cos(a)*r,Math.sin(a)*r],q=[Math.cos(b)*r,Math.sin(b)*r];this.quad([x-w,y+p[0],z+p[1]],[x+w,y+p[0],z+p[1]],[x+w,y+q[0],z+q[1]],[x-w,y+q[0],z+q[1]],'#171d2d');this.tri([x+w,y,z],[x+w,y+p[0],z+p[1]],[x+w,y+q[0],z+q[1]],'#7d899b');this.tri([x-w,y,z],[x-w,y+q[0],z+q[1]],[x-w,y+p[0],z+p[1]],'#7d899b')}}
}
function createCarGeometry(hex){const g=new Geometry();g.box(0,.15,0,2.15,.55,4,hex);g.quad([-1,.4,-1.8],[1,.4,-1.8],[.95,.37,2.25],[-.95,.37,2.25],hex);g.quad([-.85,.45,-.8],[.85,.45,-.8],[.7,1.1,-.35],[-.7,1.1,-.35],'#23344c');g.quad([-.7,1.1,-.35],[.7,1.1,-.35],[.65,1.08,.6],[-.65,1.08,.6],hex);g.quad([-.65,1.08,.6],[.65,1.08,.6],[.86,.45,1.2],[-.86,.45,1.2],'#283d59');g.quad([-.85,.45,-.8],[-.7,1.1,-.35],[-.65,1.08,.6],[-.86,.45,1.2],'#2e4961');g.quad([.85,.45,-.8],[.86,.45,1.2],[.65,1.08,.6],[.7,1.1,-.35],'#23344c');for(const x of [-1.05,1.05])for(const z of [-1.2,1.3])g.wheel(x,-.12,z);g.box(0,.8,-1.65,2.6,.14,.5,hex);for(const x of [-.72,.72]){g.box(x,.48,-1.65,.12,.7,.15,'#23344c');g.box(x,.2,2.02,.5,.17,.08,'#fff6d0');g.box(x,.2,-2.02,.45,.16,.08,'#ff677d')}return g}
function createWorld(track){
 const g=new Geometry(),theme=track.theme,p=track.samples;
 const xs=p.map(v=>v.x),zs=p.map(v=>v.z),cx=(Math.min(...xs)+Math.max(...xs))/2,cz=(Math.min(...zs)+Math.max(...zs))/2;
 g.box(cx,-2,cz,1800,2,1800,theme.ground);
 for(let i=0;i<p.length-1;i++){
  const a=p[i],b=p[i+1],w=track.width/2,at=(v,offset,y=0)=>[v.x+v.nx*offset,v.y+y,v.z+v.nz*offset];
  g.quad(at(a,-w),at(b,-w),at(b,w),at(a,w),theme.road);
  for(const side of [-1,1]){
   const e=w*side,inside=e-side*.25;
   g.quad(at(a,inside,.025),at(b,inside,.025),at(b,e,.025),at(a,e,.025),theme.edge);
   // Walls are outside the usable road, matching the physics boundary.
   g.quad(at(a,e,0),at(a,e,1.1),at(b,e,1.1),at(b,e,0),i%12<6?theme.edge:theme.accent);
   g.quad(at(a,e,1.1),at(a,e+side*.3,1.1),at(b,e+side*.3,1.1),at(b,e,1.1),theme.edge);
  }
  if(Math.floor(a.s/8)%2===0)g.quad(at(a,-.12,.035),at(b,-.12,.035),at(b,.12,.035),at(a,.12,.035),'#dce6eb');
 }
 for(const [index,s] of [[-1,6],...track.checkpoints.map((s,i)=>[i,s]),[99,track.finish]]){
  const a=sampleAt(track,s),w=track.width/2,accent=index===99?'#ffdb79':index===-1?'#7cecff':theme.accent;
  for(const side of [-1,1])g.box(a.x+a.nx*(w+.4)*side,a.y+2.8,a.z+a.nz*(w+.4)*side,.7,5.6,.7,accent);
  const at=(d,forward,y)=>[a.x+a.nx*d+a.tx*forward,a.y+y,a.z+a.nz*d+a.tz*forward];
  g.quad(at(-w,0,5.1),at(w,0,5.1),at(w,.6,5.1),at(-w,.6,5.1),accent);
  for(let n=0;n<10;n++){const left=-w+n*track.width/10,right=left+track.width/10;g.quad(at(left,-.8,.05),at(left,.8,.05),at(right,.8,.05),at(right,-.8,.05),index===99?(n%2?'#20293c':'#fbfcff'):accent)}
 }
 for(let i=0;i<70;i++){
  const a=sampleAt(track,8+(track.length-16)*(i/70)),side=i%2?1:-1,d=track.width/2+10+(i*17%25),x=a.x+a.nx*d*side,z=a.z+a.nz*d*side;
  if(track.theme.ground==='#487660'||track.theme.ground==='#6cae83'||track.theme.ground==='#718b8e'){
   g.box(x,a.y-1,z,.65,3,.65,'#795a50');g.cone(x,a.y,z,2.5,6,i%2?'#376b60':'#4d8d75');
  }else g.cone(x,a.y-3,z,2+(i%3),3+(i%4),i%2?theme.accent:theme.ground);
 }
 for(let i=0;i<18;i++){const a=sampleAt(track,track.length*i/18),side=i%2?1:-1,d=track.width/2+65+(i%3)*20;g.cone(a.x+a.nx*d*side,-1,a.z+a.nz*d*side,25+i%4*7,35+i%3*13,theme.ground,5)}
 return g;
}
export class Renderer{
 constructor(canvas){
  this.canvas=canvas;this.gl=canvas.getContext('webgl',{antialias:true,alpha:false,powerPreference:'high-performance'});
  if(!this.gl)throw Error('WebGL is unavailable. Enable browser graphics or try Safari/Chrome on a supported device.');
  const gl=this.gl,vs=`attribute vec3 aPosition;attribute vec3 aNormal;attribute vec3 aColor;uniform mat4 uVP;uniform mat4 uModel;uniform vec3 uEye;varying vec3 vColor;varying float vFog;void main(){vec4 world=uModel*vec4(aPosition,1.0);vec3 normal=normalize(mat3(uModel)*aNormal);float light=.62+.38*max(dot(normal,normalize(vec3(-.5,1.0,.3))),0.0);vColor=aColor*light;vFog=clamp((distance(world.xyz,uEye)-90.0)/340.0,0.0,.95);gl_Position=uVP*world;}`;
  const fs=`precision mediump float;varying vec3 vColor;varying float vFog;uniform vec3 uSky;void main(){gl_FragColor=vec4(mix(vColor,uSky,vFog),1.0);}`;
  const shader=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s};
  this.program=gl.createProgram();gl.attachShader(this.program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(this.program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(this.program);if(!gl.getProgramParameter(this.program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(this.program));
  this.uniforms=Object.fromEntries(['uVP','uModel','uEye','uSky'].map(n=>[n,gl.getUniformLocation(this.program,n)]));this.attributes=['aPosition','aNormal','aColor'].map(n=>gl.getAttribLocation(this.program,n));
  gl.enable(gl.DEPTH_TEST);this.camera=null;this.info={drawCalls:0,vertices:0,frames:0};
 }
 upload(geometry){const gl=this.gl,buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(geometry.data),gl.STATIC_DRAW);return {buffer,count:geometry.data.length/9}}
 setTrack(track,car,hex='#46d9ff'){if(this.world)this.gl.deleteBuffer(this.world.buffer);this.world=this.upload(createWorld(track));this.track=track;this.setColor(hex);this.camera=null;this.render(car,0,true)}
 setColor(hex){if(this.car)this.gl.deleteBuffer(this.car.buffer);this.car=this.upload(createCarGeometry(hex))}
 resize(){const w=this.canvas.clientWidth,h=this.canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,1.5,Math.sqrt(1400000/Math.max(1,w*h)));const width=Math.max(1,Math.floor(w*dpr)),height=Math.max(1,Math.floor(h*dpr));if(this.canvas.width!==width||this.canvas.height!==height){this.canvas.width=width;this.canvas.height=height}this.gl.viewport(0,0,width,height)}
 draw(mesh,transform){const gl=this.gl;gl.bindBuffer(gl.ARRAY_BUFFER,mesh.buffer);for(let i=0;i<3;i++){gl.enableVertexAttribArray(this.attributes[i]);gl.vertexAttribPointer(this.attributes[i],3,gl.FLOAT,false,36,i*12)}gl.uniformMatrix4fv(this.uniforms.uModel,false,transform);gl.drawArrays(gl.TRIANGLES,0,mesh.count);this.info.drawCalls++;this.info.vertices+=mesh.count}
 render(car,dt=1/60,snap=false){
  if(!this.track)return;this.resize();const f=[Math.sin(car.yaw),Math.cos(car.yaw)],desired=[car.x-f[0]*14,car.y+7.8,car.z-f[1]*14];
  if(!this.camera||snap)this.camera=desired;else for(let i=0;i<3;i++)this.camera[i]+=(desired[i]-this.camera[i])*(1-Math.exp(-6*dt));
  const target=[car.x+f[0]*13,car.y+1.1,car.z+f[1]*13],gl=this.gl,sky=color(this.track.theme.sky);
  gl.clearColor(...sky,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);
  gl.uniformMatrix4fv(this.uniforms.uVP,false,multiply(perspective(this.canvas.width/this.canvas.height),lookAt(this.camera,target)));
  gl.uniform3fv(this.uniforms.uEye,this.camera);gl.uniform3fv(this.uniforms.uSky,sky);this.info.drawCalls=0;this.info.vertices=0;
  this.draw(this.world,identity);this.draw(this.car,model(car));this.info.frames++;
 }
}
