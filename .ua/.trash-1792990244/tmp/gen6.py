import json
P="src/bot/ui/desktop/"
def fn(f,n,s,e,summ,tags,c="simple"):
    return {"id":f"function:{P}{f}:{n}","type":"function","name":n,"filePath":P+f,"lineRange":[s,e],"summary":summ,"tags":tags,"complexity":c}
nodes=[
{"id":f"file:{P}__init__.py","type":"file","name":"__init__.py","filePath":P+"__init__.py","summary":"Package marker for the Windows desktop app (WebView2 window plus system tray icon); contains only a docstring.","tags":["entry-point","package","desktop","windows"],"complexity":"simple"},
{"id":f"file:{P}icon_images.py","type":"file","name":"icon_images.py","filePath":P+"icon_images.py","summary":"Draws the app icon with Pillow (blue rounded square with a Z and an optional status dot), so no image assets are needed in the repo.","tags":["utility","icon","pillow","desktop"],"complexity":"simple"},
{"id":f"file:{P}tray_icon.py","type":"file","name":"tray_icon.py","filePath":P+"tray_icon.py","summary":"System tray integration using pystray; builds a dynamic menu delegating to the Desktop controller and updates icon/title as the bot state changes.","tags":["tray","pystray","ui","desktop","event-handler"],"complexity":"moderate"},
{"id":f"file:{P}windows_autostart.py","type":"file","name":"windows_autostart.py","filePath":P+"windows_autostart.py","summary":"Manages start-with-Windows via an HKCU Run registry entry, including command construction for frozen or source runs and migration of stale entries.","tags":["windows","registry","autostart","configuration"],"complexity":"moderate","languageNotes":"winreg is imported lazily inside functions and guarded by os.name checks so the module is importable on non-Windows."},
fn("icon_images.py","make_icon",17,31,"Renders a supersampled (4x) RGBA rounded-square icon with a white Z, optionally adding a colored state dot at the bottom right, then downsizes with LANCZOS.",["icon","pillow","rendering"]),
fn("icon_images.py","write_ico",34,38,"Writes a multi-size .ico file (16 to 256 px) to the given path, creating parent directories; used at build time for the executable.",["icon","build","file-io"]),
{"id":f"class:{P}tray_icon.py:Tray","type":"class","name":"Tray","filePath":P+"tray_icon.py","lineRange":[26,92],"summary":"Wraps a pystray Icon whose menu items (toggle/restart bot, update, VPS move, autostart, quit) call into the Desktop controller; supports run, stop, notify, refresh and autostart toggling.",
 "tags":["tray","ui","controller","pystray"],"complexity":"moderate"},
fn("windows_autostart.py","command",18,24,"Builds the command line stored in the Run key: the frozen executable or pythonw.exe -m bot, with 'gui --tray --start-bot'.",["autostart","command-line"]),
fn("windows_autostart.py","is_enabled",27,37,"Returns True when the Run key value exists and equals the current command; always False off Windows.",["registry","autostart","query"]),
fn("windows_autostart.py","set_enabled",40,52,"Creates or deletes the HKCU Run value for autostart; raises OSError on non-Windows.",["registry","autostart","mutation"]),
fn("windows_autostart.py","migrate",55,71,"If autostart is already enabled but points to a different command, rewrites it to the current one; never enables it on its own.",["registry","autostart","migration"]),
]
E=[]
def e(s,t,ty,w): E.append({"source":s,"target":t,"type":ty,"direction":"forward","weight":w})
f=lambda n:f"file:{P}{n}"
for t in ["config.py"]: pass
for n in ["src/bot/config.py",P+"__init__.py",P+"icon_images.py",P+"windows_autostart.py"]: e(f("tray_icon.py"),"file:"+n,"imports",0.7)
e(f("windows_autostart.py"),"file:src/bot/config.py","imports",0.7)
for n in nodes[4:]:
    e("file:"+n["filePath"],n["id"],"contains",1.0)
    e("file:"+n["filePath"],n["id"],"exports",0.8) if n["name"] in("make_icon","write_ico","Tray","command","is_enabled","set_enabled","migrate") else None
e(f"class:{P}tray_icon.py:Tray",f"function:{P}icon_images.py:make_icon","calls",0.8)
e(f"class:{P}tray_icon.py:Tray",f"function:{P}windows_autostart.py:is_enabled","calls",0.8)
e(f"class:{P}tray_icon.py:Tray",f"function:{P}windows_autostart.py:set_enabled","calls",0.8)
e(f"function:{P}windows_autostart.py:is_enabled",f"function:{P}windows_autostart.py:command","calls",0.8)
e(f"function:{P}windows_autostart.py:migrate",f"function:{P}windows_autostart.py:set_enabled","calls",0.8)
ids={n["id"] for n in nodes}
for x in E: assert x["source"] in ids or x["source"].startswith("file:src/bot/config"),x; 
json.dump({"nodes":nodes,"edges":E},open(".ua/intermediate/batch-6.json","w"),indent=1)
bad=[x for x in E if x["target"] not in ids and x["target"]!="file:src/bot/config.py"]
print(len(nodes),len(E),bad)
