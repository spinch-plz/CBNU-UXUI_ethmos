/* ===== 글자 아웃라인 렌더러 =====
   글꼴 파일을 쓰지 않고, 글자마다 미리 뽑아 둔 SVG path(GLY)로 그린다.
   브라우저의 줄바꿈·정렬은 그대로 쓰도록 글자 하나하나를 인라인 <svg>로 바꿔 끼운다. */
const GLY={{GLYPHS_JSON}};
const OTX=(()=>{
const NS='http://www.w3.org/2000/svg';
const WS={pret:[300,400,500,600,700],serif:[400,600,700]};
let defs=null;const made=new Set(),missed=new Set();
const f3=n=>Math.round(n*1000)/1000;
/* 글꼴의 ascent·descent(px). 브라우저 글꼴(Pretendard)은 정수로 반올림, Figma에서 뽑은 격동명조는 Figma처럼 반올림 없이 */
const MET=(f,fs)=>{const m=GLY[f].m,a=m[0]*fs/1000,d=m[1]*fs/1000;return GLY[f].raw?[a,d]:[Math.round(a),Math.round(d)]};
const NLH=(f,fs)=>{const [a,d]=MET(f,fs);return Math.round(a+d)};
function pickW(f,w){if(f==='serif')return w<=500?400:w<=650?600:700;let b=300;for(const x of WS.pret)if(Math.abs(x-w)<Math.abs(b-w)||(Math.abs(x-w)===Math.abs(b-w)&&x>b))b=x;return b}
function sprite(){if(defs)return defs;const s=document.createElementNS(NS,'svg');s.setAttribute('width','0');s.setAttribute('height','0');s.setAttribute('aria-hidden','true');s.style.cssText='position:absolute;width:0;height:0;overflow:hidden';defs=document.createElementNS(NS,'defs');s.appendChild(defs);document.body.appendChild(s);return defs}
function glyph(f,w,c){const e=GLY[f].w[w][c];if(!e)return null;
  const id='g'+f[0]+w+'_'+c.codePointAt(0).toString(36);
  if(e[1]&&!made.has(id)){made.add(id);const p=document.createElementNS(NS,'path');p.id=id;p.setAttribute('d',e[1]);sprite().appendChild(p)}
  return {adv:e[0],id:e[1]?id:null}}
const isH=c=>{const x=c.charCodeAt(0);return (x>=0xAC00&&x<=0xD7A3)||(x>=0x3130&&x<=0x318F)||(x>=0x1100&&x<=0x11FF)};
const OPEN='([{<「『“‘',CLOSE=')]}>」』”’.,!?:;%°·~…';
function tokens(s,keep){if(keep)return [s];const out=[];let cur='';
  for(const ch of s){if(cur){const pv=cur[cur.length-1];let brk=false;
      if(isH(pv)&&isH(ch))brk=true;else if(isH(pv)||isH(ch))brk=!(OPEN.includes(pv)||CLOSE.includes(ch));
      if(brk){out.push(cur);cur=''}}
    cur+=ch}
  if(cur)out.push(cur);return out}
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
function html(text,cs){
  const f=/EthSerif/.test(cs.fontFamily)?'serif':'pret';
  const w=pickW(f,parseInt(cs.fontWeight)||400),fs=parseFloat(cs.fontSize),ls=parseFloat(cs.letterSpacing)||0;
  const [ra,rd]=MET(f,fs);
  let LH=parseFloat(cs.lineHeight);if(!(LH>0))LH=NLH(f,fs);
  const by=f3((LH-(ra+rd))/2+ra);
  const pre=/pre/.test(cs.whiteSpace),keep=cs.wordBreak==='keep-all',ul=/underline/.test(cs.textDecorationLine),uy=f3(by+fs*.1),uh=f3(Math.max(1,fs*.06));
  const sh=cs.textShadow&&cs.textShadow!=='none'?cs.textShadow.match(/^(rgba?\([^)]+\))\s+(.+)$/):null;
  const one=ch=>{const g=glyph(f,w,ch);if(!g){missed.add(f+w+ch);return '<ot-m>'+esc(ch)+'</ot-m>'}
    const gw=f3(g.adv*fs/1000+ls);
    return '<svg class="og" style="width:'+gw+'px!important;height:'+f3(LH)+'px!important" width="'+gw+'" height="'+f3(LH)+'" viewBox="0 0 '+gw+' '+f3(LH)+'" aria-hidden="true">'+(g.id?'<use href="#'+g.id+'" transform="translate(0 '+by+') scale('+(+(fs/1000).toFixed(5))+')"/>':'')+(ul?'<rect y="'+uy+'" width="'+gw+'" height="'+uh+'"/>':'')+'</svg>'};
  const space=()=>{const g=glyph(f,w,' ');const a=g?g.adv:250,sw=f3(a*fs/1000+ls);
    return ul?'<ot-s class="ul" style="width:'+sw+'px;height:'+f3(LH)+'px;background-position:0 '+uy+'px;background-size:100% '+uh+'px"></ot-s>':'<ot-s style="word-spacing:'+sw+'px"> </ot-s>'};
  let out='';
  const lines=pre?text.split('\n'):[text];
  lines.forEach((ln,li)=>{
    if(li)out+='<br>';
    const parts=ln.split(/(\s+)/);
    for(const p of parts){if(!p)continue;
      if(/^\s+$/.test(p)){out+=space();continue}
      for(const t of tokens(p,keep)){const cs2=[...t];
        out+=cs2.length===1?one(cs2[0]):'<ot-w>'+cs2.map(one).join('')+'</ot-w>'}}});
  return '<ot-t data-by="'+by+'" data-lh="'+f3(LH)+'"'+(sh?' style="filter:drop-shadow('+sh[2]+' '+sh[1]+')"':'')+'>'+out+'<ot-r>'+esc(text)+'</ot-r></ot-t>'}
function conv(tn){
  if(!tn.parentNode)return;let el=tn.parentElement;if(!el||el.namespaceURI===NS)return;
  if(el.localName==='ot-t'){const t=document.createTextNode(tn.nodeValue);el.replaceWith(t);tn=t;el=t.parentElement;if(!el)return}
  if(el.closest('ot-t,script,style,textarea,select,option,[data-noot]'))return;
  const v=tn.nodeValue;if(!v)return;
  const cs=getComputedStyle(el);
  if(/^\s+$/.test(v)){/* 공백만 있는 글자: 양옆이 모두 인라인일 때만 실제로 폭을 차지함 */
    const inl=n=>n&&(n.nodeType===3?/\S/.test(n.nodeValue):/^inline/.test(getComputedStyle(n).display));
    if(/flex|grid/.test(cs.display)||!inl(tn.previousSibling)||!inl(tn.nextSibling))return}
  /* line-height:normal 은 글꼴(없음)에 따라 달라지므로, 글자가 놓인 줄을 만드는 요소들에 원래 글꼴 기준 값을 직접 박아 줌 */
  for(let a=el;a&&a!==root;a=a.parentElement){const c=getComputedStyle(a);
    if(c.lineHeight==='normal'){const f=/EthSerif/.test(c.fontFamily)?'serif':'pret';a.style.lineHeight=NLH(f,parseFloat(c.fontSize))+'px'}
    if(!/^inline/.test(c.display))break}
  const cs2=getComputedStyle(el);
  const t=document.createElement('template');t.innerHTML=html(v,cs2);tn.replaceWith(t.content);
  let bc=el;while(bc&&bc!==root&&/^inline$/.test(getComputedStyle(bc).display))bc=bc.parentElement;if(bc)dirty.add(bc)}
/* 한 줄에 크기가 다른 글자가 섞이면 브라우저는 베이스라인을 맞춰 줄 높이를 정한다.
   글자 상자를 위쪽 정렬로 쓰는 대신, 서로 다른 베이스라인 위치만큼 위쪽 여백을 줘서 같은 결과를 만든다. */
const dirty=new Set();
function fixLines(){for(const c of dirty){if(!c.isConnected)continue;
  c.querySelectorAll(':scope > .ostrut').forEach(x=>x.remove());
  const runs=[...c.querySelectorAll('ot-t')].filter(r=>{let a=r.parentElement;while(a&&a!==c&&/^inline$/.test(getComputedStyle(a).display))a=a.parentElement;return a===c});
  if(!runs.length)continue;
  const cs=getComputedStyle(c),f=/EthSerif/.test(cs.fontFamily)?'serif':'pret',fs=parseFloat(cs.fontSize),[ra,rd]=MET(f,fs);
  const L=parseFloat(cs.lineHeight)>0?parseFloat(cs.lineHeight):NLH(f,fs),byc=(L-(ra+rd))/2+ra;
  let mx=byc;runs.forEach(r=>{mx=Math.max(mx,+r.dataset.by)});
  const same=runs.every(r=>Math.abs(+r.dataset.by-mx)<.01)&&Math.abs(byc-mx)<.01;
  const set=(r,d)=>r.querySelectorAll(':scope > svg.og,:scope > ot-w > svg.og').forEach(g=>{d>.01?g.style.setProperty('margin-top',f3(d)+'px','important'):g.style.removeProperty('margin-top')});
  runs.forEach(r=>set(r,same?0:mx-(+r.dataset.by)));
  if(!same&&mx-byc>.01&&!/flex|grid/.test(cs.display)){const g=document.createElementNS(NS,'svg');g.setAttribute('class','og ostrut');g.setAttribute('width','0');g.setAttribute('height',f3(L));g.setAttribute('aria-hidden','true');g.style.cssText='width:0!important;height:'+f3(L)+'px!important;margin-top:'+f3(mx-byc)+'px!important';c.insertBefore(g,c.firstChild)}}
  dirty.clear()}
function scan(n){if(n.nodeType===3){conv(n);return}if(n.nodeType!==1)return;ghosts(n);
  const w=document.createTreeWalker(n,NodeFilter.SHOW_TEXT),l=[];let x;while(x=w.nextNode())l.push(x);l.forEach(conv)}
/* 입력창 placeholder·드롭다운 표시 글자도 같은 방식으로 그린다(직접 타이핑하는 글자는 브라우저 기본 글꼴) */
const ro=window.ResizeObserver?new ResizeObserver(es=>es.forEach(e=>place(e.target))):null;
function place(el){const g=el._gh;if(!g||!el.isConnected)return;const cs=getComputedStyle(el);
  g.style.left=el.offsetLeft+'px';g.style.top=el.offsetTop+'px';g.style.width=el.offsetWidth+'px';g.style.height=el.offsetHeight+'px'}
function ghostText(el){const g=el._gh;if(!g)return;let t='';
  if(el.tagName==='SELECT'){const o=el.options[el.selectedIndex];t=o?o.text:''}else t=el.value?'':(el.getAttribute('placeholder')||'');
  if(g.textContent!==t)g.textContent=t}
function ghost(el){if(el._gh||el.type==='hidden'||el.type==='checkbox'||el.type==='radio'||el.type==='range')return;
  if(el.tagName!=='SELECT'&&!el.getAttribute('placeholder'))return;
  const cs=getComputedStyle(el),g=document.createElement('ot-gh');g.setAttribute('aria-hidden','true');
  const ph=el.tagName!=='SELECT';const col=ph?getComputedStyle(el,'::placeholder').color:cs.color;
  /* select는 글자만 투명하게, 입력창은 placeholder를 CSS로 투명하게 */
  g.style.cssText='position:absolute;pointer-events:none;display:flex;align-items:'+(el.tagName==='TEXTAREA'?'flex-start':'center')+';overflow:hidden;white-space:'+(el.tagName==='TEXTAREA'?'pre-wrap':'nowrap')+';font:'+cs.font+';letter-spacing:'+cs.letterSpacing+';color:'+(ph?col:cs.color)+';padding:'+cs.padding+';border:'+cs.borderWidth+' solid transparent;line-height:'+(cs.lineHeight==='normal'?'normal':cs.lineHeight)+';text-align:'+cs.textAlign;
  if(!ph)el.style.color='transparent';
  /* 스크롤 영역 안의 입력창: 스크롤 영역이 위치 기준(relative)이 아니면 글자가 안 따라 움직이므로 기준으로 지정 */
  for(let a=el.parentElement;a&&a!==el.offsetParent&&a!==root;a=a.parentElement){const o=getComputedStyle(a);if(/(auto|scroll)/.test(o.overflowY+o.overflowX)&&o.position==='static')a.style.position='relative'}
  el.after(g);el._gh=g;place(el);ghostText(el);if(ro)ro.observe(el)}
function ghosts(n){if(n.nodeType!==1)return;(n.matches('select,input,textarea')?[n]:[...n.querySelectorAll('select,input,textarea')]).forEach(ghost)}
let mo=null,root=null;
function start(r){root=r;const cfg={childList:true,subtree:true,characterData:true};
  mo=new MutationObserver(ms=>{mo.disconnect();
    for(const m of ms){if(m.type==='characterData')conv(m.target);else m.addedNodes.forEach(scan)}
    fixLines();mo.observe(root,cfg)});
  root.addEventListener('input',e=>ghostText(e.target));root.addEventListener('change',e=>ghostText(e.target));
  scan(root);fixLines();mo.observe(root,cfg)}
return {start,scan,missed,get miss(){return missed.size}}})();
