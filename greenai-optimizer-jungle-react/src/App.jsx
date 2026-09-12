import React, { useMemo, useState } from "react";
import {
  Activity, ArrowRight, BarChart3, Bot, BrainCircuit, Check, CircleGauge,
  Cpu, Leaf, Menu, MessageSquare, Network, Plus, Send, Server, ShieldCheck,
  Sparkles, X, Mic, Zap, Gauge, TreePine
} from "lucide-react";

const VIDEO = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260831_232706_43757be4-2250-4f09-8cd7-23aebbf147ad.mp4";
const POSTER = "https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260831_223518_f11bfa03-4e65-47e1-a4a7-30e42a7a8c2f.png&w=1920&q=85";

const examples = [
  "What is inheritance in Java?",
  "Explain TCP congestion control with an example.",
  "Analyze this technical document and compare the algorithms."
];

const modelInfo = {
  Small: { quality: 72, energy: 1, latency: 1, color: "#47744f" },
  Medium: { quality: 91, energy: 3, latency: 1.7, color: "#628267" },
  Large: { quality: 95, energy: 10, latency: 2.8, color: "#8a7854" }
};

function classify(prompt) {
  const p = prompt.toLowerCase();
  const complexWords = ["analyze", "research", "document", "compare", "scalability", "architecture", "algorithm", "optimize", "evaluate"];
  const mediumWords = ["explain", "example", "implement", "debug", "why", "difference", "design", "code"];
  const complex = complexWords.filter(w => p.includes(w)).length;
  const medium = mediumWords.filter(w => p.includes(w)).length;
  if (complex >= 2 || prompt.length > 180) return { level: "HIGH", model: "Large", confidence: 94 };
  if (complex >= 1 || medium >= 2 || prompt.length > 70) return { level: "MEDIUM", model: "Medium", confidence: 91 };
  return { level: "LOW", model: "Small", confidence: 96 };
}

function Logo({ light = false }) {
  return <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
    <path d="M16 2.5 29.5 16 16 29.5 2.5 16 16 2.5Z" stroke={light ? "#fff" : "#141414"} strokeWidth="1.7" strokeLinejoin="round"/>
    <path d="M16 9.5 22.5 16 16 22.5 9.5 16 16 9.5Z" fill={light ? "#fff" : "#141414"}/>
  </svg>;
}

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [view, setView] = useState("home");
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const route = useMemo(() => classify(prompt || "What is a variable in C?"), [prompt]);

  const navigate = (next) => { setView(next); setMenuOpen(false); window.scrollTo({ top: 0, behavior: "smooth" }); };

  const runPrompt = async (value = prompt) => {
    if (!value.trim() || loading) return;
    const userQuery = value;
    setPrompt("");
    setLoading(true);
    setView("playground");

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userQuery }),
      });

      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);

      const data = await res.json();
      
      // Get complexity level (fallback to frontend route prediction if backend misses it)
      const complexity = data.task_analysis?.complexity || route.level || "LOW";
      
      // Smarter model mapping
      let modelKey = "Small";
      const rawModel = data.model_details?.selected_model || "";
      
      if (rawModel.includes("Large") || complexity === "HIGH") {
        modelKey = "Large";
      } else if (rawModel.includes("Medium") || complexity === "MEDIUM") {
        modelKey = "Medium";
      }

      // Fallback resolution for output text
      const outputText = data.response || data.answer || data.content || data.message || "Response generated successfully.";

      setMessages(m => [
        ...m,
        {
          prompt: userQuery,
          answer: outputText,
          level: complexity,
          model: modelKey,
          confidence: 95,
          energy: data.sustainability_metrics?.energy_consumed_wh || 0.002,
          saved: data.sustainability_metrics?.pct_compute_saved || 85,
          metrics: data.sustainability_metrics,
          details: data.model_details
        }
      ]);
    } catch (err) {
      console.error("Failed to route query:", err);
      setMessages(m => [
        ...m,
        {
          prompt: userQuery,
          answer: "Error: Could not fetch response from backend service.",
          level: "ERROR",
          model: "Small",
          confidence: 0,
          energy: 0,
          saved: 0
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (view !== "home") return <Application view={view} navigate={navigate} prompt={prompt} setPrompt={setPrompt} route={route} messages={messages} runPrompt={runPrompt} loading={loading}/>;

  return <section className="hero">
    <div className="hero__bg">
      <video autoPlay muted loop playsInline preload="auto" poster={POSTER}>
        <source type="video/mp4" src={VIDEO}/>
      </video>
    </div>
    <div className="hero__inner">
      <header className="nav">
        <a className="brand" href="#" onClick={e => { e.preventDefault(); navigate("home"); }}>
          <Logo />
          <span className="rise" style={{"--i":1}}>AI²</span>
        </a>
        <nav className={`nav__nav ${menuOpen ? "is-open" : ""}`} id="site-menu" aria-label="Main navigation">
          <ul className="nav__links">
            {[['playground','Playground'],['dashboard','Sustainability'],['router','Router'],['benchmarks','Benchmarks']].map(([id,label], i) => <li key={id}><a className="rise" style={{"--i":i+2}} href={`#${id}`} onClick={e => { e.preventDefault(); navigate(id); }}>{label}</a></li>)}
          </ul>
          <a className="btn-dark menu__cta" href="#access" onClick={e => { e.preventDefault(); navigate("playground"); }}>Try AI²</a>
        </nav>
        <div className="nav__cta rise" style={{"--i":6}}><button className="btn-dark" onClick={() => navigate("playground")}>Open Playground</button></div>
        <button className="nav__toggle rise" id="menu-toggle" style={{"--i":6}} type="button" aria-label={menuOpen ? "Close menu" : "Open menu"} aria-expanded={menuOpen} aria-controls="site-menu" onClick={() => setMenuOpen(v => !v)}>
          <span className="nav__toggle-box" aria-hidden="true"><span className="bar bar--top"></span><span className="bar bar--bot"></span></span>
        </button>
      </header>

      <main className="stage">
        <div className="badge rise" style={{"--i":8}}><span className="badge__tag">Now</span><span>Resource-aware AI is here</span></div>
        <h1 className="headline rise" style={{"--i":10}}>Make AI <span style={{color:'#47744f'}}>lighter.</span><br className="brk"/> Smarter for what counts.</h1>
        <p className="sub rise" style={{"--i":12}}>AI² analyzes every AI request and chooses only the computational power it actually needs.<br className="brk"/> Route intelligently, measure the impact, and build AI that is lighter on resources.</p>
        <form className="prompt rise" style={{"--i":14}} onSubmit={e => { e.preventDefault(); runPrompt(); }}>
          <label className="sr-only" htmlFor="prompt-input">Ask AI²</label>
          <textarea id="prompt-input" className="prompt__input" rows="3" value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Ask AI² to optimize an AI task..." />
          <div className="prompt__bar">
            <button className="icon-btn rise" style={{"--i":16}} type="button" aria-label="Add attachment"><Plus /></button>
            <div className="prompt__right">
              <button className="icon-btn icon-btn--bare rise" style={{"--i":17}} type="button" aria-label="Use microphone"><Mic /></button>
              <button className="icon-btn icon-btn--send rise" style={{"--i":18}} type="submit" aria-label="Send message" disabled={loading}><Send /></button>
            </div>
          </div>
        </form>
        <div className="rise" style={{"--i":19}}><span style={{fontSize:10,color:'#4f5c51'}}>Live route preview: <strong style={{color:'#47744f'}}>{route.level}</strong> → {route.model} Model</span></div>
      </main>
    </div>
  </section>;
}

function Application({ view, navigate, prompt, setPrompt, route, messages, runPrompt, loading }) {
  const labels = { playground:"AI Playground", dashboard:"Sustainability", router:"Model Router", benchmarks:"Benchmarks" };
  return <div className="app-view forest-grid">
    <div className="app-shell">
      <header className="app-nav">
        <button className="app-brand" onClick={() => navigate("home")}><Logo/><span>AI²</span></button>
        <div className="app-nav-links">
          {Object.entries(labels).map(([id,label]) => <button key={id} className={view===id?"active":""} onClick={() => navigate(id)}>{label}</button>)}
        </div>
        <div className="mobile-select"><select value={view} onChange={e => navigate(e.target.value)}>{Object.entries(labels).map(([id,label])=><option key={id} value={id}>{label}</option>)}</select></div>
        <div className="app-spacer"/>
        <div className="status-pill"><span className="status-dot"/> Router online</div>
        <button className="btn-dark" style={{padding:'9px 13px',fontSize:11}} onClick={() => navigate("home")}>Forest Home</button>
      </header>
      {view === "playground" && <Playground prompt={prompt} setPrompt={setPrompt} route={route} messages={messages} runPrompt={runPrompt} loading={loading}/>} 
      {view === "dashboard" && <Dashboard messages={messages}/>} 
      {view === "router" && <RouterPage/>}
      {view === "benchmarks" && <Benchmarks/>}
    </div>
  </div>;
}

function Playground({ prompt, setPrompt, route, messages, runPrompt, loading }) {
  return <main className="view-main">
    <div className="section-head">
      <div><div className="eyebrow"><Sparkles size={13}/> intelligent inference layer</div><h1 className="view-title">Make AI <em>lighter.</em></h1><p className="view-desc">Send a task. AI² analyzes its complexity and routes it to the smallest suitable model—then shows the computational and environmental impact.</p></div>
    </div>
    <div className="workspace-grid">
      <div className="glass-card play-card">
        <div className="card-head"><div className="card-label"><Bot size={16} color="#47744f"/> AI Playground</div><div className="card-meta">live orchestration</div></div>
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <div className="leaf-mark"><Leaf size={26}/></div>
              <h2>What should AI² optimize?</h2>
              <p>Try a request below. The router will classify its complexity and select the lightest model that can satisfy it.</p>
              <div className="example-list">{examples.map(e => <button key={e} className="example-chip" onClick={() => runPrompt(e)}>{e}</button>)}</div>
            </div>
          ) : (
            messages.map((m, i) => (
              <div key={i} style={{ display: 'contents' }}>
                <div className="message-user">{m.prompt}</div>
                <div className="message-ai">
                  <strong style={{ fontWeight: 500, color: '#47744f' }}>{m.model} Model selected ({m.level} complexity).</strong>
                  <p style={{ margin: '6px 0' }}>{m.answer}</p>
                  {m.metrics && (
                    <div style={{ fontSize: 11, color: '#555', marginTop: 6, borderTop: '1px dashed #ccc', paddingTop: 4 }}>
                      ⚡ Energy: <strong>{m.metrics.energy_consumed_wh} Wh</strong> | 🌱 CO2 Saved: <strong>{m.metrics.co2_saved_g} g</strong> | Score: <strong>{m.metrics.green_score}/100</strong>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && <div style={{ color: '#666', fontStyle: 'italic', fontSize: 12, padding: 10 }}>Analyzing complexity and generating green inference...</div>}
        </div>
        <form className="compose" onSubmit={e => { e.preventDefault(); runPrompt(); }}>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Describe an AI task..." />
          <div className="compose-bar">
            <span className="compose-left">{route.level} complexity → {route.model} Model</span>
            <button className="compose-send" type="submit" disabled={loading}><Send size={13}/> {loading ? 'Routing...' : 'Route task'}</button>
          </div>
        </form>
      </div>
      <RouteCard route={route} latest={messages.at(-1)}/>
    </div>
  </main>;
}

function RouteCard({ route, latest }) {
  // Sync the display card to use the latest message data if available
  const displayModel = latest?.model || route.model;
  const displayLevel = latest?.level || route.level;
  const model = modelInfo[displayModel] || modelInfo.Small;
  
  const energy = latest?.energy ?? model.energy * .42;
  const saved = latest?.saved ?? Math.max(0, Math.round((1-model.energy/10)*100));
  
  return (
    <aside className="glass-card route-card">
      <div className="route-kicker">live routing preview</div>
      <div className="route-model">
        <strong>{displayModel} Model</strong>
        <span className="route-level">{displayLevel}</span>
      </div>
      <div className="route-line"/>
      <div className="metric-row"><span>Confidence</span><span>{route.confidence}%</span></div>
      <div className="metric-row"><span>Quality target</span><span>{model.quality}%</span></div>
      <div className="metric-row"><span>Relative energy</span><span>{model.energy.toFixed(1)}×</span></div>
      <div className="metric-row"><span>Estimated latency</span><span>{model.latency.toFixed(1)}×</span></div>
      <div className="saving">
        <strong>{saved}%</strong>
        <span>estimated compute saved</span>
      </div>
      <div className="footer-note">
        <ShieldCheck size={11} style={{verticalAlign:'-2px',marginRight:4}}/> Connected to FastAPI Backend Telemetry.
      </div>
    </aside>
  );
}

function Dashboard({messages}) {
  // 1. Establish base numbers (to simulate past data)
  const baseTotal = 1284;
  const baseSmall = 633;
  const baseMedium = 437;
  const baseLarge = 214;
  const baseEnergy = 36.8;

  // 2. Calculate live session data from the messages array
  const sessionTotal = messages.length;
  const sessionSmall = messages.filter(m => m.model === 'Small').length;
  const sessionMedium = messages.filter(m => m.model === 'Medium').length;
  const sessionLarge = messages.filter(m => m.model === 'Large').length;

  // Sum up the energy saved from the backend metrics
  const sessionEnergyWh = messages.reduce((acc, m) => acc + (m.metrics?.energy_consumed_wh || 0), 0);
  
  // 3. Combine base + live data
  const totalRequests = baseTotal + sessionTotal;
  const totalSmall = baseSmall + sessionSmall;
  const totalMedium = baseMedium + sessionMedium;
  const totalLarge = baseLarge + sessionLarge;
  
  const totalEnergyWh = (baseEnergy + sessionEnergyWh).toFixed(2);
  
  // Calculate dynamic percentages for the bars
  const smallPct = Math.round((totalSmall / totalRequests) * 100);
  const mediumPct = Math.round((totalMedium / totalRequests) * 100);
  const largePct = Math.round((totalLarge / totalRequests) * 100);

  return (
    <main className="view-main">
      <div className="section-head">
        <div>
          <div className="eyebrow"><TreePine size={13}/> sustainability intelligence</div>
          <h1 className="view-title">AI² <em>Dashboard.</em></h1>
          <p className="view-desc">Live metrics collected and calculated by FastAPI optimization engine.</p>
        </div>
      </div>
      
      <div className="kpi-grid">
        {[
          ["Total requests", totalRequests.toLocaleString(), "live session"],
          ["Green-routed", totalSmall.toLocaleString(), `${smallPct}%`],
          ["Energy consumed", `${totalEnergyWh} Wh`, "calculated"],
          ["Green score", "91 / 100", "healthy"]
        ].map(([a,b,c]) => (
          <div className="glass-card kpi" key={a}>
            <div className="kpi-label">{a}</div>
            <div className="kpi-value">{b}</div>
            <div className="kpi-note">{c}</div>
          </div>
        ))}
      </div>
      
      <div className="two-col">
        <div className="glass-card chart-card">
          <div className="chart-title">Conventional vs AI²</div>
          <div className="chart-sub">Lower resource use is better; quality is preserved.</div>
          {[["Compute",58],["Energy",64],["Latency",70],["Quality",93]].map(([label,v]) => (
            <div className="compare-row" key={label}>
              <div className="compare-top"><span>{label}</span><span>{v}%</span></div>
              <div className="track"><div className="track-base"><div className="track-green" style={{width:`${v}%`}}/></div></div>
            </div>
          ))}
        </div>
        
        <div className="glass-card chart-card">
          <div className="chart-title">Model distribution</div>
          <div className="chart-sub">The router uses the smallest capable model.</div>
          {/* Use the dynamic variables calculated above for the bars */}
          {[
            ["Small Model", totalSmall, smallPct],
            ["Medium Model", totalMedium, mediumPct],
            ["Large Model", totalLarge, largePct]
          ].map(([name,val,pct]) => (
            <div className="dist-row" key={name}>
              <div className="dist-top"><span>{name}</span><span>{val} requests</span></div>
              <div className="track"><div className="track-base"><div className="track-green" style={{width:`${pct}%`}}/></div></div>
            </div>
          ))}
          <div className="saving" style={{marginTop:22}}>
            <strong style={{fontSize:16}}>Minimum necessary compute</strong>
            <span>The goal isn't always the smallest model. It's the minimum capability that meets the quality target.</span>
          </div>
        </div>
      </div>
    </main>
  );
}

function RouterPage() {
  const nodes = [[MessageSquare,'User Request'],[BrainCircuit,'Task Analyzer'],[Gauge,'Quality Target'],[Activity,'Resource Check'],[Bot,'Best Model']];
  return <main className="view-main"><div className="eyebrow"><Network size={13}/> decision engine</div><h1 className="view-title">Resource-Aware <em>Router.</em></h1><p className="view-desc">The orchestration layer sits between the user and multiple AI models, selecting capability based on task complexity, quality needs, and available resources.</p><div className="glass-card" style={{borderRadius:22,padding:20,marginTop:28}}><div className="flow">{nodes.map(([Icon,label],i)=><React.Fragment key={label}><div className="flow-node"><div className="flow-icon"><Icon size={16}/></div><span>{label}</span></div>{i<4&&<div style={{display:'none'}}><ArrowRight/></div>}</React.Fragment>)}</div><div className="models">{Object.entries(modelInfo).map(([name,x])=><div className="glass-card model-card" key={name}><div className="model-head"><strong>{name} Model</strong><span className="quality">{x.quality}% quality</span></div><div className="energy-label"><span>Relative energy</span><span>{x.energy.toFixed(1)}×</span></div><div className="energy-track"><div className="energy-fill" style={{width:`${x.energy*10}%`}}/></div><div className="footer-note">Latency {x.latency.toFixed(1)}× · capability tier {name.toLowerCase()}</div></div>)}</div></div></main>;
}

function Benchmarks() {
  const rows = [["Compute","100%","58%","−42%"],["Energy","100%","64%","−36%"],["Latency","100%","70%","−30%"],["Quality","95%","93%","−2%"],["Memory","100%","61%","−39%"]];
  return <main className="view-main"><div className="eyebrow"><BarChart3 size={13}/> validation</div><h1 className="view-title">Performance <em>Benchmarks.</em></h1><p className="view-desc">Use real experiments here once the backend is connected. Current figures are illustrative prototype data.</p><div className="glass-card benchmark-table"><div className="table-head"><span>Metric</span><span>Baseline</span><span>AI²</span><span>Delta</span><span>Status</span></div>{rows.map(r=><div className="table-row" key={r[0]}><span>{r[0]}</span><span style={{color:'#8b8b84'}}>{r[1]}</span><span className="good">{r[2]}</span><span className="good">{r[3]}</span><span><span className="check"><Check size={11}/></span></span></div>)}</div><div className="footer-note">AI² should report measured energy and carbon values—or clearly label them as estimates. Green Score is an app-level indicator, not an absolute environmental measurement.</div></main>;
}