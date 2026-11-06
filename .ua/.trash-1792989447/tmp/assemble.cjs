const fs=require("fs");const I="D:/pylosSever/.ua/intermediate/";
const rd=f=>JSON.parse(fs.readFileSync(I+f,"utf8"));
const g=rd("assembled-graph.json"),scan=rd("scan-result.json");
let layers=rd("layers.json");if(!Array.isArray(layers))layers=layers.layers;
let tour=rd("tour.json");if(!Array.isArray(tour))tour=tour.steps;
const ids=new Set(g.nodes.map(n=>n.id));
const pre=["file:","config:","document:","service:","pipeline:","table:","schema:","resource:","endpoint:"];
const fixId=i=>pre.some(p=>i.startsWith(p))?i:"file:"+i;
layers=layers.map(l=>{let n=l.nodeIds||l.nodes||[];n=n.map(x=>typeof x==="object"?x.id:x).map(fixId).filter(i=>ids.has(i));
 return {id:l.id||"layer:"+l.name.toLowerCase().replace(/\s+/g,"-"),name:l.name,description:l.description,nodeIds:n}});
tour=tour.map(s=>{const o={...s};if(o.nodesToInspect&&!o.nodeIds){o.nodeIds=o.nodesToInspect;delete o.nodesToInspect}
 if(o.whyItMatters&&!o.description){o.description=o.whyItMatters;delete o.whyItMatters}
 o.nodeIds=(o.nodeIds||[]).map(fixId).filter(i=>ids.has(i));return o}).sort((a,b)=>a.order-b.order);
const p=scan.project||scan;
const out={version:"1.0.0",project:{name:p.name||scan.name,languages:p.languages||scan.languages,frameworks:p.frameworks||scan.frameworks,description:p.description||scan.description,analyzedAt:new Date().toISOString(),gitCommitHash:"634d4754adb71c20217a691782b8bf13d5e67a49"},nodes:g.nodes,edges:g.edges,layers,tour};
fs.writeFileSync(I+"assembled-graph.json",JSON.stringify(out,null,2));
console.log(JSON.stringify(out.project),layers.length,tour.length);
