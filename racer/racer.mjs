import {tracks} from './tracks.mjs';
import {STEP} from './physics.mjs';
import {RaceSession,formatTime} from './race.mjs';
import {Renderer} from './renderer.mjs';
import {Controls} from './controls.mjs';
const $=id=>document.getElementById(id),screens=['menu','trackMenu','help','pauseMenu','result'];
let current=0,session=new RaceSession(tracks[0]),renderer,noticeTimer;
function notify(text){$('notice').textContent=text;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>$('notice').textContent='',2600)}
function view(screen){for(const id of screens)$(id).hidden=id!==screen;const active=['countdown','racing','paused'].includes(session.mode);$('hud').hidden=!active;$('driveControls').hidden=!active||session.mode==='paused';if(screen)$('countdown').textContent=''}
try{renderer=new Renderer($('scene'));renderer.setTrack(session.track,session.car)}catch(error){$('graphicsMessage').textContent=error.message;$('graphicsError').hidden=false;$('playButton').disabled=true}
function startTrack(index){
 if(!renderer)return;current=index;controls.clear();session=new RaceSession(tracks[index]);session.start();renderer.setTrack(session.track,session.car);
 $('trackLabel').textContent=(index+1)+'. '+session.track.name;$('notice').textContent='';view(null);
}
function pause(){if(session.mode==='paused'){session.resume();controls.clear();view(null)}else if(['racing','countdown'].includes(session.mode)){session.pause();controls.clear();view('pauseMenu')}}
const controls=new Controls($('driveControls'),action=>{if(action==='restart'&&session.mode!=='menu')startTrack(current);if(action==='pause')pause()});
function trackMenu(){session.mode='menu';controls.clear();drawTracks();view('trackMenu')}
function drawTracks(){
 $('trackCards').replaceChildren();
 for(const [index,track] of tracks.entries()){
  const card=document.createElement('article');card.className='track-card';
  const number=document.createElement('span');number.className='track-number';number.textContent='TRACK '+String(track.id).padStart(2,'0');
  const title=document.createElement('h3');title.textContent=track.name;
  const info=document.createElement('p');info.textContent=track.difficulty+' • '+Math.round(track.length)+'m';
  const best=document.createElement('p');best.textContent='Gold '+formatTime(track.gold)+' • Silver '+formatTime(track.silver);
  const play=document.createElement('button');play.textContent='RACE';play.addEventListener('click',()=>startTrack(index));
  card.append(number,title,info,best,play);$('trackCards').appendChild(card);
 }
}
function finish(){
 controls.clear();const result=session.result;
 $('resultTrack').textContent=session.track.name;$('resultTime').textContent=formatTime(result.time);$('resultBest').textContent=formatTime(result.time);$('resultMedal').textContent=result.medal.toUpperCase()+' MEDAL';
 $('resultUnlock').textContent='Finish any time to progress. Improve your line on the next run.';$('nextButton').hidden=current===tracks.length-1;view('result');
}
$('playButton').onclick=()=>startTrack(current);$('trackSelectButton').onclick=trackMenu;$('trackBack').onclick=()=>view('menu');
$('controlsButton').onclick=()=>view('help');$('helpBack').onclick=()=>view('menu');
for(const id of ['restartButton','pauseRestart','retryButton'])$(id).onclick=()=>startTrack(current);
$('pauseButton').onclick=pause;$('resumeButton').onclick=pause;
for(const id of ['pauseTracks','resultTracks'])$(id).onclick=trackMenu;
$('nextButton').onclick=()=>{if(current<tracks.length-1)startTrack(current+1)};
addEventListener('blur',()=>{if(['racing','countdown'].includes(session.mode))pause()});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&['racing','countdown'].includes(session.mode))pause()});
$('scene').addEventListener('webglcontextlost',e=>{e.preventDefault();if(['racing','countdown'].includes(session.mode))pause();$('graphicsMessage').textContent='The graphics context was interrupted. Reload Racer to restore 3D rendering; saved progress stays on this device.';$('graphicsError').hidden=false});
let last=performance.now(),acc=0;
function frame(now){
 const dt=Math.min((now-last)/1000,.12);last=now;acc+=dt;
 while(acc>=STEP){const mode=session.mode,recoveries=session.recoveries;session.step(controls.value(),STEP);if(session.recoveries>recoveries){controls.clear();renderer.camera=null;notify('Back to checkpoint · +3 seconds')}if(mode!=='finished'&&session.mode==='finished')finish();acc-=STEP}
 if(renderer&&!renderer.gl.isContextLost())renderer.render(session.car,dt);
 $('timer').textContent=formatTime(session.time);$('speed').textContent=Math.round(Math.hypot(session.car.vx,session.car.vz)*3.6)+' KM/H';
 $('checkpointLabel').textContent='CHECKPOINTS '+session.nextCheckpoint+' / '+session.track.checkpoints.length;
 $('countdown').textContent=session.mode==='countdown'?String(Math.max(1,Math.ceil(session.remaining))):session.mode==='racing'&&session.goTime>0?'GO!':'';
 requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
