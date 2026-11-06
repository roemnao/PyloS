const fs=require("fs");
const e=JSON.parse(fs.readFileSync(".ua/tmp/e2.json","utf8"));
const r=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-extract-results-2.json","utf8"));
const F={
"src/bot/agent/tools/assign_events.py":["Calendar event assignment tools for the agent: resolves people by name, creates/updates/cancels/lists events via the server client, and remembers recent chat participants.",["agent-tool","calendar","events","people-resolution"],"complex"],
"src/bot/agent/tools/read_chat_memory.py":["Agent tool that reads stored chat history/memory for a conversation, filtered by message filter and Vietnam time.",["agent-tool","memory","chat-history"],"simple"],
"src/bot/core/message_filter.py":["Decides whether an incoming Zalo message should be handled (mention, chatter detection, group rules) using settings and storage state.",["filter","message-routing","core","decision"],"moderate"],
"src/bot/core/message_handler.py":["Central Bot class that receives Zalo messages, applies filtering, rate limiting and roles, dispatches owner commands, runs the AI agent and sends formatted replies.",["message-handler","orchestration","core","entry-point"],"complex"],
"src/bot/core/owner_commands.py":["Parses and executes owner/admin chat commands (modes, event assignment, help text) with role checks.",["commands","admin","core","parsing"],"complex"],
"src/bot/core/rate_limiter.py":["Small RateLimiter class throttling per-key message frequency.",["rate-limiting","utility","core"],"simple"],
"src/bot/core/reply_formatting.py":["Reply formatting helpers: UTF-16 length counting, splitting long messages to platform limits, and converting markdown to plain text.",["formatting","utility","text-processing"],"simple"],
"src/bot/core/roles.py":["Role-based permission helpers mapping users to roles and checking whether a role allows an action.",["roles","permissions","core"],"simple"],
"src/bot/core/text_fold.py":["Tiny helper that folds text (case and diacritics) for accent-insensitive matching.",["utility","text-processing","normalization"],"simple"],
"src/bot/storage/__init__.py":["Package barrel re-exporting the data stores and text file helpers.",["barrel","storage","entry-point"],"simple"],
"src/bot/storage/data_stores.py":["Collection of persistent stores (groups, seen messages, history, memory, state, usage, stats, activity, failures) backed by JSON files.",["storage","persistence","data-model","json"],"complex"],
"src/bot/storage/text_files.py":["Atomic text writing plus JSON-lines and JSON-object file wrappers used by the stores.",["storage","file-io","utility","json"],"moderate"],
"src/bot/zalo/receive_webhook.py":["FastAPI app factory exposing the webhook endpoint that receives Zalo events and records them in storage.",["webhook","fastapi","api-handler","zalo"],"simple"]};
const S={
"src/bot/agent/tools/assign_events.py":{match_member:"Fuzzy-matches a name to a team member.",resolve_people:"Resolves mentioned names to people records.",_assign:"Creates an event assignment.",_update:"Updates an existing event.",_cancel:"Cancels an event.",_list:"Lists upcoming events.",_mine:"Lists events for the caller.",_tools:"Builds the list of event tool definitions for the registry.",_summary:"Builds a summary string for an event.",_remember:"Remembers recent chat participants.",_event_id:"Derives an event id."},
"src/bot/agent/tools/read_chat_memory.py":{_read:"Reads chat memory entries for the tool call."},
"src/bot/core/message_filter.py":{Decision:"Result of a message filtering decision.",MessageFilter:"Applies filtering rules to incoming messages.",is_chatter:"Detects casual chatter messages."},
"src/bot/core/message_handler.py":{ZaloSender:"Protocol for sending Zalo messages.",Job:"Queued message job record.",Bot:"Main bot orchestrator handling messages end to end.",strip_name_prefix:"Strips bot name prefix from message text."},
"src/bot/core/owner_commands.py":{help_text:"Returns command help text.",ParsedCommand:"Parsed command structure.",parse_command:"Parses a chat message into a command.",describe_mode:"Describes a bot mode.",CommandHandler:"Executes owner commands.",_pick_people:"Selects people matching a query."},
"src/bot/core/rate_limiter.py":{RateLimiter:"Limits request frequency per key."},
"src/bot/core/reply_formatting.py":{utf16_len:"UTF-16 length of text.",split_message:"Splits text into chunks within the limit.",to_plain_text:"Converts markdown to plain text."},
"src/bot/core/roles.py":{role_of:"Returns the role of a user.",required_role:"Returns the role required for an action.",allows:"Checks role permits action."},
"src/bot/core/text_fold.py":{fold:"Folds text for comparison."},
"src/bot/storage/data_stores.py":{GroupState:"Per-group state record.",GroupStore:"Stores group configuration and state.",SeenStore:"Tracks seen message ids.",HistoryStore:"Stores chat history.",MemoryDataStore:"Stores agent memory.",StateStore:"Stores general bot state.",UsageStore:"Tracks usage counters.",StatsStore:"Stores statistics.",ActivityStore:"Stores activity logs.",FailedStore:"Stores failed message records.",safe_name:"Sanitizes names for file paths."},
"src/bot/storage/text_files.py":{atomic_write_text:"Writes text atomically via temp file and rename.",JsonLinesFile:"Append/read wrapper for JSON-lines files.",JsonObjectFile:"Read/write wrapper for a JSON object file."},
"src/bot/zalo/receive_webhook.py":{create_app:"Creates the FastAPI webhook app."}};
const nodes=[],edges=[];
for(const x of r.results){
 const p=x.path,f=F[p];
 nodes.push({id:"file:"+p,type:"file",name:p.split("/").pop(),filePath:p,summary:f[0],tags:f[1].length>=3?f[1]:[...f[1],"python"],complexity:f[2]});
 for(const t of e.batchImportData[p]||[])edges.push({source:"file:"+p,target:"file:"+t,type:"imports",direction:"forward",weight:0.7});
 const seen=new Set();
 const add=(k,o,m)=>{if(!S[p]||!S[p][o.name]||seen.has(o.name))return;seen.add(o.name);
  const id=k+":"+p+":"+o.name;
  nodes.push({id,type:k,name:o.name,filePath:p,lineRange:[o.startLine,o.endLine],summary:S[p][o.name],tags:[k==="class"?"class":"function",p.split("/")[2],"python"],complexity:(o.endLine-o.startLine)>60?"complex":(o.endLine-o.startLine)>15?"moderate":"simple"});
  edges.push({source:"file:"+p,target:id,type:"contains",direction:"forward",weight:1.0});
  if(!o.name.startsWith("_"))edges.push({source:"file:"+p,target:id,type:"exports",direction:"forward",weight:0.8});};
 (x.classes||[]).forEach(c=>add("class",c));(x.functions||[]).forEach(c=>add("function",c));
}
const out={nodes,edges};
fs.writeFileSync(".ua/intermediate/batch-2.json",JSON.stringify(out,null,1));
console.log(nodes.length,edges.length);
