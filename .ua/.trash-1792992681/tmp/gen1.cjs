const fs=require("fs");
const b=require("../intermediate/batches.json").batches.find(x=>x.batchIndex===1);
const ex=require("./ua-file-extract-results-1.json").results;
const L={};for(const r of ex){L[r.path]={};for(const f of (r.functions||[]))L[r.path][f.name]=[f.startLine,f.endLine];for(const c of (r.classes||[]))L[r.path][c.name]=[c.startLine,c.endLine];}
const F={
"src/bot/config.py":["Loads bot Settings from environment variables and the settings.env file, with typed helpers and validation errors surfaced as user-readable messages.",["configuration","settings","environment","dataclass"],"complex"],
"src/bot/storage/process_lock.py":["Single-instance file lock preventing two bot processes from running on the same data directory.",["lock","process-management","storage"],"simple"],
"src/bot/system/__init__.py":["Package marker for the system subpackage.",["package","barrel","system"],"simple"],
"src/bot/system/auto_update.py":["Source-install auto-updater: checks pending git commits, runs git pull, reinstalls dependencies when needed and reports the result.",["auto-update","git","system","utility"],"moderate"],
"src/bot/system/bot_process.py":["Manages background bot and admin processes using lock and PID files, systemd on VPS, standby flags and status reporting shared by CLI and web UI.",["process-management","service","systemd","status"],"complex"],
"src/bot/system/first_run_setup.py":["First-run preparation of the userdata directory, creating missing folders and template files and generating a random admin token.",["setup","onboarding","security","utility"],"simple"],
"src/bot/system/handover.py":["Builds and imports zip bundles of bot data to migrate the bot between local machine and VPS, validating entry names and sizes before writing.",["handover","backup","zip","migration"],"moderate"],
"src/bot/system/handover_job.py":["Background job orchestrating a bot transfer between local and VPS: precheck, stop old side, copy data, start new side, rollback on failure.",["handover","job","orchestration","rollback"],"complex"],
"src/bot/system/remote_config.py":["Applies bot settings pushed from the owner web, caches them locally, and sends a per-minute heartbeat with the last error.",["remote-config","heartbeat","sync","configuration"],"complex"],
"src/bot/system/remote_server.py":["HTTP client from the local app to the VPS admin server using REMOTE_URL and admin token, with sync and async helpers and user-friendly RemoteError.",["http-client","remote","vps","networking"],"moderate"],
"src/bot/system/server_info.py":["Read-only collection of host info (uptime, memory, git commit, latest remote commit, systemd state) for the Server page.",["monitoring","system-info","git","utility"],"moderate"],
"src/bot/ui/admin/__init__.py":["Package marker for the admin UI subpackage.",["package","barrel","admin-ui"],"simple"],
"src/bot/ui/admin/admin_sessions.py":["In-memory Gmail login sessions and device-key registry for the admin web server, with 12-hour expiry.",["authentication","session","admin-ui","security"],"moderate"],
"src/bot/ui/admin/admin_web_server.py":["FastAPI admin server bound to localhost, exposing authenticated /api routes for settings, bot control, VPS connection, handover, history and logs with DNS-rebinding and origin protections.",["api-handler","fastapi","admin-ui","security","entry-point"],"complex"],
"src/bot/ui/admin/settings_file.py":["Reads and atomically writes the .env settings file preserving comments, validating changes through Settings and backing up to .env.bak.",["settings","env-file","validation","admin-ui"],"moderate"],
"src/bot/ui/desktop/desktop_app.py":["Windows desktop management app showing the admin UI in a WebView2 window with a tray icon, single-instance behavior, and update and handover actions.",["desktop-app","gui","webview","entry-point"],"complex"],
"src/bot/userdata_paths.py":["Defines APP_HOME and userdata folder layout constants, plus legacy-data migration into userdata/.",["paths","configuration","migration","utility"],"complex"],
};
const S={
"src/bot/config.py:ConfigError":["class","Exception for missing or invalid configuration with a message ready to show to users.",["error","configuration"],"simple"],
"src/bot/config.py:Settings":["class","Dataclass holding all bot settings with from_env loading and a check for required secrets before a command runs.",["settings","dataclass","configuration"],"complex"],
"src/bot/storage/process_lock.py:AlreadyRunning":["class","Exception raised when the instance lock is already held.",["error","lock"],"simple"],
"src/bot/storage/process_lock.py:InstanceLock":["class","File lock that acquires exclusive ownership of a data directory, optionally retrying for a wait period.",["lock","process-management"],"moderate"],
"src/bot/system/auto_update.py:update":["function","Performs the git pull update, reinstalls pip dependencies if changed, and returns an UpdateResult.",["auto-update","git"],"moderate"],
"src/bot/system/auto_update.py:pending_commits":["function","Counts new GitHub commits not yet present locally after a git fetch.",["git","update-check"],"simple"],
"src/bot/system/bot_process.py:start":["function","Starts the bot process (systemd service on VPS, hidden spawn otherwise) and returns a Result.",["process-management","service"],"moderate"],
"src/bot/system/bot_process.py:stop":["function","Stops the bot process, killing the supervisor first so it does not respawn.",["process-management","service"],"moderate"],
"src/bot/system/bot_process.py:status_info":["function","Returns bot status as data for the gateway status command and Overview page.",["status","monitoring"],"moderate"],
"src/bot/system/first_run_setup.py:ensure_home":["function","Creates missing userdata folders and template files without overwriting, returning the created files.",["setup","filesystem"],"simple"],
"src/bot/system/first_run_setup.py:ensure_admin_token":["function","Generates a random admin token and saves it to .env when none exists so the UI never runs unprotected.",["security","setup"],"simple"],
"src/bot/system/handover.py:export_bundle":["function","Writes the data zip bundle to a destination and returns its manifest.",["handover","zip"],"simple"],
"src/bot/system/handover.py:validate_bundle":["function","Checks each zip entry name and size before anything is written.",["validation","security","zip"],"moderate"],
"src/bot/system/handover.py:import_bundle":["function","Replaces local data with a bundle, refusing if the bot is running and keeping a backup.",["handover","restore","zip"],"moderate"],
"src/bot/system/handover_job.py:start":["function","Starts a background transfer to vps or local, raising JobError if busy or target invalid.",["handover","job"],"moderate"],
"src/bot/system/handover_job.py:precheck":["function","Returns non-blocking warnings or raises JobError if the transfer cannot proceed.",["validation","handover"],"moderate"],
"src/bot/system/remote_config.py:RemoteConfig":["class","Holds the latest web-supplied configuration, applies overrides via a callback, and writes web-set SYSTEM.md and MEMORY.md with backups.",["remote-config","state"],"complex"],
"src/bot/system/remote_config.py:RemoteSync":["class","Sends a per-minute heartbeat and fetches new config; network errors are logged only.",["heartbeat","sync"],"moderate"],
"src/bot/system/remote_server.py:call_sync":["function","Calls the VPS and returns JSON, raising RemoteError with a Vietnamese message on failure.",["http-client","remote"],"moderate"],
"src/bot/system/remote_server.py:stream":["function","Streams bytes such as live logs from the VPS, raising before the first byte if unreachable.",["streaming","http-client"],"moderate"],
"src/bot/system/server_info.py:collect":["function","Aggregates uptime, memory, code version, systemd state and last update run into a dict for the Server page.",["monitoring","aggregation"],"moderate"],
"src/bot/ui/admin/admin_sessions.py:AdminSessions":["class","In-memory store of random Gmail-login session tokens with 12-hour expiry.",["session","authentication"],"moderate"],
"src/bot/ui/admin/admin_sessions.py:AdminDevices":["class","Registry of device keys that let remote apps control this admin page after Gmail login.",["authentication","devices"],"moderate"],
"src/bot/ui/admin/admin_web_server.py:AdminContext":["class","Request context that rereads the .env on each request so Settings changes apply immediately.",["context","settings"],"simple"],
"src/bot/ui/admin/admin_web_server.py:create_app":["function","Builds the FastAPI app with auth, host and origin middleware and all /api routes for settings, bot control, VPS connection, handover, history and logs.",["fastapi","routes","factory","security"],"complex"],
"src/bot/ui/admin/settings_file.py:update":["function","Writes validated changes into .env keeping comments, backing up to .env.bak with an atomic write.",["env-file","atomic-write"],"moderate"],
"src/bot/ui/admin/settings_file.py:validate":["function","Cleans and validates changes using the Settings.from_env rules of the bot.",["validation","settings"],"simple"],
"src/bot/ui/desktop/desktop_app.py:Desktop":["class","Desktop app controller: runs or reuses the admin server, shows a WebView2 window and tray, and offers handover, update and folder-open actions.",["desktop-app","gui","controller"],"complex"],
"src/bot/ui/desktop/desktop_app.py:run_gui":["function","Entry point that launches the desktop management app.",["entry-point","gui"],"simple"],
"src/bot/userdata_paths.py:app_home":["function","Resolves APP_HOME, the directory holding userdata and code, for frozen and source runs.",["paths","configuration"],"simple"],
"src/bot/userdata_paths.py:migrate_legacy":["function","Moves legacy .env, data, logs, workspace and tools into userdata and returns what moved.",["migration","filesystem"],"moderate"],
};
const nodes=[],edges=[];
for(const f of b.files){const p=f.path;const [s,t,c]=F[p];nodes.push({id:"file:"+p,type:"file",name:p.split("/").pop(),filePath:p,summary:s,tags:t,complexity:c});
 for(const i of b.batchImportData[p]||[])edges.push({source:"file:"+p,target:"file:"+i,type:"imports",direction:"forward",weight:0.7});}
for(const k in S){const i=k.lastIndexOf(":");const p=k.slice(0,i),n=k.slice(i+1);const [ty,s,t,c]=S[k];const lr=L[p][n];if(!lr)throw k;
 nodes.push({id:`${ty}:${p}:${n}`,type:ty,name:n,filePath:p,lineRange:lr,summary:s,tags:t,complexity:c});
 edges.push({source:"file:"+p,target:`${ty}:${p}:${n}`,type:"contains",direction:"forward",weight:1.0});
 if(!n.startsWith("_"))edges.push({source:"file:"+p,target:`${ty}:${p}:${n}`,type:"exports",direction:"forward",weight:0.8});}
const add=(a,b2)=>edges.push({source:a,target:b2,type:"calls",direction:"forward",weight:0.8});
add("function:src/bot/system/handover_job.py:start","function:src/bot/system/remote_server.py:call_sync");
add("function:src/bot/system/handover_job.py:precheck","function:src/bot/system/handover.py:validate_bundle");
add("function:src/bot/system/handover.py:import_bundle","function:src/bot/system/handover.py:validate_bundle");
add("function:src/bot/ui/admin/settings_file.py:update","function:src/bot/ui/admin/settings_file.py:validate");
const ids=new Set(nodes.map(n=>n.id));const bad=edges.filter(e=>!ids.has(e.source)||(!ids.has(e.target)&&!e.target.startsWith("file:")));
const imp=Object.values(b.batchImportData).reduce((a,x)=>a+x.length,0);
console.log("nodes",nodes.length,"edges",edges.length,"imports",edges.filter(e=>e.type=="imports").length,imp,"bad",bad.length,JSON.stringify(bad));
fs.writeFileSync("../intermediate/batch-1.json",JSON.stringify({nodes,edges},null,1));
