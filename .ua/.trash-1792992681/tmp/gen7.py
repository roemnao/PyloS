import json
nodes=[];edges=[]
def N(id,t,name,fp,s,tags,c,lr=None):
    d={"id":id,"type":t,"name":name,"filePath":fp,"summary":s,"tags":tags,"complexity":c}
    if lr:d["lineRange"]=lr
    nodes.append(d)
def E(s,t,ty,w):edges.append({"source":s,"target":t,"type":ty,"direction":"forward","weight":w})
SW="src/bot/agent/tools/schedule_web.py";SC="src/bot/system/server_client.py";SU="src/bot/system/session_upload.py"
N("file:"+SW,"file","schedule_web.py",SW,"Registers agent tools (add appointment, add task, view agenda, list tasks, complete task) that call the time-management web API; only enabled when an API key is configured.",["agent-tool","api-client","scheduling","integration"],"moderate")
N("file:"+SC,"file","server_client.py",SC,"Async HTTP client for the web server's agent API, reading URL and key from settings.env/environment and returning errors as dicts instead of raising.",["http-client","configuration","api-client","integration"],"moderate")
N("file:"+SU,"file","session_upload.py",SU,"Buffers filter/agent session events in memory and uploads them to the web in batches on a background loop, retaining events on failure.",["background-task","telemetry","queue","integration"],"moderate")
fn=[(SW,"_request",31,35,"Wraps the shared server request and normalizes error responses to a dict with an error key.",["helper","api-client"]),
(SW,"_create_event",44,50,"Tool handler that POSTs a new calendar event with title, start, optional end/allDay and an attribution note.",["tool-handler","scheduling"]),
(SW,"_create_task",53,59,"Tool handler that POSTs a new to-do with optional deadline and Eisenhower quadrant.",["tool-handler","scheduling"]),
(SW,"_complete_task",71,76,"Tool handler that marks a task done via PATCH after validating the id and URL-quoting it.",["tool-handler","scheduling"]),
(SW,"_tools",86,154,"Builds the list of Tool definitions with Vietnamese descriptions and JSON schemas, returning empty if no API key is set.",["tool-registry","factory","configuration"]),
(SC,"env_values",22,28,"Merges settings.env values with process environment variables, with environment taking precedence.",["configuration","utility"]),
(SC,"base_url",31,36,"Normalizes a web or API address into a URL ending with /api/agent, falling back to the default.",["utility","url"]),
(SC,"server_config",39,41,"Returns the resolved API base URL and trimmed API key from the environment.",["configuration"]),
(SC,"request",48,68,"Performs an authenticated async HTTP call with Bearer key, converting network, JSON and HTTP errors into error dicts.",["http-client","error-handling","async"])]
for p,n,a,b,s,t in fn:
    N(f"function:{p}:{n}","function",n,p,s,t,"moderate" if b-a>20 else "simple",[a,b])
    E("file:"+p,f"function:{p}:{n}","contains",1.0)
N("class:"+SU+":SessionUploader","class","SessionUploader",SU,"Bounded event queue with record(), batched flush() to the web and a periodic run() loop that retries on failure without ever raising into the bot.",["queue","background-task","class"],"moderate",[21,76])
E("file:"+SU,"class:"+SU+":SessionUploader","contains",1.0)
E("file:"+SU,"class:"+SU+":SessionUploader","exports",0.8)
for n in ["_request","_create_event","_create_task","_complete_task","_tools"]:pass
for n in ["env_values","base_url","server_config","request"]:E("file:"+SC,f"function:{SC}:{n}","exports",0.8)
E("file:"+SW,"file:src/bot/agent/tools/__init__.py","imports",0.7)
E("file:"+SW,"file:"+SC,"imports",0.7)
E("file:"+SU,"file:src/bot/system/__init__.py","imports",0.7)
E("file:"+SU,"file:"+SC,"imports",0.7)
E(f"function:{SW}:_request",f"function:{SC}:request","calls",0.8)
E(f"function:{SU}".replace("function","class")+":SessionUploader",f"function:{SC}:request","calls",0.8)
json.dump({"nodes":nodes,"edges":edges},open(".ua/intermediate/batch-7.json","w"),ensure_ascii=False,indent=1)
ids={n["id"] for n in nodes}
ok={"file:src/bot/agent/tools/__init__.py","file:src/bot/system/__init__.py"}
print([e for e in edges if e["source"] not in ids or (e["target"] not in ids and e["target"] not in ok)],len(nodes),len(edges))
