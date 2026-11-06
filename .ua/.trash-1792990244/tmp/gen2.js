const fs=require("fs");
const b=JSON.parse(fs.readFileSync(".ua/intermediate/batches.json")).batches.find(x=>x.batchIndex===2);
const R=JSON.parse(fs.readFileSync(".ua/tmp/ua-file-extract-results-2.json")).results;
const nodes=[],edges=[];
const F={
"src/bot/agent/tools/assign_events.py":["Calendar-assignment agent tools (giao_lich, sua_lich, huy_lich, lich_cua_toi, lich_da_giao) that resolve recipients from mentions/names/teams, call the web calendar server, and remember assigned events locally for later edits.",["agent-tool","calendar","scheduling","api-client"],"complex"],
"src/bot/agent/tools/read_chat_memory.py":["Agent tool doc_memorydata that lets the model read recent raw messages of the current chat from memorydata, optionally keyword-filtered with accent-insensitive matching.",["agent-tool","memory","chat-history"],"simple"],
"src/bot/core/message_filter.py":["Layered filter deciding whether an incoming Zalo message is addressed to the bot, using rules (triggers, mentions, chatter) and a Gemini classifier in 'all' mode.",["filter","routing","llm-classifier","core"],"moderate"],
"src/bot/core/message_handler.py":["Central Bot orchestrator: owns stores, filter, commands and rate limiters, queues per-chat jobs, runs the agent, and sends replies with retries and failure logging.",["orchestrator","message-handler","async","core"],"complex"],
"src/bot/core/owner_commands.py":["Slash-command parsing and CommandHandler implementing role-gated bot commands (help, allow, deny, mode, status, reset, leader, team).",["commands","permissions","core"],"moderate"],
"src/bot/core/rate_limiter.py":["In-memory sliding-window per-minute rate limiter keyed by user or chat.",["rate-limiting","utility","core"],"simple"],
"src/bot/core/reply_formatting.py":["Prepares outgoing text for Zalo: UTF-16 length counting, splitting into chunks under the 2000-unit limit, and stripping markdown to plain text.",["formatting","utility","zalo"],"simple"],
"src/bot/core/roles.py":["Defines the basic/leader/owner role hierarchy and maps commands to the minimum role required.",["permissions","roles","core"],"simple"],
"src/bot/core/text_fold.py":["Normalizes text to lowercase without Vietnamese diacritics for accent-insensitive comparison.",["utility","text-normalization","vietnamese"],"simple"],
"src/bot/storage/__init__.py":["Package barrel re-exporting storage stores, mode constants and file helpers.",["barrel","storage","entry-point"],"simple"],
"src/bot/storage/data_stores.py":["File-backed persistence classes for group settings, seen IDs, chat history, memorydata, state, token usage, stats, activity and failed replies.",["storage","persistence","data-model"],"complex"],
"src/bot/storage/text_files.py":["Low-level file helpers: atomic text write, JSON-lines file and JSON object file wrappers.",["storage","file-io","utility"],"moderate"],
"src/bot/zalo/receive_webhook.py":["FastAPI app factory exposing the authenticated Zalo webhook endpoint and a health check.",["webhook","fastapi","api-handler","zalo"],"simple"],
};
const S={
"src/bot/agent/tools/assign_events.py":{
match_member:["function","Finds member IDs whose name matches a query by exact, single-word, then prefix match after accent folding.",["matching","utility"],"simple"],
resolve_people:["function","Resolves recipients from team names, real mentions and fuzzy names against group members, returning people and unresolved names.",["resolution","people"],"moderate"],
_assign:["function","Tool handler creating an event: enforces role limits, resolves assignees, posts to the web server and remembers the event.",["tool-handler","calendar"],"moderate"],
_update:["function","Tool handler modifying an assigned event (time, title, add/remove people), defaulting to the latest event in the chat.",["tool-handler","calendar"],"moderate"],
_tools:["function","Builds the Tool list with Vietnamese schemas for the calendar tools, returning empty if the server client is not configured.",["tool-registry","schema"],"moderate"]},
"src/bot/agent/tools/read_chat_memory.py":{_read:["function","Handler that reads recent messages for ctx.chat_id from MemoryDataStore, applies optional folded keyword filter, and formats lines with time and sender.",["tool-handler","memory"],"simple"]},
"src/bot/core/message_filter.py":{
Decision:["class","Frozen dataclass holding the filter verdict: passed flag, stage, reason, cleaned prompt and tokens used.",["data-model","dataclass"],"simple"],
is_chatter:["function","Returns true when text is empty or only interjections like ha/ok/hmm after folding.",["heuristic","utility"],"simple"],
MessageFilter:["class","Decides if a message calls the bot via triggers, mentions, name matching, mode, budget and an AI classification fallback.",["filter","llm-classifier"],"moderate"]},
"src/bot/core/message_handler.py":{
ZaloSender:["class","Protocol describing the async Zalo send_message and send_chat_action interface.",["protocol","interface"],"simple"],
Job:["class","Frozen dataclass wrapping an IncomingMessage for the per-chat queue.",["data-model","queue"],"simple"],
Bot:["class","Main bot coordinating stores, filtering, commands, rate limiting, per-chat queues and workers, agent calls and reliable reply sending.",["orchestrator","async","state"],"complex"],
strip_name_prefix:["function","Removes a leading 'Name:' prefix from model replies when it matches a known bot name.",["text-processing","utility"],"simple"]},
"src/bot/core/owner_commands.py":{
help_text:["function","Builds the help message listing commands allowed for a role.",["help","formatting"],"simple"],
ParsedCommand:["class","Frozen dataclass with a command name and its lowercase argument.",["data-model","command"],"simple"],
parse_command:["function","Parses '/cmd arg' text into a ParsedCommand if the command is known.",["parser","command"],"simple"],
describe_mode:["function","Describes the all/default reply mode in Vietnamese.",["formatting","mode"],"simple"],
CommandHandler:["class","Executes slash commands with role checks against group, history and usage stores, returning reply text.",["command-handler","permissions"],"moderate"],
_pick_people:["function","Picks Zalo IDs from real mentions, or by name matching or raw numeric IDs, reporting names not found.",["resolution","people"],"simple"]},
"src/bot/core/rate_limiter.py":{RateLimiter:["class","Sliding-window limiter with injectable clock; allow(key) returns false once per-minute hits are exceeded, 0 disables.",["rate-limiting","sliding-window"],"simple"]},
"src/bot/core/reply_formatting.py":{
utf16_len:["function","Counts text length in UTF-16 code units.",["utility","unicode"],"simple"],
_max_prefix:["function","Returns the longest prefix index that fits within a UTF-16 limit.",["utility","unicode"],"simple"],
split_message:["function","Splits text into chunks within the limit, preferring paragraph, line, sentence then space boundaries.",["chunking","formatting"],"moderate"],
to_plain_text:["function","Strips bold, heading and bullet markdown into plain text for Zalo.",["markdown","formatting"],"simple"]},
"src/bot/core/roles.py":{
role_of:["function","Determines a user's role: owner, leader (all-assign or group leader) or basic.",["permissions","roles"],"simple"],
required_role:["function","Returns the minimum role for a command and argument.",["permissions","roles"],"moderate"],
allows:["function","Checks whether a role rank meets the needed rank.",["permissions","roles"],"simple"]},
"src/bot/core/text_fold.py":{fold:["function","Lowercases, maps d-stroke to d and strips combining marks via NFD.",["text-normalization","vietnamese"],"simple"]},
"src/bot/storage/data_stores.py":{
GroupState:["class","Dataclass for per-chat settings: allowed flag, mode, label, leaders and teams.",["data-model","settings"],"simple"],
GroupStore:["class","Persistent per-group settings store with mtime-based reload, allow/mode/leader/team operations and assignment permission checks.",["storage","settings"],"complex"],
SeenStore:["class","Bounded persisted set of processed message IDs for deduplication.",["storage","deduplication"],"simple"],
safe_name:["function","Converts a chat ID into a filesystem-safe filename.",["utility","filesystem"],"simple"],
HistoryStore:["class","Per-chat JSON-lines conversation history with append, recent and clear.",["storage","history"],"simple"],
MemoryDataStore:["class","Per-chat log of all messages (including filtered ones) with trimming, used for the memory tool.",["storage","memory"],"moderate"],
StateStore:["class","Small persisted status object updated with keyword fields.",["storage","state"],"simple"],
UsageStore:["class","Tracks daily token usage and budget-exceeded notification state.",["storage","usage"],"moderate"],
StatsStore:["class","Daily counters with retention limit and recent-days queries.",["storage","metrics"],"moderate"],
ActivityStore:["class","Records last activity, type and name per chat.",["storage","activity"],"simple"],
FailedStore:["class","Queue of replies that failed to send, supporting pending lookup and resolution marking.",["storage","retry"],"moderate"]},
"src/bot/storage/text_files.py":{
atomic_write_text:["function","Writes text atomically to a path via temporary file replacement.",["file-io","atomic"],"simple"],
JsonLinesFile:["class","JSON-lines file wrapper with tolerant read_all, append, rewrite, tail, count and trim.",["file-io","jsonl"],"moderate"],
JsonObjectFile:["class","JSON object file wrapper with safe read and atomic write.",["file-io","json"],"simple"]},
"src/bot/zalo/receive_webhook.py":{create_app:["function","Creates a FastAPI app with a secret-validated POST webhook that forwards payloads to the handler, and a /health endpoint.",["factory","fastapi","webhook"],"simple"]},
};
for(const f of b.files){
 const r=R.find(x=>x.path===f.path)||{};
 const [sum,tags,cx]=F[f.path];
 nodes.push({id:"file:"+f.path,type:"file",name:f.path.split("/").pop(),filePath:f.path,summary:sum,tags,complexity:cx});
 const ranges={};for(const x of [...(r.functions||[]),...(r.classes||[])])ranges[x.name]=[x.startLine,x.endLine];
 for(const [n,[k,s,t,c]] of Object.entries(S[f.path]||{})){
  if(!ranges[n])throw new Error("missing "+f.path+n);
  nodes.push({id:`${k}:${f.path}:${n}`,type:k,name:n,filePath:f.path,lineRange:ranges[n],summary:s,tags:t,complexity:c});
  edges.push({source:"file:"+f.path,target:`${k}:${f.path}:${n}`,type:"contains",direction:"forward",weight:1});
  if((r.exports||[]).some(e=>e.name===n)&&!n.startsWith("_"))edges.push({source:"file:"+f.path,target:`${k}:${f.path}:${n}`,type:"exports",direction:"forward",weight:0.8});
 }
 for(const t of b.batchImportData[f.path]||[])edges.push({source:"file:"+f.path,target:"file:"+t,type:"imports",direction:"forward",weight:0.7});
}
const call=(s,t)=>edges.push({source:s,target:t,type:"calls",direction:"forward",weight:0.8});
call("function:src/bot/agent/tools/assign_events.py:match_member","function:src/bot/core/text_fold.py:fold");
call("class:src/bot/core/message_handler.py:Bot","class:src/bot/core/message_filter.py:MessageFilter");
call("class:src/bot/core/message_handler.py:Bot","class:src/bot/core/owner_commands.py:CommandHandler");
call("class:src/bot/core/message_handler.py:Bot","class:src/bot/core/rate_limiter.py:RateLimiter");
call("function:src/bot/core/owner_commands.py:_pick_people","function:src/bot/agent/tools/assign_events.py:match_member");
call("function:src/bot/agent/tools/read_chat_memory.py:_read","class:src/bot/storage/data_stores.py:MemoryDataStore");
edges.push({source:"class:src/bot/core/message_handler.py:Bot",target:"class:src/bot/storage/data_stores.py:GroupStore",type:"depends_on",direction:"forward",weight:0.6});
fs.writeFileSync(".ua/intermediate/batch-2.json",JSON.stringify({nodes,edges},null,1));
const ids=new Set(nodes.map(n=>n.id));const imp=new Set(Object.values(b.batchImportData).flat().map(p=>"file:"+p));
let bad=0;for(const e of edges)for(const x of [e.source,e.target])if(!ids.has(x)&&!imp.has(x)){bad++;console.log("bad",x)}
console.log(nodes.length,edges.length,"imports",edges.filter(e=>e.type=="imports").length,Object.values(b.batchImportData).flat().length,"bad",bad);
