import json
S="src/bot/agent/tools/schedule_web.py";C="src/bot/system/server_client.py";U="src/bot/system/session_upload.py"
nodes=[];edges=[]
def fn(p,n,a,b,s,t,c="simple",k="function"):
    nodes.append(dict(id=f"{k}:{p}:{n}",type=k,name=n,filePath=p,lineRange=[a,b],summary=s,tags=t,complexity=c))
    edges.append(dict(source=f"file:{p}",target=f"{k}:{p}:{n}",type="contains",direction="forward",weight=1.0))
def fl(p,s,t,c,ln=None):
    nodes.append(dict(id=f"file:{p}",type="file",name=p.split("/")[-1],filePath=p,summary=s,tags=t,complexity=c))
fl(S,"Registers Vietnamese-named agent tools (add event, add task, view agenda, list tasks, complete task) that call the time-management web API. Tools are only exposed when SCHEDULE_API_KEY is configured and default to owner-only.",["agent-tool","api-client","scheduling","integration"],"moderate")
fl(C,"HTTP client for the iforgotmywayhome web agent API: reads URL and key from settings.env/environment, normalizes the base URL, and performs authenticated async requests returning error dicts instead of raising.",["http-client","configuration","api-client","integration"],"moderate")
fl(U,"Buffers session steps in a bounded in-memory queue and uploads them in batches to the web /sessions endpoint from a background loop, tolerating network failures without affecting the bot.",["background-task","queue","telemetry","resilience"],"moderate")
fn(S,"_request",31,35,"Wraps server_client.request, collapsing error responses to a plain {error} dict.",["api-client","helper","error-handling"])
fn(S,"_note",38,41,"Appends a 'created via Zalo by <user>' attribution line to the optional note.",["helper","formatting","scheduling"])
fn(S,"_create_event",44,50,"Tool handler that POSTs a new calendar event (title, start, optional end/allDay, note) to /events.",["tool-handler","scheduling","api-client"])
fn(S,"_create_task",53,59,"Tool handler that POSTs a to-do with optional deadline and Eisenhower quadrant to /tasks.",["tool-handler","scheduling","api-client"])
fn(S,"_agenda",62,63,"Tool handler that fetches the agenda for a given date (default today) via GET /agenda.",["tool-handler","scheduling","api-client"])
fn(S,"_list_tasks",66,68,"Tool handler that lists pending tasks via GET /tasks, wrapping the list under a 'tasks' key.",["tool-handler","scheduling","api-client"])
fn(S,"_complete_task",71,76,"Tool handler that marks a task done via PATCH /tasks/{id}, validating and URL-quoting the id.",["tool-handler","scheduling","validation"])
fn(S,"_owner_only",79,80,"Reads SCHEDULE_OWNER_ONLY from settings and returns whether tools are restricted to the bot owner (default true).",["configuration","helper","security"])
fn(S,"_tools",86,154,"Builds the list of five Tool definitions with descriptions and JSON-schema parameters; returns empty when no API key is configured.",["tool-registry","factory","schema-definition"],"moderate")
fn(C,"env_values",22,28,"Merges settings.env values with os.environ into one dict, for contexts that do not load settings.env into the environment.",["configuration","helper","dotenv"])
fn(C,"base_url",31,36,"Normalizes a web or API address to end with /api/agent, falling back to DEFAULT_URL.",["helper","url","normalization"])
fn(C,"server_config",39,41,"Returns the (base URL, API key) pair from the current environment configuration.",["configuration","helper","api-client"])
fn(C,"configured",44,45,"True when an API key is present.",["configuration","helper","predicate"])
fn(C,"request",48,68,"Async httpx call to the agent API with Bearer auth; returns parsed JSON or an {error,status,message} dict on missing key, network failure, non-JSON, or HTTP errors.",["http-client","async","error-handling","api-client"],"moderate")
fn(U,"SessionUploader",21,76,"Queues session events (deque capped at 1000), flushes them in batches of 100 to POST /sessions, requeues on failure preserving order, and runs a periodic background loop.",["queue","background-task","telemetry","resilience"],"moderate","class")
E=lambda s,t,ty,w:edges.append(dict(source=s,target=t,type=ty,direction="forward",weight=w))
E("file:"+S,"file:src/bot/agent/tools/__init__.py","imports",.7)
E("file:"+S,"file:"+C,"imports",.7)
E("file:"+U,"file:src/bot/system/__init__.py","imports",.7)
E("file:"+U,"file:"+C,"imports",.7)
E("function:"+S+":_request","function:"+C+":request","calls",.8)
E("function:"+S+":_tools","class:src/bot/agent/tools/__init__.py:Tool","calls",.8)
E("function:"+S+":_owner_only","function:"+C+":env_values","calls",.8)
E("function:"+S+":_tools","function:"+C+":server_config","calls",.8)
E("class:"+U+":SessionUploader","function:"+C+":request","calls",.8)
E("function:"+C+":request","function:"+C+":server_config","calls",.8)
E("function:"+C+":server_config","function:"+C+":base_url","calls",.8)
E("function:"+C+":server_config","function:"+C+":env_values","calls",.8)
for p,n in [(S,"_tools"),(C,"request"),(C,"server_config"),(C,"env_values"),(C,"base_url"),(C,"configured"),(U,"SessionUploader")]:
    k="class" if n=="SessionUploader" else "function"
    E("file:"+p,f"{k}:{p}:{n}","exports",.8)
json.dump(dict(nodes=nodes,edges=edges),open(".ua/intermediate/batch-7.json","w"),ensure_ascii=False,indent=1)
ids={n["id"] for n in nodes}
ok={"file:src/bot/agent/tools/__init__.py","file:src/bot/system/__init__.py","class:src/bot/agent/tools/__init__.py:Tool"}
bad=[e for e in edges if (e["source"] not in ids|ok) or (e["target"] not in ids|ok)]
print(len(nodes),len(edges),bad)
