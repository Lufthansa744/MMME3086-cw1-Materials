// Render only Figure2 and update only its raster-manifest record.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const source=path.resolve('data/taskA/figure2_mesh_compact.svg');
const target=source.replace(/\.svg$/,'.png');
const manifestPath=path.resolve('data/taskA/raster_render_manifest.json');
const metadata=await sharp(source,{density:144}).png().toFile(target);
let manifest;
try{manifest=JSON.parse(await fs.readFile(manifestPath,'utf8'));}
catch(e){if(e.code!=='ENOENT')throw e;manifest={renderer:'sharp',versions:sharp.versions,densityDpi:144,records:[]};}
const record={source,sourceSha256:hash(await fs.readFile(source)),output:target,outputSha256:hash(await fs.readFile(target)),width:metadata.width,height:metadata.height};
const oldIndex=manifest.records.findIndex(r=>path.resolve(r.source)===source);
if(oldIndex<0)manifest.records.push(record);else manifest.records[oldIndex]=record;
await fs.writeFile(manifestPath,JSON.stringify(manifest,null,2));
console.log(JSON.stringify(record));
