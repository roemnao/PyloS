import json
N=[];E=[]
def f(p,s,t,c,ln=None):
    N.append({"id":"file:"+p,"type":"file","name":p.split('/')[-1],"filePath":p,"summary":s,"tags":t,"complexity":c,**({"languageNotes":ln} if ln else {})})
def fn(p,n,a,b,s,t,c,k="function"):
    N.append({"id":f"{k}:{p}:{n}","type":k,"name":n,"filePath":p,"lineRange":[a,b],"summary":s,"tags":t,"complexity":c})
    E.append({"source":"file:"+p,"target":f"{k}:{p}:{n}","type":"contains","direction":"forward","weight":1.0})
C="tests/conftest.py"
f(C,"Shared pytest fixtures and fakes for the test suite: fake Zalo client, fake Gemini agent, a mocked web API server, and factories for Settings, Bot and incoming webhook events.",["test","fixtures","test-doubles","pytest"],"moderate","Uses httpx.MockTransport to intercept the web API client and monkeypatches environment/config so tests never touch real machine settings.")
fn(C,"FakeZalo",20,36,"In-memory Zalo client double that records sent messages, can fail a configurable number of times to exercise retry logic, and exposes sent texts per chat.",["test-double","zalo","fake"],"simple","class")
fn(C,"FakeAgent",39,58,"Fake AI agent recording reply and classify calls; returns canned reply text and a configurable filter verdict or error to drive message-filter scenarios.",["test-double","agent","fake"],"simple","class")
fn(C,"FakeWeb",127,156,"Fake web backend (/api/agent/*) served through an httpx handler; checks bearer key, records calls, and answers from a route table with optional offline mode.",["test-double","http-mock","web-api"],"moderate","class")
fn(C,"make_settings",61,74,"Builds a Settings object from an isolated env dict rooted in tmp_path, with rate limits and budget disabled and per-test overrides.",["test-helper","settings","factory"],"simple")
fn(C,"event",77,98,"Builds a Zalo bot webhook payload (message.text.received by default) with auto-incrementing message ids and configurable sender, chat and timestamp.",["test-helper","payload-builder","webhook"],"simple")
fn(C,"make_bot",115,124,"Pytest fixture returning a factory that constructs a Bot wired to the fake Zalo and agent with zero retry delay.",["fixture","factory","bot"],"simple")
fn(C,"web",160,169,"Pytest fixture that installs FakeWeb as the httpx transport, points config at tmp_path and sets schedule API env vars.",["fixture","http-mock","monkeypatch"],"moderate")
f("tests/test_bot.py","Async tests for the Bot message handler covering access control, trigger modes, owner commands, dedupe, restart persistence, splitting, rate limits, budget, ordering, leader/role commands and tool context.",["test","bot","message-handler","integration"],"complex")
fn("tests/test_bot.py","send",9,11,"Test helper that feeds a payload to the bot and drains its processing queue.",["test-helper","async"],"simple")
f("tests/test_desktop.py","Tests for desktop packaging concerns: app home resolution (source, frozen, fallback), hidden subprocess windows, first-run setup, admin token, tool discovery, graceful gateway stop, logging, free port, autostart registry and secret scanning.",["test","desktop","packaging","system"],"complex")
f("tests/test_filter.py","Tests for MessageFilter rules (trigger, tag, name, chatter, non-text) versus AI classification, plus Gemini classify behavior including JSON requests, token counting, timeout retry and thinking fallback.",["test","message-filter","gemini","classification"],"moderate")
fn("tests/test_filter.py","msg",12,17,"Builds an incoming message via to_incoming with optional mentions, group flag and non-text content.",["test-helper","message-builder"],"simple")
f("tests/test_memorydata.py","Tests for per-chat memory logging: every message is logged while only passed ones reach the session, unallowed chats are skipped, the store trims, and the read-chat-memory tool is scoped to its own chat.",["test","memory","storage","tool"],"simple")
f("tests/test_personal.py","Tests for the personal-account Zalo client: session loading, incoming mapping, thread type selection, error wrapping, listener dispatch, network error detection and mention/tag building and name learning.",["test","zalo","personal-account","mentions"],"moderate")
fn("tests/test_personal.py","FakeApi",29,52,"Fake zlapi client used to capture sent messages and simulate results or errors for PersonalZalo tests.",["test-double","zalo","fake"],"simple","class")
f("tests/test_remote_config.py","Tests for remote config and web sync: whitelisting allowed keys, live apply and restart persistence, heartbeat fetch with network tolerance, session uploader batching, bot chain recording and link-code handling.",["test","remote-config","web-sync","system"],"moderate")
for p in ["bot","desktop","filter","memorydata","personal","remote_config"]:
    E.append({"source":f"file:tests/test_{p}.py","target":"file:"+C,"type":"imports","direction":"forward","weight":0.7})
json.dump({"nodes":N,"edges":E},open(".ua/intermediate/batch-4.json","w"),indent=1)
ids={n["id"] for n in N}
ok=all(e["source"] in ids and (e["target"] in ids) for e in E)
print(len(N),len(E),ok, len(ids)==len(N))
