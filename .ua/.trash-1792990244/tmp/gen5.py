import json
nodes=[];edges=[]
def F(p,s,t,c,ln=None):
    d=dict(id="file:"+p,type="file",name=p.split("/")[-1],filePath=p,summary=s,tags=t,complexity=c)
    if ln: d["languageNotes"]=ln
    nodes.append(d)
def N(kind,p,n,r,s,t,c):
    nodes.append(dict(id=f"{kind}:{p}:{n}",type=kind,name=n,filePath=p,lineRange=r,summary=s,tags=t,complexity=c))
    edges.append(dict(source="file:"+p,target=f"{kind}:{p}:{n}",type="contains",direction="forward",weight=1.0))
def E(s,t,ty,w): edges.append(dict(source=s,target=t,type=ty,direction="forward",weight=w))
M="src/bot/core/mention_tags.py";Z="src/bot/zalo/"
F(M,"Handles @mention tagging in Zalo group replies: inserts missing '@' before member names when the requester asked to tag someone, and converts '@Name' text into Zalo mention objects with UTF-16 positions using accent-insensitive, longest-first matching.",["mention","text-processing","utility","unicode"],"moderate","Uses same-length diacritic folding so character offsets stay valid, and UTF-16 length counting to match the offsets Zalo (JavaScript) expects.")
N("function",M,"fold_same_length",[28,30],"Strips Vietnamese diacritics and lowercases text while preserving length so match positions map back to the original string.",["utility","unicode","text-processing"],"simple")
N("function",M,"utf16_len",[33,35],"Returns the length of a string in UTF-16 code units, matching how Zalo computes mention offsets.",["utility","unicode"],"simple")
N("function",M,"build_mentions",[57,70],"Scans text for '@Name' occurrences matching known group members (longest names first, word boundaries) and returns Zalo mention dicts with pos, len, uid and type.",["mention","parsing","api-helper"],"moderate")
N("function",M,"add_tags",[73,94],"Inserts '@' before member names in a reply when the request shows tag/remind/call intent and the name appears in both request and reply, avoiding overlaps with longer names.",["mention","text-processing","heuristic"],"moderate")
F(Z+"__init__.py","Package init re-exporting the Zalo Bot Platform client, error type and incoming-message parsing helpers.",["barrel","entry-point","package-init"],"simple")
E("file:"+Z+"__init__.py","file:"+Z+"bot_platform_api.py","imports",0.7)
E("file:"+Z+"__init__.py","file:"+Z+"incoming_message.py","imports",0.7)
B=Z+"bot_platform_api.py"
F(B,"Async httpx client for the official Zalo Bot Platform API, wrapping getMe, getUpdates, sendMessage, typing actions and webhook management, with token redaction in all errors.",["api-client","http","zalo","security"],"moderate")
N("class",B,"ZaloError",[15,22],"Exception for Zalo API failures (ok=false) or network errors, carrying description, error_code and a network flag.",["exception","error-handling"],"simple")
N("class",B,"ZaloClient",[25,78],"Async client posting to the bot API; call() parses JSON, raises ZaloError with the token redacted, and thin methods cover get_me, get_updates, send_message, send_chat_action and webhook calls.",["api-client","http","async"],"moderate")
I=Z+"incoming_message.py"
F(I,"Defines the IncomingMessage dataclass and parsers that normalize Zalo webhook or getUpdates payloads (object, list, wrapped or not) into message objects with dedupe keys.",["data-model","parsing","zalo","normalization"],"moderate")
N("class",I,"IncomingMessage",[22,52],"Frozen dataclass for a normalized incoming Zalo event with chat/sender info, text, mentions and is_group, is_text and dedupe_key helpers.",["data-model","dataclass"],"moderate")
N("function",I,"parse_event",[64,87],"Converts one raw event dict into an IncomingMessage, returning None when message, chat id or sender id is missing.",["parsing","validation"],"moderate")
N("function",I,"parse_updates",[90,101],"Accepts a webhook payload or getUpdates result in any shape and returns the list of valid IncomingMessage objects.",["parsing","api-helper"],"simple")
R=Z+"receive_polling.py"
F(R,"Long-polling receive loop using getUpdates: removes any webhook, then polls with exponential backoff, tolerating timeouts and network errors, and records heartbeat state.",["polling","resilience","async","entry-point"],"moderate")
N("function",R,"run_polling",[22,74],"Runs the never-exiting getUpdates loop, deleting the webhook first, handling 408 timeouts, network errors and unexpected exceptions with backoff and de-duplicated logging, and passing results to the handler.",["polling","error-handling","async"],"complex")
N("function",R,"_sleep_or_stop",[77,81],"Sleeps for given seconds but wakes early if the stop event is set.",["async","utility"],"simple")
P=Z+"personal_account.py"
F(P,"Runs the bot on a personal Zalo account via the unofficial zlapi library: loads a QR-login session, listens over websocket in a background thread, forwards messages to the event loop, and sends replies with group mention support.",["zalo","personal-account","websocket","threading"],"complex","Bridges synchronous zlapi to asyncio using run_coroutine_threadsafe and asyncio.to_thread; defines a dynamic subclass of ZaloAPI inside login().")
N("function",P,"load_session",[40,68],"Reads the session file in several formats (QR-login JSON, cookie dict, or cookie list) and returns cookies, IMEI and user agent, raising ConfigError on problems.",["session","config","parsing"],"moderate")
N("function",P,"to_incoming",[71,98],"Maps zlapi onMessage arguments into an IncomingMessage, marking own messages as bot-sent to avoid self-replies.",["adapter","parsing"],"moderate")
N("function",P,"mention_names",[115,129],"Extracts {uid: name} from mention entries of a message by slicing text with UTF-16 offsets, skipping @All.",["mention","unicode","parsing"],"moderate")
N("class",P,"PersonalZalo",[143,335],"Personal-account transport with ZaloClient-compatible send_message and send_chat_action; handles login, websocket listening thread, group member caching, learned mention names and mention-aware sending.",["zalo","transport","threading","service"],"complex")
N("function",P,"_is_network_error",[338,350],"Walks the exception cause chain to decide whether a zlapi login failure is really a network error.",["error-handling","utility"],"simple")
N("function",P,"_log_failure",[353,356],"Done-callback that logs exceptions from handler futures scheduled onto the event loop.",["logging","callback"],"simple")
for s in ["src/bot/config.py","src/bot/core/mention_tags.py","src/bot/core/vietnam_time.py","src/bot/storage/__init__.py","src/bot/userdata_paths.py",B,I]:
    E("file:"+P,"file:"+s,"imports",0.7)
E("file:"+R,"file:src/bot/core/vietnam_time.py","imports",0.7)
E("file:"+R,"file:src/bot/storage/__init__.py","imports",0.7)
E("file:"+R,"file:"+Z+"__init__.py","imports",0.7)
E("function:"+P+":to_incoming","class:"+I+":IncomingMessage","calls",0.8)
E("class:"+P+":PersonalZalo","function:"+M+":build_mentions","calls",0.8)
E("function:"+R+":run_polling","class:"+B+":ZaloClient","calls",0.8)
E("function:"+R+":run_polling","function:src/bot/core/vietnam_time.py:now_ms","calls",0.8)
E("class:"+P+":PersonalZalo","function:src/bot/core/vietnam_time.py:now_ms","calls",0.8)
E("function:"+P+":load_session","class:src/bot/config.py:ConfigError","calls",0.8)
E("class:"+P+":PersonalZalo","class:src/bot/config.py:Settings","depends_on",0.6)
for n in ["fold_same_length","utf16_len","build_mentions","add_tags"]:
    E("file:"+M,"function:"+M+":"+n,"exports",0.8)
E("file:"+B,"class:"+B+":ZaloError","exports",0.8);E("file:"+B,"class:"+B+":ZaloClient","exports",0.8)
E("file:"+I,"class:"+I+":IncomingMessage","exports",0.8);E("file:"+I,"function:"+I+":parse_updates","exports",0.8)
E("file:"+R,"function:"+R+":run_polling","exports",0.8)
E("file:"+P,"class:"+P+":PersonalZalo","exports",0.8)
ids={n["id"] for n in nodes}
ext={"file:src/bot/config.py","file:src/bot/core/vietnam_time.py","file:src/bot/storage/__init__.py","file:src/bot/userdata_paths.py","function:src/bot/core/vietnam_time.py:now_ms","class:src/bot/config.py:ConfigError","class:src/bot/config.py:Settings"}
ok=ids|ext
bad=[e for e in edges if e["source"] not in ok or e["target"] not in ok]
print(len(nodes),len(edges),bad)
json.dump(dict(nodes=nodes,edges=edges),open("D:/pylosSever/.ua/intermediate/batch-5.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
