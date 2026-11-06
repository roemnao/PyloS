const fs=require("fs");
const nodes=[],edges=[];
const base=p=>p.split("/").pop();
function N(id,type,path,summary,tags,cx,extra={}){nodes.push({id,type,name:base(path),filePath:path,summary,tags,complexity:cx,...extra});}
function E(s,t,type,w){edges.push({source:s,target:t,type,direction:"forward",weight:w});}
const F=(p,s,t,c,ln)=>{N("file:"+p,"file",p,s,t,c,ln?{languageNotes:ln}:{});};
F(".gitattributes","Git attributes forcing CRLF line endings for .cmd batch files.",["configuration","git","line-endings"],"simple");
N("config:.ua/config.json","config",".ua/config.json","Understand-Anything plugin config setting the output language to English.",["configuration","tooling","understand-anything"],"simple");
F("scripts/packaging/ZaloBot.spec","PyInstaller spec that builds a windowed single-file ZaloBot.exe, bundling package data and hidden imports while never packaging userdata.",["build-system","packaging","pyinstaller","deployment"],"moderate","PyInstaller spec files are executed Python.");
F("scripts/packaging/check_secrets.py","Post-build check verifying the packaged exe and build dir contain no .env/userdata and none of the secret values from settings.env.",["security","build-system","validation","script"],"moderate");
N("document:scripts/packaging/version_info.txt","document","scripts/packaging/version_info.txt","Windows version resource for ZaloBot.exe (version 0.2.0, product and company metadata) consumed by PyInstaller.",["packaging","metadata","build-system"],"simple");
F("scripts/packaging/zalobot_entry.py","PyInstaller entry point that delegates to bot.command_line.main.",["entry-point","packaging","cli"],"simple");
F("src/bot/__init__.py","Package init declaring the bot description and __version__ 0.1.0.",["package-init","metadata","entry-point"],"simple");
F("src/bot/core/__init__.py","Package marker for the core module.",["package-init","core","barrel"],"simple");
N("document:src/bot/templates/MEMORY.md","document","src/bot/templates/MEMORY.md","Template for the long-term memory file of the bot, loaded into the prompt as reference data and reloaded live.",["template","memory","documentation"],"simple");
N("document:src/bot/templates/SYSTEM.md","document","src/bot/templates/SYSTEM.md","Default system prompt template: Vietnamese plain-text assistant role, answer style, and prompt-injection limits.",["template","prompt","documentation","security"],"simple");
N("config:src/bot/templates/env.example","config","src/bot/templates/env.example","Example settings.env template listing required tokens, Gemini model, owner ID, and allowed chats, copied to userdata on first run.",["configuration","template","environment","secrets"],"moderate");
F("src/bot/templates/tool_example.py.tmpl","Template showing how to define a custom Tool with a handler returning the current Vietnam time; not loaded until renamed.",["template","tool","example","plugin"],"simple");
F("src/bot/ui/__init__.py","Package marker for the UI module.",["package-init","ui","barrel"],"simple");
F("src/bot/ui/admin/static/admin_page.js","Single-page admin UI script: token login, hash-routed pages (overview, servers, groups, history, workspace, playground, logs, failed, settings, tools), local/VPS targeting, and Gmail login, rendering via textContent only.",["frontend","admin-ui","spa","api-client"],"complex","Vanilla JS with a small h() DOM helper; avoids innerHTML for XSS safety.");
N("document:src/bot/ui/admin/static/fonts/OFL.txt","document","src/bot/ui/admin/static/fonts/OFL.txt","SIL Open Font License 1.1 notice for bundled fonts (Cinzel, Cormorant Garamond, Be Vietnam Pro).",["license","documentation","fonts"],"simple");
F("src/bot/ui/admin/static/theme.js","IIFE managing light/dark theme persisted in localStorage, updating theme-color meta and toggle buttons.",["frontend","theme","ui","utility"],"simple");
const T=(p,s,tags,c)=>{F(p,s,["test","pytest",...tags],c);};
T("tests/test_admin.py","Tests the admin FastAPI app: auth, host/origin checks, secret handling, settings editing, groups, history, workspace, logs, playground, bot control, QR login, and Gmail session tokens.",["admin","api"],"complex");
T("tests/test_agent.py","Tests GeminiAgent with a fake models client: retries, empty replies, function-calling loop, tool registry, and prompt builder.",["agent","gemini"],"moderate");
T("tests/test_assign_events.py","Tests the assign_events calendar tool: person resolution, permissions by role, update/cancel, and listing.",["tools","calendar"],"moderate");
T("tests/test_config_client_webhook.py","Tests Settings validation, ZaloClient URL/errors, secret redaction logging, and the webhook secret check.",["config","webhook"],"moderate");
T("tests/test_gmail_connect.py","Tests Gmail-based VPS connection: hashed device keys, expiry, admin restriction, and revocation.",["gmail","auth"],"moderate");
T("tests/test_handover.py","Tests moving bot data between local and VPS: export/import bundles, unsafe names, rollback, and endpoints.",["handover","migration"],"complex");
T("tests/test_paths.py","Tests migration of legacy home files into userdata and restoration of defaults.",["paths","migration"],"moderate");
T("tests/test_polling.py","Tests that Zalo polling delivers updates and survives errors.",["polling","zalo"],"simple");
T("tests/test_qrlogin.py","Tests the Zalo QR login flow with fake HTTP: approval, decline, cancel, cookies, session saving.",["zalo","login"],"moderate");
function Fn(p,name,s,tags,cx,lr){const id="function:"+p+":"+name;nodes.push({id,type:"function",name,filePath:p,lineRange:lr,summary:s,tags,complexity:cx});E("file:"+p,id,"contains",1.0);}
const cs="scripts/packaging/check_secrets.py";
Fn(cs,"secrets_from_env","Reads secret keys from settings.env and returns their UTF-8 and UTF-16-LE byte forms, skipping values under 8 chars.",["security","utility"],"simple",[21,28]);
Fn(cs,"check_exe","Scans the PyInstaller archive entries and raw bytes of the exe for forbidden names and secret values.",["security","validation"],"moderate",[31,47]);
Fn(cs,"check_dir","Scans build directory files for forbidden names and secret bytes.",["security","validation"],"simple",[50,57]);
Fn(cs,"main","CLI entry running exe and directory checks and returning exit code 0 or 1.",["entry-point","cli"],"simple",[60,75]);
const js="src/bot/ui/admin/static/admin_page.js";
const J=[["h","DOM builder helper creating elements with attributes and children using textContent.",[43,62],"moderate"],
["api","Fetch wrapper adding the bearer token and target routing, throwing ApiError on failure.",[99,112],"moderate"],
["tryLogin","Validates the entered admin token against the API and starts the app.",[136,148],"simple"],
["render","Router that clears the current page and dispatches to the page renderer.",[168,181],"simple"],
["renderOverview","Draws the overview page with bot status, stats, alerts, and start/stop control.",[262,338],"complex"],
["connectVps","Handles connecting to a VPS with Gmail code or key and updates target state.",[386,425],"moderate"],
["renderGroups","Renders the group list with allow/deny and leader controls.",[573,627],"moderate"],
["renderHistory","Renders conversation history browsing and toggle.",[631,694],"moderate"],
["renderLogs","Renders grouped, filterable logs with live updates.",[807,880],"complex"],
["renderSettings","Renders the settings form with write-only secret fields and saving.",[965,1047],"complex"],
["gmailLogin","Runs Gmail code login flow and stores the returned session token.",[1085,1115],"moderate"],
["boot","Initializes the app: restores token, loads status, builds nav, and shows the first page.",[1136,1165],"moderate"]];
J.forEach(([n,s,lr,c])=>Fn(js,n,s,["frontend","ui"],c,lr));
const id="class:"+js+":ApiError";
nodes.push({id,type:"class",name:"ApiError",filePath:js,lineRange:[92,92],summary:"Error subclass carrying HTTP status for failed admin API calls.",tags:["error","api-client"],complexity:"simple"});
E("file:"+js,id,"contains",1.0);
E("file:scripts/packaging/ZaloBot.spec","file:scripts/packaging/zalobot_entry.py","deploys",0.7);
E("document:scripts/packaging/version_info.txt","file:scripts/packaging/ZaloBot.spec","related",0.5);
E("file:scripts/packaging/check_secrets.py","file:scripts/packaging/ZaloBot.spec","related",0.5);
E("config:src/bot/templates/env.example","file:src/bot/__init__.py","configures",0.6);
E("document:src/bot/templates/SYSTEM.md","file:src/bot/__init__.py","related",0.5);
E("file:src/bot/ui/admin/static/theme.js","file:src/bot/ui/admin/static/admin_page.js","related",0.5);
E("document:src/bot/ui/admin/static/fonts/OFL.txt","file:src/bot/ui/admin/static/admin_page.js","related",0.5);
E("file:src/bot/ui/admin/admin_web_server.py","file:tests/test_admin.py","tested_by",0.5);
fs.writeFileSync(".ua/intermediate/batch-12.json",JSON.stringify({nodes,edges},null,1));
console.log(nodes.length,edges.length);
