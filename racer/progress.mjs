import {tracks} from './tracks.mjs';
import {medalFor} from './race.mjs';
export const SAVE_KEY='ezyplay_racer_v1';
export const carColors=[{hex:'#46d9ff',name:'Glacier blue'},{hex:'#ff6479',name:'Coral red'},{hex:'#ffd166',name:'Sunburst yellow'},{hex:'#a78bfa',name:'Electric violet'}];
const validId=id=>Number.isInteger(id)&&id>=1&&id<=tracks.length;
const count=n=>Number.isFinite(n)&&n>=0?n:0;
export function normalizeProgress(raw){
 const data=raw&&typeof raw==='object'&&!Array.isArray(raw)?raw:{};
 const completed=new Set(Array.isArray(data.completed)?data.completed.filter(validId):[]),bestTimes={},medals={};
 for(const track of tracks){
  const time=data.bestTimes?.[track.id];
  if(Number.isFinite(time)&&time>0&&time<36000){bestTimes[track.id]=time;completed.add(track.id);medals[track.id]=['Gold','Silver','Bronze'].includes(data.medals?.[track.id])?data.medals[track.id]:medalFor(track,time)}
 }
 const highest=completed.size?Math.max(...completed)+1:1;
 const unlocked=Math.min(tracks.length,Math.max(1,highest,Number.isInteger(data.unlocked)?data.unlocked:1));
 return {...data,version:1,unlocked,completed:[...completed].sort((a,b)=>a-b),bestTimes,medals,color:carColors.some(c=>c.hex===data.color)?data.color:carColors[0].hex,stats:Object.fromEntries(['attempts','finishes','distance','airtime','recoveries'].map(k=>[k,count(data.stats?.[k])]))};
}
export function loadProgress(storage){try{return normalizeProgress(JSON.parse((storage||globalThis.localStorage).getItem(SAVE_KEY)||'{}'))}catch{return normalizeProgress({})}}
export function saveProgress(progress,storage){try{(storage||globalThis.localStorage).setItem(SAVE_KEY,JSON.stringify(progress));return true}catch{return false}}
export function applyResult(progress,track,result){
 if(result.track!==track.id||!Number.isFinite(result.time)||result.time<=0)throw Error('Invalid race result');
 const next=JSON.parse(JSON.stringify(progress)),old=next.bestTimes[track.id];
 if(!old||result.time<old)next.bestTimes[track.id]=result.time;
 const rank={Bronze:1,Silver:2,Gold:3},medal=medalFor(track,result.time);
 if(!next.medals[track.id]||rank[medal]>rank[next.medals[track.id]])next.medals[track.id]=medal;
 if(!next.completed.includes(track.id))next.completed.push(track.id);
 next.completed.sort((a,b)=>a-b);next.unlocked=Math.max(next.unlocked,Math.min(tracks.length,track.id+1));next.stats.finishes++;
 return next;
}
