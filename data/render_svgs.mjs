import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';

const args=process.argv.slice(2);const dirs=args.filter(v=>!v.startsWith('--'));
const compactOnly=args.includes('--compact-only');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const dir of dirs){
  const files=(await fs.readdir(dir)).filter(n=>n.endsWith('.svg')&&(!compactOnly||n.includes('compact')));
  const records=[];
  for(const name of files){
    const source=path.join(dir,name),target=source.slice(0,-4)+'.png';
    const metadata=await sharp(source,{density:144}).png().toFile(target);
    records.push({source:path.resolve(source),sourceSha256:hash(await fs.readFile(source)),output:path.resolve(target),outputSha256:hash(await fs.readFile(target)),width:metadata.width,height:metadata.height});
  }
  await fs.writeFile(path.join(dir,'raster_render_manifest.json'),JSON.stringify({renderer:'sharp',versions:sharp.versions,densityDpi:144,records},null,2));
  console.log(`Rendered ${records.length} actual SVG plots in ${dir}`);
}
