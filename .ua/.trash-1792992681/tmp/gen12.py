import json
N=[];E=[]
def node(id,t,path,summary,tags,cx,ln=None,name=None,**kw):
    d={"id":id,"type":t,"name":name or path.split('/')[-1],"filePath":path,"summary":summary,"tags":tags,"complexity":cx}
    if ln:d["lineRange"]=ln
    d.update(kw);N.append(d)
def edge(s,t,ty,w):E.append({"source":s,"target":t,"type":ty,"direction":"forward","weight":w})
F=lambda p:"file:"+p
node("config:.gitattributes","config",".gitattributes","Git attributes forcing CRLF line endings for Windows .cmd scripts.",["configuration","git","line-endings"],"simple")
node(F("scripts/packaging/ZaloBot.spec"),"file","scripts/packaging/ZaloBot.spec","PyInstaller spec building a windowed single-file ZaloBot.exe from the packaging entry script, bundling the bot package data files and hidden imports while excluding userdata.",["packaging","pyinstaller","build-system","deployment"],"moderate",languageNotes="PyInstaller spec is executable Python using SPECPATH, Analysis, PYZ and EXE globals injected by PyInstaller.")
node(F("scripts/packaging/check_secrets.py"),"file","scripts/packaging/check_secrets.py","Post-build guard that scans the built exe and build directory for forbidden files and secret values read from the settings env file, exiting non-zero on any leak.",["security","build-system","validation","script"],"moderate")
node("document:scripts/packaging/version_info.txt","document","scripts/packaging/version_info.txt","PyInstaller Windows version resource (file and product version 0.2.0.0) embedded into ZaloBot.exe.",["packaging","metadata","windows","build-system"],"simple")
node(F("scripts/packaging/zalobot_entry.py"),"file","scripts/packaging/zalobot_entry.py","PyInstaller entry point that delegates to bot.command_line.main; with no arguments it opens the management app.",["entry-point","packaging","cli"],"simple")
node(F("src/bot/__init__.py"),"file","src/bot/__init__.py","Top-level package initializer for the bot package.",["package-init","entry-point","module"],"simple")
node(F("src/bot/core/__init__.py"),"file","src/bot/core/__init__.py","Package marker for the core bot logic subpackage.",["package-init","module","core"],"simple")
node("document:src/bot/templates/MEMORY.md","document","src/bot/templates/MEMORY.md","Template for the bot's long-term memory file, copied into the user workspace on first run.",["template","documentation","memory","prompt"],"simple")
node("document:src/bot/templates/SYSTEM.md","document","src/bot/templates/SYSTEM.md","Template system prompt describing the bot's personality, copied into the user workspace on first run.",["template","documentation","prompt","persona"],"simple")
node("config:src/bot/templates/env.example","config","src/bot/templates/env.example","Example environment settings file listing Zalo, Gemini, admin and webhook options, copied as the initial settings.env on first run.",["configuration","template","environment","secrets"],"moderate")
node(F("src/bot/templates/tool_example.py.tmpl"),"file","src/bot/templates/tool_example.py.tmpl","Template for an example agent tool, copied to the user's tools folder as _example.py on first run.",["template","tool","agent","example"],"simple",languageNotes="Python template with a .tmpl suffix so it is not imported as part of the package.")
node(F("src/bot/ui/__init__.py"),"file","src/bot/ui/__init__.py","Package marker for the UI subpackage.",["package-init","module","ui"],"simple")
node(F("src/bot/ui/admin/static/admin_page.js"),"file","src/bot/ui/admin/static/admin_page.js","Single-page admin dashboard script providing login, overview, servers, groups, history, workspace, playground, logs, settings and handover views against the admin REST API, plus Gmail login and VPS connection.",["frontend","admin-ui","javascript","dashboard","api-client"],"complex",languageNotes="Plain browser JavaScript with a hash-based router and helper-built DOM; no bundler or modules.")
node("document:src/bot/ui/admin/static/fonts/OFL.txt","document","src/bot/ui/admin/static/fonts/OFL.txt","SIL Open Font License 1.1 text covering the bundled Cinzel, Cormorant Garamond and Be Vietnam Pro web fonts.",["license","documentation","fonts"],"moderate")
node(F("src/bot/ui/admin/static/theme.js"),"file","src/bot/ui/admin/static/theme.js","Light/dark theme switcher that defaults to dark, persists the choice in localStorage and wires up data-theme-toggle buttons.",["frontend","theme","javascript","ui"],"simple")
for nm,s,l in [("secrets_from_env","Reads secret keys from an env file and returns their UTF-8 and UTF-16 byte encodings for values of at least 8 characters.",[21,28]),
 ("check_exe","Walks the PyInstaller archive table of contents flagging forbidden entries and any member or raw exe bytes containing a secret.",[31,47]),
 ("check_dir","Scans every file in the build directory for secret byte sequences.",[50,57]),
 ("main","CLI entry that resolves the exe and build paths, loads secrets, runs both checks and prints a pass or fail report with exit code 0 or 1.",[60,75])]:
    node(f"function:scripts/packaging/check_secrets.py:{nm}","function","scripts/packaging/check_secrets.py",s,["validation","security","build-system"],"simple",l,name=nm)
    edge(F("scripts/packaging/check_secrets.py"),f"function:scripts/packaging/check_secrets.py:{nm}","contains",1.0)
tests={
 "test_admin.py":("Tests the admin web API: token and origin checks, security headers, settings editing, groups, history, workspace, logs, playground, bot control, Zalo QR login, updates and Gmail login sessions.","src/bot/ui/admin/admin_web_server.py","complex"),
 "test_agent.py":("Tests GeminiAgent retry, function-calling loop and round limits, the tool registry and discovery, and PromptBuilder workspace loading.","src/bot/agent/gemini_agent.py","moderate"),
 "test_assign_events.py":("Tests the assign_events tool: resolving people, assigning, updating and cancelling events, and role-based permissions.","src/bot/agent/tools/assign_events.py","moderate"),
 "test_config_client_webhook.py":("Tests settings validation, the Zalo client's URL building and token redaction, the log redact filter and the webhook secret check.","src/bot/config.py","moderate"),
 "test_gmail_connect.py":("Tests device key issuing, hashing and expiry on the VPS and local Gmail-based connection to a remote server.","src/bot/ui/admin/admin_sessions.py","moderate"),
 "test_handover.py":("Tests exporting and importing workspace bundles, rollback, prechecks and the handover endpoints between local and VPS.","src/bot/system/handover.py","complex"),
 "test_paths.py":("Tests migration of legacy home files into the userdata layout and related path behavior.","src/bot/userdata_paths.py","moderate"),
 "test_polling.py":("Tests that Zalo polling delivers updates and survives errors.","src/bot/zalo/receive_polling.py","simple"),
 "test_qrlogin.py":("Tests the Zalo QR login flow with fake responses, including decline, expiry, cancel and saving the session.","src/bot/zalo/qr_login.py","moderate"),
 "test_remote_proxy.py":("Tests the local-to-VPS proxy: token substitution, login requirement, blocked paths and error handling.","src/bot/system/remote_server.py","moderate"),
}
for f,(s,prod,cx) in tests.items():
    p="tests/"+f
    node(F(p),"file",p,s,["test","pytest","unit-test"],cx)
    edge(F(prod),F(p),"tested_by",0.5)
for a,b in [("src/bot/system/remote_server.py","test_gmail_connect.py"),("src/bot/system/remote_server.py","test_handover.py"),
 ("src/bot/ui/admin/admin_web_server.py","test_remote_proxy.py"),("src/bot/ui/admin/admin_web_server.py","test_handover.py"),("src/bot/ui/admin/admin_web_server.py","test_gmail_connect.py"),
 ("src/bot/zalo/receive_webhook.py","test_config_client_webhook.py"),("src/bot/system/log_files.py","test_config_client_webhook.py"),
 ("src/bot/system/bot_process.py","test_admin.py"),("src/bot/ui/admin/settings_file.py","test_admin.py"),("src/bot/ui/admin/settings_file.py","test_gmail_connect.py"),
 ("src/bot/storage/process_lock.py","test_paths.py"),("src/bot/storage/__init__.py","test_polling.py")]:
    edge(F(a),F("tests/"+b),"tested_by",0.5)
edge(F("scripts/packaging/ZaloBot.spec"),F("scripts/packaging/zalobot_entry.py"),"deploys",0.7)
edge(F("scripts/packaging/ZaloBot.spec"),"document:scripts/packaging/version_info.txt","depends_on",0.6)
edge(F("scripts/build-exe.ps1"),F("scripts/packaging/check_secrets.py"),"triggers",0.6)
edge(F("scripts/build-exe.ps1"),F("scripts/packaging/ZaloBot.spec"),"triggers",0.6)
for t in ["config:src/bot/templates/env.example","document:src/bot/templates/SYSTEM.md","document:src/bot/templates/MEMORY.md",F("src/bot/templates/tool_example.py.tmpl")]:
    edge(F("src/bot/system/first_run_setup.py"),t,"depends_on",0.6)
for js in ["admin_page.js","theme.js"]:
    edge(F("src/bot/ui/admin/static/index.html"),F("src/bot/ui/admin/static/"+js),"depends_on",0.6)
edge("document:src/bot/ui/admin/static/fonts/OFL.txt",F("src/bot/ui/admin/static/theme.css"),"documents",0.5)
seen=set();E2=[]
for e in E:
    k=(e["source"],e["target"],e["type"])
    if k not in seen:seen.add(k);E2.append(e)
json.dump({"nodes":N,"edges":E2},open("D:/pylosSever/.ua/intermediate/batch-12.json","w"),indent=1)
ids={n["id"] for n in N}
ext=sorted({x for e in E2 for x in (e["source"],e["target"]) if x not in ids})
print(len(N),len(E2));print(ext)
import os
for x in ext:
    if x.startswith("file:") and not os.path.exists("D:/pylosSever/"+x[5:]):print("MISSING",x)
