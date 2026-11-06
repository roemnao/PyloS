const fs=require("fs");
const r=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-extract-results-4.json","utf8"));
const imp=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-analyzer-input-4.json","utf8")).batchImportData;
const fsum={
"tests/conftest.py":["Shared pytest fixtures and fakes (FakeZalo, FakeAgent, FakeWeb) plus settings, event and bot factory helpers used across the bot test suite.",["test","fixtures","mocking","test-helper"]],
"tests/test_bot.py":["Extensive tests of the bot message pipeline: trigger and mode handling, owner/allow/deny rules, dedupe, rate limits, budget, history, leader roles and reply splitting.",["test","bot","message-handling","permissions"]],
"tests/test_desktop.py":["Tests for desktop packaging support: app home resolution, hidden subprocesses, autostart, tray actions, ports, logging and secret scanning.",["test","desktop","packaging","windows"]],
"tests/test_filter.py":["Tests for the message filter that decides via rules or Gemini classification whether the bot should respond, including retries and error handling.",["test","filter","gemini","classification"]],
"tests/test_memorydata.py":["Tests for chat memory logging, store trimming and the tool that reads only the current chat's history.",["test","memory","storage","tool"]],
"tests/test_personal.py":["Tests for the personal Zalo account integration: session loading, message mapping, sending, mentions, member lists and tag handling using a fake API.",["test","zalo-personal","mentions","mocking"]],
"tests/test_remote_config.py":["Tests for remote web config application, heartbeat, session uploader batching and link-code handling.",["test","remote-config","web-sync","heartbeat"]]};
const cx={"tests/conftest.py":"moderate","tests/test_bot.py":"complex","tests/test_desktop.py":"complex","tests/test_filter.py":"moderate","tests/test_memorydata.py":"moderate","tests/test_personal.py":"moderate","tests/test_remote_config.py":"moderate"};
const hum=n=>n.replace(/^test_/,"").replace(/^_/,"").replace(/_/g," ");
const files=r.results.map(x=>x.path).sort();
const per={};
for(const f of r.results){
 const p=f.path,nodes=[],edges=[];
 const fid="file:"+p;
 nodes.push({id:fid,type:"file",name:p.split("/").pop(),filePath:p,summary:fsum[p][0],tags:fsum[p][1],complexity:cx[p]});
 for(const i of imp[p])edges.push({source:fid,target:"file:"+i,type:"imports",direction:"forward",weight:0.7});
 if(p!=="tests/conftest.py")edges.push({source:fid,target:"file:tests/conftest.py",type:"depends_on",direction:"forward",weight:0.6});
 const isT=p!=="tests/conftest.py";
 for(const c of f.classes||[]){
  const id=`class:${p}:${c.name}`;
  nodes.push({id,type:"class",name:c.name,filePath:p,lineRange:[c.startLine,c.endLine],summary:`Test double ${c.name} used to simulate collaborators in ${p.split("/").pop()}.`,tags:["test-double","mocking","test-helper"],complexity:c.endLine-c.startLine>25?"moderate":"simple"});
  edges.push({source:fid,target:id,type:"contains",direction:"forward",weight:1.0});
 }
 for(const fn of f.functions||[]){
  const len=fn.endLine-fn.startLine+1;
  if(isT&&len<10)continue;
  const id=`function:${p}:${fn.name}`;
  const t=fn.name.startsWith("test_");
  nodes.push({id,type:"function",name:fn.name,filePath:p,lineRange:[fn.startLine,fn.endLine],
   summary:t?`Test case verifying: ${hum(fn.name)}.`:`Helper or fixture providing ${hum(fn.name)} for the tests.`,
   tags:t?["test","unit-test",p.includes("bot")?"bot":"behavior"]:["test-helper","fixture","setup"],
   complexity:len>30?"moderate":"simple"});
  edges.push({source:fid,target:id,type:"contains",direction:"forward",weight:1.0});
 }
 per[p]={nodes,edges};
}
const N=files.reduce((a,p)=>a+per[p].nodes.length,0),E=files.reduce((a,p)=>a+per[p].edges.length,0);
const parts=Math.max(1,Math.ceil(Math.max(N/60,E/120)));
console.log(N,E,parts);
const out=".ua/intermediate/";
if(parts==1){fs.writeFileSync(out+"batch-4.json",JSON.stringify({nodes:files.flatMap(p=>per[p].nodes),edges:files.flatMap(p=>per[p].edges)},null,1));}
else{const sz=Math.ceil(files.length/parts);for(let k=0;k<parts;k++){const fs2=files.slice(k*sz,(k+1)*sz);if(!fs2.length)continue;
fs.writeFileSync(out+`batch-4-part-${k+1}.json`,JSON.stringify({nodes:fs2.flatMap(p=>per[p].nodes),edges:fs2.flatMap(p=>per[p].edges)},null,1));console.log("part",k+1,fs2.length);}}
