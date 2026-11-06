const fs=require('fs');const graph=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const issues=[],warnings=[];const nodeIds=new Set(),seen=new Map();
graph.nodes.forEach((n,i)=>{if(!n.id){issues.push(`Node[${i}] missing id`);return}
 ['type','name','summary'].forEach(k=>{if(!n[k])issues.push(`Node '${n.id}' missing ${k}`)});
 if(!n.tags||!n.tags.length)issues.push(`Node '${n.id}' missing tags`);
 if(seen.has(n.id))issues.push(`Duplicate node ID '${n.id}'`);else seen.set(n.id,i);nodeIds.add(n.id)});
graph.edges.forEach((e,i)=>{if(!nodeIds.has(e.source))issues.push(`Edge[${i}] source '${e.source}' missing`);if(!nodeIds.has(e.target))issues.push(`Edge[${i}] target '${e.target}' missing`)});
const ft=new Set(['file','config','document','service','pipeline','table','schema','resource','endpoint']);
const asg=new Map();graph.layers.forEach(l=>(l.nodeIds||[]).forEach(id=>{if(!nodeIds.has(id))issues.push(`Layer '${l.id}' refs missing '${id}'`);if(asg.has(id))issues.push(`'${id}' in multiple layers`);asg.set(id,l.id)}));
graph.nodes.filter(n=>ft.has(n.type)).forEach(n=>{if(!asg.has(n.id))issues.push(`File node '${n.id}' not in any layer`)});
graph.tour.forEach((s,i)=>(s.nodeIds||[]).forEach(id=>{if(!nodeIds.has(id))issues.push(`Tour[${i}] refs missing '${id}'`)}));
const we=new Set([...graph.edges.map(e=>e.source),...graph.edges.map(e=>e.target)]);
graph.nodes.forEach(n=>{if(!we.has(n.id))warnings.push(`Orphan node '${n.id}'`)});
const cnt=(a,k)=>a.reduce((m,x)=>(m[x[k]]=(m[x[k]]||0)+1,m),{});
fs.writeFileSync(process.argv[3],JSON.stringify({issues,warnings,stats:{nodes:graph.nodes.length,edges:graph.edges.length,layers:graph.layers.length,tour:graph.tour.length,nodeTypes:cnt(graph.nodes,'type'),edgeTypes:cnt(graph.edges,'type')}},null,2));
