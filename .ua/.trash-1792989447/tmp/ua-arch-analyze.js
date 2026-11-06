const fs=require("fs");
const g=JSON.parse(fs.readFileSync("intermediate/assembled-graph.json","utf8"));
const T=new Set(["file","config","document","service","pipeline","table","schema","resource","endpoint"]);
const n=g.nodes.filter(x=>T.has(x.type));
const L={
 entry:["layer:entry-and-orchestration","Entry & Orchestration","Package entry points, CLI, central configuration, and path resolution that boot the bot."],
 agent:["layer:agent","AI Agent","Gemini-powered agent, system prompt construction, and agent tools (scheduling, memory, event assignment)."],
 core:["layer:core","Core Message Logic","Message filtering, handling, owner commands, roles, rate limiting, and formatting of replies."],
 zalo:["layer:zalo-integration","Zalo Integration","Zalo platform adapters: bot API, personal account, QR login, webhook and polling receivers."],
 storage:["layer:storage","Storage","Persistent data stores, text files, and process locking."],
 system:["layer:system-services","System & Remote Services","Auto-update, bot process supervision, handover, remote config/server, logging and first-run setup."],
 ui:["layer:ui","Admin Web UI & Desktop","FastAPI admin web server with static HTML/CSS/JS assets, plus desktop tray app and autostart."],
 tests:["layer:tests","Tests","pytest suites covering bot, admin, agent, storage, polling, updater, and remote features."],
 pack:["layer:packaging-scripts","Packaging & Scripts","PowerShell/CMD scripts, PyInstaller spec, and build/secret-check tooling for the Windows executable."],
 cfg:["layer:config-templates","Configuration & Templates","Project config, env example, prompt/memory templates, and workspace tool examples."],
 docs:["layer:documentation","Documentation","README, project map, plans, and operational guides."]
};
const a={};for(const k in L)a[k]=[];
for(const x of n){const p=x.filePath||x.id.replace(/^[a-z]+:/,"");let k;
 if(p.startsWith("tests/"))k="tests";
 else if(p.startsWith("scripts/")||p==="ZaloBot.cmd")k="pack";
 else if(p.startsWith("src/bot/templates/")||p.startsWith("tools/")||p.startsWith("workspace/")||x.type==="config"||p===".gitattributes")k="cfg";
 else if(x.type==="document"&&!p.startsWith("src/bot/ui/"))k="docs";
 else if(p.startsWith("src/bot/ui/"))k="ui";
 else if(p.startsWith("src/bot/agent/"))k="agent";
 else if(p.startsWith("src/bot/core/")&&!p.endsWith("__init__.py")||p.startsWith("src/bot/core/"))k="core";
 else if(p.startsWith("src/bot/zalo/"))k="zalo";
 else if(p.startsWith("src/bot/storage/"))k="storage";
 else if(p.startsWith("src/bot/system/"))k="system";
 else k="entry";
 a[k].push(x.id);}
const out=Object.keys(L).filter(k=>a[k].length).map(k=>({id:L[k][0],name:L[k][1],description:L[k][2],nodeIds:a[k]}));
fs.writeFileSync("intermediate/layers.json",JSON.stringify(out,null,1));
console.log(n.length,out.reduce((s,l)=>s+l.nodeIds.length,0));
out.forEach(l=>console.log(l.name,l.nodeIds.length));
