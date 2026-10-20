(function(){
var D=__DATA__, IMG=__IMG__, CODE=__CODE__;
var app=document.getElementById('app');
var ORDER=[]; D.modules.forEach(function(m){m.lessons.forEach(function(id){ORDER.push(id)})});
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function typo(x){x=x.replace(/(\d) (\d{3})(?!\d)/g,'$1\u00a0$2').replace(/(\d) (pt|sp|dp|px|₽|%|мин|сек|ч|дн|дней|дня|день|раз|из)(?=[^A-Za-zА-Яа-яЁё]|$)/g,'$1\u00a0$2');return x.replace(/ (\u2014|\u2013) /g,'\u00a0$1 ').replace(/(^|[ (\u00ab\u00a0])([A-Za-z\u0410-\u042f\u0430-\u044f\u0401\u0451]{1,2}) (?=\S)/g,'$1$2\u00a0').replace(/(^|[ (\u00ab\u00a0])([A-Za-z\u0410-\u042f\u0430-\u044f\u0401\u0451]{1,2}) (?=\S)/g,'$1$2\u00a0').replace(/(\d)([\u2013-])(\d)/g,'$1\u2060$2\u2060$3').replace(/([A-Za-z\u0410-\u044f\u0401\u0451])-([A-Za-z\u0410-\u044f\u0401\u0451]{1,3})(?![A-Za-z\u0410-\u044f\u0401\u0451])/g,'$1\u2011$2').replace(/(^|[^A-Za-z\u0410-\u044f\u0401\u0451])([A-Za-z\u0410-\u044f\u0401\u0451]{1,3})-(?=[A-Za-z\u0410-\u044f\u0401\u0451])/g,'$1$2\u2011')}
function t(s){return typo(esc(s)).replace(/&lt;(\/?)(b|i)&gt;/g,'<$1$2>')}
function ul(a){return '<ul class="plain">'+(a||[]).map(function(x){return '<li>'+t(x)+'</li>'}).join('')+'</ul>'}
function ol(a){return '<ol>'+(a||[]).map(function(x){return '<li>'+t(x)+'</li>'}).join('')+'</ol>'}
function modOf(id){for(var i=0;i<D.modules.length;i++){if(D.modules[i].lessons.indexOf(id)>-1)return D.modules[i]}return null}
function title(id){return D.titles[id]||id}

/* ---------- экран телефона из блоков ---------- */
function screen(blocks,inter,focus){
  var h='<div class="bar"></div>';
  (blocks||[]).forEach(function(b){
    var hi=b.hi?(focus?' fx':' hi'):'', tap=(inter&&b.tap)?' tap':'', tag=(inter&&b.tap)?'button':'div', at=(inter&&b.tap)?' type="button" data-next':'';
    switch(b.k){
      case 'big': h+='<div class="big'+hi+'">'+t(b.text)+'</div>';break;
      case 'ttl': h+='<div class="ttl'+hi+'">'+t(b.text)+'</div>';break;
      case 'lbl': h+='<div class="lbl'+hi+'">'+t(b.text)+'</div>';break;
      case 'text': h+='<div class="text'+hi+'">'+t(b.text)+'</div>';break;
      case 'field': h+='<'+tag+at+' class="field'+hi+tap+'">'+t(b.text)+'</'+tag+'>';break;
      case 'item': h+='<'+tag+at+' class="item'+hi+tap+'"><span>'+t(b.text)+'</span>'+(b.small?'<small>'+t(b.small)+'</small>':'')+'</'+tag+'>';break;
      case 'btn': h+='<'+tag+at+' class="btn'+hi+tap+'">'+t(b.text)+'</'+tag+'>';break;
      case 'ghost': h+='<'+tag+at+' class="ghost'+tap+'">'+t(b.text)+'</'+tag+'>';break;
      case 'chips': var it=b.items||[]; h+='<div class="chips c'+Math.min(4,Math.max(2,it.length))+(focus&&b.hi?' fx':'')+'">'+it.map(function(x,i){var on=(b.on===i); return (inter&&b.tap&&on)?'<button type="button" data-next class="chip hi tap">'+esc(x)+'</button>':'<div class="chip'+(on?(focus?' sel':' hi'):'')+'">'+esc(x)+'</div>'}).join('')+'</div>';break;
      case 'tabs': h+='<div class="tabs t'+(b.items||[]).length+'">'+(b.items||[]).map(function(x,i){return '<span'+(b.on===i?' class="on"':'')+'>'+esc(x)+'</span>'}).join('')+'</div>';break;
      case 'map': h+='<div class="map"></div>';break;
      case 'img': h+='<div class="img">'+t(b.text||'')+'</div>';break;
      case 'blk': for(var i=0;i<(b.n||1);i++)h+='<div class="blk"></div>';break;
      case 'timer': h+='<div class="timer">'+t(b.text)+'</div>';break;
      case 'row': h+='<div class="row'+(focus&&b.hi?' fx':'')+'"><span>'+t(b.l)+'</span><span>'+t(b.r)+'</span></div>';break;
      case 'fab': h+='<'+tag+at+' class="fab'+tap+'">'+t(b.text||'+')+'</'+tag+'>';break;
      case 'stars': h+='<div class="stars">★★★★★</div>';break;
      case 'sp': h+='<div class="sp"></div>';break;
      case 'cols': h+='<div class="cols">'+(b.items||[]).map(function(x){return '<div class="colc">'+(b.img!==false?'<i></i>':'')+'<span>'+esc(x)+'</span></div>'}).join('')+'</div>';break;
      case 'grid': h+='<div class="gridov">'+new Array((b.cols||4)+1).join('<i></i>')+'</div>';break;
      case 'home': h+='<div class="homeind"></div>';break;
      case 'gap': h+='<div class="gapm"><span>'+esc(b.text||'')+'</span></div>';break;
    }
  });
  return h;
}

/* ---------- блоки ---------- */
var R={
 p:function(b){return '<p>'+t(b.text)+'</p>'},
 sub:function(b){return '<h3>'+t(b.text)+'</h3>'},
 list:function(b){return ul(b.items)},
 quote:function(b){return '<div class="quote"><q>'+t(b.text)+'</q><span>'+t(b.who)+'</span>'+(b.note?'<p>'+t(b.note)+'</p>':'')+'</div>'},
 formula:function(b){return '<div class="formula"><div class="parts">'+b.parts.map(function(p){return '<div class="part"><b>'+t(p.b)+'</b><small>'+t(p.small)+'</small></div>'}).join('')+'</div>'+(b.example?'<div class="row"><div class="ex">'+t(b.example)+'</div>'+(b.copy?'<button class="copy" type="button" data-copy="'+esc(b.copy)+'">Скопировать формулу</button>':'')+'</div>':'')+'</div>'},
 chain:function(b){return '<div class="chain" style="--n:'+b.nodes.length+'">'+b.nodes.map(function(n){return '<div class="node'+(n.on?' on':'')+'"><b>'+t(n.b)+'</b>'+(n.small?'<small>'+t(n.small)+'</small>':'')+'</div>'}).join('')+'</div>'},
 terms:function(b){return '<dl>'+b.items.map(function(x){return '<dt>'+t(x[0])+'</dt><dd>'+t(x[1])+'</dd>'}).join('')+'</dl>'},
 steps:function(b){return '<ol class="steps">'+b.items.map(function(s){return '<li><div><div class="t">'+t(s.t)+'</div><div class="d">'+t(s.d)+'</div></div></li>'}).join('')+'</ol>'},
 pairs:function(b){return '<div class="pairs">'+b.groups.map(function(g){
   function side(c,x,l){return '<div class="'+c+'"><span class="tag">'+l+'</span><div class="q">'+t(x.q)+'</div><div class="why">'+t(x.why)+'</div>'+(x.src?'<span class="src">'+t(x.src)+'</span>':'')+'</div>'}
   return (g.rule?'<div class="rule">'+t(g.rule)+'</div>':'')+'<div class="pair">'+side('bad',g.bad,'Плохо')+side('good',g.good,'Хорошо')+'</div>'}).join('')+'</div>'},
 table:function(b){return '<div class="scroll"><table><thead><tr>'+b.head.map(function(h){return '<th>'+t(h)+'</th>'}).join('')+'</tr></thead><tbody>'+b.rows.map(function(r){return '<tr>'+r.map(function(c){return '<td>'+t(c)+'</td>'}).join('')+'</tr>'}).join('')+'</tbody></table></div>'},
 files:function(b){return '<div class="files">'+b.items.map(function(f){var a=f.href?'<a class="btn-main fbtn" href="'+esc(f.href)+'" target="_blank" rel="noopener"'+(f.download?' download':'')+'>'+t(f.btn||'Открыть')+'</a>':'<span class="fsoon">Ссылка скоро будет здесь</span>';var c=f.copy?'<button class="copy" type="button" data-copy="'+esc(f.copy)+'">Скопировать текст</button>':'';return '<div class="fcard"><span class="kind">'+t(f.kind)+'</span><h3>'+t(f.title)+'</h3><p>'+t(f.text)+'</p><div class="frow">'+a+c+'</div></div>'}).join('')+'</div>'},
 note:function(b){return '<div class="note"><b>'+t(b.title)+'</b><p>'+t(b.text)+'</p></div>'},
 two:function(b){return '<div class="two">'+b.boxes.map(function(x){return '<div class="box"><h3>'+t(x.title)+'</h3>'+(x.text?'<p>'+t(x.text)+'</p>':'')+(x.items?ul(x.items):'')+'</div>'}).join('')+'</div>'},
 tree:function(b){return '<div class="tree"><div class="root"><b>'+t(b.root.b)+'</b>'+(b.root.small?'<small>'+t(b.root.small)+'</small>':'')+'</div><div class="stem"></div><div class="branches" style="--n:'+Math.min(4,b.leaves.length)+'">'+b.leaves.map(function(l){return '<div class="leaf"><b>'+t(l.b)+'</b>'+(l.small?'<small>'+t(l.small)+'</small>':'')+(l.scr?'<span class="scr">'+t(l.scr)+'</span>':'')+'</div>'}).join('')+'</div></div>'},
 myths:function(b){return '<div class="myths">'+b.items.map(function(m){return '<div class="myth"><div class="m"><i>Миф</i><span>'+t(m.myth)+'</span></div><div class="r"><i>На самом деле</i><span>'+t(m.truth)+'</span></div></div>'}).join('')+'</div>'},
 canvas:function(b){
   var n=b.columns.length, gt='grid-template-columns:repeat('+n+',minmax(0,1fr))';
   var g=b.groups?'<div class="cv-groups" style="'+gt+'">'+b.groups.map(function(x){return '<div style="grid-column:span '+x.span+'">'+t(x.label)+'</div>'}).join('')+'</div>':'';
   var R=b.columns[0].length, ev=R>1&&b.columns.every(function(c){return c.length===R});
   return '<div class="canvas">'+g+'<div class="cv-cols'+(ev?' even':'')+'" style="'+gt+(ev?';--r:'+(2*R):'')+'">'+b.columns.map(function(col){return '<div class="cv-col">'+col.map(function(c){
     return '<div class="cv-cell'+(c.hl?' hl':'')+'"><div class="cv-head">'+(c.kicker?'<i>'+t(c.kicker)+'</i>':'')+'<b>'+t(c.title)+'</b></div><div class="cv-body">'+(c.hint?'<em>'+t(c.hint)+'</em>':'')+(c.items||[]).map(function(i){return '<span>'+t(i)+'</span>'}).join('')+'</div></div>'}).join('')+'</div>'}).join('')+'</div>'+(b.caption?'<span class="cap">'+t(b.caption)+'</span>':'')+'</div>'},
 flow:function(b){
   function node(n,no){return '<div class="fl-n '+(n.kind||'screen')+'">'+(no?'<em class="fl-no">'+no+'</em>':'')+'<span>'+t(n.text)+(n.note?'<small>'+t(n.note)+'</small>':'')+'</span></div>'}
   var kinds={};
   var N=b.nodes.length, per=N<=6?N:Math.ceil(N/2);
   var h='<div class="fl" style="--n:'+per+'">'+b.nodes.map(function(n,i){kinds[n.kind||'screen']=1;
     var br=n.branch?'<div class="fl-br"'+(n.branch.to?' data-to="'+n.branch.to+'"':'')+'><i>'+t(n.branch.label)+'</i>'+n.branch.nodes.map(function(x){kinds[x.kind||'screen']=1;return node(x)}).join('')+'</div>':'';
     return '<div class="fl-col'+(((i+1)%per===0&&i<N-1)?' rowend':'')+((i%per===0&&i>0)?' rowstart':'')+'">'+node(n,('0'+(i+1)).slice(-2))+br+'</div>'}).join('')+'</div>';
   var names={start:'начало',screen:'экран',action:'действие человека',decision:'развилка',error:'ошибка',end:'цель достигнута'};
   var lg='<div class="legend">'+['start','screen','action','decision','error','end'].filter(function(k){return kinds[k]}).map(function(k){return '<span class="l-'+k+'">'+names[k]+'</span>'}).join('')+'</div>';
   return h+lg+(b.caption?'<span class="cap" style="text-align:left">'+t(b.caption)+'</span>':'')},
 wire:function(b){return '<div class="wires w'+b.screens.length+'">'+b.screens.map(function(s,i){return '<div class="wire"><span class="wn">'+('0'+(i+1)).slice(-2)+'</span><div class="phone'+(b.focus?' focus':'')+'">'+screen(s.blocks,false,b.focus)+'</div><b>'+t(s.title)+'</b>'+(s.note?'<small>'+t(s.note)+'</small>':'')+'</div>'}).join('')+'</div>'+(b.caption?'<span class="cap" style="text-align:left">'+t(b.caption)+'</span>':'')},
 shots:function(b){var it=b.items||[]; if(!it.length)return '';
   var n=Math.min(4,it.filter(function(x){return !x.wide}).length||1);
   return (b.title?'<h3>'+t(b.title)+'</h3>':'')+(b.lead?'<p>'+t(b.lead)+'</p>':'')+(function(){var o='',run=[];function fl(){if(run.length){o+='<div class="shots" style="--n:'+Math.min(4,run.length)+'">'+run.map(F).join('')+'</div>';run=[]}}
     it.forEach(function(x){if(x.wide){fl();o+=F(x)}else run.push(x)});fl();return o})()+(b.caption?'<span class="cap" style="text-align:left">'+t(b.caption)+'</span>':'');
   function F(x){var src=IMG[x.img]||(window.NOIMG?'':((window.IMGBASE||'img/')+x.img+(x.ext||'.webp')));
     if(!src)return '<figure class="shotc noimg'+(x.wide?' wide':'')+'"><a class="frame" href="'+esc(x.link||'#')+'" target="_blank" rel="noopener"><span>'+t(x.app||'')+'</span><em>открыть экран в SCRN →</em></a><figcaption><b>'+t(x.title)+'</b>'+(x.note?'<small>'+t(x.note)+'</small>':'')+'</figcaption></figure>';
     return '<figure class="shotc'+(x.wide?' wide':'')+'"><a class="frame" href="'+esc(src)+'" target="_blank" rel="noopener" title="Открыть крупно"><img loading="lazy" alt="'+esc((x.app?x.app+': ':'')+x.title)+'" src="'+esc(src)+'"'+(x.src?' data-f="'+esc(x.src)+'" onerror="this.onerror=null;this.src=this.dataset.f"':'')+'></a><figcaption>'+(x.app?'<i>'+t(x.app)+(x.tag?' · '+t(x.tag):'')+'</i>':'')+'<b>'+t(x.title)+'</b>'+(x.note?'<small>'+t(x.note)+'</small>':'')+(x.link?'<a class="srcl" href="'+esc(x.link)+'" target="_blank" rel="noopener">открыть в SCRN</a>':'')+'</figcaption></figure>'}},
 shot:function(b){return IMG[b.img]?'<div class="shotrow"><div class="phone shot"><img alt="'+esc(b.alt||'')+'" src="'+IMG[b.img]+'"></div><div class="side" style="display:flex;flex-direction:column;gap:10px"><div class="stitle" style="font-family:var(--display);font-size:24px;color:var(--ink)">'+t(b.title)+'</div><p>'+t(b.text)+'</p>'+(b.items?ul(b.items):'')+'</div></div>':''},
 'case':function(b,ctx){
   var id='c'+(ctx.cases.length); ctx.cases.push(b.steps);
   return '<div class="case"><div class="casehead"><span class="kind">'+t(b.kind)+'</span><h3>'+t(b.title)+'</h3>'+(b.sub?'<p>'+t(b.sub)+'</p>':'')+'</div>'+(b.story?'<div class="qquote">'+t(b.story)+'</div>':'')+'<div class="slider" data-case="'+id+'" tabindex="0"></div><span class="cap">'+t(b.caption||'Схемы экранов, не скриншоты')+(b.link?' · <a href="'+esc(b.link)+'" target="_blank" rel="noopener">'+t(b.linkText||'настоящие экраны в каталоге SCRN')+'</a>':'')+'</span>'+(b.verdict?'<div class="verdict"><b>Что забрать себе</b><span>'+t(b.verdict)+'</span></div>':'')+'</div>'},
 ai:function(b){return '<div class="two"><div class="box"><h3>Отдаём нейросети</h3>'+ul(b.give)+'</div><div class="box"><h3>Оставляем себе</h3>'+ul(b.keep)+'</div></div>'+(b.steps?'<h3>По шагам</h3><ol class="steps">'+b.steps.map(function(s){return '<li><div><div class="t">'+t(s.t)+'</div>'+(s.d?'<div class="d">'+t(s.d)+'</div>':'')+'</div></li>'}).join('')+'</ol>':'')+(b.prompt?'<div class="qquote">'+t(b.prompt)+'</div>':'')+(b.check?'<div class="box"><h3>Проверь ответ</h3>'+ul(b.check)+'</div>':'')+(b.mistake?'<div class="note"><b>Ошибка новичка</b><p>'+t(b.mistake)+'</p></div>':'')+(b.passport?'<div class="note"><b>В паспорт проекта</b><p>'+t(b.passport)+'</p></div>':'')},
 task:function(b){return '<p><b>Что должно получиться:</b> '+t(b.result)+'</p>'+(b.need?'<div class="note"><b>Что понадобится</b><p>'+t(b.need)+'</p></div>':'')+'<div class="task">'+b.parts.map(function(p){return '<div class="box"><h3>'+t(p.title)+'</h3>'+ol(p.steps)+'</div>'}).join('')+'</div>'+(b.submit?'<h3>Что сдавать</h3>'+R.table({head:['Что','В каком виде','Как проверяют'],rows:b.submit}):'')+(b.note?'<div class="note"><b>На что куратор смотрит в первую очередь</b><p>'+t(b.note)+'</p></div>':'')+(b.stuck?'<h3>Если застрял</h3>'+R.faq({items:b.stuck}):'')},
 check:function(b,ctx){return '<p>Отметки сохраняются в этом браузере.</p><div class="check">'+b.items.map(function(x,i){return '<label><input type="checkbox" data-ck="'+ctx.id+'-'+i+'"><span>'+t(x)+'</span></label>'}).join('')+'</div>'},
 faq:function(b){return '<div>'+b.items.map(function(x){return '<details><summary>'+t(x[0])+'</summary><p>'+t(x[1])+'</p></details>'}).join('')+'</div>'}
};

/* ---------- «где мы» ---------- */
function where(L){
  var cur=ORDER.indexOf(L.id), curMod=modOf(L.id);
  var h='<div class="wslide"><div class="where" id="where">';
  D.modules.forEach(function(m){
    h+='<div class="col'+(m===curMod?' cur':'')+'"><span>'+t(m.short||m.name)+'</span>';
    m.lessons.forEach(function(id){var k=ORDER.indexOf(id);var c=k<cur?'done':k===cur?'cur':'later';
      h+='<a class="pill '+c+'" href="#/'+id+'">'+t(D.short[id]||title(id))+'</a>'});
    h+='</div>';
  });
  h+=(D.later&&D.later.length?'<div class="col far"><span>Дальше</span>'+D.later.map(function(x){return '<span class="pill later">'+t(x)+'</span>'}).join('')+'</div>':'')+'</div><div class="wnav"><button type="button" data-w="-1" aria-label="Модули левее">←</button><button type="button" data-w="1" aria-label="Модули правее">→</button></div></div>';
  var st=D.stages[(L.stage&&L.stage.n||curMod.stage)-1], s=L.stage||{};
  h+='<div class="stagebar">'+D.stages.map(function(x,i){var n=i+1,cn=st.n;return '<div class="'+(n===cn?'on':n<cn?'done':'')+'"><i>этап '+n+'</i><b>'+t(x.name)+'</b></div>'}).join('')+'</div>';
  h+='<div class="stagecard"><div class="big"><span class="num">0'+st.n+'</span><div><b>'+t(st.name)+'</b><small>'+t(st.what)+'</small></div></div><div class="facts">'+
    '<div class="fact"><i>На входе в урок</i><span>'+t(s.input)+'</span></div>'+
    '<div class="fact on"><i>Что делаем в этом уроке</i><span>'+t(s.doing)+'</span></div>'+
    '<div class="fact"><i>На выходе</i><span>'+t(s.output)+'</span></div>'+
    '<div class="fact"><i>Где это пригодится дальше</i><span>'+t(s.next)+'</span></div>'+
    (s.agent?'<div class="fact" style="grid-column:1/-1"><i>Кто помогает из нейросети</i><span>'+t(s.agent)+'</span></div>':'')+
  '</div></div>';
  return h;
}

/* ---------- страницы ---------- */
function corner(a,b){return '<div class="corner"><span>PERASPERADASTRA\nUX/UI-DESIGNER</span><span>'+esc(a)+(b?'\n'+esc(b):'')+'</span></div>'}
function lesson(id){
  var L=D.lessons[id], m=modOf(id), ctx={id:id,cases:[]};
  if(!L){return home()}
  var secs=[{id:'gde',nav:'Где мы',title:'Где мы сейчас',html:where(L)}];
  L.sections.forEach(function(s){secs.push({id:s.id,nav:s.nav,title:s.title,intro:s.intro,html:s.blocks.map(function(b){return R[b.type]?R[b.type](b,ctx):''}).join('')})});
  if(L.quiz&&L.quiz.length)secs.push({id:'test',nav:'Тест',title:'Тест',intro:L.quiz.length+' вопросов. После каждого ответа будет объяснение. Ошибиться можно: вариант останется подсвеченным, а ты выберешь другой.',html:'<div class="quiz" id="quiz" aria-live="polite"></div>'});
  var k=ORDER.indexOf(id), prev=ORDER[k-1], next=ORDER[k+1];
  var h='<div class="top"><a href="#/">← Все методички</a><span class="eyebrow">'+t(m.name)+' · урок '+(m.lessons.indexOf(id)+(m.lessons[0]==='s0'?0:1))+' из '+(m.lessons.length-(m.lessons[0]==='s0'?1:0))+'</span></div>';
  h+='<header>'+corner('МОДУЛЬ «'+m.name.toUpperCase()+'»','МЕТОДИЧКА К УРОКУ')+'<div class="hrow"><h1>'+t(L.title)+'</h1><span class="lnum" aria-hidden="true">'+('0'+(ORDER.indexOf(id)+(ORDER[0]==='s0'?0:1))).slice(-2)+'</span></div><p class="lead">'+t(L.lead)+'</p><span class="save">Сохрани, чтобы не потерять</span><nav aria-label="Разделы">'+secs.map(function(s,i){return '<a href="#/'+id+'/'+s.id+'" data-n="'+('0'+(i+1)).slice(-2)+'">'+t(s.nav)+'</a>'}).join('')+'</nav></header>';
  var F=(D.figs||{})[id], fk=ORDER.indexOf(id);
  secs.forEach(function(s,i){var fr='';if(F&&s.id==='glavnoe')fr='<div class="figrow'+(fk%2?' flip':'')+'"><div class="fig"><span class="fig-read">наведи курсор</span><div class="stage" data-fig="'+F[0]+'" data-label="'+esc(F[2])+'"></div></div><div class="figtext"><b>'+t(F[1])+'</b><p>'+t(F[2])+'</p></div></div>';
    h+='<section id="s-'+s.id+'">'+corner(('0'+(i+1)).slice(-2)+' / '+L.title.toUpperCase())+'<h2>'+t(s.title)+'</h2>'+(s.intro?'<p>'+t(s.intro)+'</p>':'')+s.html+fr+'</section>'});
  h+='<div class="pager">'+(prev?'<a href="#/'+prev+'">← Предыдущий урок<b>'+t(title(prev))+'</b></a>':'<a href="#/">← Оглавление<b>Все методички</b></a>')+(next&&D.lessons[next]?'<a class="next" href="#/'+next+'">Следующий урок →<b>'+t(title(next))+'</b></a>':'<a class="next" href="#/">Оглавление →<b>Все методички</b></a>')+'</div>';
  h+='<footer>Perasperadastra · Mission to UX/UI · примеры приложений приведены как наблюдение со стороны</footer>';
  app.innerHTML=h; document.title=L.title+': методичка'; if(window.HLmount)HLmount(app);
  var W=document.getElementById('where');if(W){var c=W.querySelector('.col.cur');var c0=W.querySelector('.col');if(c&&c0)W.scrollLeft=Math.max(0,c.offsetLeft-c0.offsetLeft);
    var cols=[].slice.call(W.querySelectorAll('.col')),raf=0,fit=function(){raf=0;var r=W.getBoundingClientRect(),m=0;cols.forEach(function(c){var b=c.getBoundingClientRect();if(b.right>r.left+24&&b.left<r.right-24)m=Math.max(m,c.offsetHeight)});if(m)W.style.height=(m+12)+'px'};
    var upd=function(){var nb=W.parentNode.querySelectorAll('.wnav button');nb[0].disabled=W.scrollLeft<4;nb[1].disabled=W.scrollLeft>W.scrollWidth-W.clientWidth-4;if(!raf)raf=requestAnimationFrame(fit)};upd();fit();W.addEventListener('scroll',upd,{passive:true});
    W.parentNode.querySelector('.wnav').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var col=W.querySelector('.col');W.scrollBy({left:(+b.dataset.w)*((col?col.offsetWidth:220)+10)*2,behavior:'smooth'})})}
  bind(L,ctx);
}
/* ---------- карточка задания для ZenClass: #/zadanie/<id> ---------- */
var ZPAGE={1:'Бриф',2:'Исследование',3:'Проектирование',4:'Визуал и дизайн-система',5:'Тестирование',6:'Кейс'};
function zadanie(id){
  var L=D.lessons[id], m=modOf(id); if(!L)return home();
  var T=null; L.sections.forEach(function(s){s.blocks.forEach(function(b){if(b.type==='task'&&!T)T=b})}); if(!T)return lesson(id);
  var k=ORDER.indexOf(id)+(ORDER[0]==='s0'?0:1), num=('0'+k).slice(-2), st=(L.stage&&L.stage.n)||m.stage;
  var sd=0;for(var q=0;q<id.length;q++)sd=(sd*31+id.charCodeAt(q))%997;var rn=function(a,b){sd=(sd*73+41)%997;return Math.round(a+(b-a)*sd/997)};
  var zs='--x1:'+rn(55,95)+'%;--y1:'+rn(0,12)+'%;--x2:'+rn(0,40)+'%;--y2:'+rn(30,55)+'%;--x3:'+rn(50,100)+'%;--y3:'+rn(70,95)+'%';
  var h='<header class="zone" style="'+zs+'">'+corner('ЗАДАНИЕ К УРОКУ','МОДУЛЬ «'+m.name.toUpperCase()+'»')+
    '<div class="hrow"><div class="ztitle"><span class="zkick">Домашнее задание · урок '+num+'</span><h1>'+t(L.title)+'</h1></div><span class="lnum" aria-hidden="true">'+num+'</span></div>'+
    '<div class="zres"><i>Что должно получиться</i><p>'+t(T.result)+'</p></div>';
  if(T.parts&&T.parts.length){var n=T.parts.length;
    h+='<div class="zpart"><h2>'+(n===2?'Два шага':n===3?'Три шага':n+' '+plural(n,'шаг','шага','шагов'))+' до сдачи</h2><div class="zroute" style="--n:'+n+'">'+T.parts.map(function(p,i){var ti=String(p.title).replace(/^Часть\s*\d+\.\s*/,'');
      return '<div class="zstep"><span class="zn">'+('0'+(i+1)).slice(-2)+'</span><b>'+t(ti)+'</b></div>'}).join('')+'</div></div>';
  }
  if(T.submit&&T.submit.length){
    h+='<div class="zpart"><h2>Что сдать</h2><div class="zsub">'+T.submit.map(function(r){
      return '<div class="zitem"><span class="zbox" aria-hidden="true"></span><div><b>'+t(r[0])+'</b><p>'+t(r[1])+'</p>'+(r[2]?'<p class="zchk"><i>Как проверяют</i>'+t(r[2])+'</p>':'')+'</div></div>'}).join('')+'</div>'+
      (T.note?'<div class="zcur"><i>Куратор смотрит первым</i><p>'+t(T.note)+'</p></div>':'')+'</div>';
  }
  var how;
  if(id==='s0')how=['Сделай скриншот проекта «Диплом» с паспортом.','Допиши одну строку: какой скилл стоит и когда в календаре слоты на курс.','Отправь скриншот и строку в ответе ниже.'];
  else if(id==='s1')how=['Собери все части задания в одном фрейме в Figma или в одном документе.','Открой доступ по ссылке на комментирование.','Пришли ссылку в ответе ниже.'];
  else how=['Положи результат на страницу «'+ZPAGE[st]+'» в своей копии шаблона в Figma.','Заполни блок «Работа с нейросетью»'+(st===4?', картинкам от нейросети поставь бейдж «Сгенерировано ИИ»':'')+' и поставь статус «На проверке».','Пришли ссылку на файл с доступом на комментирование в ответе ниже.'];
  h+='<div class="zpart"><h2>Как сдать</h2><div class="zhow">'+how.map(function(x,i){return '<div class="zh'+(i===how.length-1?' on':'')+'"><span class="zn">'+(i+1)+'</span><p>'+t(x)+'</p></div>'}).join('')+'</div>'+
    '<p class="zmore">Пошаговая инструкция, самопроверка и «Если застрял» — в методичке этого урока, раздел «Задание».</p></div></header>';
  h+='<footer>Perasperadastra · Mission to UX/UI</footer>';
  app.innerHTML=h; document.title='Задание: '+L.title;
}
function plural(n,a,b,c){var x=n%10,y=n%100;return x===1&&y!==11?a:x>=2&&x<=4&&(y<12||y>14)?b:c}
function home(){
  var n=(ORDER[0]==='s0')?-1:0;
  var h='<header>'+corner('PER ASPERA AD ASTRA','МЕТОДИЧКИ К УРОКАМ')+'<span class="kicker">Методички курса</span><h1 class="brand">Mission<br>to UX/UI</h1><p class="lead"><b>По одной на каждый урок.</b> Что прошли, что запомнить, шаблон, плохо и хорошо, два кейса по шагам, подробное задание и тест.</p><span class="save">Сохрани, чтобы не потерять</span></header>';
  h+='<section>'+corner('КАРТА КУРСА')+'<h2>Шесть этапов диплома</h2><p><b>Диплом — мобильное приложение.</b> Мы идём к нему шестью этапами. В каждой методичке первый блок показывает, на каком этапе ты сейчас и что на нём делаешь.</p><div class="stagebar">'+D.stages.map(function(x){return '<div><i>этап '+x.n+'</i><b>'+t(x.name)+'</b><small>'+t(x.what)+'</small></div>'}).join('')+'</div></section>';
  D.modules.forEach(function(m,mi){
    h+='<section>'+corner('МОДУЛЬ '+('0'+(mi+1)).slice(-2),'ЭТАП '+m.stage)+'<h2>'+t(m.name)+'</h2><p>'+t(m.about)+'</p><div class="cards">'+m.lessons.map(function(id){n++;var L=D.lessons[id];
      var F=(D.figs||{})[id];return '<a class="lcard'+(L?'':' off')+(F?' withfig':'')+'" href="#/'+id+'">'+(F?'<div class="micro" data-fig="'+F[0]+'" data-micro="1"></div>':'')+'<span class="n">'+('0'+n).slice(-2)+'</span><span><b>'+t(title(id))+'</b><small>'+t(L?(L.card||''):'готовится')+'</small></span></a>'}).join('')+'</div></section>';
  });
  h+='<footer>Perasperadastra · Mission to UX/UI</footer>';
  app.innerHTML=h; document.title='Методички курса'; if(window.HLmount)HLmount(app);
}
/* схемы пути: линии-соединители между шагами, перенос строки и подписи развилок */
var FLOW_OPP={'да':'нет','нет':'да','есть':'нет','yes':'no','no':'yes'};
function flowDraw(fl){
  var old=fl.querySelector(':scope>svg.fl-lines'); if(old)old.remove();
  fl.querySelectorAll(':scope>.fl-lab').forEach(function(x){x.remove()});
  var cols=[].slice.call(fl.querySelectorAll(':scope>.fl-col')); if(!cols.length)return;
  var R=fl.getBoundingClientRect(), NS='http://www.w3.org/2000/svg', RAD=8;
  var svg=document.createElementNS(NS,'svg'); svg.setAttribute('class','fl-lines'); svg.setAttribute('aria-hidden','true');
  svg.setAttribute('width',R.width); svg.setAttribute('height',R.height);
  var mid='flA'+(flowDraw.n=(flowDraw.n||0)+1);
  svg.innerHTML='<defs><marker id="'+mid+'" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0.6 L7.4,4 L0,7.4 z" class="fl-head"/></marker></defs>';
  function box(e){var b=e.getBoundingClientRect();return {l:b.left-R.left,r:b.right-R.left,t:b.top-R.top,b:b.bottom-R.top,cx:(b.left+b.right)/2-R.left,cy:(b.top+b.bottom)/2-R.top}}
  /* ломаная со скруглёнными углами: точки идут только по горизонтали и вертикали */
  function poly(pts){
    var d='M'+pts[0][0]+','+pts[0][1];
    for(var k=1;k<pts.length-1;k++){
      var p0=pts[k-1],p1=pts[k],p2=pts[k+1];
      var l1=Math.hypot(p1[0]-p0[0],p1[1]-p0[1]), l2=Math.hypot(p2[0]-p1[0],p2[1]-p1[1]);
      if(l1<0.5||l2<0.5)continue;
      var r=Math.min(RAD,l1/2,l2/2);
      var bx=p1[0]-(p1[0]-p0[0])/l1*r, by=p1[1]-(p1[1]-p0[1])/l1*r, ax=p1[0]+(p2[0]-p1[0])/l2*r, ay=p1[1]+(p2[1]-p1[1])/l2*r;
      d+=' L'+bx+','+by+' Q'+p1[0]+','+p1[1]+' '+ax+','+ay;
    }
    var e=pts[pts.length-1]; return d+' L'+e[0]+','+e[1];
  }
  function line(pts,cls){
    var p=document.createElementNS(NS,'path');p.setAttribute('d',poly(pts));p.setAttribute('class','fl-line'+(cls?' '+cls:''));p.setAttribute('marker-end','url(#'+mid+')');svg.appendChild(p);
    var c=document.createElementNS(NS,'circle');c.setAttribute('cx',pts[0][0]);c.setAttribute('cy',pts[0][1]);c.setAttribute('r',2.6);c.setAttribute('class','fl-port'+(cls?' '+cls:''));svg.appendChild(c);
  }
  function label(txt,x,y){var s=el('span','fl-lab',txt);fl.appendChild(s);var w=s.offsetWidth||30;x=Math.max(w/2+4,Math.min(R.width-w/2-4,x));s.style.left=x+'px';s.style.top=y+'px'}
  function opp(t){t=(t||'').trim().toLowerCase().split(/[ ,]/)[0];return FLOW_OPP[t]||null}
  var mains=cols.map(function(c){return c.querySelector(':scope>.fl-n')});
  /* строки: колонки с одинаковым верхом */
  var rows=[]; cols.forEach(function(c){var bb=box(c),t=Math.round(bb.t); var r=rows.length&&Math.abs(rows[rows.length-1].t-t)<4?rows[rows.length-1]:null; if(!r){r={t:t,bottom:0};rows.push(r)} r.bottom=Math.max(r.bottom,bb.b); c._row=rows.length-1});
  /* основной путь */
  for(var i=0;i<mains.length-1;i++){
    var a=box(mains[i]), z=box(mains[i+1]), sameRow=cols[i]._row===cols[i+1]._row;
    var bi=cols[i].querySelector(':scope>.fl-br>i'), out=bi?opp(bi.textContent):null;
    if(sameRow){
      var x1=a.r+3, x2=z.l-3, mx=(x1+x2)/2;
      line(Math.abs(a.cy-z.cy)<2?[[x1,a.cy],[x2,z.cy]]:[[x1,a.cy],[mx,a.cy],[mx,z.cy],[x2,z.cy]]);
      if(out) label(out,mx,a.cy-12);
    } else {
      /* перенос строки: вправо, вниз в промежуток между строками, влево и вниз в первый шаг новой строки */
      var row=rows[cols[i]._row], nrow=rows[cols[i+1]._row], gx=Math.min(a.r+13,R.width-7), yMid=row.bottom+(nrow.t-row.bottom)/2;
      line([[a.r+3,a.cy],[gx,a.cy],[gx,yMid],[z.cx,yMid],[z.cx,z.t-3]]); cols[i+1]._wrapY=yMid; cols[i+1]._wrapX=[z.cx,gx];
      if(out) label(out,(gx+z.cx)/2,yMid);
    }
  }
  /* ветки: от развилки вниз к своим шагам */
  cols.forEach(function(c,i){
    var nodes=[].slice.call(c.querySelectorAll(':scope>.fl-br>.fl-n')); if(!nodes.length)return;
    var prev=box(mains[i]);
    nodes.forEach(function(n){var b=box(n); line([[prev.cx,prev.b+3],[b.cx,b.t-3]]); prev=b});
  });
  /* возврат ветки на основной путь: data-to — номер шага */
  cols.forEach(function(c,i){
    var br=c.querySelector(':scope>.fl-br[data-to]'); if(!br)return;
    var to=+br.getAttribute('data-to')-1; if(!(to>=0&&to<mains.length))return;
    var nodes=br.querySelectorAll(':scope>.fl-n'); if(!nodes.length)return;
    var L=box(nodes[nodes.length-1]), T=box(mains[to]), tc=cols[to], tHasBr=!!tc.querySelector(':scope>.fl-br');
    var rowB=rows[c._row], rowT=rows[tc._row], lowY=T.b-Math.min(10,(T.b-T.t)/4);
    if(to===i){ /* петля к своей же развилке: по левому краю */
      var xs=Math.min(L.l,T.l)-12; line([[L.l-3,L.cy],[xs,L.cy],[xs,lowY],[T.l-3,lowY]],'back'); return;
    }
    if(tc._wrapY!=null&&L.cx>=Math.min(tc._wrapX[0],tc._wrapX[1])&&L.cx<=Math.max(tc._wrapX[0],tc._wrapX[1])&&tc._row>c._row){ /* цель — начало следующей строки: вливаемся в линию переноса */
      var pth=document.createElementNS(NS,'path');pth.setAttribute('d',poly([[L.cx,L.b+3],[L.cx,tc._wrapY]]));pth.setAttribute('class','fl-line back');svg.appendChild(pth);
      var c0=document.createElementNS(NS,'circle');c0.setAttribute('cx',L.cx);c0.setAttribute('cy',L.b+3);c0.setAttribute('r',2.6);c0.setAttribute('class','fl-port back');svg.appendChild(c0);
      var j=document.createElementNS(NS,'circle');j.setAttribute('cx',L.cx);j.setAttribute('cy',tc._wrapY);j.setAttribute('r',3);j.setAttribute('class','fl-join');svg.appendChild(j);
      return;
    }
    if(tc._row===c._row){ /* та же строка: под строкой и вверх в цель, у каждого обхода своя полоса */
      rowB.k=(rowB.k||0)+1; var lane=rowB.bottom+4+rowB.k*8;
      if(!tHasBr){ line([[L.cx,L.b+3],[L.cx,lane],[T.cx,lane],[T.cx,T.b+3]],'back'); }
      else { var sx=to<i?T.r+13:T.l-13; line([[L.cx,L.b+3],[L.cx,lane],[sx,lane],[sx,lowY],[to<i?T.r+3:T.l-3,lowY]],'back'); }
      return;
    }
    if(tc._row>c._row){ /* цель в следующих строках: вниз до промежутка над её строкой */
      var prevB=rows[tc._row-1].bottom, ly=prevB+(rowT.t-prevB)*0.78, tx=T.cx+(cols[to-1]&&cols[to-1]._row!==tc._row?14:0);
      line([[L.cx,L.b+3],[L.cx,ly],[tx,ly],[tx,T.t-3]],'back'); return;
    }
    /* цель в строке выше: по левому полю вверх, под строку цели, вверх в неё */
    rowT.k=(rowT.k||0)+1; var lx=7, ly2=rowT.bottom+4+rowT.k*8;
    line([[L.l-3,L.cy],[lx,L.cy],[lx,ly2],[T.cx-14,ly2],[T.cx-14,T.b+3]],'back');
  });
  fl.insertBefore(svg,fl.firstChild);
}
function flowsInit(root){
  root.querySelectorAll('.fl').forEach(function(fl){
    flowDraw(fl);
    if(window.ResizeObserver){var w=0;new ResizeObserver(function(){var nw=fl.getBoundingClientRect().width;if(Math.abs(nw-w)>1){w=nw;flowDraw(fl)}}).observe(fl)}
  });
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){root.querySelectorAll('.fl').forEach(flowDraw)});
}
function el(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e}
function store(k,v){try{if(v===undefined){return JSON.parse(localStorage.getItem(k)||'{}')||{}}localStorage.setItem(k,JSON.stringify(v))}catch(e){return {}}}

function bind(L,ctx){
  flowsInit(app);
  var KEY='paaa-guide-check', saved=store(KEY)||{};
  app.querySelectorAll('[data-ck]').forEach(function(b){var id=b.getAttribute('data-ck');if(saved[id])b.checked=true;
    b.addEventListener('change',function(){saved[id]=b.checked;store(KEY,saved)})});
  app.querySelectorAll('[data-copy]').forEach(function(btn){var text=btn.getAttribute('data-copy');
    btn.addEventListener('click',function(){var done=function(){btn.textContent='Скопировано';setTimeout(function(){btn.textContent='Скопировать формулу'},1600)};
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(done).catch(function(){btn.textContent=text})}else{btn.textContent=text}})});
  app.querySelectorAll('header nav a').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();var s=document.getElementById('s-'+a.getAttribute('href').split('/').pop());if(s)s.scrollIntoView({behavior:'smooth',block:'start'})})});
  /* слайдеры */
  app.querySelectorAll('.slider').forEach(function(box){
    var steps=ctx.cases[+box.getAttribute('data-case').slice(1)], k=0;
    var phone=el('div','phone'), side=el('div','side'); box.appendChild(phone); box.appendChild(side);
    function go(n){k=Math.max(0,Math.min(steps.length-1,n));draw()}
    function draw(){
      var st=steps[k]; phone.innerHTML=screen(st.screen,true);
      var tp=phone.querySelector('[data-next]');
      if(tp){tp.setAttribute('aria-label','Дальше');tp.addEventListener('click',function(){go(k===steps.length-1?0:k+1)})}
      side.textContent='';
      side.appendChild(el('div','stepn','Шаг '+(k+1)+' из '+steps.length));
      side.appendChild(el('div','stitle',st.t)); side.appendChild(el('div','snote',st.n));
      if(st.p){var part=el('div','spart');part.appendChild(el('i',null,st.p[0]));part.appendChild(document.createTextNode(st.p[1]));side.appendChild(part)}
      var dots=el('div','dots');
      steps.forEach(function(_,j){var d=el('button');d.type='button';d.setAttribute('aria-label','Шаг '+(j+1));if(j===k)d.setAttribute('aria-current','true');d.addEventListener('click',function(){go(j)});dots.appendChild(d)});
      side.appendChild(dots);
      var nav=el('div','snav'), prev=el('button','btn-ghost','Назад'), next=el('button','btn-main',k===steps.length-1?'С начала':'Дальше');
      prev.type='button';next.type='button';prev.disabled=k===0;
      prev.addEventListener('click',function(){go(k-1)}); next.addEventListener('click',function(){go(k===steps.length-1?0:k+1)});
      nav.appendChild(prev);nav.appendChild(next);side.appendChild(nav);
      side.appendChild(el('div','hint',k===steps.length-1?'Сценарий пройден':(tp?'Нажми на оранжевый элемент на экране':'Нажми «Дальше»')));
    }
    box.addEventListener('keydown',function(e){if(e.key==='ArrowRight'){go(k+1)}else if(e.key==='ArrowLeft'){go(k-1)}});
    draw();
  });
  /* тест */
  var root=document.getElementById('quiz'); if(!root)return;
  var Q=L.quiz, i=0, firstTry=0, missed=false;
  function render(){
    root.textContent=''; if(i>=Q.length){return finish()}
    var q=Q[i]; missed=false;
    var bar=el('div','qbar'), fill=el('i'); fill.style.width=(i/Q.length*100)+'%'; bar.appendChild(fill); root.appendChild(bar);
    root.appendChild(el('div','qmeta','Вопрос '+(i+1)+' из '+Q.length));
    root.appendChild(el('div','qtext',q.q));
    if(q.quote)root.appendChild(el('div','qquote',q.quote));
    var opts=el('div','opts'), fb=el('div'), foot=el('div','qfoot');
    q.opts.forEach(function(o,n){
      var b=el('button','opt',o.t); b.type='button'; b.setAttribute('data-k','АБВГД'.charAt(n));
      b.addEventListener('click',function(){
        fb.className='fb '+(o.ok?'ok':'no'); fb.textContent='';
        fb.appendChild(el('b',null,o.ok?'Верно':'Не совсем')); fb.appendChild(el('span',null,o.why));
        if(o.ok){b.classList.add('is-right'); if(!missed)firstTry++;
          opts.querySelectorAll('.opt').forEach(function(x){x.disabled=true});
          foot.textContent=''; foot.appendChild(el('span','qmeta',missed?'Получилось не с первой попытки':'С первой попытки'));
          var next=el('button','btn-main',i===Q.length-1?'Показать результат':'Следующий вопрос'); next.type='button';
          next.addEventListener('click',function(){i++;render();root.scrollIntoView({block:'nearest'})});
          foot.appendChild(next); next.focus();
        }else{missed=true; b.classList.add('is-wrong'); b.disabled=true; foot.textContent=''; foot.appendChild(el('span','qmeta','Выбери другой вариант'))}
      });
      opts.appendChild(b);
    });
    root.appendChild(opts); root.appendChild(fb); root.appendChild(foot);
  }
  function finish(){
    var bar=el('div','qbar'), fill=el('i'); fill.style.width='100%'; bar.appendChild(fill); root.appendChild(bar);
    root.appendChild(el('div','qmeta','Результат')); root.appendChild(el('div','score',firstTry+' из '+Q.length));
    var msg=firstTry===Q.length?'Все ответы с первой попытки. Можно садиться за задание.':firstTry>=Q.length-2?'Почти всё с первой попытки. Перечитай раздел «Плохо и хорошо» и переходи к заданию.':'Часть ответов получилась не сразу. Вернись к шагам и парам «плохо и хорошо», потом пройди тест ещё раз.';
    root.appendChild(el('p',null,msg));
    var foot=el('div','qfoot'), again=el('button','btn-ghost','Пройти ещё раз'); again.type='button';
    again.addEventListener('click',function(){i=0;firstTry=0;render()}); foot.appendChild(again); root.appendChild(foot);
  }
  render();
}
var last='';
var FORCE=null;
function route(){
  var p=(FORCE!==null?FORCE:(location.hash||'#/')).replace(/^#\/?/,'').split('/'), id=p[0], sec=p[1]; FORCE=null;
  if(id==='_code'&&CODE[sec]){last='';app.innerHTML='<section><h2>Код: '+esc(title(sec)||sec)+'</h2><p>Скопируй всё целиком.</p><button class="btn-main" id="cpy" type="button">Скопировать код</button><textarea id="code" style="width:100%;height:60vh;background:#191919;color:#8e8e8c;border:1px solid #2a2a2a;border-radius:10px;font:12px monospace;padding:12px"></textarea></section>';var ta=document.getElementById('code');(function(){var b=atob(CODE[sec]),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text().then(function(x){ta.value=x;document.getElementById('cpy').textContent='Скопировать код ('+x.length+' знаков)'})})();document.getElementById('cpy').addEventListener('click',function(){var b=this;ta.focus();ta.select();var ok=false;try{ok=document.execCommand('copy')}catch(e){}if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(ta.value).then(function(){b.textContent='Скопировано'}).catch(function(){b.textContent=ok?'Скопировано':'Выдели и скопируй вручную'})}else{b.textContent=ok?'Скопировано':'Выдели и скопируй вручную'}});return}
  if(id==='zadanie'&&D.lessons[sec]){ if(last!=='z'+sec){zadanie(sec); window.scrollTo(0,0)} last='z'+sec; return }
  if(id&&D.lessons[id]){ if(last!==id){lesson(id); window.scrollTo(0,0)} last=id;
    if(sec){var s=document.getElementById('s-'+sec); if(s)s.scrollIntoView()} }
  else{last='';home();window.scrollTo(0,0)}
}
window.addEventListener('hashchange',route); route();
/* переходы работают и там, где ссылки с решёткой заблокированы (предпросмотр, вложенные окна) */
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#/"]'); if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey)return;
  if(a.closest('header nav'))return; e.preventDefault(); var h=a.getAttribute('href');
  try{ if(location.hash!==h){ history.pushState(null,'',h) } }catch(x){}
  FORCE=h; route()});
window.addEventListener('popstate',function(){route()});
})();
