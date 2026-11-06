export class Controls{
 constructor(root,onAction){
  this.keys=new Set();this.pointers=new Map();this.root=root;
  this.mapping={KeyW:'throttle',ArrowUp:'throttle',KeyS:'brake',ArrowDown:'brake',KeyA:'left',ArrowLeft:'left',KeyD:'right',ArrowRight:'right'};
  for(const button of root.querySelectorAll('[data-drive]')){
   const action=button.dataset.drive;
   button.addEventListener('pointerdown',e=>{if(e.button!==0)return;e.preventDefault();button.setPointerCapture(e.pointerId);this.pointers.set(e.pointerId,{action,button});this.paint()});
   const release=e=>{this.pointers.delete(e.pointerId);this.paint()};
   for(const event of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(event,release);
  }
  addEventListener('keydown',e=>{
   if(/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName))return;
   if(this.mapping[e.code]){e.preventDefault();this.keys.add(e.code);this.paint()}
   if(!e.repeat&&e.code==='KeyR'){e.preventDefault();onAction('restart')}
   if(!e.repeat&&e.code==='Escape'){e.preventDefault();onAction('pause')}
  });
  addEventListener('keyup',e=>{if(this.mapping[e.code]){e.preventDefault();this.keys.delete(e.code);this.paint()}});
  addEventListener('blur',()=>this.clear());addEventListener('pagehide',()=>this.clear());
  document.addEventListener('visibilitychange',()=>{if(document.hidden)this.clear()});
 }
 held(action){return [...this.keys].some(key=>this.mapping[key]===action)||[...this.pointers.values()].some(p=>p.action===action)}
 value(){return {throttle:+this.held('throttle'),brake:+this.held('brake'),steer:+this.held('right')-+this.held('left')}}
 paint(){for(const button of this.root.querySelectorAll('[data-drive]')){const held=this.held(button.dataset.drive);button.classList.toggle('held',held);button.setAttribute('aria-pressed',String(held))}}
 clear(){this.keys.clear();this.pointers.clear();this.paint()}
}
