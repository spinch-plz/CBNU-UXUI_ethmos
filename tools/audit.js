const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:960}});
 await p.goto('file://'+process.cwd()+'/dist/index.html');await p.waitForTimeout(600);
 const routes=['login','perm','email','signup','profile','c:0','c:1','c:2','c:3','c:4','d:0','d:1','d:2','d:3','d:4','b:0','b:1','b:2','promise','widgets'];
 const acc={};
 for(const scn of ['bad','normal','good']){
  await p.evaluate(s=>{S.scn=s},scn);
  for(const r of routes){
   await p.evaluate(v=>nav(v,true),r);await p.waitForTimeout(500);
   const rows=await p.evaluate(()=>{const out=[];const w=document.createTreeWalker(document.getElementById('phone'),NodeFilter.SHOW_TEXT);let n;
    while(n=w.nextNode()){const t=n.textContent;if(!t.trim())continue;const el=n.parentElement;if(el.closest('script,style'))continue;const cs=getComputedStyle(el);
     out.push([/Eth|Serif/i.test(cs.fontFamily.split(',')[0])?'serif':'pret',cs.fontWeight,t])}
    return out});
   for(const [f,w,t] of rows){const k=f+':'+w;acc[k]=(acc[k]||new Set());for(const c of t)acc[k].add(c)}
  }}
 const o={};for(const k in acc)o[k]=[...acc[k]].filter(c=>c.trim()||c===' ').sort().join('');
 fs.writeFileSync('data/audit.json',JSON.stringify(o,null,1));
 for(const k in o)console.log(k,[...o[k]].length);
 await b.close();})();
