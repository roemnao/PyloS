const f=(n,s,t,c,l)=>({id:"file:scripts/"+n,type:"file",name:n,filePath:"scripts/"+n,summary:s,tags:t,complexity:c,languageNotes:l});
const nodes=[
f("build-exe.ps1","Builds the one-file windowed ZaloBot.exe with PyInstaller, scans the output for leaked secrets, and copies the exe next to userdata\ unless -NoCopy is given.",["build-system","packaging","powershell","security"],"simple","Requires ASCII-only content because Windows PowerShell 5.1 reads BOM-less files as ANSI."),
f("install-task.ps1","Registers Windows Task Scheduler tasks that launch the bot and the admin UI at logon through run-forever.ps1, with unlimited run time and auto-restart.",["deployment","scheduler","powershell","automation"],"simple"),
f("run-forever.ps1","Supervisor loop that runs the bot or admin UI via python -m bot and restarts it after exit, logging to supervisor.log and stopping on exit codes 2, 3 and 5.",["supervisor","entry-point","powershell","process-management"],"simple"),
f("uninstall-task.ps1","Stops and unregisters the bot and admin scheduled tasks, then force-kills leftover python processes running the bot or admin command.",["deployment","scheduler","powershell","cleanup"],"simple"),
{id:"function:scripts/install-task.ps1:Register-BotTask",type:"function",name:"Register-BotTask",filePath:"scripts/install-task.ps1",lineRange:[20,34],summary:"Creates a hidden PowerShell scheduled-task action with a logon trigger and restart-on-failure settings, registers it, and starts it immediately.",tags:["scheduler","task-registration","powershell"],complexity:"simple"}];
const e=(s,t,ty,w)=>({source:s,target:t,type:ty,direction:"forward",weight:w});
const edges=[
e("file:scripts/install-task.ps1","function:scripts/install-task.ps1:Register-BotTask","contains",1.0),
e("file:scripts/install-task.ps1","file:scripts/run-forever.ps1","depends_on",0.6),
e("file:scripts/uninstall-task.ps1","file:scripts/install-task.ps1","related",0.5)];
require("fs").writeFileSync(".ua/intermediate/batch-10.json",JSON.stringify({nodes,edges},null,1));
const ids=new Set(nodes.map(n=>n.id));console.log(edges.every(x=>ids.has(x.source)&&ids.has(x.target)));
