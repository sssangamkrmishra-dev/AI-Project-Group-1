import React, { useState } from 'react';
import { 
  Activity, 
  Brain, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp, 
  AlertCircle, 
  FileText, 
  BarChart2, 
  Target,
  ChevronRight,
  RefreshCw,
  Zap,
  Network,
  Table as TableIcon
} from 'lucide-react';

const Card = ({ className, children }) => (
  <div className={`bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all duration-300 ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, color }) => (
  <span className={`px-2.5 py-1 rounded-md text-xs font-bold border ${color}`}>
    {children}
  </span>
);

const ProgressBar = ({ label, val, color }) => (
  <div className="group">
    <div className="flex justify-between text-sm mb-1.5">
      <span className="font-medium text-slate-600 group-hover:text-slate-900 transition-colors">{label}</span>
      <span className="font-bold text-slate-800">{(val * 100).toFixed(0)}%</span>
    </div>
    <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
      <div 
        className={`h-full rounded-full transition-all duration-1000 ease-out ${color}`}
        style={{ width: `${val * 100}%` }}
      />
    </div>
  </div>
);

const SelectGroup = ({ icon: Icon, label, val, set, opts }) => (
  <div className="space-y-2">
    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
      <Icon className="w-3.5 h-3.5" />
      {label}
    </label>
    <div className="relative group">
      <select
        className="w-full pl-4 pr-10 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl text-slate-700 font-semibold 
                   focus:outline-none focus:border-indigo-500 focus:bg-white
                   appearance-none transition-all cursor-pointer hover:border-indigo-200"
        value={val}
        onChange={(e) => set(e.target.value)}
      >
        {opts.map(o => (
          <option key={o.v || o} value={o.v || o}>{o.l || o}</option>
        ))}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-hover:text-indigo-500 transition-colors">
        <ChevronRight className="w-4 h-4 rotate-90" />
      </div>
    </div>
  </div>
);

const BNGraph = () => (
  <div className="w-full overflow-x-auto">
    <svg viewBox="0 0 850 420" className="w-full min-w-[600px] h-auto text-slate-600 font-sans">
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <path d="M0,0 L0,6 L9,3 z" fill="#94a3b8" />
        </marker>
      </defs>
      
      {/* Connections */}
      <g className="stroke-slate-400 stroke-[1.5] fill-none" markerEnd="url(#arrow)">
        <path d="M100,90 L212,190" /> {/* Mock -> Skill */}
        <path d="M300,90 L212,190" /> {/* Cons -> Skill */}
        <path d="M250,240 L400,240" /> {/* Skill -> Conf */}
        <path d="M500,90 L440,205" /> {/* Rej -> Conf */}
        <path d="M212,280 L400,350" /> {/* Skill -> Ready */}
        <path d="M425,280 L425,325" /> {/* Conf -> Ready */}
        <path d="M700,90 L450,350" /> {/* Res -> Ready */}
      </g>

      {/* Nodes */}
      <g className="font-bold text-[10px] uppercase tracking-wider" textAnchor="middle">
        {/* Layer 1: Evidence */}
        <g transform="translate(100,50)">
          <circle r="40" className="fill-white stroke-indigo-500 stroke-2" />
          <text y="-2" className="fill-slate-700">Mock</text>
          <text y="10" className="fill-slate-700">Performance</text>
        </g>
        <g transform="translate(300,50)">
          <circle r="40" className="fill-white stroke-indigo-500 stroke-2" />
          <text y="4" className="fill-slate-700">Consistency</text>
        </g>
        <g transform="translate(500,50)">
          <circle r="40" className="fill-white stroke-indigo-500 stroke-2" />
          <text y="-2" className="fill-slate-700">Rejection</text>
          <text y="10" className="fill-slate-700">Count</text>
        </g>
        <g transform="translate(700,50)">
          <circle r="40" className="fill-white stroke-indigo-500 stroke-2" />
          <text y="-2" className="fill-slate-700">Resume</text>
          <text y="10" className="fill-slate-700">Score</text>
        </g>

        {/* Layer 2: Latent */}
        <g transform="translate(212,235)">
          <circle r="40" className="fill-violet-50 stroke-violet-500 stroke-2" />
          <text y="-2" className="fill-violet-900">Skill</text>
          <text y="10" className="fill-violet-900">Level</text>
        </g>
        <g transform="translate(440,235)">
          <circle r="40" className="fill-pink-50 stroke-pink-500 stroke-2" />
          <text y="4" className="fill-pink-900">Confidence</text>
        </g>

        {/* Layer 3: Target */}
        <g transform="translate(425,370)">
          <circle r="45" className="fill-emerald-50 stroke-emerald-500 stroke-2" />
          <text y="-2" className="fill-emerald-900">Placement</text>
          <text y="10" className="fill-emerald-900">Readiness</text>
        </g>
      </g>
    </svg>
  </div>
);

const ConditionalTable = ({ parents, columns, data }) => (
  <div className="overflow-x-auto border rounded-lg bg-white">
    <table className="w-full text-xs text-left">
      <thead className="bg-slate-100 font-bold text-slate-700">
        <tr>
          {parents.map(p => <th key={p} className="p-3 border-b border-slate-200">{p}</th>)}
          {columns.map(c => <th key={c} className="p-3 border-b border-slate-200 bg-indigo-50 text-indigo-700">{c}</th>)}
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100">
        {Object.entries(data).map(([key, probs]) => {
          const parentStates = key.split('_');
          return (
            <tr key={key} className="hover:bg-slate-50 transition-colors">
              {parentStates.map((s, i) => <td key={i} className="p-3 font-medium text-slate-600">{s}</td>)}
              {columns.map(c => <td key={c} className="p-3 text-slate-500 font-mono">{(probs[c] * 100).toFixed(0)}%</td>)}
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

const PriorTable = ({ data }) => (
  <div className="flex gap-2 flex-wrap">
    {Object.entries(data).map(([key, val]) => (
      <div key={key} className="flex-1 min-w-[100px] bg-slate-50 border rounded p-2 text-center">
        <div className="text-xs text-slate-500 font-medium mb-1">{key}</div>
        <div className="text-sm font-bold text-slate-800">{(val * 100).toFixed(0)}%</div>
      </div>
    ))}
  </div>
);

class BN {
  constructor() {
    this.cpt = {
      mock: { 'Excellent': 0.15, 'Good': 0.30, 'Average': 0.40, 'Poor': 0.15 },
      cons: { 'HighlyConsistent': 0.20, 'Moderate': 0.35, 'Irregular': 0.30, 'Rare': 0.15 },
      rej: { 'None': 0.25, '1-2': 0.35, '3-5': 0.25, 'MoreThan5': 0.15 },
      res: { 'High': 0.25, 'Medium': 0.50, 'Low': 0.25 },
      skill: {
        'Excellent_HighlyConsistent': {'High': 0.85, 'Medium': 0.13, 'Low': 0.02},
        'Excellent_Moderate': {'High': 0.75, 'Medium': 0.20, 'Low': 0.05},
        'Excellent_Irregular': {'High': 0.55, 'Medium': 0.35, 'Low': 0.10},
        'Excellent_Rare': {'High': 0.35, 'Medium': 0.45, 'Low': 0.20},
        'Good_HighlyConsistent': {'High': 0.70, 'Medium': 0.25, 'Low': 0.05},
        'Good_Moderate': {'High': 0.55, 'Medium': 0.35, 'Low': 0.10},
        'Good_Irregular': {'High': 0.35, 'Medium': 0.45, 'Low': 0.20},
        'Good_Rare': {'High': 0.20, 'Medium': 0.45, 'Low': 0.35},
        'Average_HighlyConsistent': {'High': 0.45, 'Medium': 0.45, 'Low': 0.10},
        'Average_Moderate': {'High': 0.30, 'Medium': 0.50, 'Low': 0.20},
        'Average_Irregular': {'High': 0.15, 'Medium': 0.50, 'Low': 0.35},
        'Average_Rare': {'High': 0.08, 'Medium': 0.37, 'Low': 0.55},
        'Poor_HighlyConsistent': {'High': 0.20, 'Medium': 0.50, 'Low': 0.30},
        'Poor_Moderate': {'High': 0.10, 'Medium': 0.40, 'Low': 0.50},
        'Poor_Irregular': {'High': 0.05, 'Medium': 0.25, 'Low': 0.70},
        'Poor_Rare': {'High': 0.02, 'Medium': 0.18, 'Low': 0.80}
      },
      conf: {
        'None_High': {'Confident': 0.70, 'Neutral': 0.25, 'Anxious': 0.04, 'Frustrated': 0.01},
        'None_Medium': {'Confident': 0.50, 'Neutral': 0.40, 'Anxious': 0.08, 'Frustrated': 0.02},
        'None_Low': {'Confident': 0.25, 'Neutral': 0.45, 'Anxious': 0.25, 'Frustrated': 0.05},
        '1-2_High': {'Confident': 0.50, 'Neutral': 0.35, 'Anxious': 0.12, 'Frustrated': 0.03},
        '1-2_Medium': {'Confident': 0.30, 'Neutral': 0.40, 'Anxious': 0.25, 'Frustrated': 0.05},
        '1-2_Low': {'Confident': 0.10, 'Neutral': 0.30, 'Anxious': 0.45, 'Frustrated': 0.15},
        '3-5_High': {'Confident': 0.30, 'Neutral': 0.35, 'Anxious': 0.28, 'Frustrated': 0.07},
        '3-5_Medium': {'Confident': 0.15, 'Neutral': 0.30, 'Anxious': 0.40, 'Frustrated': 0.15},
        '3-5_Low': {'Confident': 0.05, 'Neutral': 0.15, 'Anxious': 0.45, 'Frustrated': 0.35},
        'MoreThan5_High': {'Confident': 0.15, 'Neutral': 0.25, 'Anxious': 0.40, 'Frustrated': 0.20},
        'MoreThan5_Medium': {'Confident': 0.08, 'Neutral': 0.17, 'Anxious': 0.45, 'Frustrated': 0.30},
        'MoreThan5_Low': {'Confident': 0.03, 'Neutral': 0.07, 'Anxious': 0.40, 'Frustrated': 0.50}
      },
      ready: {
        'High_Confident_High': {'WellPrepared': 0.90, 'ModeratelyPrepared': 0.08, 'Underprepared': 0.01, 'HighRisk': 0.01},
        'High_Confident_Medium': {'WellPrepared': 0.75, 'ModeratelyPrepared': 0.20, 'Underprepared': 0.04, 'HighRisk': 0.01},
        'High_Confident_Low': {'WellPrepared': 0.55, 'ModeratelyPrepared': 0.30, 'Underprepared': 0.12, 'HighRisk': 0.03},
        'High_Neutral_High': {'WellPrepared': 0.75, 'ModeratelyPrepared': 0.20, 'Underprepared': 0.04, 'HighRisk': 0.01},
        'High_Neutral_Medium': {'WellPrepared': 0.60, 'ModeratelyPrepared': 0.30, 'Underprepared': 0.08, 'HighRisk': 0.02},
        'High_Neutral_Low': {'WellPrepared': 0.40, 'ModeratelyPrepared': 0.35, 'Underprepared': 0.20, 'HighRisk': 0.05},
        'High_Anxious_High': {'WellPrepared': 0.50, 'ModeratelyPrepared': 0.35, 'Underprepared': 0.12, 'HighRisk': 0.03},
        'High_Anxious_Medium': {'WellPrepared': 0.35, 'ModeratelyPrepared': 0.40, 'Underprepared': 0.20, 'HighRisk': 0.05},
        'High_Anxious_Low': {'WellPrepared': 0.20, 'ModeratelyPrepared': 0.35, 'Underprepared': 0.35, 'HighRisk': 0.10},
        'High_Frustrated_High': {'WellPrepared': 0.35, 'ModeratelyPrepared': 0.40, 'Underprepared': 0.20, 'HighRisk': 0.05},
        'High_Frustrated_Medium': {'WellPrepared': 0.20, 'ModeratelyPrepared': 0.35, 'Underprepared': 0.35, 'HighRisk': 0.10},
        'High_Frustrated_Low': {'WellPrepared': 0.10, 'ModeratelyPrepared': 0.25, 'Underprepared': 0.45, 'HighRisk': 0.20},
        'Medium_Confident_High': {'WellPrepared': 0.50, 'ModeratelyPrepared': 0.40, 'Underprepared': 0.08, 'HighRisk': 0.02},
        'Medium_Confident_Medium': {'WellPrepared': 0.30, 'ModeratelyPrepared': 0.50, 'Underprepared': 0.17, 'HighRisk': 0.03},
        'Medium_Confident_Low': {'WellPrepared': 0.15, 'ModeratelyPrepared': 0.40, 'Underprepared': 0.35, 'HighRisk': 0.10},
        'Medium_Neutral_High': {'WellPrepared': 0.30, 'ModeratelyPrepared': 0.50, 'Underprepared': 0.17, 'HighRisk': 0.03},
        'Medium_Neutral_Medium': {'WellPrepared': 0.18, 'ModeratelyPrepared': 0.52, 'Underprepared': 0.25, 'HighRisk': 0.05},
        'Medium_Neutral_Low': {'WellPrepared': 0.08, 'ModeratelyPrepared': 0.30, 'Underprepared': 0.45, 'HighRisk': 0.17},
        'Medium_Anxious_High': {'WellPrepared': 0.15, 'ModeratelyPrepared': 0.40, 'Underprepared': 0.35, 'HighRisk': 0.10},
        'Medium_Anxious_Medium': {'WellPrepared': 0.08, 'ModeratelyPrepared': 0.35, 'Underprepared': 0.42, 'HighRisk': 0.15},
        'Medium_Anxious_Low': {'WellPrepared': 0.03, 'ModeratelyPrepared': 0.20, 'Underprepared': 0.52, 'HighRisk': 0.25},
        'Medium_Frustrated_High': {'WellPrepared': 0.08, 'ModeratelyPrepared': 0.30, 'Underprepared': 0.42, 'HighRisk': 0.20},
        'Medium_Frustrated_Medium': {'WellPrepared': 0.04, 'ModeratelyPrepared': 0.20, 'Underprepared': 0.46, 'HighRisk': 0.30},
        'Medium_Frustrated_Low': {'WellPrepared': 0.02, 'ModeratelyPrepared': 0.10, 'Underprepared': 0.43, 'HighRisk': 0.45},
        'Low_Confident_High': {'WellPrepared': 0.12, 'ModeratelyPrepared': 0.35, 'Underprepared': 0.40, 'HighRisk': 0.13},
        'Low_Confident_Medium': {'WellPrepared': 0.06, 'ModeratelyPrepared': 0.25, 'Underprepared': 0.49, 'HighRisk': 0.20},
        'Low_Confident_Low': {'WellPrepared': 0.02, 'ModeratelyPrepared': 0.13, 'Underprepared': 0.50, 'HighRisk': 0.35},
        'Low_Neutral_High': {'WellPrepared': 0.06, 'ModeratelyPrepared': 0.25, 'Underprepared': 0.48, 'HighRisk': 0.21},
        'Low_Neutral_Medium': {'WellPrepared': 0.03, 'ModeratelyPrepared': 0.17, 'Underprepared': 0.50, 'HighRisk': 0.30},
        'Low_Neutral_Low': {'WellPrepared': 0.01, 'ModeratelyPrepared': 0.09, 'Underprepared': 0.45, 'HighRisk': 0.45},
        'Low_Anxious_High': {'WellPrepared': 0.03, 'ModeratelyPrepared': 0.15, 'Underprepared': 0.47, 'HighRisk': 0.35},
        'Low_Anxious_Medium': {'WellPrepared': 0.01, 'ModeratelyPrepared': 0.09, 'Underprepared': 0.45, 'HighRisk': 0.45},
        'Low_Anxious_Low': {'WellPrepared': 0.01, 'ModeratelyPrepared': 0.04, 'Underprepared': 0.40, 'HighRisk': 0.55},
        'Low_Frustrated_High': {'WellPrepared': 0.02, 'ModeratelyPrepared': 0.10, 'Underprepared': 0.38, 'HighRisk': 0.50},
        'Low_Frustrated_Medium': {'WellPrepared': 0.01, 'ModeratelyPrepared': 0.05, 'Underprepared': 0.34, 'HighRisk': 0.60},
        'Low_Frustrated_Low': {'WellPrepared': 0.00, 'ModeratelyPrepared': 0.02, 'Underprepared': 0.28, 'HighRisk': 0.70}
      }
    };
  }

  infer(e) {
    const skP = this.cpt.skill[`${e.mock}_${e.cons}`];
    const cfP = { 'Confident': 0, 'Neutral': 0, 'Anxious': 0, 'Frustrated': 0 };
    
    for (const sk in skP) {
      const cd = this.cpt.conf[`${e.rej}_${sk}`];
      for (const cs in cd) cfP[cs] += cd[cs] * skP[sk];
    }
    
    const rdP = { 'WellPrepared': 0, 'ModeratelyPrepared': 0, 'Underprepared': 0, 'HighRisk': 0 };
    for (const sk in skP) {
      for (const cs in cfP) {
        const rd = this.cpt.ready[`${sk}_${cs}_${e.res}`] || this.cpt.ready['Low_Frustrated_Low'];
        const jp = skP[sk] * cfP[cs];
        for (const rs in rd) rdP[rs] += rd[rs] * jp;
      }
    }
    
    const tot = Object.values(rdP).reduce((a, b) => a + b, 0);
    for (const k in rdP) rdP[k] /= tot;
    
    return { skP, cfP, rdP };
  }
}

export default function App() {
  const [inp, setInp] = useState({ mock: 'Average', cons: 'Moderate', rej: '1-2', res: 'Medium' });
  const [res, setRes] = useState(null);
  const [load, setLoad] = useState(false);
  
  // Instance for CPT visualization
  const bnModel = new BN();

  const run = () => {
    setLoad(true);
    setTimeout(() => {
      const bn = new BN();
      const inf = bn.infer(inp);
      
      const mlR = Object.keys(inf.rdP).reduce((a, b) => inf.rdP[a] > inf.rdP[b] ? a : b);
      const rf = [];
      if (['3-5', 'MoreThan5'].includes(inp.rej)) rf.push('High Rejections');
      if (['Irregular', 'Rare'].includes(inp.cons)) rf.push('Inconsistent');
      if (['Poor', 'Average'].includes(inp.mock)) rf.push('Low Mock Score');
      if (inp.res === 'Low') rf.push('Poor Resume');
      if (inf.cfP['Anxious'] > 0.3 || inf.cfP['Frustrated'] > 0.2) rf.push('High Stress Risk');

      setRes({ ...inf, mlR, rf });
      setLoad(false);
    }, 800);
  };

  const getCfg = (s) => {
    switch(s) {
      case 'WellPrepared': return { i: CheckCircle, c: 'text-emerald-600', b: 'bg-emerald-500', bg: 'bg-emerald-50', br: 'border-emerald-200' };
      case 'ModeratelyPrepared': return { i: TrendingUp, c: 'text-blue-600', b: 'bg-blue-500', bg: 'bg-blue-50', br: 'border-blue-200' };
      case 'Underprepared': return { i: AlertCircle, c: 'text-amber-600', b: 'bg-amber-500', bg: 'bg-amber-50', br: 'border-amber-200' };
      case 'HighRisk': return { i: AlertTriangle, c: 'text-rose-600', b: 'bg-rose-500', bg: 'bg-rose-50', br: 'border-rose-200' };
      default: return { i: Activity, c: 'text-slate-600', b: 'bg-slate-500', bg: 'bg-slate-50', br: 'border-slate-200' };
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12 font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Header */}
        <div className="lg:col-span-12 text-center mb-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm border border-slate-100 mb-4">
            <Brain className="w-5 h-5 text-indigo-600" />
            <span className="text-sm font-bold text-slate-600 uppercase tracking-wide">Bayesian Inference Engine</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight mb-2">
            Placement Readiness <span className="text-indigo-600">BN</span>
          </h1>
          <p className="text-slate-500 font-medium">Probabilistic student assessment model</p>
        </div>

        {/* Inputs */}
        <div className="lg:col-span-4 space-y-6">
          <Card className="h-full border-t-4 border-t-indigo-500">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50">
              <h3 className="font-bold text-xl flex items-center gap-2 text-slate-800">
                <Activity className="w-5 h-5 text-indigo-500" />
                Student Profile
              </h3>
            </div>
            <div className="p-6 space-y-6">
              <SelectGroup 
                label="Mock Performance" icon={BarChart2} val={inp.mock} set={v => setInp({...inp, mock: v})}
                opts={['Excellent', 'Good', 'Average', 'Poor']}
              />
              <SelectGroup 
                label="Consistency" icon={RefreshCw} val={inp.cons} set={v => setInp({...inp, cons: v})}
                opts={['HighlyConsistent', 'Moderate', 'Irregular', 'Rare']}
              />
              <SelectGroup 
                label="Rejection Count" icon={AlertCircle} val={inp.rej} set={v => setInp({...inp, rej: v})}
                opts={['None', '1-2', '3-5', 'MoreThan5']}
              />
              <SelectGroup 
                label="Resume Score (ATS)" icon={FileText} val={inp.res} set={v => setInp({...inp, res: v})}
                opts={[{l:'High (70+)', v:'High'}, {l:'Medium (40-70)', v:'Medium'}, {l:'Low (<40)', v:'Low'}]}
              />
              
              <button 
                onClick={run} disabled={load}
                className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 
                           text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-indigo-500/30 
                           transform transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-wait
                           flex items-center justify-center gap-3"
              >
                {load ? <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"/> : <Zap className="w-5 h-5" />}
                {load ? 'Computing...' : 'Analyze Profile'}
              </button>
            </div>
          </Card>
        </div>

        {/* Results */}
        <div className="lg:col-span-8 space-y-8">
          {!res ? (
            <Card className="h-[400px] flex flex-col items-center justify-center border-dashed border-2 border-slate-200 bg-slate-50/50">
              <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-sm mb-6">
                <Target className="w-10 h-10 text-slate-300" />
              </div>
              <h3 className="text-xl font-bold text-slate-400">Ready to Analyze</h3>
              <p className="text-slate-400 mt-2">Configure inputs to run the Bayesian Network</p>
            </Card>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {(() => {
                const cfg = getCfg(res.mlR);
                const MainIcon = cfg.i;
                return (
                  <Card className={`relative overflow-hidden border-l-8 ${cfg.br.replace('border', 'border-l')} ${cfg.br}`}>
                    <div className={`absolute top-0 right-0 p-8 opacity-10 ${cfg.c}`}>
                      <MainIcon className="w-48 h-48 -rotate-12 transform translate-x-12 -translate-y-12" />
                    </div>
                    <div className="p-8 relative z-10">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`w-2 h-2 rounded-full ${cfg.b.replace('bg-', 'bg-')}`} />
                            <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Prediction</span>
                          </div>
                          <h2 className={`text-4xl font-black ${cfg.c} flex items-center gap-3`}>
                            {res.mlR.replace(/([A-Z])/g, ' $1').trim()}
                          </h2>
                          <p className="text-slate-500 mt-2 font-medium max-w-md">
                            Based on Bayesian inference, the student is most likely {res.mlR.toLowerCase().replace(/([a-z])([A-Z])/g, '$1 $2')}.
                          </p>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-sm font-bold text-slate-400 uppercase">Confidence</span>
                          <span className={`text-5xl font-black ${cfg.c}`}>
                            {(res.rdP[res.mlR] * 100).toFixed(0)}<span className="text-2xl">%</span>
                          </span>
                        </div>
                      </div>

                      {res.rf.length > 0 && (
                        <div className="mt-8 flex flex-wrap gap-2">
                          {res.rf.map(r => (
                            <Badge key={r} color="bg-rose-50 border-rose-200 text-rose-700">
                              <AlertTriangle className="w-3 h-3 inline mr-1" />{r}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })()}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-6">
                  <h4 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <Target className="w-5 h-5 text-indigo-500" />
                    Readiness Probability
                  </h4>
                  <div className="space-y-5">
                    {Object.entries(res.rdP).map(([k, v]) => (
                      <ProgressBar key={k} label={k.replace(/([A-Z])/g, ' $1').trim()} val={v} color={getCfg(k).b} />
                    ))}
                  </div>
                </Card>

                <div className="space-y-6">
                  <Card className="p-5 bg-white border-l-4 border-l-violet-500">
                    <div className="flex justify-between items-center mb-4">
                      <h5 className="font-bold text-slate-700 text-sm uppercase">Latent: Skill Level</h5>
                      <Brain className="w-4 h-4 text-violet-400" />
                    </div>
                    <div className="space-y-3">
                      {Object.entries(res.skP).map(([k, v]) => (
                        <div key={k} className="flex justify-between items-center text-sm">
                          <span className="font-medium text-slate-600">{k}</span>
                          <span className="font-bold text-slate-900">{(v * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </Card>

                  <Card className="p-5 bg-white border-l-4 border-l-pink-500">
                    <div className="flex justify-between items-center mb-4">
                      <h5 className="font-bold text-slate-700 text-sm uppercase">Latent: Confidence</h5>
                      <Activity className="w-4 h-4 text-pink-400" />
                    </div>
                    <div className="space-y-3">
                      {Object.entries(res.cfP).map(([k, v]) => (
                        <div key={k} className="flex justify-between items-center text-sm">
                          <span className="font-medium text-slate-600">{k}</span>
                          <span className="font-bold text-slate-900">{(v * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {/* Network Graph */}
          <Card className="border-t-4 border-t-slate-500">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
              <h3 className="font-bold text-xl flex items-center gap-2 text-slate-800">
                <Network className="w-5 h-5 text-slate-500" />
                Network Structure
              </h3>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">DAG Visualization</span>
            </div>
            <div className="p-6 overflow-hidden">
              <BNGraph />
            </div>
          </Card>

          {/* CPT Tables */}
          <div className="space-y-6">
            <h3 className="text-xl font-bold flex items-center gap-2 text-slate-800">
              <TableIcon className="w-5 h-5 text-indigo-600" />
              Conditional Probability Tables (CPTs)
            </h3>
            
            {/* Prior Distributions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-4">
                <h4 className="text-sm font-bold text-slate-600 mb-3 uppercase">P(Mock Performance)</h4>
                <PriorTable data={bnModel.cpt.mock} />
              </Card>
              <Card className="p-4">
                <h4 className="text-sm font-bold text-slate-600 mb-3 uppercase">P(Consistency)</h4>
                <PriorTable data={bnModel.cpt.cons} />
              </Card>
              <Card className="p-4">
                <h4 className="text-sm font-bold text-slate-600 mb-3 uppercase">P(Rejections)</h4>
                <PriorTable data={bnModel.cpt.rej} />
              </Card>
              <Card className="p-4">
                <h4 className="text-sm font-bold text-slate-600 mb-3 uppercase">P(Resume Score)</h4>
                <PriorTable data={bnModel.cpt.res} />
              </Card>
            </div>

            {/* Conditional Tables */}
            <Card className="p-5 border-l-4 border-l-violet-500">
              <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                P(Skill Level | Mock, Consistency)
              </h4>
              <ConditionalTable 
                parents={['Mock Perf', 'Consistency']}
                columns={['High', 'Medium', 'Low']}
                data={bnModel.cpt.skill}
              />
            </Card>

            <Card className="p-5 border-l-4 border-l-pink-500">
              <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                P(Confidence | Rejections, Skill Level)
              </h4>
              <ConditionalTable 
                parents={['Rejections', 'Skill Level']}
                columns={['Confident', 'Neutral', 'Anxious', 'Frustrated']}
                data={bnModel.cpt.conf}
              />
            </Card>

            <Card className="p-5 border-l-4 border-l-emerald-500">
              <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                P(Readiness | Skill, Confidence, Resume)
              </h4>
              <ConditionalTable 
                parents={['Skill', 'Confidence', 'Resume']}
                columns={['WellPrepared', 'ModeratelyPrepared', 'Underprepared', 'HighRisk']}
                data={bnModel.cpt.ready}
              />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}