const fs=require("fs");
const inp=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-analyzer-input-1.json","utf8"));
const ext=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-extract-results-1.json","utf8"));
const F={
"src/bot/config.py":["Central typed Settings dataclass loaded from environment/.env with validation helpers and secret checks for the bot.","complex",["configuration","settings","environment","validation"]],
"src/bot/storage/process_lock.py":["Cross-process single-instance file lock with retrying acquire and context-manager support.","simple",["utility","locking","process","concurrency"]],
"src/bot/system/__init__.py":["Package marker for the system management subpackage.","simple",["package","barrel","system"]],
"src/bot/system/auto_update.py":["Git-based self-update: checks pending commits on the remote, pulls and reinstalls dependencies, returning an UpdateResult.","moderate",["auto-update","git","system","deployment"]],
"src/bot/system/bot_process.py":["Cross-platform bot lifecycle control: PID files, locks, spawn/stop/restart, systemd and Windows task integration, standby flag and status reporting.","complex",["process-management","lifecycle","systemd","service"]],
"src/bot/system/first_run_setup.py":["First-run bootstrap that creates the userdata home with template files and guarantees an admin access token in .env.","simple",["setup","bootstrap","security","configuration"]],
"src/bot/system/handover.py":["Exports and imports a zip bundle of bot data to move the bot between machines, with strict path/size validation and backup pruning.","complex",["handover","backup","zip","data-migration"]],
"src/bot/system/handover_job.py":["Orchestrates a step-tracked handover job moving the bot between local machine and VPS, with prechecks and rollback on failure.","complex",["handover","job-orchestration","rollback","vps"]],
"src/bot/system/remote_config.py":["Syncs web-managed configuration to the running bot: whitelisted override parsing, cached config, heartbeat sync and last-error log handler.","complex",["remote-config","sync","heartbeat","configuration"]],
"src/bot/system/remote_server.py":["HTTP client layer (async and sync, via httpx) for calling the remote VPS server, with streaming, file upload/download and Vietnamese error messages.","complex",["http-client","remote","vps","api-client"]],
"src/bot/system/server_info.py":["Collects server status data (uptime, memory, git version versus remote head, systemd state, last update run) for the admin Server page.","moderate",["monitoring","server-info","git","system"]],
"src/bot/ui/admin/__init__.py":["Package marker for the admin web UI subpackage.","simple",["package","barrel","admin"]],
"src/bot/ui/admin/admin_sessions.py":["In-memory TTL admin session tokens plus persistent hashed device tokens that can be listed and revoked.","moderate",["authentication","sessions","security","admin"]],
"src/bot/ui/admin/admin_web_server.py":["FastAPI factory building the admin web app: auth, bot control, handover, groups, history, workspace files, settings, logs, failed replies, Zalo login, update and playground endpoints.","complex",["fastapi","admin","api-handler","web-server","entry-point"]],
"src/bot/ui/admin/settings_file.py":["Reads, validates and writes the .env settings file with field specs, comment-preserving updates and .env.bak backups.","moderate",["settings","env-file","validation","admin"]],
"src/bot/ui/desktop/desktop_app.py":["Desktop GUI application (window plus tray) that hosts the admin web server, controls the bot, checks updates and manages VPS handover.","complex",["desktop","gui","tray","entry-point"]],
"src/bot/userdata_paths.py":["Resolves the app home and userdata paths (frozen exe versus source) and migrates legacy data layout into userdata/.","moderate",["paths","migration","filesystem","configuration"]],
};
const FN={
"src/bot/config.py:ConfigError":["Exception for missing or invalid configuration carrying a user-ready message.",["exception","configuration","error-handling"]],
"src/bot/config.py:Settings":["Settings dataclass built by from_env, exposing personal-mode check, secret requirement validation and the list of secrets to redact.",["settings","dataclass","configuration"]],
"src/bot/config.py:_int":["Parses an integer environment variable with default and minimum bound.",["parsing","utility","environment"]],
"src/bot/config.py:_bool":["Parses a boolean environment variable with a default.",["parsing","utility","environment"]],
"src/bot/config.py:_csv":["Splits a comma-separated string into a tuple of trimmed values.",["parsing","utility","environment"]],
"src/bot/storage/process_lock.py:AlreadyRunning":["Exception raised when another instance holds the lock.",["exception","locking","process"]],
"src/bot/storage/process_lock.py:InstanceLock":["File-based instance lock with acquire (optional retry wait), release and context-manager protocol.",["locking","process","concurrency"]],
"src/bot/system/auto_update.py:update":["Runs the git pull and pip install update flow and returns an UpdateResult.",["auto-update","git","deployment"]],
"src/bot/system/auto_update.py:pending_commits":["Fetches the remote and counts commits not yet present locally.",["git","auto-update","version"]],
"src/bot/system/auto_update.py:unavailable_reason":["Returns a user-facing reason updating is impossible, or None when allowed.",["auto-update","validation","git"]],
"src/bot/system/bot_process.py:start":["Starts the bot via systemd or a spawned process, honoring standby and lock checks.",["lifecycle","process-management","systemd"]],
"src/bot/system/bot_process.py:stop":["Stops the bot gracefully via stop flag, systemd or kill and waits for exit.",["lifecycle","process-management","systemd"]],
"src/bot/system/bot_process.py:restart":["Stops then starts the bot.",["lifecycle","process-management","service"]],
"src/bot/system/bot_process.py:status_info":["Builds a data dict describing bot state for the status command and overview page.",["status","monitoring","process-management"]],
"src/bot/system/bot_process.py:systemctl":["Runs a systemctl action for a unit and wraps the outcome in a Result.",["systemd","process-management","subprocess"]],
"src/bot/system/bot_process.py:is_running":["Checks whether a process currently holds the service lock.",["process-management","locking","status"]],
"src/bot/system/bot_process.py:run_hidden":["Runs a system command without opening a console window.",["subprocess","utility","windows"]],
"src/bot/system/bot_process.py:Service":["Descriptor of a managed service (bot or GUI) with its names and lock/pid settings.",["dataclass","service","process-management"]],
"src/bot/system/bot_process.py:Result":["Outcome object for process actions with an ok property and message.",["dataclass","result","process-management"]],
"src/bot/system/first_run_setup.py:ensure_home":["Creates missing userdata directories and template files and returns the created list.",["setup","filesystem","bootstrap"]],
"src/bot/system/first_run_setup.py:ensure_admin_token":["Generates and persists a random admin token to .env when absent.",["security","setup","configuration"]],
"src/bot/system/handover.py:export_bundle":["Writes a zip of bot data sources plus manifest to the destination.",["export","zip","handover"]],
"src/bot/system/handover.py:import_bundle":["Validates and restores a bundle over local data after backing up, refusing while the bot runs.",["import","zip","backup"]],
"src/bot/system/handover.py:validate_bundle":["Checks every archive name and size before anything is written.",["validation","security","zip"]],
"src/bot/system/handover.py:HandoverError":["Exception with user-ready message for handover failures.",["exception","handover","error-handling"]],
"src/bot/system/handover_job.py:Job":["Dataclass tracking handover job state and steps, with a public serializable view.",["dataclass","job","handover"]],
"src/bot/system/handover_job.py:start":["Starts a handover job to vps or local, optionally in a thread, rejecting concurrent jobs.",["job-orchestration","threading","handover"]],
"src/bot/system/handover_job.py:precheck":["Compares local and remote status, returning warnings or raising JobError when a move is impossible.",["validation","handover","vps"]],
"src/bot/system/handover_job.py:_to_vps":["Step sequence moving the bot from this machine to the VPS: stop, export, upload, import, start, verify.",["handover","vps","job-orchestration"]],
"src/bot/system/handover_job.py:_to_local":["Step sequence moving the bot from the VPS to this machine.",["handover","local","job-orchestration"]],
"src/bot/system/handover_job.py:_rollback_local":["On failure, restarts the bot locally to avoid downtime.",["rollback","handover","recovery"]],
"src/bot/system/handover_job.py:JobError":["Exception with user-facing explanation for handover job errors.",["exception","handover","error-handling"]],
"src/bot/system/remote_config.py:overrides":["Converts web config values into whitelisted Settings overrides and lists ignored keys.",["config","validation","remote-config"]],
"src/bot/system/remote_config.py:RemoteConfig":["Holds the latest web config, applies it to the running bot, persists cache and managed files.",["remote-config","state","configuration"]],
"src/bot/system/remote_config.py:RemoteSync":["Async loop sending a per-minute heartbeat and fetching new config; network errors are only logged.",["heartbeat","sync","async"]],
"src/bot/system/remote_config.py:LastError":["Logging handler retaining the latest error to report through the heartbeat.",["logging","handler","monitoring"]],
"src/bot/system/remote_config.py:read_cached":["Loads the last fetched web config from the cache file, or empty dict.",["cache","config","remote-config"]],
"src/bot/system/remote_server.py:request":["Async HTTP request to the VPS with auth and error mapping to RemoteError.",["http-client","async","vps"]],
"src/bot/system/remote_server.py:json_request":["Async request returning parsed JSON, converting HTTP errors to RemoteError.",["http-client","json","async"]],
"src/bot/system/remote_server.py:stream":["Async generator streaming bytes such as live logs from the VPS.",["streaming","http-client","async"]],
"src/bot/system/remote_server.py:call_sync":["Synchronous JSON call to the VPS raising RemoteError with Vietnamese messages.",["http-client","sync","vps"]],
"src/bot/system/remote_server.py:download_sync":["Downloads a handover bundle from the VPS to a destination file.",["download","handover","http-client"]],
"src/bot/system/remote_server.py:upload_sync":["Uploads a handover bundle to the VPS and returns the JSON response.",["upload","handover","http-client"]],
"src/bot/system/remote_server.py:status_sync":["Returns configured/ok/running/standby/error summary for the tray menu.",["status","tray","http-client"]],
"src/bot/system/remote_server.py:RemoteError":["Exception carrying a user-ready message for remote call failures.",["exception","remote","error-handling"]],
"src/bot/system/remote_server.py:Reply":["Simple dataclass wrapping an HTTP reply from the VPS.",["dataclass","http","remote"]],
"src/bot/system/server_info.py:collect":["Aggregates uptime, memory, code version, systemd state and last update into one dict.",["monitoring","aggregation","server-info"]],
"src/bot/system/server_info.py:code_version":["Reports the running commit and the latest remote commit via git ls-remote.",["git","version","monitoring"]],
"src/bot/system/server_info.py:_memory":["Reads total and available memory in bytes.",["system","memory","monitoring"]],
"src/bot/ui/admin/admin_sessions.py:AdminSessions":["Issues and validates short-lived in-memory session tokens with a TTL.",["authentication","sessions","security"]],
"src/bot/ui/admin/admin_sessions.py:AdminDevices":["Persists hashed device tokens for remote apps, with issue, validate, list and revoke.",["authentication","devices","persistence"]],
"src/bot/ui/admin/admin_web_server.py:create_app":["Builds the FastAPI app with middleware and all admin API routes (auth, bot control, handover, groups, settings, logs, Zalo login, update, playground).",["fastapi","routing","api-handler"]],
"src/bot/ui/admin/admin_web_server.py:AdminContext":["Holds shared state for the admin app, including a settings accessor.",["context","state","admin"]],
"src/bot/ui/admin/settings_file.py:FieldSpec":["Dataclass describing one editable .env field.",["dataclass","schema","settings"]],
"src/bot/ui/admin/settings_file.py:validate":["Cleans and validates changes using Settings.from_env rules.",["validation","settings","env-file"]],
"src/bot/ui/admin/settings_file.py:update":["Writes validated changes to .env preserving comments and backing up to .env.bak.",["env-file","persistence","settings"]],
"src/bot/ui/admin/settings_file.py:read_values":["Parses the .env file into a key-value dict.",["env-file","parsing","settings"]],
"src/bot/ui/desktop/desktop_app.py:Desktop":["Main desktop app controller: window, tray, embedded admin server, bot start/stop, update checks and VPS handover actions.",["gui","controller","tray"]],
"src/bot/ui/desktop/desktop_app.py:run_gui":["Entry point launching the desktop GUI, with options for tray-only, auto-start bot and after-update.",["entry-point","gui","desktop"]],
"src/bot/ui/desktop/desktop_app.py:update_flag_file":["Returns the path of data/update.txt used to show the update button.",["path","update","gui"]],
"src/bot/userdata_paths.py:app_home":["Resolves the writable application home directory for frozen or source runs.",["paths","filesystem","configuration"]],
"src/bot/userdata_paths.py:migrate_legacy":["Moves legacy .env, data, logs, workspace and tools into userdata, restoring git defaults.",["migration","filesystem","legacy"]],
"src/bot/userdata_paths.py:is_frozen":["True when running from the PyInstaller-packaged exe.",["environment","pyinstaller","paths"]],
"src/bot/userdata_paths.py:needs_migration":["Detects legacy layout data needing migration into userdata.",["migration","detection","paths"]],
"src/bot/userdata_paths.py:done_file":["Maps a failed-replies filename to its _done counterpart.",["naming","utility","paths"]],
};
const nodes=[],edges=[];
for(const r of ext.results){
 const m=F[r.path];
 nodes.push({id:"file:"+r.path,type:"file",name:r.path.split("/").pop(),filePath:r.path,summary:m[0],tags:m[2],complexity:m[1]});
 for(const imp of inp.batchImportData[r.path]||[])edges.push({source:"file:"+r.path,target:"file:"+imp,type:"imports",direction:"forward",weight:0.7});
 const items=[...(r.functions||[]).map(x=>["function",x]),...(r.classes||[]).map(x=>["class",x])];
 for(const [k,x] of items){const key=r.path+":"+x.name;const d=FN[key];if(!d)continue;
  const id=k+":"+key;const len=x.endLine-x.startLine;
  nodes.push({id,type:k,name:x.name,filePath:r.path,lineRange:[x.startLine,x.endLine],summary:d[0],tags:d[1],complexity:len>100?"complex":len>25?"moderate":"simple"});
  edges.push({source:"file:"+r.path,target:id,type:"contains",direction:"forward",weight:1.0});
  if((r.exports||[]).some(e=>e.name===x.name))edges.push({source:"file:"+r.path,target:id,type:"exports",direction:"forward",weight:0.8});
 }}
const cnt=Object.values(inp.batchImportData).reduce((a,b)=>a+b.length,0);
console.log("imports",edges.filter(e=>e.type=="imports").length,cnt,"nodes",nodes.length,"edges",edges.length);
const files=ext.results.map(r=>r.path).sort();
const parts=Math.ceil(Math.max(nodes.length/60,edges.length/120));
const ids=new Set(nodes.map(n=>n.id));
const imps=new Set(Object.values(inp.batchImportData).flat().map(p=>"file:"+p));
console.log("bad edges",edges.filter(e=>!(ids.has(e.target)||imps.has(e.target))).length);
fs.mkdirSync(".ua/intermediate",{recursive:true});
if(parts<=1){fs.writeFileSync(".ua/intermediate/batch-1.json",JSON.stringify({nodes,edges},null,1));console.log("single");}
else{const sz=Math.ceil(files.length/parts);for(let k=0;k<parts;k++){const s=new Set(files.slice(k*sz,(k+1)*sz));const pn=nodes.filter(n=>s.has(n.filePath));const pi=new Set(pn.map(n=>n.id));const pe=edges.filter(e=>pi.has(e.source));fs.writeFileSync(`.ua/intermediate/batch-1-part-${k+1}.json`,JSON.stringify({nodes:pn,edges:pe},null,1));console.log("part",k+1,pn.length,pe.length);}}
