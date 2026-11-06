const fs=require("fs");
const b=JSON.parse(fs.readFileSync(".ua/intermediate/batches.json","utf8")).batches.find(x=>x.batchIndex===3);
const nodes=[],edges=[];
const F=(p,summary,tags,cx,ln)=>nodes.push({id:"file:"+p,type:"file",name:p.split("/").pop(),filePath:p,summary,tags,complexity:cx,...(ln?{languageNotes:ln}:{})});
const N=(kind,p,name,range,summary,tags,cx)=>{nodes.push({id:kind+":"+p+":"+name,type:kind,name,filePath:p,lineRange:range,summary,tags,complexity:cx});
 edges.push({source:"file:"+p,target:kind+":"+p+":"+name,type:"contains",direction:"forward",weight:1});};
const E=(s,t,type,w)=>edges.push({source:s,target:t,type,direction:"forward",weight:w});
const B="src/bot/";
F(B+"__main__.py","Module entry point for python -m bot that delegates to command_line.main and exits with its return code.",["entry-point","cli","bootstrap"],"simple");
F(B+"agent/__init__.py","Package barrel re-exporting the agent classes, PromptBuilder and the tool registry API.",["barrel","entry-point","agent"],"simple");
F(B+"agent/gemini_agent.py","Gemini-backed agent running a bounded function-calling loop with retries on transient errors, plus a JSON classify helper and an EchoAgent fallback when no API key exists.",["agent","llm","gemini","function-calling","service"],"complex","Uses dataclasses, a typing.Protocol for the Agent interface and asyncio timeouts with lazy google-genai imports.");
F(B+"agent/system_prompt.py","Builds the per-conversation system prompt from hot-reloaded SYSTEM.md and MEMORY.md plus context such as time, group members, sender role and available tools.",["prompt","agent","caching","configuration"],"moderate");
F(B+"agent/tools/__init__.py","Defines ToolContext, Tool and ToolRegistry and discovers tool modules (built-in and user-supplied) that expose a TOOLS list, with owner-only enforcement and error capture.",["registry","plugin-system","agent","tools","discovery"],"moderate");
F(B+"agent/tools/_example.py","Template tool (not loaded because of the leading underscore) showing how to declare a current_time tool via TOOLS.",["example","tool","template"],"simple");
F(B+"command_line.py","Argparse CLI for the bot: run, console, webhook management, gateway/admin control, health check, QR Zalo login and update commands, plus the async bot runtime wiring.",["cli","entry-point","orchestration","asyncio","bootstrap"],"complex");
F(B+"core/vietnam_time.py","Time helpers using a fixed UTC+7 timezone: epoch milliseconds, current Vietnam datetime and ISO date.",["utility","time","timezone"],"simple");
F(B+"system/log_files.py","Configures root logging to console and a rotating file, with a filter that redacts secrets from messages and tracebacks.",["logging","security","utility","configuration"],"simple");
F(B+"zalo/qr_login.py","Synchronous QR-code login flow for a personal Zalo account, polling id.zalo.me endpoints, collecting cookies and generating an IMEI to persist a session.",["authentication","zalo","qr-login","http","session"],"complex","Blocking requests-based flow with a threading.Event for cancellation; meant to run in a worker thread.");
let p=B+"agent/gemini_agent.py";
N("class",p,"Turn",[22,25],"Immutable conversation turn with role, text and optional speaker name.",["data-model","dataclass","agent"],"simple");
N("class",p,"ToolStep",[29,34],"Record of one tool invocation (name, args, result, duration) kept for session review.",["data-model","dataclass","tool-call"],"simple");
N("class",p,"AgentReply",[38,43],"Result of an agent call: reply text, token count, tool steps, model and elapsed ms.",["data-model","dataclass","agent"],"simple");
N("class",p,"Agent",[46,47],"Protocol defining the async reply interface agents implement.",["interface","protocol","agent"],"simple");
N("function",p,"_usage_tokens",[50,52],"Extracts total token count from a Gemini response's usage metadata, defaulting to 0.",["helper","tokens","gemini"],"simple");
N("function",p,"_rejects_thinking",[55,57],"Detects a 400 error caused by a model not supporting the thinking parameter.",["helper","error-handling","gemini"],"simple");
N("function",p,"_is_transient",[60,67],"Classifies httpx transport errors and 5xx server errors as retryable.",["helper","retry","error-handling"],"simple");
N("class",p,"GeminiAgent",[70,215],"Calls Gemini with manual function-calling loop limited by max rounds, retries transient errors, supports live reconfiguration and a low-thinking JSON classify method with timeout retry and thinking fallback.",["agent","llm","gemini","function-calling","retry"],"complex");
N("class",p,"EchoAgent",[218,226],"Fake agent for console mode without an API key: echoes the last message and disables AI filtering.",["agent","fallback","testing-aid"],"simple");
E("class:"+p+":GeminiAgent","class:"+B+"agent/tools/__init__.py:ToolRegistry","calls",0.8);
p=B+"agent/system_prompt.py";
N("class",p,"_CachedFile",[23,39],"Reads a text file, strips HTML comments and reloads only when its mtime changes.",["cache","file-io","hot-reload"],"simple");
N("class",p,"PromptBuilder",[42,89],"Assembles the system prompt: base SYSTEM.md, Vietnam-time context, group mention rules, role-based scheduling rules and MEMORY.md treated as data.",["prompt","builder","agent"],"moderate");
E("class:"+p+":PromptBuilder","function:"+B+"core/vietnam_time.py:now_vn","calls",0.8);
p=B+"agent/tools/__init__.py";
N("class",p,"ToolContext",[24,39],"Frozen context passed to tool handlers describing chat, user, role, mentions, members and teams.",["data-model","dataclass","context"],"simple");
N("class",p,"Tool",[46,53],"Frozen tool definition with name, description, handler, JSON-schema parameters and owner_only flag.",["data-model","dataclass","tool"],"simple");
N("class",p,"ToolRegistry",[56,93],"Registers tools, exposes Gemini declarations and dispatches calls, enforcing owner-only access and returning errors as dicts.",["registry","dispatch","security","agent"],"moderate");
N("function",p,"_load_external",[96,110],"Loads user-written tool modules from a directory, skipping underscore files and isolating failures.",["plugin-loader","dynamic-import","resilience"],"moderate");
N("function",p,"discover",[113,131],"Builds a registry from built-in tool modules via pkgutil and external user tools directory.",["discovery","plugin-system","registry"],"moderate");
E("function:"+p+":discover","function:"+p+":_load_external","calls",0.8);
p=B+"agent/tools/_example.py";
N("function",p,"_current_time",[11,12],"Example handler returning current Vietnam time and timezone.",["example","tool","time"],"simple");
E("function:"+p+":_current_time","function:"+B+"core/vietnam_time.py:now_vn","calls",0.8);
p=B+"command_line.py";
const cl=[["_build_agent",50,62,"Creates tool registry and a GeminiAgent from settings, or an EchoAgent when allowed and no key is set."],
["_run",65,170,"Main async runtime: picks personal or official Zalo client, logs in, builds Bot, handles signals and runs receive loops."],
["_start_server_sync",173,191,"Starts background tasks for syncing settings and heartbeat with the schedule web server when an API key is set."],
["_bot_status",194,209,"Builds the non-sensitive status payload sent with heartbeats."],
["_console",223,256,"Interactive terminal chat that feeds lines to Bot using ConsoleZalo."],
["_zalo_call",259,264,"Runs a single Zalo API method for CLI commands such as me or webhook management."],
["_health",267,278,"Checks last poll timestamp against a maximum age for monitoring."],
["_zalo_login",281,332,"Runs QR login from the CLI, saving the QR image, printing status and applying the session."],
["_update",335,350,"Pulls new code from GitHub and restarts the bot."],
["_admin",353,407,"Controls the admin web UI process: run, start, stop, restart, status."],
["_prepare_home",410,427,"Migrates legacy data into userdata once and creates missing sample folders/files."],
["_utf8_console",430,437,"Forces UTF-8 console output streams."],
["_attach_parent_console",440,451,"Attaches the windowed exe to the parent cmd console to print command output."],
["main",454,615,"Parses CLI arguments with argparse subcommands and dispatches to the matching handler."]];
for(const [n,a,z,s] of cl)N("function",p,n,[a,z],s,["cli",n==="main"?"entry-point":"command"],z-a>40?"complex":z-a>12?"moderate":"simple");
N("class",p,"ConsoleZalo",[212,220],"Fake Zalo client that prints bot replies and chat actions to the terminal.",["adapter","console","testing-aid"],"simple");
E("function:"+p+":_build_agent","function:"+B+"agent/tools/__init__.py:discover","calls",0.8);
E("function:"+p+":_build_agent","class:"+B+"agent/gemini_agent.py:GeminiAgent","calls",0.8);
E("function:"+p+":_build_agent","class:"+B+"agent/gemini_agent.py:EchoAgent","calls",0.8);
E("function:"+p+":_run","class:"+B+"core/message_handler.py:Bot","calls",0.8);
E("function:"+p+":_run","class:"+B+"agent/system_prompt.py:PromptBuilder","calls",0.8);
E("function:"+p+":_zalo_login","class:"+B+"zalo/qr_login.py:QrLogin","calls",0.8);
E("function:"+p+":_zalo_login","function:"+B+"zalo/qr_login.py:apply_session","calls",0.8);
E("function:"+p+":_health","function:"+B+"core/vietnam_time.py:now_ms","calls",0.8);
E("function:"+p+":_build_agent","class:"+B+"config.py:Settings","calls",0.8);
p=B+"core/vietnam_time.py";
N("function",p,"now_ms",[11,12],"Returns the current epoch time in milliseconds.",["time","utility"],"simple");
N("function",p,"now_vn",[15,16],"Returns the current timezone-aware datetime in UTC+7.",["time","utility","timezone"],"simple");
N("function",p,"today_vn",[19,20],"Returns today's Vietnam date as an ISO string.",["time","utility","date"],"simple");
E("function:"+p+":today_vn","function:"+p+":now_vn","calls",0.8);
p=B+"system/log_files.py";
N("class",p,"RedactFilter",[11,32],"Logging filter replacing configured secrets with *** in messages and exception text.",["logging","security","redaction"],"moderate");
N("function",p,"setup_logging",[35,58],"Resets root logger with console and rotating file handlers, adds redaction and quiets noisy libraries.",["logging","configuration","setup"],"moderate");
E("function:"+p+":setup_logging","class:"+p+":RedactFilter","calls",0.8);
p=B+"zalo/qr_login.py";
N("class",p,"QrLoginError",[54,55],"Base exception for QR login failures.",["exception","error-handling","zalo"],"simple");
N("class",p,"Cancelled",[58,59],"Exception raised when the login is cancelled by the user.",["exception","cancellation","zalo"],"simple");
N("class",p,"ZaloSession",[63,79],"Dataclass holding cookies, IMEI and user info, with save() writing a chmod-600 JSON file atomically.",["data-model","session","persistence","security"],"simple");
N("class",p,"QrStatus",[83,88],"Dataclass describing the current QR login state, QR image, name and message for UIs.",["data-model","status","dataclass"],"simple");
N("function",p,"make_imei",[91,92],"Generates an IMEI as uuid4 plus md5 of the user agent, mimicking Zalo Web.",["helper","identity","zalo"],"simple");
N("function",p,"cookies_for",[95,110],"Flattens a cookie jar to a name-value dict for a host, preferring more specific domains.",["cookies","http","helper"],"moderate");
N("class",p,"QrLogin",[113,257],"Drives the QR login: fetches the QR code, long-polls scan and confirm, validates the session and returns a ZaloSession, with cancel support and status callbacks.",["authentication","qr-login","state-machine","http","zalo"],"complex");
N("function",p,"save_qr_png",[260,262],"Decodes a base64 QR image and writes it to a PNG file.",["file-io","qr-login","helper"],"simple");
N("function",p,"apply_session",[265,271],"Saves the session and switches RECEIVE_MODE to personal in the .env file.",["session","configuration","zalo"],"simple");
E("class:"+p+":QrLogin","class:"+p+":ZaloSession","calls",0.8);
E("class:"+p+":QrLogin","function:"+p+":make_imei","calls",0.8);
E("class:"+p+":QrLogin","function:"+p+":cookies_for","calls",0.8);
E("class:"+p+":Cancelled","class:"+p+":QrLoginError","inherits",0.9);
let cnt=0;for(const [f,ts] of Object.entries(b.batchImportData))for(const t of ts){E("file:"+f,"file:"+t,"imports",0.7);cnt++}
const ex=(p,names,kind)=>names.forEach(n=>E("file:"+p,kind+":"+p+":"+n,"exports",0.8));
ex(B+"agent/gemini_agent.py",["Turn","ToolStep","AgentReply","Agent","GeminiAgent","EchoAgent"],"class");
ex(B+"agent/tools/__init__.py",["ToolContext","Tool","ToolRegistry"],"class");
ex(B+"zalo/qr_login.py",["QrLoginError","Cancelled","ZaloSession","QrStatus","QrLogin"],"class");
// validation
const ids=new Set(nodes.map(n=>n.id));
const known=new Set();
for(const [f,ts] of Object.entries(b.batchImportData)){known.add("file:"+f);ts.forEach(t=>known.add("file:"+t));}
const nm=b.neighborMap;
const bad=edges.filter(e=>{for(const x of [e.source,e.target]){if(ids.has(x)||known.has(x))continue;
 const m=x.match(/^(function|class):(.*?):(.*)$/);if(m){const ok=Object.values(nm).flat().some(n=>n.path===m[2]&&n.symbols.includes(m[3]));if(ok)continue;}return true}return false});
fs.mkdirSync(".ua/intermediate",{recursive:true});
fs.writeFileSync(".ua/intermediate/batch-3.json",JSON.stringify({nodes,edges},null,1));
console.log(nodes.length,edges.length,cnt,"bad:",JSON.stringify(bad));
