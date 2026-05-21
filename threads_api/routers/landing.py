from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/landing")
def landing_page():
    return HTMLResponse(_HTML)


_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>THREADY — Autonomous posting for Threads</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root{
    --bg:#f6f6f4;
    --bg-2:#efeeea;
    --card:#ffffff;
    --card-2:#fafaf7;
    --line:#e6e4de;
    --line-2:#d6d4cd;
    --text:#0e0e10;
    --muted:#6a6a72;
    --muted-2:#9a9aa2;
    --accent:#2563eb;
    --accent-soft:rgba(37,99,235,.10);
    --accent-line:rgba(37,99,235,.28);
    --good:#0fa18a;
    --warn:#b45309;
    --maxw:1200px;
    --pad:clamp(20px,4vw,40px);
    --sans: system-ui, -apple-system, "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:var(--sans);-webkit-font-smoothing:antialiased}
  body{
    font-size:16px;line-height:1.55;
    background:
      radial-gradient(1200px 600px at 80% -10%, rgba(37,99,235,.08), transparent 60%),
      radial-gradient(900px 500px at -10% 10%, rgba(37,99,235,.04), transparent 60%),
      var(--bg);
    background-attachment: fixed;
  }
  a{color:inherit;text-decoration:none}
  ::selection{background:var(--accent);color:#fff}

  .wrap{max-width:var(--maxw);margin:0 auto;padding:0 var(--pad)}
  .mono{font-family:var(--mono);letter-spacing:-.01em}
  .eyebrow{
    font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
    display:inline-flex;align-items:center;gap:10px;
  }
  .eyebrow::before{content:"";width:18px;height:1px;background:var(--line-2)}
  .pill{
    display:inline-flex;align-items:center;gap:8px;
    padding:6px 10px;border:1px solid var(--line-2);border-radius:999px;
    font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--muted);text-transform:uppercase;
    background:rgba(255,255,255,.6);
  }
  .pill .dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 0 4px rgba(15,161,138,.16)}

  /* NAV */
  nav.top{
    position:sticky;top:0;z-index:20;
    backdrop-filter:blur(10px);
    background:rgba(246,246,244,.72);
    border-bottom:1px solid var(--line);
  }
  .nav-inner{display:flex;align-items:center;justify-content:space-between;height:64px}
  .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-weight:600;letter-spacing:.04em}
  .brand .logo{width:38px;height:24px}
  .brand .logo svg{display:block;width:100%;height:100%;overflow:visible}
  /* logo threads animate like the page threads — layer drift + per-path sway */
  @keyframes logo-drift { 0%,100%{transform:translate(-1.5px,0)} 50%{transform:translate(1.5px,0)} }
  @keyframes logo-sway-1{ 0%,100%{transform:translate(0,-.8px)} 50%{transform:translate(0,.8px)} }
  @keyframes logo-sway-2{ 0%,100%{transform:translate(0,1px)}   50%{transform:translate(0,-1px)} }
  @keyframes logo-sway-3{ 0%,100%{transform:translate(0,-.7px)} 50%{transform:translate(0,.7px)} }
  .brand .logo svg{animation:logo-drift 9s ease-in-out infinite;transform-origin:center;will-change:transform}
  .brand .logo svg path{transform-origin:center;will-change:transform}
  .brand .logo svg path:nth-of-type(1){animation:logo-sway-1 5s   ease-in-out infinite}
  .brand .logo svg path:nth-of-type(2){animation:logo-sway-2 6.5s ease-in-out -1.5s infinite}
  .brand .logo svg path:nth-of-type(3){animation:logo-sway-3 4.5s ease-in-out -2.5s infinite}
  .brand .logo svg path:nth-of-type(4){animation:logo-sway-2 5.5s ease-in-out -1s   infinite}
  .brand .logo svg path:nth-of-type(5){animation:logo-sway-1 7s   ease-in-out -3s   infinite}
  .brand .logo svg path:nth-of-type(6){animation:logo-sway-3 6s   ease-in-out -2s   infinite}
  .brand .logo svg path:nth-of-type(7){animation:logo-sway-2 4s   ease-in-out -.8s  infinite}
  .nav-links{display:flex;gap:28px;font-size:13px;color:var(--muted)}
  .nav-links a:hover{color:var(--text)}
  .nav-cta{
    font-family:var(--mono);font-size:12px;letter-spacing:.06em;
    padding:9px 14px;border:1px solid var(--line-2);border-radius:8px;color:var(--text);
    background:linear-gradient(180deg, #ffffff, #f3f2ee);
  }
  .nav-cta:hover{border-color:var(--accent-line);color:var(--accent)}
  @media (max-width:760px){ .nav-links{display:none} }

  /* HERO — scattered canvas (no UI inside, just animated lines + scattered title) */
  .hero{padding:0;position:relative;overflow:hidden;min-height:560px}
  .hero-threads{
    position:absolute;inset:0;pointer-events:none;z-index:0;overflow:visible;
  }
  .hero-threads.full{inset:0}
  .hero-threads svg{width:100%;height:100%;display:block;overflow:visible}

  /* scattered heading words spread across the hero */
  .scatter{
    position:absolute;inset:88px 5% 56px 5%;
    pointer-events:none;z-index:1;
  }
  .scatter .sw{
    position:absolute;display:inline-block;
    font-weight:500;line-height:1.1;letter-spacing:-.025em;
    white-space:nowrap;color:var(--text);
    padding-bottom:.12em;
    will-change:transform;
  }
  .scatter .sw em{
    font-style:normal;
    background:linear-gradient(180deg,#3b82f6 0%, #1d4ed8 70%);
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  }
  .scatter .sw.tw{
    background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;color:transparent;
    background-size:200% 100%;
    animation: tw-shift 14s linear infinite;
  }
  .scatter .sw.tw-a{background-image:linear-gradient(120deg,var(--t2) 0%,var(--t3) 50%,var(--t4) 100%)}
  .scatter .sw.tw-b{background-image:linear-gradient(120deg,var(--t4) 0%,var(--t5) 50%,var(--t2) 100%);animation-delay:-3s}
  .scatter .sw.tw-c{background-image:linear-gradient(120deg,var(--t2) 0%,var(--t5) 50%,var(--t1) 100%);animation-delay:-6s}
  .scatter .sw:nth-child(1){animation: sway-c 10s ease-in-out infinite}
  .scatter .sw:nth-child(2){animation: sway-b 12s ease-in-out -2s infinite, tw-shift 14s linear infinite}
  .scatter .sw:nth-child(3){animation: sway-a 8s  ease-in-out -1s infinite}
  .scatter .sw:nth-child(4){animation: sway-c 9s  ease-in-out -3s infinite}
  .scatter .sw:nth-child(5){animation: sway-b 11s ease-in-out -4s infinite}
  .scatter .sw:nth-child(6){animation: sway-a 8.5s ease-in-out -2.5s infinite}
  .scatter .sw:nth-child(7){animation: sway-c 9.5s ease-in-out -1.5s infinite, tw-shift 14s linear -3s infinite}

  /* HERO INTRO — clean two-column block right under the hero */
  .hero-intro{padding:56px 0 80px;background:var(--bg);position:relative;border-top:none}
  .hero-intro .intro-grid{
    display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:start;
  }
  .hero-intro .intro-copy{display:flex;flex-direction:column;gap:18px}
  .hero-intro .pill{align-self:flex-start}
  .hero-intro .hero-sub{margin:0;color:var(--muted);font-size:17px;max-width:54ch}
  .hero-intro .hero-cta{margin-top:8px;display:flex;gap:12px;flex-wrap:wrap}
  /* KPI panel back to in-flow */
  .hero-intro .hero-panel{position:static;width:auto;background:linear-gradient(180deg,var(--card),var(--bg-2))}

  @media (max-width:820px){
    .hero{min-height:520px}
    .hero-intro .intro-grid{grid-template-columns:1fr;gap:32px}
  }
  .hero-grid{display:grid;grid-template-columns:1.25fr .9fr;gap:64px;align-items:end}
  @media (max-width:980px){ .hero-grid{grid-template-columns:1fr;gap:40px} }

  h1.hero-title{
    font-size:clamp(44px, 7vw, 92px);
    line-height:.96;letter-spacing:-.035em;font-weight:500;
    margin:18px 0 22px;
    text-wrap:balance;
  }
  h1.hero-title em{
    font-style:normal;color:var(--accent);
    background:linear-gradient(180deg, #3b82f6 0%, #1d4ed8 70%);
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  }
  /* heading sways in tandem with the threads — each line on its own phase */
  h1.hero-title .line{display:block;will-change:transform;transform-origin:left center}
  h1.hero-title .line-1{animation: sway-c 9s  ease-in-out infinite}
  h1.hero-title .line-2{animation: sway-b 11s ease-in-out -2s infinite}
  h1.hero-title .line-3{animation: sway-a 8s  ease-in-out -4s infinite}
  /* coloured words borrow the thread palette; they cycle hues in a slow loop */
  h1.hero-title .tw{
    background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    color:transparent;
  }
  h1.hero-title .tw-a{
    background-image:linear-gradient(120deg,var(--t2) 0%,var(--t3) 50%,var(--t4) 100%);
    background-size:200% 100%;
    animation: tw-shift 12s linear infinite;
  }
  h1.hero-title .tw-b{
    background-image:linear-gradient(120deg,var(--t4) 0%,var(--t5) 50%,var(--t2) 100%);
    background-size:200% 100%;
    animation: tw-shift 14s linear -3s infinite;
  }
  @keyframes tw-shift {
    0%   { background-position: 0%   50%; }
    100% { background-position: 200% 50%; }
  }
  .hero-sub{max-width:54ch;color:var(--muted);font-size:17px}
  .hero-cta{display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
  .btn{
    display:inline-flex;align-items:center;gap:10px;
    padding:13px 18px;border-radius:10px;font-size:14px;font-weight:500;
    border:1px solid transparent;cursor:pointer;transition:transform .15s ease, background .2s;
  }
  .btn-primary{background:var(--t2);color:#ffffff;border-color:var(--t2)}
  .btn-primary:hover{background:#d85a4a;border-color:#d85a4a;transform:translateY(-1px)}
  .btn-ghost{background:transparent;border-color:var(--line-2);color:var(--text)}
  .btn-ghost:hover{border-color:var(--t2);color:var(--t2)}

  /* Hero stat panel */
  .hero-panel{
    border:1px solid var(--line);
    border-radius:14px;
    background:linear-gradient(180deg, var(--card), var(--bg-2));
    padding:22px;
    position:relative;
  }
  .hero-panel-head{
    display:flex;align-items:center;justify-content:space-between;
    font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;
    border-bottom:1px dashed var(--line-2);padding-bottom:14px;margin-bottom:18px;
  }
  .kpi{display:grid;grid-template-columns:1fr 1fr;gap:18px 22px}
  .kpi .cell{padding:10px 0}
  .kpi .label{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px}
  .kpi .num{font-family:var(--mono);font-size:32px;font-weight:500;letter-spacing:-.02em;line-height:1}
  .kpi .num .unit{font-size:14px;color:var(--muted);margin-left:6px;letter-spacing:0}
  .kpi .delta{font-family:var(--mono);font-size:11px;color:var(--good);margin-top:6px}

  /* SECTION SCAFFOLD */
  section{padding:96px 0;border-top:1px solid var(--line)}
  .section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin-bottom:48px;flex-wrap:wrap}
  .section-head h2{
    margin:10px 0 0;font-size:clamp(28px,3.4vw,42px);letter-spacing:-.02em;font-weight:500;line-height:1.05;max-width:22ch;
  }
  .section-head p{color:var(--muted);max-width:48ch;margin:0}
  .index{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.18em}

  /* HOW IT WORKS */
  .pipeline{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;position:relative}
  @media (max-width:1100px){ .pipeline{grid-template-columns:repeat(3,1fr)} }
  @media (max-width:720px){ .pipeline{grid-template-columns:1fr} }
  .step{
    border:1px solid var(--line);border-radius:14px;background:var(--card);
    padding:26px 24px 28px;position:relative;overflow:hidden;
  }
  .step::after{
    content:"";position:absolute;inset:auto -1px -1px -1px;height:1px;
    background:linear-gradient(90deg, transparent, rgba(239,111,94,.4), transparent);
    opacity:0;transition:opacity .3s;
  }
  .step:hover::after{opacity:1}
  .step .ix{
    font-family:var(--mono);font-size:11px;color:var(--t2);letter-spacing:.12em;
    display:flex;align-items:center;gap:10px;margin-bottom:18px;
  }
  .step .ix .line{flex:1;height:1px;background:linear-gradient(90deg,rgba(239,111,94,.4),transparent)}
  .step h3{margin:0 0 8px;font-size:20px;font-weight:500;letter-spacing:-.01em}
  .step p{color:var(--muted);margin:0;font-size:14.5px}
  .step .glyph{margin-bottom:22px;height:64px;display:flex;align-items:center;justify-content:flex-start}
  .step ul{list-style:none;padding:0;margin:16px 0 0;display:flex;flex-direction:column;gap:6px}
  .step ul li{font-family:var(--mono);font-size:12px;color:var(--muted);display:flex;gap:10px}
  .step ul li::before{content:"→";color:var(--t2);opacity:.8}

  /* DASHBOARD */
  .dash{
    border:1px solid var(--line);border-radius:16px;overflow:hidden;
    background:linear-gradient(180deg,#ffffff,#faf9f5);
  }
  .dash-bar{
    display:flex;align-items:center;justify-content:space-between;
    padding:12px 16px;border-bottom:1px solid var(--line);
    background:#f3f2ee;
  }
  .dash-bar .left{display:flex;align-items:center;gap:14px}
  .traffic{display:flex;gap:6px}
  .traffic i{width:10px;height:10px;border-radius:50%;background:#d6d4cd;display:inline-block}
  .traffic i:nth-child(1){background:#ef4444}
  .traffic i:nth-child(2){background:#f59e0b}
  .traffic i:nth-child(3){background:#22c55e}
  .url{
    font-family:var(--mono);font-size:11px;color:var(--muted);
    background:#ffffff;border:1px solid var(--line);padding:4px 10px;border-radius:6px;
  }
  .dash-bar .right{display:flex;gap:14px;font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
  .dash-bar .right .live{color:var(--good);display:flex;align-items:center;gap:6px}
  .dash-bar .right .live::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--good);animation:pulse 1.6s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}

  .dash-body{padding:22px;display:grid;grid-template-columns:1.4fr 1fr;gap:18px}
  @media (max-width:900px){ .dash-body{grid-template-columns:1fr} }
  .dash-card{
    border:1px solid var(--line);border-radius:12px;background:var(--card);padding:18px;
  }
  .dash-card h4{margin:0;font-size:13px;font-weight:500;color:var(--muted);font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase}
  .dash-card .big{font-family:var(--mono);font-size:30px;letter-spacing:-.02em;margin-top:8px}
  .dash-card .sub{color:var(--muted);font-size:12px;margin-top:4px;font-family:var(--mono)}
  .row-2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media (max-width:600px){ .row-2{grid-template-columns:1fr} }
  .legend{display:flex;gap:18px;font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:10px}
  .legend i{display:inline-block;width:10px;height:2px;background:var(--accent);margin-right:6px;vertical-align:middle}
  .legend .a i{background:var(--accent)}
  .legend .b i{background:#9333ea}
  .chart{width:100%;display:block}

  /* ACCOUNTS */
  .accounts{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
  @media (max-width:760px){ .accounts{grid-template-columns:1fr} }
  .participant-head{
    display:flex;align-items:center;justify-content:space-between;
    padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:12px;
    grid-column:1 / -1;
  }
  .participant-head .who{display:flex;align-items:center;gap:14px}
  .avatar{
    width:38px;height:38px;border-radius:50%;
    background:linear-gradient(135deg,#f3f2ee,#e6e4de);
    border:1px solid var(--line-2);display:flex;align-items:center;justify-content:center;
    font-family:var(--mono);font-size:14px;color:var(--text);
  }
  .participant-head .meta{display:flex;gap:18px;font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.04em}
  .participant-head .meta b{color:var(--text);font-weight:500}

  .account{
    border:1px solid var(--line);border-radius:12px;background:var(--card);
    padding:18px 18px 16px;display:flex;flex-direction:column;gap:14px;
    transition:border-color .2s, transform .2s;
  }
  .account:hover{border-color:var(--accent-line);transform:translateY(-2px)}
  .acc-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
  .handle{font-family:var(--mono);font-size:14px;font-weight:500}
  .handle .at{color:var(--muted-2)}
  .lang{
    font-family:var(--mono);font-size:10px;letter-spacing:.12em;
    padding:3px 8px;border-radius:6px;border:1px solid var(--line-2);color:var(--muted);
  }
  .niche{color:var(--muted);font-size:13px;margin-top:-6px}
  .acc-stats{display:flex;justify-content:space-between;align-items:center;border-top:1px dashed var(--line-2);padding-top:12px}
  .acc-stats .s{display:flex;flex-direction:column}
  .acc-stats .s .v{font-family:var(--mono);font-size:14px}
  .acc-stats .s .k{font-family:var(--mono);font-size:10px;color:var(--muted-2);letter-spacing:.1em;text-transform:uppercase}
  .sparkline{width:80px;height:24px}

  /* CHAT */
  .chat-wrap{display:grid;grid-template-columns:1fr 1.1fr;gap:36px;align-items:stretch}
  @media (max-width:900px){ .chat-wrap{grid-template-columns:1fr} }
  .chat-copy h3{font-size:22px;margin:14px 0 12px;font-weight:500;letter-spacing:-.01em}
  .chat-copy p{color:var(--muted);max-width:42ch}
  .chat-copy ul{list-style:none;padding:0;margin:24px 0 0;display:flex;flex-direction:column;gap:10px}
  .chat-copy ul li{font-family:var(--mono);font-size:12.5px;color:var(--muted);display:flex;gap:10px}
  .chat-copy ul li::before{content:"//";color:var(--accent);opacity:.7}

  /* Assistant section: coral palette overrides */
  #assistant .chat-copy ul li::before{color:var(--t2)}
  #assistant .msg.user{background:rgba(239,111,94,.12);border-color:rgba(239,111,94,.35);color:#a8412e}
  #assistant .send{
    border-color:rgba(239,111,94,.4);
    background:rgba(239,111,94,.15);
    color:var(--t2);
  }

  .chat-ui{
    border:1px solid var(--line);border-radius:14px;background:var(--card);overflow:hidden;display:flex;flex-direction:column;min-height:440px;
  }
  .chat-head{padding:14px 18px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between}
  .chat-head .who{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:13px}
  .chat-head .who .dot{width:8px;height:8px;border-radius:50%;background:var(--good)}
  .chat-head .meta{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.08em}
  .chat-body{padding:18px;flex:1;display:flex;flex-direction:column;gap:14px;overflow-y:auto;max-height:340px}
  .msg{max-width:78%;padding:11px 14px;border-radius:12px;font-size:14px;line-height:1.5}
  .msg.user{align-self:flex-end;background:var(--accent-soft);border:1px solid var(--accent-line);color:#1d4ed8}
  .msg.bot{align-self:flex-start;background:#f7f6f2;border:1px solid var(--line-2)}
  .msg.bot .data{
    margin-top:10px;border-top:1px dashed var(--line-2);padding-top:10px;
    font-family:var(--mono);font-size:12px;color:var(--muted);display:grid;grid-template-columns:auto 1fr;gap:4px 14px
  }
  .msg.bot .data b{color:var(--text);font-weight:500}
  .chat-input{
    border-top:1px solid var(--line);padding:12px 14px;display:flex;align-items:center;gap:10px;
    background:#faf9f5;
  }
  .chat-input input{
    flex:1;background:transparent;border:none;outline:none;color:var(--text);font-family:var(--sans);font-size:14px;
  }
  .chat-input input::placeholder{color:var(--muted-2)}
  .send{
    width:30px;height:30px;border-radius:8px;border:1px solid var(--accent-line);
    background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;cursor:pointer;
  }
  .send:disabled{opacity:.4;cursor:default}
  .tool-hint{font-family:var(--mono);font-size:12px;color:var(--t2);align-self:flex-start;display:flex;align-items:center;gap:8px}
  .tool-hint::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--t2);animation:pulse 1s ease-in-out infinite}

  /* TECH STACK */
  .stack{display:flex;flex-wrap:wrap;gap:10px}
  .badge{
    display:inline-flex;align-items:center;gap:10px;
    padding:10px 14px;border:1px solid var(--line-2);border-radius:10px;
    background:var(--card);font-family:var(--mono);font-size:13px;color:var(--text);
  }
  .badge .bdot{width:8px;height:8px;border-radius:2px;background:var(--t2);box-shadow:0 0 10px rgba(239,111,94,.4)}

  /* COMPLIANCE / SAFETY */
  .safety-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
  @media (max-width:900px){ .safety-grid{grid-template-columns:1fr} }
  .safety-card{
    position:relative;
    border:1px solid var(--line);border-radius:14px;background:var(--card);
    padding:28px 26px 26px;display:flex;flex-direction:column;gap:10px;
    transition:border-color .2s, transform .2s;
  }
  .safety-card:hover{border-color:rgba(239,111,94,.35);transform:translateY(-2px)}
  .safety-card .safety-ix{
    font-family:var(--mono);font-size:12px;color:var(--t2);letter-spacing:.12em;
    display:flex;align-items:center;gap:10px;
  }
  .safety-card .safety-ix::after{
    content:"";flex:1;height:1px;background:linear-gradient(90deg,rgba(239,111,94,.4),transparent);
  }
  .safety-card h3{
    margin:6px 0 4px;font-size:20px;font-weight:500;letter-spacing:-.01em;line-height:1.2;
    text-wrap:balance;
  }
  .safety-card p{margin:0;color:var(--muted);font-size:14.5px}
  .safety-card .safety-tag{
    align-self:flex-start;margin-top:auto;padding:4px 8px;border:1px solid var(--line-2);border-radius:6px;
    font-family:var(--mono);font-size:10px;letter-spacing:.12em;color:var(--muted);
  }

  /* USE CASES */
  .usecases-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
  @media (max-width:900px){ .usecases-grid{grid-template-columns:repeat(2,1fr)} }
  @media (max-width:620px){ .usecases-grid{grid-template-columns:1fr} }
  .usecase{
    position:relative;border:1px solid var(--line);border-radius:12px;background:var(--card);
    padding:22px 22px 24px;display:flex;flex-direction:column;gap:8px;
    transition:border-color .2s, transform .2s;
  }
  .usecase:hover{border-color:var(--accent-line);transform:translateY(-2px)}
  .usecase.wide{grid-column:span 2}
  @media (max-width:620px){ .usecase.wide{grid-column:auto} }
  .usecase .uc-ix{
    font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.16em;
  }
  .usecase h3{
    margin:2px 0 2px;font-size:18px;font-weight:500;letter-spacing:-.01em;line-height:1.2;text-wrap:balance;
  }
  .usecase p{margin:0;color:var(--muted);font-size:14px}

  /* PRICING */
  .pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;align-items:stretch}
  @media (max-width:900px){ .pricing-grid{grid-template-columns:1fr} }
  .price-card{
    position:relative;border:1px solid var(--line);border-radius:16px;background:var(--card);
    padding:28px 26px 28px;display:flex;flex-direction:column;gap:14px;
  }
  .price-card.featured{
    background:linear-gradient(180deg,#ffffff,#fdf6f4);
    border-color:rgba(239,111,94,.4);
    box-shadow:0 12px 36px -24px rgba(239,111,94,.4);
  }
  .price-card .price-flag{
    position:absolute;top:-12px;right:18px;
    background:var(--t2);color:#fff;font-family:var(--mono);font-size:10px;letter-spacing:.12em;
    padding:5px 10px;border-radius:999px;text-transform:uppercase;font-weight:500;
  }
  .price-card .price-tier{
    font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.14em;text-transform:uppercase;
  }
  .price-card .price-amount{
    display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;
    border-bottom:1px dashed var(--line-2);padding-bottom:14px;
  }
  .price-card .price-amount .amount{
    font-family:var(--mono);font-size:34px;letter-spacing:-.02em;font-weight:500;color:var(--text);line-height:1;
  }
  .price-card .price-amount .per{
    font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.04em;
  }
  .price-card .price-min{
    font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.08em;
  }
  .price-card .price-list{
    list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;flex:1;
  }
  .price-card .price-list li{
    font-size:14px;color:var(--text);display:flex;gap:10px;align-items:flex-start;
  }
  .price-card .price-list li::before{
    content:"";flex-shrink:0;width:14px;height:14px;margin-top:3px;border-radius:50%;
    background-color:rgba(239,111,94,.15);
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10' fill='none'><path d='M2 5l2 2 4-4' stroke='%23ef6f5e' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    background-repeat:no-repeat;background-position:center;
  }

  /* CTA */
  .cta{
    position:relative;
    border:1px solid var(--line);border-radius:18px;
    background:
      radial-gradient(800px 300px at 100% 0%, rgba(37,99,235,.10), transparent 60%),
      linear-gradient(180deg,#ffffff,#f3f2ee);
    padding:56px clamp(24px,4vw,64px);
    display:grid;grid-template-columns:1.05fr 1fr;gap:48px;align-items:start;
  }
  /* Threads (absolutely positioned) stay out of the grid flow */
  .cta > .cta-thread{grid-column:1 / -1;grid-row:1}
  @media (max-width:760px){ .cta{grid-template-columns:1fr;padding:40px clamp(20px,5vw,40px);gap:32px} }
  .cta h2{font-size:clamp(28px,4vw,44px);margin:10px 0 14px;letter-spacing:-.02em;line-height:1.05;font-weight:500}
  .cta p.lead{color:var(--muted);max-width:46ch;margin:0 0 24px;font-size:16px}

  /* "What happens next" stepper */
  .next-steps{list-style:none;padding:0;margin:24px 0 0;display:flex;flex-direction:column;gap:14px}
  .next-steps li{
    display:grid;grid-template-columns:28px 1fr;gap:14px;align-items:flex-start;
    font-size:14px;color:var(--muted);
  }
  .next-steps li b{color:var(--text);font-weight:500;display:block;margin-bottom:2px}
  .next-steps li .ix{
    width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
    border:1px solid var(--line-2);background:#fff;
    font-family:var(--mono);font-size:11px;color:var(--t2);font-weight:500;
  }

  /* Demo form */
  .demo-form{
    background:#fff;border:1px solid var(--line);border-radius:14px;
    padding:28px clamp(20px,3vw,32px);display:flex;flex-direction:column;gap:14px;
    box-shadow:0 1px 0 rgba(0,0,0,.02), 0 24px 48px -32px rgba(15,15,20,.18);
  }
  .demo-form .form-head{
    display:flex;align-items:center;justify-content:space-between;gap:14px;
    border-bottom:1px dashed var(--line-2);padding-bottom:14px;margin-bottom:4px;
  }
  .demo-form .form-head .title{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
  .demo-form .form-head .meta{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.08em}
  .demo-form .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  @media (max-width:520px){ .demo-form .row{grid-template-columns:1fr} }
  .demo-form .field{display:flex;flex-direction:column;gap:6px;min-width:0}
  .demo-form label{
    font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted-2);
  }
  .demo-form label .req{color:var(--t2);margin-left:4px}
  .demo-form input,
  .demo-form select,
  .demo-form textarea{
    appearance:none;-webkit-appearance:none;
    font:inherit;font-size:14.5px;color:var(--text);
    background:#fafaf6;border:1px solid var(--line);border-radius:8px;
    padding:10px 12px;outline:none;width:100%;
    transition:border-color .15s, background .15s, box-shadow .15s;
  }
  .demo-form input:focus,
  .demo-form select:focus,
  .demo-form textarea:focus{
    border-color:var(--t2);background:#fff;
    box-shadow:0 0 0 4px rgba(239,111,94,.14);
  }
  .demo-form textarea{min-height:84px;resize:vertical;line-height:1.45}
  .demo-form select{background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6' fill='none'><path d='M1 1l4 4 4-4' stroke='%236a6a72' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/></svg>");background-repeat:no-repeat;background-position:right 12px center;padding-right:32px}
  .demo-form .actions{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-top:6px;flex-wrap:wrap}
  .demo-form .submit{
    display:inline-flex;align-items:center;gap:10px;
    background:var(--t2);color:#fff;border:1px solid var(--t2);
    border-radius:10px;padding:13px 20px;font-size:14px;font-weight:600;
    cursor:pointer;transition:transform .15s ease, background .2s;
  }
  .demo-form .submit:hover{background:#d85a4a;border-color:#d85a4a;transform:translateY(-1px)}
  .demo-form .fineprint{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.04em}
  .demo-form .fineprint b{color:var(--text);font-weight:500}

  /* Success state */
  .demo-form.is-sent .form-body{display:none}
  .demo-form .form-success{display:none}
  .demo-form.is-sent .form-success{
    display:flex;flex-direction:column;gap:14px;align-items:flex-start;
    padding:8px 0 6px;
  }
  .demo-form .form-success .ok{
    display:inline-flex;align-items:center;gap:10px;
    font-family:var(--mono);font-size:12px;color:var(--good);letter-spacing:.08em;text-transform:uppercase;
  }
  .demo-form .form-success .ok::before{
    content:"";width:18px;height:18px;border-radius:50%;
    background:var(--good);
    -webkit-mask:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 18 18' fill='none'><path d='M4 9l3.5 3.5L14 6' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>") center/contain no-repeat;
            mask:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 18 18' fill='none'><path d='M4 9l3.5 3.5L14 6' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>") center/contain no-repeat;
    background:var(--good);
  }
  .demo-form .form-success h3{font-size:22px;margin:0;font-weight:500;letter-spacing:-.01em}
  .demo-form .form-success p{margin:0;color:var(--muted);max-width:42ch;font-size:14.5px}
  .demo-form .form-success .receipt{
    font-family:var(--mono);font-size:11.5px;color:var(--muted-2);letter-spacing:.04em;
    border-top:1px dashed var(--line-2);padding-top:12px;margin-top:8px;width:100%;
    display:grid;grid-template-columns:auto 1fr;gap:4px 14px;
  }
  .demo-form .form-success .receipt b{color:var(--text);font-weight:500}

  /* FOOTER */
  footer{padding:36px 0 56px;color:var(--muted-2);border-top:1px solid var(--line);margin-top:60px}
  .foot{display:flex;justify-content:space-between;align-items:center;font-family:var(--mono);font-size:12px;flex-wrap:wrap;gap:16px}

  /* misc */
  .ticker{
    border-top:1px solid var(--line);border-bottom:1px solid var(--line);
    overflow:hidden;white-space:nowrap;font-family:var(--mono);font-size:12px;color:var(--muted);
    background:#f3f2ee;
  }
  .ticker-track{display:inline-flex;gap:40px;padding:12px 0;animation:scroll 40s linear infinite}
  .ticker-track span{display:inline-flex;align-items:center;gap:10px}
  .ticker-track span::before{content:"●";color:var(--accent);font-size:8px}
  @keyframes scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}

  /* Logo mark */
  .logo-svg{width:100%;height:100%;display:block}

  /* ============================================================
     THREAD MOTIF — coloured threads weaving through the page
     ============================================================ */
  :root{
    --t1:#2563eb;  /* indigo / accent */
    --t2:#ef6f5e;  /* coral   */
    --t3:#e9a23b;  /* saffron */
    --t4:#0fa18a;  /* teal    */
    --t5:#9333ea;  /* purple  */
  }
  /* containers that anchor thread overlays */
  .hero, section, .pipeline, .dash, .cta, .participant-head, .account{position:relative}
  /* always keep real content above thread layers */
  .hero > .wrap, section > .wrap{position:relative;z-index:2}

  /* shared overlay surface */
  .thread-layer{position:absolute;inset:0;pointer-events:none;z-index:0;overflow:visible}
  .thread-layer svg{width:100%;height:100%;display:block;overflow:visible}
  .t{fill:none;stroke-linecap:round;stroke-linejoin:round}
  .knot{stroke:none}

  /* section seams now host real curving threads, not dashed strokes */
  section{border-top:none}
  .seam{
    position:absolute;left:-40px;right:-40px;top:-48px;height:96px;
    pointer-events:none;z-index:3;overflow:visible;
  }
  .seam svg{width:100%;height:100%;display:block;overflow:visible}

  /* HERO — one continuous thread layer wrapping the heading
     in a C-shape (top + right + bottom) so the three regions read as one. */
  .hero-threads{
    position:absolute;left:0;right:0;pointer-events:none;z-index:0;overflow:visible;
  }
  .hero-threads.frame{inset:0}
  .hero-threads svg{width:100%;height:100%;display:block;overflow:visible}

  /* PIPELINE — wavy threads visible only between cards */
  .pipeline-thread{
    position:absolute;left:-40px;right:-40px;top:50%;transform:translateY(-50%);
    height:160px;pointer-events:none;z-index:0;
  }
  .pipeline-thread svg{width:100%;height:100%;display:block;overflow:visible}
  /* step cards stay opaque so they cover the wavy threads except at gaps */
  .step{background:var(--card);z-index:1}

  /* PARTICIPANT — woven thread along the left edge of the header card */
  .participant-head{padding-left:34px !important}
  .participant-thread{
    position:absolute;top:10px;bottom:10px;left:12px;width:4px;border-radius:3px;
    background:linear-gradient(180deg,var(--t1) 0%,var(--t2) 25%,var(--t3) 50%,var(--t4) 75%,var(--t5) 100%);
    opacity:.9;
  }

  /* CTA — corner thread loops, top + bottom bands */
  .cta-thread{position:absolute;left:0;right:0;pointer-events:none;z-index:0;overflow:visible}
  .cta-thread.top{top:0;height:48px}
  .cta-thread.bottom{bottom:0;height:48px}
  .cta-thread svg{width:100%;height:100%;display:block;overflow:visible}
  .cta > *{position:relative;z-index:1}
  .cta{overflow:visible}

  /* generic thread band layer (top / bottom of each section) */
  .section-threads{
    position:absolute;left:-30px;right:-30px;pointer-events:none;z-index:0;overflow:visible;
  }
  .section-threads.top{top:0;height:96px}
  .section-threads.bottom{bottom:0;height:96px}
  .section-threads svg{width:100%;height:100%;display:block;overflow:visible}

  /* ---- ANIMATION ----
     Layer-level drift + per-path sway. Bigger amplitudes so the motion reads. */
  @keyframes drift-a {
    0%, 100% { transform: translate3d(-90px, -6px, 0); }
    50%      { transform: translate3d( 90px,  6px, 0); }
  }
  @keyframes drift-b {
    0%, 100% { transform: translate3d( 100px,  8px, 0); }
    50%      { transform: translate3d(-100px, -8px, 0); }
  }
  @keyframes drift-c {
    0%, 100% { transform: translate3d(-70px,  10px, 0); }
    50%      { transform: translate3d( 80px, -10px, 0); }
  }
  /* Sway: individual thread paths translate vertically a few px, so threads
     weave past each other within a layer rather than moving as one block. */
  @keyframes sway-a { 0%,100%{transform:translate(0, -4px)} 50%{transform:translate(0, 4px)} }
  @keyframes sway-b { 0%,100%{transform:translate(0,  5px)} 50%{transform:translate(0,-5px)} }
  @keyframes sway-c { 0%,100%{transform:translate(0, -6px)} 50%{transform:translate(0, 6px)} }
  @keyframes sway-d { 0%,100%{transform:translate(0,  3px)} 50%{transform:translate(0,-3px)} }
  @keyframes sway-e { 0%,100%{transform:translate(0, -5px)} 50%{transform:translate(0, 5px)} }

  .hero-threads svg, .section-threads svg, .pipeline-thread svg,
  .cta-thread svg, .seam svg{
    transform-origin: center;
    will-change: transform;
  }
  /* layer-level horizontal drift */
  .hero-threads.frame svg     { animation: drift-a 14s ease-in-out infinite; }
  .section-threads.top svg   { animation: drift-b 10s ease-in-out infinite; }
  .section-threads.bottom svg{ animation: drift-c 12s ease-in-out infinite; }
  .cta-thread.top svg        { animation: drift-c 8s  ease-in-out infinite; }
  .cta-thread.bottom svg     { animation: drift-a 9s  ease-in-out infinite; }
  .pipeline-thread svg       { animation: drift-b 13s ease-in-out infinite; }
  .seam svg                  { animation: drift-c 7s  ease-in-out infinite; }

  /* per-path sway — different speeds + phases so threads cross over each other */
  .hero-threads .t:nth-child(1), .section-threads .t:nth-child(1),
  .pipeline-thread .t:nth-child(1), .cta-thread .t:nth-child(1),
  .seam .t:nth-child(1){ animation: sway-a 6s ease-in-out infinite; }
  .hero-threads .t:nth-child(2), .section-threads .t:nth-child(2),
  .pipeline-thread .t:nth-child(2), .cta-thread .t:nth-child(2),
  .seam .t:nth-child(2){ animation: sway-b 7s ease-in-out -2s infinite; }
  .hero-threads .t:nth-child(3), .section-threads .t:nth-child(3),
  .pipeline-thread .t:nth-child(3), .cta-thread .t:nth-child(3),
  .seam .t:nth-child(3){ animation: sway-c 5s ease-in-out -1s infinite; }
  .hero-threads .t:nth-child(4), .section-threads .t:nth-child(4),
  .pipeline-thread .t:nth-child(4), .cta-thread .t:nth-child(4),
  .seam .t:nth-child(4){ animation: sway-d 8s ease-in-out -3s infinite; }
  .hero-threads .t:nth-child(5), .section-threads .t:nth-child(5),
  .pipeline-thread .t:nth-child(5), .cta-thread .t:nth-child(5),
  .seam .t:nth-child(5){ animation: sway-e 4s ease-in-out -2s infinite; }

</style>
</head>
<body>

<nav class="top">
  <div class="wrap nav-inner">
    <a href="#" class="brand">
      <span class="logo">
        <!-- THREADY mark: loom warp turned into chart gridlines, threads = data lines -->
        <svg class="logo-svg" viewBox="0 0 36 24" fill="none" aria-hidden="true"
             stroke-linecap="round" stroke-linejoin="round">
          <!-- ascending data threads -->
          <!-- many thin threads weaving across the mark, with HORIZONTAL tangents
               at both ends so nothing curls up/down at the edges -->
          <path d="M 2 7  C 10 7, 14 14, 18 14 C 22 14, 30 4,  34 4"
                stroke="#2563eb" stroke-width="1.1"/>
          <path d="M 2 12 C 10 12, 14 4,  18 4  C 22 4,  30 16, 34 16"
                stroke="#ef6f5e" stroke-width="1.1"/>
          <path d="M 2 17 C 10 17, 14 10, 18 10 C 22 10, 30 20, 34 20"
                stroke="#e9a23b" stroke-width="1.1"/>
          <path d="M 2 4  C 10 4,  14 18, 22 18 C 28 18, 30 8,  34 8"
                stroke="#0fa18a" stroke-width="1"/>
          <path d="M 2 20 C 10 20, 14 8,  22 8  C 28 8,  30 18, 34 18"
                stroke="#9333ea" stroke-width="1"/>
          <path d="M 2 14 C 10 14, 14 6,  18 6  C 22 6,  30 14, 34 14"
                stroke="#2563eb" stroke-width=".9" stroke-opacity=".7"/>
          <path d="M 2 10 C 10 10, 14 20, 18 20 C 22 20, 30 6,  34 6"
                stroke="#ef6f5e" stroke-width=".9" stroke-opacity=".7"/>
        </svg>
      </span>
      <span>THREADY</span>
    </a>
    <div class="nav-links">
      <a href="#how">Workflow</a>
      <a href="#compliance">Safety</a>
      <a href="#metrics">Analytics</a>
      <a href="#accounts">Reference</a>
      <a href="#use-cases">Use cases</a>
      <a href="#pricing">Pricing</a>
    </div>
    <a href="#contact" class="nav-cta">Request pilot access ↗</a>
  </div>
</nav>

<!-- HERO -->
<header class="hero">
  <div class="hero-threads full" aria-hidden="true">
    <svg viewBox="0 0 1200 720" preserveAspectRatio="none">
      <path class="t" stroke="var(--t2)" stroke-width="1.4" vector-effect="non-scaling-stroke"
            d="M-40 60  C 240 30,  500 100, 760 50  S 1040 120, 1240 70"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".9"
            d="M-40 140 C 260 100, 540 180, 780 130 S 1080 80,  1240 150"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 230 C 220 280, 520 180, 760 240 S 1080 300, 1240 220"/>
      <path class="t" stroke="var(--t5)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 320 C 260 280, 540 380, 780 320 S 1080 260, 1240 340"/>
      <path class="t" stroke="var(--t1)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".9"
            d="M-40 410 C 240 460, 540 360, 800 420 S 1080 480, 1240 400"/>
      <path class="t" stroke="var(--t2)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".82"
            d="M-40 500 C 260 460, 540 540, 800 500 S 1080 440, 1240 520"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 590 C 240 640, 540 540, 800 600 S 1080 660, 1240 580"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 670 C 260 630, 540 700, 800 660 S 1080 620, 1240 700"/>
      <path class="t" stroke="var(--t3)" stroke-width="1"   vector-effect="non-scaling-stroke" opacity=".5"
            d="M-40 380 C 240 220, 480 460, 760 320 S 1080 580, 1240 420"/>
      <path class="t" stroke="var(--t2)" stroke-width=".95" vector-effect="non-scaling-stroke" opacity=".5"
            d="M-40 180 C 260 320, 520 80,  800 240 S 1080 420, 1240 200"/>
      <path class="t" stroke="var(--t4)" stroke-width="1"   vector-effect="non-scaling-stroke" opacity=".7"
            d="M120 30 C 240 80, 400 0, 540 60"/>
      <path class="t" stroke="var(--t5)" stroke-width="1"   vector-effect="non-scaling-stroke" opacity=".65"
            d="M700 690 C 820 660, 980 720, 1100 680"/>
      <path class="t" stroke="var(--t1)" stroke-width=".9"  vector-effect="non-scaling-stroke" opacity=".6"
            d="M40 460 C 160 420, 280 500, 380 460"/>
    </svg>
  </div>

  <div class="scatter" aria-hidden="false">
    <span class="sw"        style="top:8%;  left:6%;  font-size:clamp(48px,8vw,108px);transform:rotate(-2.5deg)">Autonomous</span>
    <span class="sw tw tw-a" style="top:22%; left:46%; font-size:clamp(42px,7vw,92px); transform:rotate(1.5deg)">posting</span>
    <span class="sw small"  style="top:36%; left:14%; font-size:clamp(20px,2vw,28px); transform:rotate(-3deg);color:var(--muted)">for</span>
    <span class="sw tw tw-c"  style="top:38%; left:24%; font-size:clamp(54px,9vw,118px);transform:rotate(2deg)">Threads</span>
    <span class="sw small"  style="top:60%; left:68%; font-size:clamp(22px,2.2vw,30px);transform:rotate(-1deg);color:var(--muted)">at the</span>
    <span class="sw"        style="top:66%; left:8%;  font-size:clamp(40px,6.4vw,86px);transform:rotate(-1.5deg)">scale of a</span>
    <span class="sw tw tw-b" style="top:78%; left:46%; font-size:clamp(46px,7.6vw,100px);transform:rotate(2.5deg)">newsroom</span>
  </div>
</header>

<section class="hero-intro">
  <div class="wrap intro-grid">
    <div class="intro-copy">
      <span class="pill"><span class="dot"></span> Live · 14 accounts · 400K views/month · Official API</span>
      <p class="hero-sub">
        AI-generated content with approval workflows, unified analytics and white-label reporting —
        built for agencies and brand teams managing dozens of accounts.
        We run 14 production accounts in four languages on the official Threads API, before we sell you anything.
      </p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#contact">Request pilot access →</a>
        <a class="btn btn-ghost" href="#contact">Book a 20-min demo</a>
      </div>
    </div>

    <aside class="hero-panel" aria-label="Headline metrics">
      <div class="hero-panel-head">
        <span>Portfolio · last 30 days</span>
        <span>● live</span>
      </div>
      <div class="kpi">
        <div class="cell">
          <div class="label">Views</div>
          <div class="num">400K<span class="unit">/ 30d</span></div>
          <div class="delta">▲ across 14 accounts</div>
        </div>
        <div class="cell">
          <div class="label">Posts published</div>
          <div class="num">12.6K<span class="unit">/ 30d</span></div>
          <div class="delta">~30 / account / day</div>
        </div>
        <div class="cell">
          <div class="label">Active accounts</div>
          <div class="num">14<span class="unit">across 4 langs</span></div>
          <div class="delta">EN · RU · ES · PT</div>
        </div>
        <div class="cell">
          <div class="label">Operators</div>
          <div class="num">4<span class="unit">participants</span></div>
          <div class="delta">Budimir · Slava · Tanya · Chiara</div>
        </div>
      </div>
    </aside>
  </div>
</section>

<!-- HOW IT WORKS -->
<section id="how"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t2)" stroke-width="1.6" vector-effect="non-scaling-stroke"
            d="M-40 60 C 150 30, 280 80, 420 40 S 700 90, 860 30 S 1140 80, 1260 50"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 50 C 200 80, 360 20, 540 60 S 820 20, 1020 70 S 1200 30, 1260 40"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 38 C 180 60, 340 28, 520 44 S 800 60, 1100 36 S 1240 50, 1260 46"/>
    </svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">01 · Workflow</span>
        <h2>Five steps from client onboarding<br/>to monthly report.</h2>
      </div>
      <p>Configure once, then Thready runs the loop — with your approval gates wherever you want them.</p>
    </div>

    <div class="pipeline">
      <div class="pipeline-thread" aria-hidden="true">
        <svg viewBox="0 0 1200 160" preserveAspectRatio="none">
          <path class="t" stroke="var(--t2)" stroke-width="2"
                vector-effect="non-scaling-stroke"
                d="M-40 80 C 100 20, 230 140, 360 80 S 620 20, 760 80 S 1020 140, 1240 80"/>
          <path class="t" stroke="var(--t4)" stroke-width="1.5" opacity=".85"
                vector-effect="non-scaling-stroke"
                d="M-40 90 C 100 150, 230 30, 360 90 S 620 150, 760 90 S 1020 30, 1240 90"/>
          <path class="t" stroke="var(--t3)" stroke-width="1.4" opacity=".8"
                vector-effect="non-scaling-stroke"
                d="M-40 70 C 120 110, 260 50, 400 100 S 660 50, 820 110 S 1080 50, 1240 100"/>
          <path class="t" stroke="var(--t5)" stroke-width="1.3" opacity=".75"
                vector-effect="non-scaling-stroke"
                d="M-40 100 C 140 50, 300 130, 460 70 S 700 130, 880 70 S 1080 130, 1240 70"/>
          <path class="t" stroke="var(--t1)" stroke-width="1.2" opacity=".7"
                vector-effect="non-scaling-stroke"
                d="M-40 60 C 160 130, 320 30, 480 80 S 720 30, 900 90 S 1100 30, 1240 80"/>
        </svg>
      </div>
      <article class="step">
        <div class="ix">STEP 01 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <path d="M28 8l16 8v12c0 12-8 18-16 20-8-2-16-8-16-20V16l16-8z" stroke="#ef6f5e" stroke-width="1.4"/>
            <path d="M20 28l6 6 12-12" stroke="#0e0e10" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>
          </svg>
        </div>
        <h3>Configure</h3>
        <p>Per-client workspace with brand voice, niche, cadence, language, blocklists and topic guardrails. Onboard a new account in under 30 minutes.</p>
        <ul>
          <li>Custom prompts per client</li>
          <li>Blocklists &amp; topic bounds</li>
          <li>Per-timezone schedule</li>
        </ul>
      </article>

      <article class="step">
        <div class="ix">STEP 02 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <rect x="6" y="10" width="44" height="36" rx="6" stroke="#ef6f5e" stroke-width="1.4"/>
            <path d="M14 20h28M14 27h20M14 34h24" stroke="#0e0e10" stroke-width="1.2" stroke-linecap="round" opacity=".55"/>
            <circle cx="46" cy="10" r="4" fill="#ef6f5e"/>
          </svg>
        </div>
        <h3>Generate</h3>
        <p>Cerebras-hosted LLM produces drafts tuned to each client's voice. Sub-second generation — queued for review, or auto-published. Your call.</p>
        <ul>
          <li>Voice-trained per client</li>
          <li>Style + topic guardrails</li>
          <li>~1s per draft</li>
        </ul>
      </article>

      <article class="step">
        <div class="ix">STEP 03 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <path d="M10 28l6 6 12-12 12 12 6-6" stroke="#ef6f5e" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="46" cy="22" r="3" fill="#ef6f5e"/>
            <circle cx="22" cy="34" r="3" fill="#0fa18a"/>
          </svg>
        </div>
        <h3>Approve <span style="color:var(--muted-2);font-weight:400;font-size:13px">— or auto-publish</span></h3>
        <p>Optional per-client approval queue. Bulk-approve, edit, reject, or hand control to your client. Skip entirely for handles you trust to run on their own.</p>
        <ul>
          <li>Human-in-the-loop, opt-in</li>
          <li>Client-facing approval UI</li>
          <li>Auto-publish per client</li>
        </ul>
      </article>

      <article class="step">
        <div class="ix">STEP 04 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="20" stroke="#ef6f5e" stroke-width="1.4"/>
            <path d="M28 14v14l9 6" stroke="#0e0e10" stroke-width="1.4" stroke-linecap="round"/>
            <circle cx="28" cy="28" r="2" fill="#ef6f5e"/>
          </svg>
        </div>
        <h3>Publish</h3>
        <p>Direct via the official Threads API. Per-timezone scheduling, automatic retries, delivery confirmation. No browser automation, no fragile workarounds.</p>
        <ul>
          <li>Official Meta API</li>
          <li>Retries &amp; backoff</li>
          <li>Delivery confirmation</li>
        </ul>
      </article>

      <article class="step">
        <div class="ix">STEP 05 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <path d="M6 44h44" stroke="#0e0e10" stroke-width="1.2" opacity=".55"/>
            <path d="M10 40l10-14 10 8 10-18 8 12" stroke="#ef6f5e" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="48" cy="28" r="3" fill="#ef6f5e"/>
          </svg>
        </div>
        <h3>Report</h3>
        <p>Per-client dashboards, ready to share. Views, engagement, follower growth, top posts — packaged for white-label client reporting or piped into your BI.</p>
        <ul>
          <li>White-label exports</li>
          <li>SQL / BI access</li>
          <li>Monthly executive PDF</li>
        </ul>
      </article>
    </div>
  </div>
    <div class="section-threads bottom" aria-hidden="true">
      <svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t2)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 50 C 200 20, 420 80, 640 40 S 940 80, 1240 50"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 30 C 220 70, 420 10, 620 40 S 880 10, 1240 30"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 70 C 240 30, 480 80, 720 50 S 1000 80, 1240 70"/>
      <path class="t" stroke="var(--t1)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".65"
            d="M-40 16 C 200 60, 420 0, 660 30 S 940 60, 1240 16"/>
      <path class="t" stroke="var(--t5)" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".55"
            d="M-40 84 C 180 50, 380 86, 580 70 S 900 86, 1240 80"/>
    </svg>
    </div>
  </section>


<!-- COMPLIANCE / SAFETY -->
<section id="compliance"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none"><path class="t" stroke="var(--t1)" stroke-width="1.5" vector-effect="non-scaling-stroke" d="M-40 44 C 140 80, 320 24, 520 60 S 820 22, 1040 64 S 1200 30, 1260 50"/>
        <path class="t" stroke="var(--t5)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85" d="M-40 60 C 180 32, 380 84, 560 44 S 860 84, 1080 36 S 1240 62, 1260 56"/>
        <path class="t" stroke="var(--t3)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7" d="M-40 30 C 200 70, 420 22, 640 60 S 880 24, 1100 52 S 1240 28, 1260 34"/></svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">02 · Compliance &amp; safety</span>
        <h2>Built to keep your clients' accounts safe.</h2>
      </div>
      <p>Account safety matters more than content quality. Three things we get right — by design, not by promise.</p>
    </div>

    <div class="safety-grid">
      <article class="safety-card">
        <div class="safety-ix">01</div>
        <h3>Official Threads API only.</h3>
        <p>No browser automation, no headless scraping, no ToS gray areas. If Meta ships it, we use it; if they don't, we don't.</p>
        <span class="safety-tag">META API</span>
      </article>
      <article class="safety-card">
        <div class="safety-ix">02</div>
        <h3>Content guardrails per client.</h3>
        <p>Blocklists, topic constraints, tone bounds and approval gates — catch issues before they go live, not after.</p>
        <span class="safety-tag">PER-CLIENT</span>
      </article>
      <article class="safety-card">
        <div class="safety-ix">03</div>
        <h3>Full audit trail.</h3>
        <p>Every post logged with prompt, draft, edit history and publish timestamp. Defensible for compliance reviews and client post-mortems.</p>
        <span class="safety-tag">AUDITABLE</span>
      </article>
    </div>
  </div>
  <div class="section-threads bottom" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none"><path class="t" stroke="var(--t5)" stroke-width="1.5" vector-effect="non-scaling-stroke" d="M-40 60 C 200 24, 420 80, 640 50 S 940 80, 1240 60"/>
       <path class="t" stroke="var(--t2)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85" d="M-40 30 C 220 70, 420 14, 620 44 S 880 80, 1240 30"/>
       <path class="t" stroke="var(--t4)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75" d="M-40 18 C 240 60, 480 12, 720 40 S 1000 60, 1240 18"/></svg></div>
</section>

<!-- METRICS / DASHBOARD -->
<section id="metrics"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t5)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 44 C 140 80, 320 24, 520 60 S 820 22, 1040 64 S 1200 30, 1260 50"/>
      <path class="t" stroke="var(--t1)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".8"
            d="M-40 60 C 180 32, 380 84, 560 44 S 860 84, 1080 36 S 1240 62, 1260 56"/>
      <path class="t" stroke="var(--t2)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7"
            d="M-40 30 C 200 70, 420 22, 640 60 S 880 24, 1100 52 S 1240 28, 1260 34"/>
    </svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">03 · Live analytics</span>
        <h2>Embedded analytics your clients can actually use.</h2>
      </div>
      <p>Pre-built dashboards per client, white-labelable, with read-only access for client logins. Pull into your BI stack via SQL, or use the chat assistant for ad-hoc questions — no more Looker tickets.</p>
    </div>

    <div class="dash" role="region" aria-label="Live Analytics — embedded Superset dashboard">
      <div class="dash-bar">
        <div class="left">
          <div class="traffic"><i></i><i></i><i></i></div>
          <div class="url">analytics.thready.internal / dashboards / portfolio</div>
        </div>
        <div class="right">
          <span id="dash-time">UTC 14:02</span>
          <span class="live">LIVE</span>
        </div>
      </div>

      <div class="dash-body">
        <div class="dash-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <h4>Views — last 30 days</h4>
              <div class="big">400,357</div>
              <div class="sub">portfolio total, 14 accounts</div>
            </div>
            <div class="legend">
              <span class="a"><i></i>Budimir</span>
              <span class="b"><i style="background:#e9a23b"></i>Slava · Tanya · Chiara</span>
            </div>
          </div>

          <!-- Stacked area chart -->
          <svg class="chart" viewBox="0 0 600 200" preserveAspectRatio="none" style="margin-top:14px">
            <defs>
              <linearGradient id="ga" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stop-color="#ef6f5e" stop-opacity=".30"/>
                <stop offset="1" stop-color="#ef6f5e" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="gb" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stop-color="#e9a23b" stop-opacity=".30"/>
                <stop offset="1" stop-color="#e9a23b" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <!-- grid -->
            <g stroke="#e6e4de" stroke-width="1">
              <line x1="0" y1="40" x2="600" y2="40"/>
              <line x1="0" y1="90" x2="600" y2="90"/>
              <line x1="0" y1="140" x2="600" y2="140"/>
              <line x1="0" y1="190" x2="600" y2="190"/>
            </g>
            <!-- series B (Slava, smaller, behind) -->
            <path d="M0 170 L40 165 L80 168 L120 160 L160 158 L200 150 L240 152 L280 145 L320 140 L360 138 L400 132 L440 130 L480 124 L520 120 L560 118 L600 112 L600 200 L0 200 Z" fill="url(#gb)"/>
            <path d="M0 170 L40 165 L80 168 L120 160 L160 158 L200 150 L240 152 L280 145 L320 140 L360 138 L400 132 L440 130 L480 124 L520 120 L560 118 L600 112" stroke="#e9a23b" stroke-width="1.4" fill="none"/>
            <!-- series A (Budimir, big, front) -->
            <path d="M0 140 L40 130 L80 132 L120 120 L160 110 L200 112 L240 96 L280 92 L320 78 L360 80 L400 64 L440 60 L480 52 L520 46 L560 40 L600 30 L600 200 L0 200 Z" fill="url(#ga)"/>
            <path d="M0 140 L40 130 L80 132 L120 120 L160 110 L200 112 L240 96 L280 92 L320 78 L360 80 L400 64 L440 60 L480 52 L520 46 L560 40 L600 30" stroke="#ef6f5e" stroke-width="1.6" fill="none"/>
          </svg>

          <!-- x labels -->
          <div class="mono" style="display:flex;justify-content:space-between;color:var(--muted-2);font-size:10px;margin-top:6px;letter-spacing:.08em">
            <span>APR 16</span><span>APR 22</span><span>APR 28</span><span>MAY 04</span><span>MAY 10</span><span>MAY 16</span>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:18px">
          <div class="dash-card">
            <h4>Top account · views / 30d</h4>
            <!-- horizontal bars -->
            <div style="display:flex;flex-direction:column;gap:10px;margin-top:14px;font-family:var(--mono);font-size:12px">
              <div>
                <div style="display:flex;justify-content:space-between"><span>mind_the_tap</span><span>100.5K</span></div>
                <div style="height:6px;background:#ece9e0;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:100%;height:100%;background:linear-gradient(90deg,#ef6f5e,#d85a4a)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>event_parsing</span><span>51.3K</span></div>
                <div style="height:6px;background:#ece9e0;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:51%;height:100%;background:linear-gradient(90deg,#ef6f5e,#d85a4a)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>cycling_superhero</span><span>44.6K</span></div>
                <div style="height:6px;background:#ece9e0;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:44%;height:100%;background:linear-gradient(90deg,#ef6f5e,#d85a4a)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>saas.memo</span><span>42.7K</span></div>
                <div style="height:6px;background:#ece9e0;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:42%;height:100%;background:linear-gradient(90deg,#ef6f5e,#d85a4a)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>claude_space</span><span>35.1K</span></div>
                <div style="height:6px;background:#ece9e0;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:35%;height:100%;background:linear-gradient(90deg,#ef6f5e,#d85a4a)"></div></div>
              </div>
            </div>
          </div>

          <div class="row-2">
            <div class="dash-card">
              <h4>Replies · 30d</h4>
              <div class="big">457</div>
              <div class="sub">peak: <b style="color:var(--text)">@cycling_superhero</b> · 230</div>
            </div>
            <div class="dash-card">
              <h4>New followers</h4>
              <div class="big" style="color:var(--good)">+195</div>
              <div class="sub">across 14 accounts · 30d</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
    <div class="section-threads bottom" aria-hidden="true">
      <svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t4)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 36 C 200 76, 420 12, 640 48 S 940 12, 1240 40"/>
      <path class="t" stroke="var(--t5)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 60 C 220 24, 420 76, 620 44 S 880 80, 1240 56"/>
      <path class="t" stroke="var(--t2)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 22 C 240 64, 480 6, 720 36 S 1000 64, 1240 22"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".65"
            d="M-40 78 C 200 42, 420 84, 660 60 S 940 84, 1240 78"/>
      <path class="t" stroke="var(--t1)" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".55"
            d="M-40 50 C 180 14, 380 70, 580 40 S 900 70, 1240 50"/>
    </svg>
    </div>
  </section>

<!-- ACCOUNTS -->
<section id="accounts"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t4)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 56 C 200 26, 380 80, 600 36 S 880 80, 1080 30 S 1240 60, 1260 48"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 40 C 160 78, 340 28, 520 64 S 800 18, 1020 56 S 1200 30, 1260 38"/>
      <path class="t" stroke="var(--t2)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7"
            d="M-40 70 C 220 40, 400 82, 580 48 S 860 82, 1080 50 S 1240 70, 1260 64"/>
    </svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">04 · Reference portfolio</span>
        <h2>We operate our own portfolio,<br/>so you don’t have to test on production.</h2>
      </div>
      <p>Fourteen live accounts across four languages, four operators, six distinct content niches — continuous. Numbers below are real workloads, not curated demos. Want benchmarks in your client’s vertical? We’ll spin up a test account during the pilot.</p>
    </div>

    <!-- Participants & accounts -->
    <div class="accounts">
      <div class="participant-head"><div class="participant-thread" aria-hidden="true"></div>
        <div class="who">
          <div class="avatar">B</div>
          <div>
            <div style="font-family:var(--mono);font-weight:500">Budimir</div>
            <div style="color:var(--muted);font-size:12.5px">Participant · 6 accounts</div>
          </div>
        </div>
        <div class="meta">
          <span>VIEWS / 30D · <b>266,958</b></span>
          <span>POSTS / DAY · <b>~180</b></span>
        </div>
      </div>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>mind_the_tap</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">London — cafés, pubs, neighbourhoods.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">100.5K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+70</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,19 20,18 30,17 40,16 50,12 60,8  70,6 80,4" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>event_parsing</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">AI & tech news, a sharper take.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">51.3K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+8</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,18 20,17 30,14 40,15 50,11 60,9  70,7 80,4" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>cycling_superhero</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">Cycling — training, races, gear.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">44.6K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+11</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,22 10,21 20,18 30,16 40,14 50,12 60,10 70,8 80,6" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>claude_space</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Daily life with Claude.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">35.1K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+9</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,21 10,19 20,17 30,18 40,14 50,12 60,10 70,8 80,6" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>budeschka</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Surreal microfiction.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">17.9K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+17</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,18 10,16 20,12 30,15 40,11 50,13 60,9  70,11 80,7" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>aire.porteno</div>
          <span class="lang">ES</span>
        </div>
        <div class="niche">Buenos Aires — cafés &amp; spaces.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">17.6K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+18</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,18 20,17 30,14 40,15 50,11 60,9  70,7 80,4" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
    </div>

    <div class="accounts" style="margin-top:32px">
      <div class="participant-head"><div class="participant-thread" aria-hidden="true"></div>
        <div class="who">
          <div class="avatar">S</div>
          <div>
            <div style="font-family:var(--mono);font-weight:500">Slava</div>
            <div style="color:var(--muted);font-size:12.5px">Participant · 4 accounts</div>
          </div>
        </div>
        <div class="meta">
          <span>VIEWS / 30D · <b>102,681</b></span>
          <span>POSTS / DAY · <b>~120</b></span>
        </div>
      </div>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>saas.memo</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">SaaS humour, founder tropes, deadpan one-liners.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">42.7K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+2</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,18 20,17 30,14 40,15 50,11 60,9  70,7 80,4" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>giraffe.from.mobile</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Turning 30 — observations, small panics, jokes.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">26.9K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+3</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,21 10,19 20,17 30,18 40,14 50,12 60,10 70,8 80,6" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>tiger.on.remote</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">A student lampoons his friends’ startups.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">21.0K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+1</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,22 10,21 20,18 30,16 40,14 50,12 60,10 70,8 80,6" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>slow.routes.in.head</div>
          <span class="lang">ES</span>
        </div>
        <div class="niche">Remote work, slow living, async culture.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">12.1K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+3</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,18 10,16 20,12 30,15 40,11 50,13 60,9  70,11 80,7" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
    </div>

    <div class="accounts" style="margin-top:32px">
      <div class="participant-head"><div class="participant-thread" aria-hidden="true"></div>
        <div class="who">
          <div class="avatar">T</div>
          <div>
            <div style="font-family:var(--mono);font-weight:500">Tanya</div>
            <div style="color:var(--muted);font-size:12.5px">Participant · 3 accounts · new, 4–5 days of data</div>
          </div>
        </div>
        <div class="meta">
          <span>VIEWS / 30D · <b>10,707</b></span>
          <span>POSTS / DAY · <b>~30</b></span>
        </div>
      </div>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>pao.e.mar</div>
          <span class="lang">PT</span>
        </div>
        <div class="niche">Rio lifestyle &mdash; beach, sun, slow rhythm.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">6.9K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+40</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,22 10,21 20,21 30,20 40,18 50,16 60,14 70,12 80,10" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>nehochu_neznau</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Late-twenties drift, in observations.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">3.2K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+2</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,21 10,20 20,20 30,19 40,18 50,16 60,12 70,9  80,5" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>trick.trend</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">Fashion &amp; culture micro-takes.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">673</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+2</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,21 10,20 20,20 30,19 40,18 50,16 60,12 70,9  80,5" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
    </div>

    <div class="accounts" style="margin-top:32px">
      <div class="participant-head"><div class="participant-thread" aria-hidden="true"></div>
        <div class="who">
          <div class="avatar">C</div>
          <div>
            <div style="font-family:var(--mono);font-weight:500">Chiara</div>
            <div style="color:var(--muted);font-size:12.5px">Participant · 1 account · new, 2 days of data</div>
          </div>
        </div>
        <div class="meta">
          <span>VIEWS / 30D · <b>20,011</b></span>
          <span>POSTS / DAY · <b>~10</b></span>
        </div>
      </div>
      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>work.with.karimi</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">Careers and work in Europe — advice, war stories.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">20.0K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">+9</span><span class="k">followers · 30d</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,22 10,21 20,21 30,20 40,18 50,16 60,14 70,12 80,10" stroke="#ef6f5e" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
    </div>
    </div>
    <div class="section-threads bottom" aria-hidden="true">
      <svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t2)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 50 C 200 20, 420 80, 640 40 S 940 80, 1240 50"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 30 C 220 70, 420 10, 620 40 S 880 10, 1240 30"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 70 C 240 30, 480 80, 720 50 S 1000 80, 1240 70"/>
      <path class="t" stroke="var(--t1)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".65"
            d="M-40 16 C 200 60, 420 0, 660 30 S 940 60, 1240 16"/>
      <path class="t" stroke="var(--t5)" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".55"
            d="M-40 84 C 180 50, 380 86, 580 70 S 900 86, 1240 80"/>
    </svg>
    </div>
  </section>


<!-- USE CASES -->
<section id="use-cases"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none"><path class="t" stroke="var(--t2)" stroke-width="1.5" vector-effect="non-scaling-stroke" d="M-40 60 C 150 30, 280 80, 420 40 S 700 90, 860 30 S 1140 80, 1260 50"/>
        <path class="t" stroke="var(--t4)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85" d="M-40 50 C 200 80, 360 20, 540 60 S 820 20, 1020 70 S 1200 30, 1260 40"/>
        <path class="t" stroke="var(--t3)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".75" d="M-40 38 C 180 60, 340 28, 520 44 S 800 60, 1100 36 S 1240 50, 1260 46"/></svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">05 · Use cases</span>
        <h2>Built for agencies and in-house teams managing&hellip;</h2>
      </div>
      <p>Five workloads we already run on our own portfolio. Bring us a sixth and we'll figure it out together.</p>
    </div>

    <div class="usecases-grid">
      <article class="usecase">
        <div class="uc-ix">01</div>
        <h3>B2B thought leadership.</h3>
        <p>Multiple executives, consistent voice, zero load on their calendars.</p>
      </article>
      <article class="usecase">
        <div class="uc-ix">02</div>
        <h3>E-commerce brand voice.</h3>
        <p>Launches, seasonal campaigns, community-style posting at volume.</p>
      </article>
      <article class="usecase">
        <div class="uc-ix">03</div>
        <h3>Multi-market campaigns.</h3>
        <p>One brand across languages and regional voices, synchronised release.</p>
      </article>
      <article class="usecase">
        <div class="uc-ix">04</div>
        <h3>Executive ghostwriting at scale.</h3>
        <p>Founders, CMOs, partners. Voice-trained per person, on their schedule.</p>
      </article>
      <article class="usecase wide">
        <div class="uc-ix">05</div>
        <h3>Research portfolios.</h3>
        <p>Spin up 20+ test accounts to A/B niche, voice and content strategy before recommending one to a client.</p>
      </article>
    </div>
  </div>
  <div class="section-threads bottom" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none"><path class="t" stroke="var(--t3)" stroke-width="1.5" vector-effect="non-scaling-stroke" d="M-40 50 C 200 80, 420 16, 640 50 S 940 80, 1240 50"/>
       <path class="t" stroke="var(--t1)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85" d="M-40 26 C 220 70, 420 10, 620 42 S 880 70, 1240 26"/>
       <path class="t" stroke="var(--t5)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75" d="M-40 70 C 240 30, 480 80, 720 50 S 1000 30, 1240 70"/></svg></div>
</section>

<!-- AI CHAT -->
<section id="assistant"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t1)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 50 C 200 80, 420 26, 620 62 S 900 22, 1100 58 S 1240 36, 1260 44"/>
      <path class="t" stroke="var(--t5)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 38 C 160 72, 360 22, 560 50 S 820 78, 1040 34 S 1200 60, 1260 52"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7"
            d="M-40 64 C 180 36, 380 80, 600 42 S 880 78, 1080 44 S 1240 64, 1260 58"/>
    </svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">06 · Assistant</span>
        <h2>A chat layer over every client’s data.</h2>
      </div>
      <p>White-label it inside your client dashboards, or use internally to skip the SQL editor. Real-time access to posts, accounts and portfolio-level metrics — in plain English.</p>
    </div>

    <div class="chat-wrap">
      <div class="chat-copy">
        <span class="mono" style="color:var(--t2);font-size:12px;letter-spacing:.1em">// QUERY THE PORTFOLIO IN PLAIN LANGUAGE</span>
        <h3>White-label it for clients, or use it internally.</h3>
        <p>Real-time read access to every post, every account, every portfolio. Ask the questions you'd otherwise file a Looker ticket for — answer in seconds, numbers attached.</p>
        <ul>
          <li>Compare engagement across our 12 fintech client accounts last week</li>
          <li>Which content cohort drove the best follower growth this month?</li>
          <li>Top 5 posts for <span style="color:var(--text)">client X</span> — ready to drop into their report</li>
          <li>Why did <span style="color:var(--text)">@client_handle</span> underperform on Tuesday?</li>
        </ul>
      </div>

      <div class="chat-ui">
        <div class="chat-head">
          <div class="who"><span class="dot"></span> Thready Assistant</div>
          <div class="meta">SESSION · 482-A · model: cerebras-llama-70b</div>
        </div>
        <div class="chat-body" id="chat-body">
          <div class="msg bot">Hi! Ask me about any account, top posts, or portfolio stats.</div>
        </div>
        <div class="chat-input">
          <input id="chat-input" placeholder="Ask about any account, post, or metric…" autocomplete="off" />
          <button class="send" id="chat-send" aria-label="send">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M4 12h16M14 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
    <div class="section-threads bottom" aria-hidden="true">
      <svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t1)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 44 C 200 80, 420 12, 640 48 S 940 80, 1240 44"/>
      <path class="t" stroke="var(--t3)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 60 C 220 24, 420 76, 620 50 S 880 24, 1240 60"/>
      <path class="t" stroke="var(--t4)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 78 C 240 40, 480 86, 720 60 S 1000 40, 1240 78"/>
      <path class="t" stroke="var(--t5)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".65"
            d="M-40 20 C 200 64, 420 8, 660 40 S 940 64, 1240 20"/>
      <path class="t" stroke="var(--t2)" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".55"
            d="M-40 36 C 180 8, 380 64, 580 32 S 900 8, 1240 36"/>
    </svg>
    </div>
  </section>

<!-- TECH STACK -->
<section id="stack"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t3)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 46 C 220 78, 420 24, 620 56 S 900 18, 1100 52 S 1240 30, 1260 40"/>
      <path class="t" stroke="var(--t2)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 60 C 180 30, 380 80, 580 44 S 840 80, 1060 40 S 1220 60, 1260 54"/>
      <path class="t" stroke="var(--t1)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7"
            d="M-40 30 C 200 64, 400 22, 600 56 S 880 24, 1080 50 S 1240 28, 1260 36"/>
    </svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">07 · Stack</span>
        <h2>Boring infrastructure where it counts. Leverage where it matters.</h2>
      </div>
      <p>Single-binary services, embedded analytics, containerized deploys. We move fast because the substrate is simple — and you don’t get paged at 2am because our queue went down.</p>
    </div>
    <div class="stack">
      <span class="badge"><span class="bdot"></span> FastAPI</span>
      <span class="badge"><span class="bdot"></span> DuckDB</span>
      <span class="badge"><span class="bdot"></span> Docker</span>
      <span class="badge"><span class="bdot"></span> Anthropic</span>
      <span class="badge"><span class="bdot"></span> Cerebras AI</span>
      <span class="badge"><span class="bdot"></span> Groq</span>
      <span class="badge"><span class="bdot"></span> Meta Threads API</span>
      <span class="badge"><span class="bdot"></span> Apache Superset</span>
    </div>
  </div>
    <div class="section-threads bottom" aria-hidden="true">
      <svg viewBox="0 0 1200 96" preserveAspectRatio="none">
      <path class="t" stroke="var(--t3)" stroke-width="1.5" vector-effect="non-scaling-stroke"
            d="M-40 50 C 200 80, 420 16, 640 50 S 940 80, 1240 50"/>
      <path class="t" stroke="var(--t1)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
            d="M-40 26 C 220 70, 420 10, 620 42 S 880 70, 1240 26"/>
      <path class="t" stroke="var(--t5)" stroke-width="1.2" vector-effect="non-scaling-stroke" opacity=".75"
            d="M-40 70 C 240 30, 480 80, 720 50 S 1000 30, 1240 70"/>
      <path class="t" stroke="var(--t2)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".65"
            d="M-40 12 C 200 56, 420 4, 660 32 S 940 56, 1240 12"/>
      <path class="t" stroke="var(--t4)" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".55"
            d="M-40 84 C 180 50, 380 88, 580 70 S 900 50, 1240 84"/>
    </svg>
    </div>
  </section>


<!-- PRICING -->
<section id="pricing"><div class="seam" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none"><path class="t" stroke="var(--t3)" stroke-width="1.5" vector-effect="non-scaling-stroke" d="M-40 46 C 220 78, 420 24, 620 56 S 900 18, 1100 52 S 1240 30, 1260 40"/>
        <path class="t" stroke="var(--t2)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85" d="M-40 60 C 180 30, 380 80, 580 44 S 840 80, 1060 40 S 1220 60, 1260 54"/>
        <path class="t" stroke="var(--t4)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".75" d="M-40 30 C 200 64, 400 22, 600 56 S 880 24, 1080 50 S 1240 28, 1260 36"/></svg></div>
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">08 · Pricing</span>
        <h2>Pricing that filters<br/>serious buyers from window-shoppers.</h2>
      </div>
      <p>Three tiers, one bill, no per-seat surprises. Volume kicks in at 20 accounts; white-label and integrations are scoped per engagement.</p>
    </div>

    <div class="pricing-grid">
      <article class="price-card">
        <div class="price-tier">Pilot</div>
        <div class="price-amount"><span class="amount">$1000</span><span class="per">/ managed account / month</span></div>
        <div class="price-min">5-account minimum</div>
        <ul class="price-list">
          <li>Official Threads API</li>
          <li>AI-generated drafts</li>
          <li>Approval queue + auto-publish</li>
          <li>Per-client analytics</li>
          <li>Email support</li>
        </ul>
        <a class="btn btn-primary" href="#contact" style="width:100%;justify-content:center">Request pilot access</a>
      </article>

      <article class="price-card featured">
        <div class="price-flag">Most agencies</div>
        <div class="price-tier">Volume</div>
        <div class="price-amount"><span class="amount">From $2500</span><span class="per">/ account / month</span></div>
        <div class="price-min">20+ accounts &middot; volume tiers</div>
        <ul class="price-list">
          <li>Everything in Pilot</li>
          <li>White-label client dashboards</li>
          <li>SQL / BI access to the warehouse</li>
          <li>Dedicated Slack channel</li>
          <li>SLA on response &amp; uptime</li>
        </ul>
        <a class="btn btn-primary" href="#contact" style="width:100%;justify-content:center">Talk to us</a>
      </article>

      <article class="price-card">
        <div class="price-tier">Enterprise</div>
        <div class="price-amount"><span class="amount">Custom</span><span class="per">quoted per engagement</span></div>
        <div class="price-min">Brand teams &middot; high volume</div>
        <ul class="price-list">
          <li>Custom integrations</li>
          <li>Dedicated infrastructure</li>
          <li>Custom voice training</li>
          <li>Onboarding by our team</li>
          <li>Quarterly business review</li>
        </ul>
        <a class="btn btn-ghost" href="#contact" style="width:100%;justify-content:center">Get a quote</a>
      </article>
    </div>
  </div>
  <div class="section-threads bottom" aria-hidden="true"><svg viewBox="0 0 1200 96" preserveAspectRatio="none"><path class="t" stroke="var(--t4)" stroke-width="1.5" vector-effect="non-scaling-stroke" d="M-40 56 C 200 26, 380 80, 600 36 S 880 80, 1080 30 S 1240 60, 1260 48"/>
       <path class="t" stroke="var(--t2)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85" d="M-40 40 C 160 78, 340 28, 520 64 S 800 18, 1020 56 S 1200 30, 1260 38"/>
       <path class="t" stroke="var(--t3)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7" d="M-40 70 C 220 40, 400 82, 580 48 S 860 82, 1080 50 S 1240 70, 1260 64"/></svg></div>
</section>

<!-- CTA / DEMO REQUEST -->
<section id="contact" style="border-top:none">
  <div class="wrap">
    <div class="cta">
      <div class="cta-thread top" aria-hidden="true">
        <svg viewBox="0 0 1200 48" preserveAspectRatio="none">
          <path class="t" stroke="var(--t2)" stroke-width="1.5" vector-effect="non-scaling-stroke"
                d="M-40 24 C 200 4, 420 44, 640 18 S 940 44, 1240 24"/>
          <path class="t" stroke="var(--t3)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
                d="M-40 38 C 220 14, 420 44, 620 28 S 880 8, 1240 38"/>
          <path class="t" stroke="var(--t4)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7"
                d="M-40 10 C 240 36, 480 4, 720 22 S 1000 40, 1240 10"/>
        </svg>
      </div>

      <div>
        <span class="eyebrow">09 · Get pilot access</span>
        <h2>Get pilot access.</h2>
        <p class="lead">
          We’re onboarding a small cohort of agency partners this quarter. Tell us about your team and the clients you’d run on Thready — we’ll reply within one business day with a calendar link for a 20-minute walkthrough on a sandboxed copy of two or three of your accounts. No commitment, no slides.
        </p>

        <ol class="next-steps">
          <li>
            <span class="ix">1</span>
            <span><b>You submit the form</b>We reply within one business day with a calendar link.</span>
          </li>
          <li>
            <span class="ix">2</span>
            <span><b>20-minute walkthrough</b>Live on your data — generation, approval gates, analytics console.</span>
          </li>
          <li>
            <span class="ix">3</span>
            <span><b>Two-week pilot</b>If it’s a fit, we wire up 2–3 client accounts and run for 14 days, free.</span>
          </li>
        </ol>
      </div>

      <form class="demo-form" id="demo-form" novalidate style="padding: 28px 32px">
        <div class="form-head">
          <span class="title">Demo request</span>
          <span class="meta">~2 min · encrypted</span>
        </div>

        <div class="form-body">
          <div class="row">
            <div class="field">
              <label for="df-company">Company<span class="req">*</span></label>
              <input id="df-company" name="company" required autocomplete="organization" placeholder="Acme Media" />
            </div>
            <div class="field">
              <label for="df-website">Company website</label>
              <input id="df-website" name="website" type="url" autocomplete="url" placeholder="acme.com" />
            </div>
          </div>

          <div class="row">
            <div class="field">
              <label for="df-name">Your name<span class="req">*</span></label>
              <input id="df-name" name="name" required autocomplete="name" placeholder="Jane Doe" />
            </div>
            <div class="field">
              <label for="df-role">Role</label>
              <input id="df-role" name="role" autocomplete="organization-title" placeholder="Head of Content" />
            </div>
          </div>

          <div class="row">
            <div class="field">
              <label for="df-email">Work email<span class="req">*</span></label>
              <input id="df-email" name="email" type="email" required autocomplete="email" placeholder="jane@acme.com" />
            </div>
            <div class="field">
              <label for="df-accounts">How many client accounts?</label>
              <select id="df-accounts" name="accounts">
                <option value="">Select…</option>
                <option>1–4 accounts (sub-pilot)</option>
                <option>5–10 accounts (pilot)</option>
                <option>11–20 accounts</option>
                <option>20+ accounts (volume)</option>
                <option>Brand team / in-house</option>
              </select>
            </div>
          </div>

          <div class="field">
            <label for="df-notes">Anything we should know? <span style="color:var(--muted-2);text-transform:none;letter-spacing:0">— optional</span></label>
            <textarea id="df-notes" name="notes" placeholder="Verticals, languages, current tooling, what 'working' would look like in 90 days…"></textarea>
          </div>

          <div class="actions">
            <button type="submit" class="submit">
              Request pilot access
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
            <span class="fineprint">By submitting you agree to our <b>privacy policy</b>. We never share your details.</span>
          </div>
        </div>

        <div class="form-success" aria-live="polite">
          <span class="ok">Request received</span>
          <h3>Thanks <span data-out="name">there</span> — we'll be in touch.</h3>
          <p>A reply with a calendar link is on its way to <b data-out="email">your inbox</b>. In the meantime feel free to ping us on Telegram for anything urgent.</p>
          <div class="receipt">
            <span>company</span><b data-out="company">—</b>
            <span>accounts</span><b data-out="accounts">—</b>
            <span>received</span><b data-out="time">—</b>
            <span>ref</span><b data-out="ref">—</b>
          </div>
          <div style="display:flex;gap:10px;margin-top:6px">
            <a class="btn btn-ghost" href="https://t.me/thready" target="_blank" rel="noopener" style="padding:10px 14px">Open Telegram</a>
            <button type="button" class="btn btn-ghost" style="padding:10px 14px;cursor:pointer" onclick="document.getElementById('demo-form').classList.remove('is-sent');document.getElementById('demo-form').reset();">Submit another</button>
          </div>
        </div>
      </form>

      <div class="cta-thread bottom" aria-hidden="true">
        <svg viewBox="0 0 1200 48" preserveAspectRatio="none">
          <path class="t" stroke="var(--t5)" stroke-width="1.5" vector-effect="non-scaling-stroke"
                d="M-40 24 C 200 44, 420 4, 640 28 S 940 4, 1240 24"/>
          <path class="t" stroke="var(--t1)" stroke-width="1.3" vector-effect="non-scaling-stroke" opacity=".85"
                d="M-40 12 C 220 36, 420 4, 620 22 S 880 36, 1240 12"/>
          <path class="t" stroke="var(--t2)" stroke-width="1.1" vector-effect="non-scaling-stroke" opacity=".7"
                d="M-40 38 C 240 16, 480 42, 720 30 S 1000 12, 1240 38"/>
        </svg>
      </div>
    </div>
  </div>
</section>

<script>
  (function(){
    var SHEET_URL = 'https://script.google.com/macros/s/AKfycbyJxf1Rl_VlxogAq9jTVfLPhqupHsMMNXmBEHzHfEMNmyzA6R-M00SDYjYRskAjDGd5/exec';
    var form = document.getElementById('demo-form');
    if(!form) return;
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var data = {};
      new FormData(form).forEach(function(v,k){ data[k] = String(v).trim(); });
      if(!data.company || !data.name || !/.+@.+\..+/.test(data.email)){
        var first = form.querySelector('input:invalid, [required]:placeholder-shown') || form.querySelector('input[required]');
        if(first){ first.focus(); first.style.borderColor = 'var(--red, #e23636)'; }
        return;
      }
      var now = new Date();
      var ref = 'DM-' + now.getFullYear().toString().slice(-2) +
                String(now.getMonth()+1).padStart(2,'0') +
                String(now.getDate()).padStart(2,'0') + '-' +
                Math.random().toString(36).slice(2,6).toUpperCase();
      data._received = now.toISOString();
      data._ref = ref;

      try{
        var key = 'thready.demo.requests';
        var arr = JSON.parse(localStorage.getItem(key) || '[]');
        arr.push(data);
        localStorage.setItem(key, JSON.stringify(arr));
      }catch(_){}

      fetch(SHEET_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      }).catch(function(){});

      var slots = form.querySelectorAll('[data-out]');
      slots.forEach(function(el){
        var k = el.getAttribute('data-out');
        if(k === 'time'){ el.textContent = now.toLocaleString(); return; }
        if(k === 'ref'){ el.textContent = ref; return; }
        if(k === 'accounts'){ el.textContent = data.accounts || '—'; return; }
        if(k === 'name'){ el.textContent = (data.name||'').split(' ')[0] || 'there'; return; }
        el.textContent = data[k] || '—';
      });

      form.classList.add('is-sent');
      window.scrollTo({ top: form.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
    });
  })();
</script>

<footer>
  <div class="wrap foot">
    <span>© 2026 THREADY · Autonomous posting infrastructure</span>
    <span>v0.4.2 · status: ● operational</span>
  </div>
</footer>


<script>
// UTC clock
(function() {
  function updateClock() {
    var h = String(new Date().getUTCHours()).padStart(2,'0');
    var m = String(new Date().getUTCMinutes()).padStart(2,'0');
    var el = document.getElementById('dash-time');
    if (el) el.textContent = 'UTC ' + h + ':' + m;
  }
  updateClock();
  setInterval(updateClock, 30000);

  var chatBody = document.getElementById('chat-body');
  var chatInput = document.getElementById('chat-input');
  var chatSend = document.getElementById('chat-send');
  if (!chatBody || !chatInput || !chatSend) {
    console.warn('Thready chat: elements not found');
    return;
  }

  var chatHistory = [];

  function addMsg(role, text) {
    var el = document.createElement('div');
    el.className = 'msg ' + role;
    el.textContent = text;
    chatBody.appendChild(el);
    chatBody.scrollTop = chatBody.scrollHeight;
    return el;
  }

  function addHint(name) {
    var el = document.createElement('div');
    el.className = 'tool-hint';
    el.textContent = name + '...';
    chatBody.appendChild(el);
    chatBody.scrollTop = chatBody.scrollHeight;
    return el;
  }

  async function send() {
    var msg = chatInput.value.trim();
    if (!msg) return;
    chatInput.value = '';
    chatSend.disabled = true;
    addMsg('user', msg);
    var botEl = addMsg('bot', '');
    var hintEl = null;
    var text = '';
    try {
      var res = await fetch('/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg, history: chatHistory})
      });
      var reader = res.body.getReader();
      var dec = new TextDecoder();
      var buf = '';
      while (true) {
        var chunk = await reader.read();
        if (chunk.done) break;
        buf += dec.decode(chunk.value, {stream: true});
        var parts = buf.split('\\n');
        buf = parts.pop();
        for (var i = 0; i < parts.length; i++) {
          var line = parts[i].replace(/\\r$/, '');
          if (!line.startsWith('data: ')) continue;
          try {
            var ev = JSON.parse(line.slice(6));
            if (ev.type === 'text') {
              if (hintEl) { hintEl.remove(); hintEl = null; }
              text += ev.text;
              botEl.textContent = text;
              chatBody.scrollTop = chatBody.scrollHeight;
            } else if (ev.type === 'tool') {
              hintEl = addHint(ev.name);
            } else if (ev.type === 'done') {
              if (hintEl) { hintEl.remove(); hintEl = null; }
              chatHistory = ev.history;
            }
          } catch(_) {}
        }
      }
    } catch (e) {
      botEl.textContent = 'Error: ' + e.message;
    }
    chatSend.disabled = false;
    chatInput.focus();
  }

  chatSend.onclick = send;
  chatInput.onkeydown = function(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };
}());
</script>
</body>
</html>
"""