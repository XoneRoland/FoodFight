import { mkdir, copyFile, cp } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../',import.meta.url));
const out=path.join(root,'dist');
await mkdir(out,{recursive:true});
for(const file of ['index.html','style.css','Food_Fight_Development.html','privacy.html'])await copyFile(path.join(root,file),path.join(out,file));
for(const dir of ['assets','food-fight','racer'])await cp(path.join(root,dir),path.join(out,dir),{recursive:true});
console.log('EzyPlay static site built in dist/');
