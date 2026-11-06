import { tracks } from './tracks.mjs';
import { createCar,updateCar,STEP } from './physics.mjs';
import { Renderer } from './renderer.mjs';
import { Controls } from './controls.mjs';
const $=id=>document.getElementById(id);
let track=tracks[0],car=createCar(track),active=false,paused=false;
let renderer;
try{renderer=new Renderer($('scene'));renderer.setTrack(track,car)}catch(error){$('graphicsMessage').textContent=error.message;$('graphicsError').hidden=false;$('playButton').disabled=true}
function restart(){car=createCar(track);controls.clear();active=true;paused=false;$('menu').hidden=true;$('pauseMenu').hidden=true;$('hud').hidden=false;$('driveControls').hidden=false;if(renderer)renderer.camera=null}
function pause(){if(!active)return;paused=!paused;controls.clear();$('pauseMenu').hidden=!paused;$('driveControls').hidden=paused}
const controls=new Controls($('driveControls'),action=>{if(action==='restart'&&active)restart();if(action==='pause')pause()});
$('playButton').onclick=restart;$('restartButton').onclick=restart;$('pauseButton').onclick=pause;$('resumeButton').onclick=pause;$('pauseRestart').onclick=restart;
$('controlsButton').onclick=()=>{$('help').hidden=false};$('helpBack').onclick=()=>{$('help').hidden=true};
$('trackSelectButton').onclick=()=>restart();$('pauseTracks').onclick=()=>{active=false;controls.clear();$('pauseMenu').hidden=true;$('hud').hidden=true;$('driveControls').hidden=true;$('menu').hidden=false};
addEventListener('blur',()=>{if(active&&!paused)pause()});document.addEventListener('visibilitychange',()=>{if(document.hidden&&active&&!paused)pause()});
let last=performance.now(),acc=0;
function frame(now){const dt=Math.min((now-last)/1000,.1);last=now;acc+=dt;while(acc>=STEP){if(active&&!paused){const result=updateCar(car,track,controls.value(),STEP);if(result.recover)car=createCar(track)}acc-=STEP}if(renderer)renderer.render(car,dt);$('speed').textContent=Math.round(Math.hypot(car.vx,car.vz)*3.6)+' KM/H';requestAnimationFrame(frame)}
requestAnimationFrame(frame);
