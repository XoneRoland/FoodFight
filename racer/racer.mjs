import {tracks} from './tracks.mjs';
import {STEP} from './physics.mjs';
import {RaceSession,formatTime} from './race.mjs';
import {Renderer} from './renderer.mjs';
import {loadProgress,saveProgress,applyResult,carColors} from './progress.mjs';
import {Controls} from './controls.mjs';
const $=id=>document.getElementById(id),screens=['menu','trackMenu','help','pauseMenu','result'];
let progress=loadProgress(),current=progress.unlocked-1,session=new RaceSession(tracks[current]),renderer,noticeTimer;
let attempted=false,finished=false,accounted={distance:0,airtime:0,recoveries:0};
function notify(text){$('notice').textContent=text;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>$('notice').textContent='',2600)}
function view(screen){for(const id of screens)$(id).hidden=id!==screen;const active=['countdown','racing','paused'].includes(session.mode);$('hud').hidden=!active;$('driveControls').hidden=!active||session.mode==='paused';if(screen)$('countdown').textContent=''}
try{renderer=new Renderer($('scene'));renderer.setTrack(session.track,session.car,progress.color)}catch(error){$('graphicsMessage').textContent=error.message;$('graphicsError').hidden=false;$('playButton').disabled=true}
function persist(){if(!saveProgress(progress))notify('Progress stays in this session; browser storage is unavailable.');updateSummary()}
function updateSummary(){
 $('progressSummary').textContent=progress.completed.length+' / 12 tracks completed · '+progress.stats.finishes+' finishes · '+(progress.stats.distance/1000).toFixed(1)+' km driven';
}
function flushStats(){
 if(!attempted)return;let changed=false;
 for(const [key,value] of [['distance',session.car.distance],['airtime',session.car.airtime],['recoveries',session.recoveries]]){const delta=Math.max(0,value-accounted[key]);if(delta>0){progress.stats[key]+=delta;accounted[key]=value;changed=true}}
 if(changed)persist();
}
function startTrack(index){
 if(!renderer||index<0||index>=tracks.length||tracks[index].id>progress.unlocked)return;
 flushStats();attempted=false;finished=false;accounted={distance:0,airtime:0,recoveries:0};current=index;controls.clear();session=new RaceSession(tracks[index]);session.start();renderer.setTrack(session.track,session.car,progress.color);
 $('trackLabel').textContent=(index+1)+'. '+session.track.name;$('notice').textContent='';view(null);
}
function pause(){if(session.mode==='paused'){session.resume();controls.clear();view(null)}else if(['racing','countdown'].includes(session.mode)){session.pause();controls.clear();flushStats();view('pauseMenu')}}
const controls=new Controls($('driveControls'),action=>{if(action==='restart'&&session.mode!=='menu')startTrack(current);if(action==='pause')pause()});
function trackMenu(){flushStats();session.mode='menu';controls.clear();drawTracks();view('trackMenu')}
function drawTracks(){
 $('trackCards').replaceChildren();
 for(const [index,track] of tracks.entries()){
  const unlocked=track.id<=progress.unlocked;const card=document.createElement('article');card.className='track-card'+(unlocked?'':' locked');card.dataset.track=track.id;
  const number=document.createElement('span');number.className='track-number';number.textContent='TRACK '+String(track.id).padStart(2,'0');
  const title=document.createElement('h3');title.textContent=track.name;
  const info=document.createElement('p');info.textContent=track.difficulty+' • '+Math.round(track.length)+'m • '+(unlocked?progress.completed.includes(track.id)?'COMPLETED':'UNLOCKED':'LOCKED');
  const best=document.createElement('p');best.textContent='Best: '+(progress.bestTimes[track.id]?formatTime(progress.bestTimes[track.id])+' · '+progress.medals[track.id]:'—')+' | Gold '+formatTime(track.gold)+' · Silver '+formatTime(track.silver);
  const play=document.createElement('button');play.textContent=unlocked?'RACE':'LOCKED';play.disabled=!unlocked;play.addEventListener('click',()=>startTrack(index));
  card.append(number,title,info,best,play);$('trackCards').appendChild(card);
 }
}
function finish(){
 controls.clear();const result=session.result;if(finished)return;finished=true;flushStats();const oldUnlock=progress.unlocked;progress=applyResult(progress,session.track,result);persist();
 $('resultTrack').textContent=session.track.name;$('resultTime').textContent=formatTime(result.time);$('resultBest').textContent=formatTime(progress.bestTimes[session.track.id]);$('resultMedal').textContent=result.medal.toUpperCase()+' MEDAL';
 $('resultUnlock').textContent=progress.unlocked>oldUnlock?'NEXT TRACK UNLOCKED':progress.completed.length===12?'All 12 tracks conquered. Chase your next gold medal!':'Personal bests and medals stay saved on this device.';$('nextButton').hidden=current===tracks.length-1;view('result');
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
for(const color of carColors){
 const button=document.createElement('button');button.className='color-choice';button.style.setProperty('--car-color',color.hex);button.setAttribute('aria-label','Car color: '+color.name);button.setAttribute('aria-pressed',String(progress.color===color.hex));
 button.onclick=()=>{progress.color=color.hex;persist();if(renderer)renderer.setColor(color.hex);for(const b of $('colorOptions').children)b.setAttribute('aria-pressed',String(b===button))};$('colorOptions').appendChild(button);
}
for(const link of document.querySelectorAll('a[href="../"]'))link.addEventListener('click',()=>{controls.clear();flushStats()});
addEventListener('pagehide',()=>{controls.clear();flushStats()});
updateSummary();
let last=performance.now(),acc=0;
function frame(now){
 const dt=Math.min((now-last)/1000,.12);last=now;acc+=dt;
 while(acc>=STEP){const mode=session.mode,recoveries=session.recoveries;session.step(controls.value(),STEP);if(session.recoveries>recoveries){controls.clear();renderer.camera=null;notify('Back to checkpoint · +3 seconds')}if(mode==='countdown'&&session.mode==='racing'&&!attempted){attempted=true;progress.stats.attempts++;persist()}if(mode!=='finished'&&session.mode==='finished')finish();acc-=STEP}
 if(renderer&&!renderer.gl.isContextLost())renderer.render(session.car,dt);
 $('timer').textContent=formatTime(session.time);$('speed').textContent=Math.round(Math.hypot(session.car.vx,session.car.vz)*3.6)+' KM/H';
 $('checkpointLabel').textContent='CHECKPOINTS '+session.nextCheckpoint+' / '+session.track.checkpoints.length;
 $('countdown').textContent=session.mode==='countdown'?String(Math.max(1,Math.ceil(session.remaining))):session.mode==='racing'&&session.goTime>0?'GO!':'';
 requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
