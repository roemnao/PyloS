const fs=require("fs");
const r=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-extract-results-1.json","utf8")).results;
const imp=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-analyzer-input-1.json","utf8")).batchImportData;
const F={
"src/bot/config.py":["Loads bot settings from environment variables into a frozen Settings dataclass with typed parsing helpers and validation.",["configuration","settings","environment","dataclass"],"complex"],
"src/bot/storage/process_lock.py":["Cross-process single-instance lock (InstanceLock) preventing two bot processes from running at once.",["lock","process","concurrency","storage"],"moderate"],
"src/bot/system/__init__.py":["Package marker for the system subpackage.",["package","barrel","system"],"simple"],
"src/bot/system/auto_update.py":["Git-based self-update helpers: checks for pending commits, runs git pull and pip install, and reports results.",["auto-update","git","system","utility"],"moderate"],
"src/bot/system/bot_process.py":["Manages the bot process lifecycle: PID files, spawn/stop/restart, systemd and Windows task integration, standby state, status and log tailing.",["process-management","lifecycle","systemd","service"],"complex"],
"src/bot/system/first_run_setup.py":["First-run helpers that create the app home directory and ensure an admin token exists.",["setup","bootstrap","admin","initialization"],"simple"],
"src/bot/system/handover.py":["Exports and imports data bundles (zip with manifest) used to hand the bot over between local machine and VPS, with validation and backups.",["handover","backup","migration","archive"],"moderate"],
"src/bot/system/handover_job.py":["Orchestrates a stepwise handover job between local and VPS with prechecks, progress tracking and rollback.",["handover","job","orchestration","rollback"],"complex"],
"src/bot/system/remote_config.py":["Syncs configuration from the remote server, caches it, applies overrides to Settings, and reports heartbeat and last errors.",["remote-config","sync","settings","heartbeat"],"complex"],
"src/bot/system/remote_server.py":["Async and sync HTTP client for the remote server API, with request, JSON, streaming, download and upload helpers.",["http-client","remote-server","api-client","networking"],"complex"],
"src/bot/system/server_info.py":["Collects server diagnostics such as uptime, memory, git version, latest remote commit and systemd state.",["diagnostics","monitoring","system","server-info"],"moderate"],
"src/bot/ui/admin/__init__.py":["Package marker for the admin UI subpackage.",["package","barrel","admin"],"simple"],
"src/bot/ui/admin/admin_sessions.py":["In-memory admin login sessions and persistent hashed device tokens for the admin web UI.",["authentication","sessions","admin","security"],"moderate"],
"src/bot/ui/admin/admin_web_server.py":["Builds the FastAPI admin web application exposing settings, bot control, handover, remote sync and status endpoints.",["web-server","fastapi","admin","api-handler"],"complex"],
"src/bot/ui/admin/settings_file.py":["Reads, validates and updates the settings env file through declarative FieldSpec definitions.",["settings","validation","env-file","admin"],"moderate"],
"src/bot/ui/desktop/desktop_app.py":["Desktop GUI application that runs the admin server, tray and bot controls, update checks and VPS handover actions.",["desktop","gui","entry-point","tray"],"complex"],
"src/bot/userdata_paths.py":["Resolves user data directories for frozen and source runs and migrates legacy data to the new app home.",["paths","migration","userdata","utility"],"complex"],
};
const C={
"src/bot/config.py":{ConfigError:"Exception raised for invalid or missing configuration.",Settings:"Frozen dataclass holding all bot settings, built from env via from_env with personal/secrets/require helpers."},
"src/bot/storage/process_lock.py":{AlreadyRunning:"Raised when another bot instance holds the lock.",InstanceLock:"File-based lock with acquire/release and context-manager support."},
"src/bot/system/auto_update.py":{UpdateError:"Error raised when an update step fails.",UpdateResult:"Result record describing an update outcome."},
"src/bot/system/bot_process.py":{Service:"Enumeration of bot service kinds that can be managed.",Result:"Operation result with an ok flag and message."},
"src/bot/system/handover.py":{HandoverError:"Error raised for handover bundle problems."},
"src/bot/system/handover_job.py":{JobError:"Error raised when a handover job step fails.",Job:"Tracks handover job state and steps and exposes a public view."},
"src/bot/system/remote_config.py":{RemoteConfig:"Holds remote-provided settings, applies updates and persists cache files.",LastError:"Recorder that captures the last error for reporting.",RemoteSync:"Background sync that fetches config, sends heartbeats and runs the loop."},
"src/bot/system/remote_server.py":{RemoteError:"Error raised for remote server request failures.",Reply:"Simple response container for remote calls."},
"src/bot/ui/admin/admin_sessions.py":{AdminSessions:"Issues and validates short-lived admin session tokens.",AdminDevices:"Persists hashed trusted-device tokens with issue, validate, list and revoke."},
"src/bot/ui/admin/admin_web_server.py":{AdminContext:"Shared context object giving admin routes access to current settings."},
"src/bot/ui/admin/settings_file.py":{FieldSpec:"Declarative description of an editable settings field."},
"src/bot/ui/desktop/desktop_app.py":{Desktop:"Main desktop application class coordinating window, tray, admin server, bot actions and updates."},
};
const Fn={
"src/bot/config.py":{_int:"Parses an integer env value with bounds and defaults.",_bool:"Parses a boolean env value."},
"src/bot/system/auto_update.py":{update:"Performs git pull and dependency install, returning an UpdateResult.",unavailable_reason:"Explains why auto update is unavailable.",pending_commits:"Lists commits waiting to be pulled."},
"src/bot/system/bot_process.py":{start:"Starts the bot via systemd, task or spawned process.",stop:"Stops the bot process and related services.",restart:"Stops then starts the bot.",status_info:"Gathers the current bot status details.",format_status:"Formats status info as readable text.",follow_log:"Streams the bot log to the console.",_spawn:"Spawns the bot subprocess detached.",systemctl:"Runs systemctl commands for the service.",is_running:"Checks whether the bot process is alive."},
"src/bot/system/first_run_setup.py":{ensure_home:"Creates the app home directory and initial files.",ensure_admin_token:"Ensures an admin token is generated and stored."},
"src/bot/system/handover.py":{export_bundle:"Creates a zip bundle of data with manifest.",import_bundle:"Validates and restores a bundle, backing up existing data.",validate_bundle:"Checks bundle manifest and contents safety.",read_manifest:"Reads manifest from a bundle."},
"src/bot/system/handover_job.py":{start:"Starts a handover job in the background.",precheck:"Checks preconditions before handover.",_to_vps:"Moves bot and data from local to VPS.",_to_local:"Moves bot and data from VPS back to local.",current:"Returns the current job."},
"src/bot/system/remote_config.py":{overrides:"Builds settings overrides from remote config.",read_cached:"Reads cached remote config from disk."},
"src/bot/system/remote_server.py":{request:"Async HTTP request to the remote server.",json_request:"Async request returning parsed JSON.",stream:"Streams a remote response.",call_sync:"Synchronous JSON call.",status_sync:"Synchronous status query.",download_sync:"Downloads a file synchronously.",upload_sync:"Uploads a file synchronously.",configured:"Whether a remote server is configured."},
"src/bot/system/server_info.py":{collect:"Aggregates server diagnostics into a dict.",_memory:"Reads memory usage.",code_version:"Returns the current code version."},
"src/bot/ui/admin/admin_web_server.py":{create_app:"Builds the FastAPI admin app with all routes, auth and dependencies."},
"src/bot/ui/admin/settings_file.py":{read_values:"Reads current values from the settings file.",validate:"Validates submitted setting values.",update:"Writes updated values back to the settings file."},
"src/bot/ui/desktop/desktop_app.py":{run_gui:"Entry that launches the desktop GUI.",update_flag_file:"Returns the path of the update flag file."},
"src/bot/userdata_paths.py":{app_home:"Resolves the writable app home directory.",migrate_legacy:"Moves legacy user data into the new home.",is_frozen:"Detects packaged execution.",needs_migration:"Checks whether migration is needed."},
};
const nodes=[],edges=[];
const cx=(a,b)=>b-a>60?"complex":b-a>20?"moderate":"simple";
for(const f of r){const p=f.path;const m=F[p];
nodes.push({id:"file:"+p,type:"file",name:p.split("/").pop(),filePath:p,summary:m[0],tags:m[1],complexity:m[2]});
for(const t of imp[p]||[])edges.push({source:"file:"+p,target:"file:"+t,type:"imports",direction:"forward",weight:0.7});
for(const c of f.classes||[]){const s=(C[p]||{})[c.name];if(!s)continue;
nodes.push({id:`class:${p}:${c.name}`,type:"class",name:c.name,filePath:p,lineRange:[c.startLine,c.endLine],summary:s,tags:["class",m[1][0],m[1][1]],complexity:cx(c.startLine,c.endLine)});
edges.push({source:"file:"+p,target:`class:${p}:${c.name}`,type:"contains",direction:"forward",weight:1.0});
edges.push({source:"file:"+p,target:`class:${p}:${c.name}`,type:"exports",direction:"forward",weight:0.8});}
for(const fn of f.functions||[]){const s=(Fn[p]||{})[fn.name];if(!s)continue;
nodes.push({id:`function:${p}:${fn.name}`,type:"function",name:fn.name,filePath:p,lineRange:[fn.startLine,fn.endLine],summary:s,tags:["function",m[1][0],m[1][1]],complexity:cx(fn.startLine,fn.endLine)});
edges.push({source:"file:"+p,target:`function:${p}:${fn.name}`,type:"contains",direction:"forward",weight:1.0});
edges.push({source:"file:"+p,target:`function:${p}:${fn.name}`,type:"exports",direction:"forward",weight:0.8});}}
const add=(a,b)=>edges.push({source:a,target:b,type:"calls",direction:"forward",weight:0.8});
add("file:src/bot/ui/desktop/desktop_app.py","file:src/bot/system/bot_process.py");
add("file:src/bot/system/handover_job.py","file:src/bot/system/handover.py");
const isum=Object.values(imp).reduce((a,b)=>a+b.length,0);
console.log(nodes.length,edges.length,isum,edges.filter(e=>e.type=="imports").length);
fs.mkdirSync(".ua/intermediate",{recursive:true});
const files=[...new Set(nodes.map(n=>n.filePath))].sort();
const parts=Math.ceil(Math.max(nodes.length/60,edges.length/120));
if(parts<=1)fs.writeFileSync(".ua/intermediate/batch-1.json",JSON.stringify({nodes,edges}));
else{const sz=Math.ceil(files.length/parts);
for(let k=0;k<parts;k++){const fs_=new Set(files.slice(k*sz,(k+1)*sz));const ns=nodes.filter(n=>fs_.has(n.filePath));const ids=new Set(ns.map(n=>n.id));
fs.writeFileSync(`.ua/intermediate/batch-1-part-${k+1}.json`,JSON.stringify({nodes:ns,edges:edges.filter(e=>ids.has(e.source))}));}
console.log("parts",parts)}
