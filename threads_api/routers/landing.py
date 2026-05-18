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
    --bg:#0a0a0a;
    --bg-2:#0e0e0f;
    --card:#111113;
    --card-2:#141417;
    --line:#1c1c20;
    --line-2:#26262c;
    --text:#ececee;
    --muted:#8a8a93;
    --muted-2:#5a5a63;
    --accent:#4a9eff;
    --accent-soft:rgba(74,158,255,.12);
    --accent-line:rgba(74,158,255,.32);
    --good:#5fd39a;
    --warn:#f6c177;
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
      radial-gradient(1200px 600px at 80% -10%, rgba(74,158,255,.10), transparent 60%),
      radial-gradient(900px 500px at -10% 10%, rgba(74,158,255,.05), transparent 60%),
      var(--bg);
    background-attachment: fixed;
  }
  a{color:inherit;text-decoration:none}
  ::selection{background:var(--accent);color:#000}

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
    background:rgba(255,255,255,.015);
  }
  .pill .dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 0 4px rgba(95,211,154,.12)}

  nav.top{
    position:sticky;top:0;z-index:20;
    backdrop-filter:blur(10px);
    background:rgba(10,10,10,.6);
    border-bottom:1px solid var(--line);
  }
  .nav-inner{display:flex;align-items:center;justify-content:space-between;height:64px}
  .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-weight:600;letter-spacing:.04em}
  .brand .logo{width:24px;height:24px}
  .nav-links{display:flex;gap:28px;font-size:13px;color:var(--muted)}
  .nav-links a:hover{color:var(--text)}
  .nav-cta{
    font-family:var(--mono);font-size:12px;letter-spacing:.06em;
    padding:9px 14px;border:1px solid var(--line-2);border-radius:8px;color:var(--text);
    background:linear-gradient(180deg, #16161a, #101013);
  }
  .nav-cta:hover{border-color:var(--accent-line);color:var(--accent)}
  @media (max-width:760px){ .nav-links{display:none} }

  .hero{padding:88px 0 56px;position:relative;overflow:hidden}
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
    background:linear-gradient(180deg, #7fbcff 0%, #4a9eff 70%);
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  }
  .hero-sub{max-width:54ch;color:var(--muted);font-size:17px}
  .hero-cta{display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
  .btn{
    display:inline-flex;align-items:center;gap:10px;
    padding:13px 18px;border-radius:10px;font-size:14px;font-weight:500;
    border:1px solid transparent;cursor:pointer;transition:transform .15s ease, background .2s;
  }
  .btn-primary{background:var(--accent);color:#04101f;border-color:var(--accent)}
  .btn-primary:hover{background:#6cb0ff;transform:translateY(-1px)}
  .btn-ghost{background:transparent;border-color:var(--line-2);color:var(--text)}
  .btn-ghost:hover{border-color:var(--accent-line);color:var(--accent)}

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

  section{padding:96px 0;border-top:1px solid var(--line)}
  .section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin-bottom:48px;flex-wrap:wrap}
  .section-head h2{
    margin:10px 0 0;font-size:clamp(28px,3.4vw,42px);letter-spacing:-.02em;font-weight:500;line-height:1.05;max-width:22ch;
  }
  .section-head p{color:var(--muted);max-width:48ch;margin:0}
  .index{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.18em}

  .pipeline{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;position:relative}
  @media (max-width:900px){ .pipeline{grid-template-columns:1fr} }
  .step{
    border:1px solid var(--line);border-radius:14px;background:var(--card);
    padding:26px 24px 28px;position:relative;overflow:hidden;
  }
  .step::after{
    content:"";position:absolute;inset:auto -1px -1px -1px;height:1px;
    background:linear-gradient(90deg, transparent, var(--accent-line), transparent);
    opacity:0;transition:opacity .3s;
  }
  .step:hover::after{opacity:1}
  .step .ix{
    font-family:var(--mono);font-size:11px;color:var(--accent);letter-spacing:.12em;
    display:flex;align-items:center;gap:10px;margin-bottom:18px;
  }
  .step .ix .line{flex:1;height:1px;background:linear-gradient(90deg,var(--accent-line),transparent)}
  .step h3{margin:0 0 8px;font-size:20px;font-weight:500;letter-spacing:-.01em}
  .step p{color:var(--muted);margin:0;font-size:14.5px}
  .step .glyph{margin-bottom:22px;height:64px;display:flex;align-items:center;justify-content:flex-start}
  .step ul{list-style:none;padding:0;margin:16px 0 0;display:flex;flex-direction:column;gap:6px}
  .step ul li{font-family:var(--mono);font-size:12px;color:var(--muted);display:flex;gap:10px}
  .step ul li::before{content:"→";color:var(--accent);opacity:.7}

  .dash{
    border:1px solid var(--line);border-radius:16px;overflow:hidden;
    background:linear-gradient(180deg,#0c0c0e,#0a0a0c);
  }
  .dash-bar{
    display:flex;align-items:center;justify-content:space-between;
    padding:12px 16px;border-bottom:1px solid var(--line);
    background:#0d0d0f;
  }
  .dash-bar .left{display:flex;align-items:center;gap:14px}
  .traffic{display:flex;gap:6px}
  .traffic i{width:10px;height:10px;border-radius:50%;display:inline-block}
  .traffic i:nth-child(1){background:#3a3a40}
  .traffic i:nth-child(2){background:#3a3a40}
  .traffic i:nth-child(3){background:#3a3a40}
  .url{
    font-family:var(--mono);font-size:11px;color:var(--muted);
    background:#0a0a0c;border:1px solid var(--line);padding:4px 10px;border-radius:6px;
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
  .legend .b i{background:#7a7aff}
  .chart{width:100%;display:block}

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
    background:linear-gradient(135deg,#1f1f24,#0e0e10);
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

  .chat-wrap{display:grid;grid-template-columns:1fr 1.1fr;gap:36px;align-items:stretch}
  @media (max-width:900px){ .chat-wrap{grid-template-columns:1fr} }
  .chat-copy h3{font-size:22px;margin:14px 0 12px;font-weight:500;letter-spacing:-.01em}
  .chat-copy p{color:var(--muted);max-width:42ch}
  .chat-copy ul{list-style:none;padding:0;margin:24px 0 0;display:flex;flex-direction:column;gap:10px}
  .chat-copy ul li{font-family:var(--mono);font-size:12.5px;color:var(--muted);display:flex;gap:10px}
  .chat-copy ul li::before{content:"//";color:var(--accent);opacity:.7}

  .chat-ui{
    border:1px solid var(--line);border-radius:14px;background:var(--card);overflow:hidden;display:flex;flex-direction:column;min-height:440px;
  }
  .chat-head{padding:14px 18px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between}
  .chat-head .who{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:13px}
  .chat-head .who .dot{width:8px;height:8px;border-radius:50%;background:var(--good)}
  .chat-head .meta{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.08em}
  .chat-body{padding:18px;flex:1;display:flex;flex-direction:column;gap:14px;overflow-y:auto;max-height:340px}
  .msg{max-width:78%;padding:11px 14px;border-radius:12px;font-size:14px;line-height:1.5}
  .msg.user{align-self:flex-end;background:var(--accent-soft);border:1px solid var(--accent-line);color:#cfe3ff}
  .msg.bot{align-self:flex-start;background:#15151a;border:1px solid var(--line-2)}
  .msg.bot .data{
    margin-top:10px;border-top:1px dashed var(--line-2);padding-top:10px;
    font-family:var(--mono);font-size:12px;color:var(--muted);display:grid;grid-template-columns:auto 1fr;gap:4px 14px
  }
  .msg.bot .data b{color:var(--text);font-weight:500}
  .tool-hint{font-family:var(--mono);font-size:12px;color:var(--accent);align-self:flex-start;display:flex;align-items:center;gap:8px}
  .tool-hint::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--accent);animation:pulse 1s ease-in-out infinite}
  .chat-input{
    border-top:1px solid var(--line);padding:12px 14px;display:flex;align-items:center;gap:10px;
    background:#0c0c0e;
  }
  .chat-input input{
    flex:1;background:transparent;border:none;outline:none;color:var(--text);font-family:var(--sans);font-size:14px;
  }
  .chat-input input::placeholder{color:var(--muted-2)}
  .send{
    width:30px;height:30px;border-radius:8px;border:1px solid var(--accent-line);
    background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;cursor:pointer;
    flex-shrink:0;
  }
  .send:disabled{opacity:.4;cursor:default}

  .stack{display:flex;flex-wrap:wrap;gap:10px}
  .badge{
    display:inline-flex;align-items:center;gap:10px;
    padding:10px 14px;border:1px solid var(--line-2);border-radius:10px;
    background:var(--card);font-family:var(--mono);font-size:13px;color:var(--text);
  }
  .badge .bdot{width:8px;height:8px;border-radius:2px;background:var(--accent);box-shadow:0 0 12px rgba(74,158,255,.5)}

  .cta{
    border:1px solid var(--line);border-radius:18px;
    background:
      radial-gradient(800px 300px at 100% 0%, rgba(74,158,255,.10), transparent 60%),
      linear-gradient(180deg,#0e0e11,#0a0a0c);
    padding:56px clamp(28px,5vw,72px);
    display:grid;grid-template-columns:1.2fr .8fr;gap:36px;align-items:center;
  }
  @media (max-width:820px){ .cta{grid-template-columns:1fr} }
  .cta h2{font-size:clamp(28px,4vw,44px);margin:6px 0 12px;letter-spacing:-.02em;line-height:1.05;font-weight:500}
  .cta p{color:var(--muted);max-width:48ch;margin:0}
  .cta-actions{display:flex;gap:12px;justify-content:flex-end;flex-wrap:wrap}
  @media (max-width:820px){ .cta-actions{justify-content:flex-start} }

  footer{padding:36px 0 56px;color:var(--muted-2);border-top:1px solid var(--line);margin-top:60px}
  .foot{display:flex;justify-content:space-between;align-items:center;font-family:var(--mono);font-size:12px;flex-wrap:wrap;gap:16px}

  .ticker{
    border-top:1px solid var(--line);border-bottom:1px solid var(--line);
    overflow:hidden;white-space:nowrap;font-family:var(--mono);font-size:12px;color:var(--muted);
    background:#0c0c0e;
  }
  .ticker-track{display:inline-flex;gap:40px;padding:12px 0;animation:scroll 40s linear infinite}
  .ticker-track span{display:inline-flex;align-items:center;gap:10px}
  .ticker-track span::before{content:"●";color:var(--accent);font-size:8px}
  @keyframes scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}

  .logo-svg{width:100%;height:100%;display:block}
</style>
</head>
<body>

<nav class="top">
  <div class="wrap nav-inner">
    <a href="#" class="brand">
      <span class="logo">
        <svg class="logo-svg" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M3 6 C8 6, 8 18, 13 18 C18 18, 18 6, 21 6" stroke="#4a9eff" stroke-width="1.6" stroke-linecap="round"/>
          <path d="M3 12 C8 12, 8 18, 13 18" stroke="#ececee" stroke-width="1.2" stroke-linecap="round" opacity=".55"/>
          <circle cx="21" cy="6" r="1.6" fill="#4a9eff"/>
        </svg>
      </span>
      <span>THREADY</span>
    </a>
    <div class="nav-links">
      <a href="#how">How it works</a>
      <a href="#metrics">Metrics</a>
      <a href="#accounts">Accounts</a>
      <a href="#assistant">Assistant</a>
      <a href="#stack">Stack</a>
    </div>
    <a href="#contact" class="nav-cta">Get in touch ↗</a>
  </div>
</nav>

<header class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="pill"><span class="dot"></span> Live · 10 accounts · 3 languages</span>
      <h1 class="hero-title">Autonomous posting<br/>for <em>Threads</em>, at the<br/>scale of a newsroom.</h1>
      <p class="hero-sub">
        Thready writes, schedules, publishes and measures content across a portfolio of Threads accounts —
        end-to-end, without humans in the loop. Two operators are running ten accounts today, generating roughly a quarter-million views every month.
      </p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#contact">Partner with us →</a>
        <a class="btn btn-ghost" href="#metrics">See live metrics</a>
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
          <div class="num">236K<span class="unit">/ 30d</span></div>
          <div class="delta">▲ 18.4% vs. prior 30d</div>
        </div>
        <div class="cell">
          <div class="label">Posts published</div>
          <div class="num">9,000<span class="unit">/ 30d</span></div>
          <div class="delta">~30 / account / day</div>
        </div>
        <div class="cell">
          <div class="label">Active accounts</div>
          <div class="num">10<span class="unit">across 3 langs</span></div>
          <div class="delta">EN · RU · ES</div>
        </div>
        <div class="cell">
          <div class="label">Operators</div>
          <div class="num">2<span class="unit">participants</span></div>
          <div class="delta">Budimir · Slava</div>
        </div>
      </div>
    </aside>
  </div>
</header>

<div class="ticker" aria-hidden="true">
  <div class="ticker-track">
    <span>BUDIMIR · 6 ACCOUNTS · 182,000 VIEWS / 30D</span>
    <span>SLAVA · 4 ACCOUNTS · 54,000 VIEWS / 30D</span>
    <span>~30 POSTS / ACCOUNT / DAY</span>
    <span>CEREBRAS LLM · CUSTOM PROMPTS PER ACCOUNT</span>
    <span>FULL PIPELINE — GENERATE · SCHEDULE · PUBLISH · MEASURE</span>
    <span>BUDIMIR · 6 ACCOUNTS · 182,000 VIEWS / 30D</span>
    <span>SLAVA · 4 ACCOUNTS · 54,000 VIEWS / 30D</span>
    <span>~30 POSTS / ACCOUNT / DAY</span>
    <span>CEREBRAS LLM · CUSTOM PROMPTS PER ACCOUNT</span>
    <span>FULL PIPELINE — GENERATE · SCHEDULE · PUBLISH · MEASURE</span>
  </div>
</div>

<section id="how">
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">01 · Pipeline</span>
        <h2>Three deterministic steps. Zero hands on the keyboard.</h2>
      </div>
      <p>Each account is configured once — niche, voice, posting cadence, language. Thready runs the rest as a continuous loop.</p>
    </div>

    <div class="pipeline">
      <article class="step">
        <div class="ix">STEP 01 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <rect x="6" y="10" width="44" height="36" rx="6" stroke="#4a9eff" stroke-width="1.4"/>
            <path d="M14 20h28M14 27h20M14 34h24" stroke="#ececee" stroke-width="1.2" stroke-linecap="round" opacity=".55"/>
            <circle cx="46" cy="10" r="4" fill="#4a9eff"/>
          </svg>
        </div>
        <h3>Generate</h3>
        <p>A Cerebras-hosted LLM produces drafts using prompts hand-tuned per account — voice, topic clusters, posting style and language are all encoded as templates.</p>
        <ul>
          <li>Custom prompt per handle</li>
          <li>Style + topic guardrails</li>
          <li>Human-quality drafts in ~1s</li>
        </ul>
      </article>

      <article class="step">
        <div class="ix">STEP 02 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <circle cx="28" cy="28" r="20" stroke="#4a9eff" stroke-width="1.4"/>
            <path d="M28 14v14l9 6" stroke="#ececee" stroke-width="1.4" stroke-linecap="round"/>
            <circle cx="28" cy="28" r="2" fill="#4a9eff"/>
          </svg>
        </div>
        <h3>Schedule &amp; publish</h3>
        <p>The scheduler picks optimal slots per timezone and per account, posts directly through the Threads API, and confirms delivery before moving on.</p>
        <ul>
          <li>Per-account time windows</li>
          <li>Automatic retries &amp; backoff</li>
          <li>~30 posts / account / day</li>
        </ul>
      </article>

      <article class="step">
        <div class="ix">STEP 03 <span class="line"></span></div>
        <div class="glyph">
          <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
            <path d="M6 44h44" stroke="#ececee" stroke-width="1.2" opacity=".55"/>
            <path d="M10 40l10-14 10 8 10-18 8 12" stroke="#4a9eff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="48" cy="28" r="3" fill="#4a9eff"/>
          </svg>
        </div>
        <h3>Measure</h3>
        <p>Views, likes, replies, follower deltas — collected per post, per account, per day — flow into a single dashboard and an AI assistant you can simply ask.</p>
        <ul>
          <li>Post-level telemetry</li>
          <li>Cohort &amp; niche analytics</li>
          <li>Anomaly alerts</li>
        </ul>
      </article>
    </div>
  </div>
</section>

<section id="metrics">
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">02 · Live analytics</span>
        <h2>An embedded Superset dashboard, plugged straight in.</h2>
      </div>
      <p>Pre-wired charts for portfolio views, per-account performance, and content cohorts. <a href="http://slavik.works:8088" target="_blank" style="color:var(--accent)">Open live dashboard ↗</a></p>
    </div>

    <div class="dash" role="region" aria-label="Live Analytics — embedded Superset dashboard">
      <div class="dash-bar">
        <div class="left">
          <div class="traffic"><i></i><i></i><i></i></div>
          <div class="url">slavik.works:8088 / superset / dashboard / portfolio</div>
        </div>
        <div class="right">
          <span id="dash-time">UTC --:--</span>
          <span class="live">LIVE</span>
        </div>
      </div>

      <div class="dash-body">
        <div class="dash-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <h4>Views — last 30 days</h4>
              <div class="big">236,000</div>
              <div class="sub">+18.4% vs. prior period</div>
            </div>
            <div class="legend">
              <span class="a"><i></i>Budimir</span>
              <span class="b"><i style="background:#7a7aff"></i>Slava</span>
            </div>
          </div>

          <svg class="chart" viewBox="0 0 600 200" preserveAspectRatio="none" style="margin-top:14px">
            <defs>
              <linearGradient id="ga" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stop-color="#4a9eff" stop-opacity=".45"/>
                <stop offset="1" stop-color="#4a9eff" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="gb" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stop-color="#7a7aff" stop-opacity=".35"/>
                <stop offset="1" stop-color="#7a7aff" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <g stroke="#1c1c20" stroke-width="1">
              <line x1="0" y1="40" x2="600" y2="40"/>
              <line x1="0" y1="90" x2="600" y2="90"/>
              <line x1="0" y1="140" x2="600" y2="140"/>
              <line x1="0" y1="190" x2="600" y2="190"/>
            </g>
            <path d="M0 170 L40 165 L80 168 L120 160 L160 158 L200 150 L240 152 L280 145 L320 140 L360 138 L400 132 L440 130 L480 124 L520 120 L560 118 L600 112 L600 200 L0 200 Z" fill="url(#gb)"/>
            <path d="M0 170 L40 165 L80 168 L120 160 L160 158 L200 150 L240 152 L280 145 L320 140 L360 138 L400 132 L440 130 L480 124 L520 120 L560 118 L600 112" stroke="#7a7aff" stroke-width="1.4" fill="none"/>
            <path d="M0 140 L40 130 L80 132 L120 120 L160 110 L200 112 L240 96 L280 92 L320 78 L360 80 L400 64 L440 60 L480 52 L520 46 L560 40 L600 30 L600 200 L0 200 Z" fill="url(#ga)"/>
            <path d="M0 140 L40 130 L80 132 L120 120 L160 110 L200 112 L240 96 L280 92 L320 78 L360 80 L400 64 L440 60 L480 52 L520 46 L560 40 L600 30" stroke="#4a9eff" stroke-width="1.6" fill="none"/>
          </svg>

          <div class="mono" style="display:flex;justify-content:space-between;color:var(--muted-2);font-size:10px;margin-top:6px;letter-spacing:.08em">
            <span>APR 16</span><span>APR 22</span><span>APR 28</span><span>MAY 04</span><span>MAY 10</span><span>MAY 16</span>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:18px">
          <div class="dash-card">
            <h4>Top accounts · views / 30d</h4>
            <div style="display:flex;flex-direction:column;gap:10px;margin-top:14px;font-family:var(--mono);font-size:12px">
              <div>
                <div style="display:flex;justify-content:space-between"><span>mind_the_tap</span><span>61.5K</span></div>
                <div style="height:6px;background:#1a1a1f;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:100%;height:100%;background:linear-gradient(90deg,#4a9eff,#2d7be0)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>cycling_superhero</span><span>36.2K</span></div>
                <div style="height:6px;background:#1a1a1f;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:59%;height:100%;background:linear-gradient(90deg,#4a9eff,#2d7be0)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>event_parsing</span><span>35.4K</span></div>
                <div style="height:6px;background:#1a1a1f;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:57%;height:100%;background:linear-gradient(90deg,#4a9eff,#2d7be0)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>saas.memo</span><span>23.1K</span></div>
                <div style="height:6px;background:#1a1a1f;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:38%;height:100%;background:linear-gradient(90deg,#7a7aff,#5a5adf)"></div></div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between"><span>giraffe.from.mobile</span><span>13.7K</span></div>
                <div style="height:6px;background:#1a1a1f;border-radius:3px;overflow:hidden;margin-top:4px"><div style="width:22%;height:100%;background:linear-gradient(90deg,#7a7aff,#5a5adf)"></div></div>
              </div>
            </div>
          </div>

          <div class="row-2">
            <div class="dash-card">
              <h4>Engagement rate</h4>
              <div class="big">2.1<span style="font-size:14px;color:var(--muted);margin-left:4px">%</span></div>
              <div class="sub">portfolio avg</div>
            </div>
            <div class="dash-card">
              <h4>Top post</h4>
              <div class="big" style="font-size:18px;color:var(--good)">8,221</div>
              <div class="sub">views · cycling_superhero</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="accounts">
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">03 · Portfolio</span>
        <h2>Ten accounts, three languages, two operators.</h2>
      </div>
      <p>Each handle is a distinct voice with its own niche, audience and prompt configuration. Performance is tracked independently.</p>
    </div>

    <!-- Budimir -->
    <div class="accounts">
      <div class="participant-head">
        <div class="who">
          <div class="avatar">B</div>
          <div>
            <div style="font-family:var(--mono);font-weight:500">Budimir</div>
            <div style="color:var(--muted);font-size:12.5px">Participant · 6 accounts</div>
          </div>
        </div>
        <div class="meta">
          <span>VIEWS / 30D · <b>182,000</b></span>
          <span>POSTS / DAY · <b>~180</b></span>
        </div>
      </div>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>mind_the_tap</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">London cafés, pubs, neighbourhoods — curious local voice.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">61.5K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 2,201</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,18 10,16 20,17 30,12 40,14 50,9 60,10 70,5 80,4" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>cycling_superhero</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">Cycling — training, racing, gear, culture. Club cyclist voice.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">36.2K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 8,221</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,18 20,15 30,16 40,11 50,12 60,8 70,9 80,5" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>event_parsing</div>
          <span class="lang">EN</span>
        </div>
        <div class="niche">AI &amp; tech news in 2026 — sharp, opinionated, no fluff.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">35.4K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 2,398</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,16 10,17 20,13 30,14 40,12 50,10 60,11 70,7 80,8" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>claude_space</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Daily Claude use — behaviour, reactions, limits. No marketing.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">24.6K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 899</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,19 10,18 20,17 30,15 40,16 50,12 60,13 70,10 80,9" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>budeschka</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Surrealist micro-fiction — absurd, concrete, unexplained.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">12.3K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 2,641</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,19 20,17 30,18 40,15 50,14 60,12 70,13 80,10" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>aire.porteno</div>
          <span class="lang">ES</span>
        </div>
        <div class="niche">Buenos Aires cafés &amp; spaces — warm, local, rioplatense voice.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">11.4K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 404</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,17 10,16 20,18 30,14 40,15 50,11 60,12 70,9 80,11" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
    </div>

    <!-- Slava -->
    <div class="accounts" style="margin-top:32px">
      <div class="participant-head">
        <div class="who">
          <div class="avatar">S</div>
          <div>
            <div style="font-family:var(--mono);font-weight:500">Slava</div>
            <div style="color:var(--muted);font-size:12.5px">Participant · 4 accounts</div>
          </div>
        </div>
        <div class="meta">
          <span>VIEWS / 30D · <b>54,000</b></span>
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
          <div class="s"><span class="v">23.1K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 567</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,18 10,17 20,14 30,15 40,12 50,11 60,8 70,9 80,6" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>giraffe.from.mobile</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Turning 30 — observations, small panics, self-irony.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">13.7K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 480</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,19 10,18 20,16 30,17 40,14 50,15 60,12 70,11 80,10" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>tiger.on.remote</div>
          <span class="lang">RU</span>
        </div>
        <div class="niche">Student mocking friends' startups — dry campus cynicism.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">10.8K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 624</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,20 10,19 20,17 30,18 40,16 50,14 60,15 70,12 80,13" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>

      <article class="account">
        <div class="acc-top">
          <div class="handle"><span class="at">@</span>slow.routes.in.head</div>
          <span class="lang">ES</span>
        </div>
        <div class="niche">Remote work, procrastination, async life — rioplatense.</div>
        <div class="acc-stats">
          <div class="s"><span class="v">6.5K</span><span class="k">views · 30d</span></div>
          <div class="s"><span class="v">top post: 162</span><span class="k">views</span></div>
          <svg class="sparkline" viewBox="0 0 80 24" fill="none"><polyline points="0,21 10,20 20,18 30,19 40,17 50,16 60,15 70,13 80,14" stroke="#4a9eff" stroke-width="1.4" fill="none"/></svg>
        </div>
      </article>
    </div>
  </div>
</section>

<section id="assistant">
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">04 · Assistant</span>
        <h2>Ask our analytics assistant.</h2>
      </div>
      <p>Real-time access to posting stats, top content, and account performance — through a chat interface, not a SQL editor.</p>
    </div>

    <div class="chat-wrap">
      <div class="chat-copy">
        <span class="mono" style="color:var(--accent);font-size:12px;letter-spacing:.1em">// QUERY THE PORTFOLIO IN PLAIN LANGUAGE</span>
        <h3>Conversational access to every post, every account, every metric.</h3>
        <p>The assistant has direct read access to the Thready data warehouse. Ask it anything you would otherwise pull from Superset — it answers in seconds, with the numbers attached.</p>
        <ul>
          <li>Top posts this week, by language</li>
          <li>Why did <span style="color:var(--text)">@mind_the_tap</span> spike on Tuesday?</li>
          <li>Compare engagement across niches</li>
          <li>Which account has the best views/post ratio?</li>
        </ul>
      </div>

      <div class="chat-ui">
        <div class="chat-head">
          <div class="who"><span class="dot"></span> Thready Assistant</div>
          <div class="meta">LIVE · model: claude-haiku-4-5</div>
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
</section>

<section id="stack">
  <div class="wrap">
    <div class="section-head">
      <div>
        <span class="eyebrow">05 · Stack</span>
        <h2>Boring tech where it counts, leverage where it matters.</h2>
      </div>
      <p>Single-binary services, embedded analytics database, containerized deploys. We move fast because the substrate is simple.</p>
    </div>
    <div class="stack">
      <span class="badge"><span class="bdot"></span> FastAPI</span>
      <span class="badge"><span class="bdot"></span> DuckDB</span>
      <span class="badge"><span class="bdot"></span> Docker</span>
      <span class="badge"><span class="bdot"></span> Cerebras AI</span>
      <span class="badge"><span class="bdot"></span> Meta Threads API</span>
      <span class="badge"><span class="bdot"></span> Apache Superset</span>
    </div>
  </div>
</section>

<section id="contact" style="border-top:none">
  <div class="wrap">
    <div class="cta">
      <div>
        <span class="eyebrow">06 · Partner</span>
        <h2>Interested in partnering?</h2>
        <p>We're onboarding a small number of additional operators and content partners. The fastest way to reach us is Telegram — usually a reply within the hour.</p>
      </div>
      <div class="cta-actions">
        <a class="btn btn-primary" href="https://t.me/budimirtbilisi" target="_blank" rel="noopener">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M21.5 3.5L2.5 11l5.5 1.8 2 6.7 3.2-3.4 5.3 4 3-16.6z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
          </svg>
          Message on Telegram
        </a>
        <a class="btn btn-ghost" href="mailto:budimirtbilisi@gmail.com">budimirtbilisi@gmail.com</a>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap foot">
    <span>© 2026 THREADY · Autonomous posting infrastructure</span>
    <span>v1.0 · status: ● operational</span>
  </div>
</footer>

<script>
// Live UTC clock in dashboard
function updateClock() {
  const now = new Date();
  const h = String(now.getUTCHours()).padStart(2,'0');
  const m = String(now.getUTCMinutes()).padStart(2,'0');
  const el = document.getElementById('dash-time');
  if (el) el.textContent = 'UTC ' + h + ':' + m;
}
updateClock();
setInterval(updateClock, 30000);

// Live chat
const chatBody = document.getElementById('chat-body');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');
let chatHistory = [];

function addMsg(role, text) {
  const el = document.createElement('div');
  el.className = 'msg ' + role;
  el.textContent = text;
  chatBody.appendChild(el);
  chatBody.scrollTop = chatBody.scrollHeight;
  return el;
}

function addToolHint(name) {
  const el = document.createElement('div');
  el.className = 'tool-hint';
  el.textContent = name + '…';
  chatBody.appendChild(el);
  chatBody.scrollTop = chatBody.scrollHeight;
  return el;
}

async function sendMessage() {
  const msg = chatInput.value.trim();
  if (!msg || chatSend.disabled) return;
  chatInput.value = '';
  chatSend.disabled = true;

  addMsg('user', msg);
  const botEl = addMsg('bot', '');
  let toolEl = null;
  let fullText = '';

  try {
    const res = await fetch('/chat/stream', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: msg, history: chatHistory}),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buf += decoder.decode(value, {stream: true});
      const lines = buf.split('\\n');
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = JSON.parse(line.slice(6));
        if (data.type === 'text') {
          if (toolEl) { toolEl.remove(); toolEl = null; }
          fullText += data.text;
          botEl.textContent = fullText;
          chatBody.scrollTop = chatBody.scrollHeight;
        } else if (data.type === 'tool') {
          toolEl = addToolHint(data.name);
        } else if (data.type === 'done') {
          if (toolEl) { toolEl.remove(); toolEl = null; }
          chatHistory = data.history;
        }
      }
    }
  } catch (e) {
    botEl.textContent = 'Connection error. Make sure the API is running.';
  }

  chatSend.disabled = false;
  chatInput.focus();
}

chatSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
</script>

</body>
</html>"""
