import json
N=[];E=[]
def node(id,type,name,fp,summary,tags,cx,lr=None,ln=None):
    d={"id":id,"type":type,"name":name,"filePath":fp,"summary":summary,"tags":tags,"complexity":cx}
    if lr:d["lineRange"]=lr
    if ln:d["languageNotes"]=ln
    N.append(d)
def edge(s,t,ty,w):E.append({"source":s,"target":t,"type":ty,"direction":"forward","weight":w})
def fn(path,name,lr,summary,tags,cx="simple"):
    node("function:%s:%s"%(path,name),"function",name,path,summary,tags,cx,lr)
    edge("file:"+path,"function:%s:%s"%(path,name),"contains",1.0)
    if path.endswith("check_secrets.py"):
        edge("file:"+path,"function:%s:%s"%(path,name),"exports",0.8)
node("config:.gitattributes","config",".gitattributes",".gitattributes","Git attributes forcing CRLF line endings for Windows .cmd batch files.",["configuration","git","line-endings"],"simple")
node("file:scripts/packaging/ZaloBot.spec","file","ZaloBot.spec","scripts/packaging/ZaloBot.spec","PyInstaller spec that builds a windowed single-file ZaloBot.exe from zalobot_entry.py, bundling package data and hidden imports (uvicorn, google.genai, zlapi) while excluding userdata.",["build-system","packaging","pyinstaller","deployment"],"moderate","Python-syntax PyInstaller spec; uses collect_data_files/collect_submodules for dynamic imports.")
node("file:scripts/packaging/check_secrets.py","file","check_secrets.py","scripts/packaging/check_secrets.py","Post-build audit script that scans the PyInstaller exe and build dir for forbidden files and secret values read from settings.env; exits 1 on any finding.",["security","packaging","script","validation"],"moderate")
fn("scripts/packaging/check_secrets.py","secrets_from_env",[21,28],"Reads the secret keys (bot token, Gemini key, admin token, webhook secret) from an env file and returns their UTF-8 and UTF-16-LE byte forms for searching.",["secrets","env-parsing","utility"])
fn("scripts/packaging/check_secrets.py","check_exe",[31,47],"Walks the PyInstaller archive TOC flagging bundled env/userdata files, then searches each entry and the raw exe bytes for secret values.",["security","scanning","packaging"],"moderate")
fn("scripts/packaging/check_secrets.py","check_dir",[50,57],"Recursively scans files under a build directory (under 200MB) for secret byte values and reports offending paths.",["security","scanning","filesystem"])
fn("scripts/packaging/check_secrets.py","main",[60,75],"CLI entry that resolves exe/build paths and settings.env, runs both checks, prints problems and returns exit code 0 or 1.",["entry-point","cli","security"])
node("document:scripts/packaging/version_info.txt","document","version_info.txt","scripts/packaging/version_info.txt","PyInstaller VSVersionInfo resource describing the Windows exe file and product version (0.2.0.0).",["packaging","windows","version-metadata"],"simple")
node("file:scripts/packaging/zalobot_entry.py","file","zalobot_entry.py","scripts/packaging/zalobot_entry.py","Tiny PyInstaller entry point that calls bot.command_line.main and exits with its code; no args opens the management app.",["entry-point","packaging","cli"],"simple")
node("file:src/bot/__init__.py","file","__init__.py","src/bot/__init__.py","Package root declaring the bot package docstring and __version__ = 0.1.0.",["entry-point","package","version"],"simple")
node("file:src/bot/core/__init__.py","file","__init__.py","src/bot/core/__init__.py","Package marker whose docstring describes the core layer: message handling, commands, filters, tags, rate limiting, formatting and time.",["package","core","barrel"],"simple")
node("document:src/bot/templates/MEMORY.md","document","MEMORY.md","src/bot/templates/MEMORY.md","Template for the long-term memory file loaded into the prompt as reference data, containing only an explanatory comment; gitignored as it may hold personal info.",["template","memory","documentation","prompt"],"simple")
node("document:src/bot/templates/SYSTEM.md","document","SYSTEM.md","src/bot/templates/SYSTEM.md","Default Vietnamese system prompt defining the assistant role, plain-text reply style for Zalo, and safety limits including prompt-injection resistance.",["prompt","template","documentation","assistant"],"simple")
node("config:src/bot/templates/env.example","config","env.example","src/bot/templates/env.example","Template for userdata/config/settings.env listing required tokens, Gemini model, owner ID and allowed chats; copied by the app on first run and never committed.",["configuration","env","template","secrets"],"moderate")
node("file:src/bot/templates/tool_example.py.tmpl","file","tool_example.py.tmpl","src/bot/templates/tool_example.py.tmpl","Example custom tool template defining a current_time Tool for Vietnam time; copied into tools/ without leading underscore to be auto-registered.",["template","tool","example","agent"],"simple")
node("file:src/bot/ui/__init__.py","file","__init__.py","src/bot/ui/__init__.py","Package marker documenting the UI layer: admin web (127.0.0.1) and desktop window/tray.",["package","ui","barrel"],"simple")
P="src/bot/ui/admin/static/admin_page.js"
node("file:"+P,"file","admin_page.js",P,"Single-page admin dashboard script: token/Gmail login, local vs VPS targeting via proxy, hash routing, and renderers for overview, servers, groups, history, workspace, playground, logs, failed messages, settings and tools, using textContent for untrusted data.",["frontend","admin-ui","javascript","spa","api-client"],"complex","Vanilla JS; builds DOM via helper h() and textContent to avoid XSS.")
for name,lr,s,t in [
 ("api",[99,112],"Fetch wrapper adding the bearer token, rewriting paths for the VPS target, parsing JSON, and throwing ApiError (and showing login on 401).",["api-client","fetch","auth"]),
 ("render",[168,181],"Runs page cleanup callbacks, resolves the current page from the hash, updates nav state and title, and invokes the page renderer with error reporting.",["routing","rendering","spa"]),
 ("controlBot",[242,256],"Disables control buttons, POSTs a bot start/stop/restart action to the API, toasts the result and refreshes status.",["bot-control","event-handler","api-client"]),
 ("boot",[1136,1165],"Initializes login form, nav, target switch and listeners, picks up a token from the URL hash (then scrubs it), and starts the app if authenticated.",["initialization","auth","entry-point"]),
]:
    fn(P,name,lr,s,t,"moderate")
node("class:"+P+":ApiError","class","ApiError",P,"Error subclass marking failures from admin API calls so reportError can distinguish them.",["error","api-client"],"simple",[92,92])
edge("file:"+P,"class:"+P+":ApiError","contains",1.0)
node("file:src/bot/ui/admin/static/theme.js","file","theme.js","src/bot/ui/admin/static/theme.js","IIFE toggling light/dark theme: defaults to dark, persists choice in localStorage, updates theme-color meta and toggle buttons.",["frontend","theming","javascript","ui"],"simple")
node("document:src/bot/ui/admin/static/fonts/OFL.txt","document","OFL.txt","src/bot/ui/admin/static/fonts/OFL.txt","SIL Open Font License 1.1 notice for the bundled Cinzel, Cormorant Garamond and Be Vietnam Pro fonts.",["license","fonts","documentation"],"simple")
T={
"tests/test_admin.py":("Pytest suite for the admin web API: auth, host/origin checks, security headers, secret handling, settings, groups, history, logs, playground, bot control, QR login, updates and Gmail login sessions.","complex",["test","admin","api","security"],["src/bot/ui/admin/admin_web_server.py","src/bot/ui/admin/admin_sessions.py","src/bot/ui/admin/settings_file.py","src/bot/system/bot_process.py"]),
"tests/test_agent.py":("Tests GeminiAgent with fake models: history conversion, retry on transient errors, function-calling loop, tool round limit, tool registry rules and prompt building.","moderate",["test","agent","gemini","prompt"],["src/bot/agent/gemini_agent.py"]),
"tests/test_assign_events.py":("Tests the assign_events tool: resolving people from tags/names, assign/update/cancel/list events, role-based limits and web-key requirement.","moderate",["test","tool","calendar","roles"],["src/bot/agent/tools/assign_events.py"]),
"tests/test_config_client_webhook.py":("Tests Settings validation, ZaloClient URL building and token hiding, log redaction filter and webhook secret checking.","moderate",["test","config","webhook","redaction"],["src/bot/system/log_files.py","src/bot/zalo/receive_webhook.py","src/bot/config.py"]),
"tests/test_gmail_connect.py":("Tests device-key storage/expiry, VPS issuing device keys for admin Gmail, and local connect-to-VPS flow with a fake web service.","moderate",["test","gmail","auth","remote"],["src/bot/system/remote_server.py","src/bot/ui/admin/admin_web_server.py","src/bot/ui/admin/admin_sessions.py","src/bot/ui/admin/settings_file.py"]),
"tests/test_handover.py":("Tests exporting/importing a data bundle between local and VPS, safety checks, rollback, prechecks and the related endpoints.","complex",["test","handover","migration","zip"],["src/bot/system/handover.py","src/bot/system/handover_job.py","src/bot/system/remote_server.py","src/bot/system/bot_process.py","src/bot/ui/admin/admin_web_server.py"]),
"tests/test_paths.py":("Tests migration of legacy home layout into userdata/, settings reading from migrated env, lock handling and restoring defaults.","moderate",["test","paths","migration","userdata"],["src/bot/userdata_paths.py"]),
"tests/test_polling.py":("Tests that polling delivers updates and survives errors.","simple",["test","polling","zalo"],["src/bot/zalo/receive_polling.py"]),
"tests/test_qrlogin.py":("Tests the Zalo QR login flow with a fake session: full flow, declined/expired, cancel, cookie selection and applying a session.","moderate",["test","qr-login","zalo","fake"],["src/bot/zalo/qr_login.py"]),
"tests/test_remote_proxy.py":("Tests the admin server VPS proxy: token substitution, login requirement, blocked paths, 401/network error handling and https enforcement.","moderate",["test","proxy","remote","security"],["src/bot/system/remote_server.py","src/bot/ui/admin/admin_web_server.py"]),
}
for p,(s,cx,tg,prods) in T.items():
    node("file:"+p,"file",p.split("/")[-1],p,s,tg,cx)
    for q in prods: edge("file:"+q,"file:"+p,"tested_by",0.5)
for c,f,s,lr,tg in [("FakeResponse","tests/test_qrlogin.py","Minimal fake HTTP response with status code, text and optional JSON payload.",[16,25],["test","fake"]),
 ("FakeZalo","tests/test_qrlogin.py","requests.Session subclass simulating id.zalo.me endpoints in call order for the QR flow, recording calls.",[28,67],["test","fake","zalo"]),
 ("FakeModels","tests/test_agent.py","Scripted stand-in for the Gemini models API used by agent tests.",[25,32],["test","fake","gemini"]),
 ("FakeWeb","tests/test_gmail_connect.py","Fake web service routing requests to the VPS app in Gmail connect tests.",[44,54],["test","fake","web"])]:
    node("class:%s:%s"%(f,c),"class",c,f,s,tg,"simple",lr); edge("file:"+f,"class:%s:%s"%(f,c),"contains",1.0)
edge("file:scripts/packaging/ZaloBot.spec","file:scripts/packaging/zalobot_entry.py","deploys",0.7)
edge("file:scripts/packaging/ZaloBot.spec","document:scripts/packaging/version_info.txt","depends_on",0.6)
edge("file:scripts/packaging/ZaloBot.spec","file:src/bot/ui/desktop/icon_images.py","depends_on",0.6)
edge("file:scripts/packaging/zalobot_entry.py","file:src/bot/command_line.py","imports",0.7)
edge("file:scripts/packaging/check_secrets.py","file:scripts/packaging/ZaloBot.spec","related",0.5)
edge("file:"+P,"file:src/bot/ui/admin/static/index.html","related",0.5)
edge("file:"+P,"file:src/bot/ui/admin/admin_web_server.py","related",0.5)
edge("file:src/bot/ui/admin/static/theme.js","file:src/bot/ui/admin/static/index.html","related",0.5)
edge("config:src/bot/templates/env.example","file:src/bot/config.py","configures",0.6)
edge("document:src/bot/templates/SYSTEM.md","file:src/bot/agent/gemini_agent.py","documents",0.5)
edge("document:src/bot/templates/MEMORY.md","file:src/bot/agent/gemini_agent.py","documents",0.5)
edge("file:src/bot/templates/tool_example.py.tmpl","file:src/bot/agent/tools/__init__.py","related",0.5)
ids={n["id"] for n in N}
print(len(N),len(E))
ext=set()
for e in E:
    for k in ("source","target"):
        if e[k] not in ids: ext.add(e[k])
print(sorted(ext))
json.dump({"nodes":N,"edges":E},open("D:/pylosSever/.ua/intermediate/batch-12.json","w"),ensure_ascii=False,indent=1)
