(function(){
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
/* клетки 20/80: порядок появления */
document.querySelectorAll('.pg .cells i').forEach(function(c,k){c.style.setProperty('--d',(k%10)*28+Math.floor(k/10)*40)});
/* анимации запускаются, когда блок на экране (работает и во встроенном iframe) */
var els=[].slice.call(document.querySelectorAll('.pg .yt,.pg .gw,.pg .walk,.pg .tsp,.pg ol.cen,.pg .split,.pg .hp,.pg .tri'));
if(still||!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('on')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}})},{threshold:.25});els.forEach(function(e){io.observe(e)})}
/* видео в карточках гайдов */
var vs=[].slice.call(document.querySelectorAll('.pg .gd video,.pg .gal video,.pg .th2 video,.pg .th3 video,.pg .feat video'));
function play(v,on){if(on){if(!v.src)v.src=v.dataset.src;if(!still){var p=v.play();if(p&&p.catch)p.catch(function(){})}}else v.pause()}
if('IntersectionObserver' in window){var vo=new IntersectionObserver(function(es){es.forEach(function(e){play(e.target,e.isIntersecting)})},{threshold:.4});vs.forEach(function(v){vo.observe(v)})}
})();
/* красная строка: первая строка абзаца встаёт под второе слово заголовка */
(function(){
function align(){document.querySelectorAll('.pg .head .txt').forEach(function(t){var h=t.querySelector('h2'),p=t.querySelector('p');if(!h||!p)return;
 var w=document.createTreeWalker(h,NodeFilter.SHOW_TEXT),n,first=true,r=document.createRange(),x=null,top=null,hr=h.getBoundingClientRect();
 while((n=w.nextNode())){var s=n.nodeValue,i=s.search(/\s\S/);if(i<0){continue}r.setStart(n,i+1);r.setEnd(n,i+2);var b=r.getBoundingClientRect();x=b.left-hr.left;top=b.top-hr.top;break}
 var pr=p.getBoundingClientRect(),lim=pr.width*.45;
 lim=Math.min(lim,pr.width*.22);p.style.textIndent=(x!==null&&top<20&&x<lim)?Math.round(x)+'px':'2.2em'})}
align();addEventListener('resize',align);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(align);
})();
/* во встроенном iframe (Тильда): якоря прокручивают родительскую страницу, кнопка навигации скрыта */
(function(){if(window.parent===window)return;document.documentElement.classList.add('in-frame');
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(!a)return;var el=document.getElementById(a.getAttribute('href').slice(1));if(!el)return;e.preventDefault();parent.postMessage({type:'pad-scroll',y:el.getBoundingClientRect().top+window.scrollY},'*')})})();
/* боковая навигация: части и разделы, подсветка текущего места */
(function(){
var parts=[].slice.call(document.querySelectorAll('.pg .part[id], .pg section.fin[id]'));if(!parts.length)return;
var inFrame=window.parent!==window,view=null,html='<ol>',secs=[];
function txt(e){return e?e.textContent.replace(/\s+/g,' ').trim():''}
parts.forEach(function(p){
  var isFin=p.tagName==='SECTION',h=p.querySelector('h2'),lab=isFin?'Итог':txt(h).replace(/^Часть\s+([IVX]+)\.\s*/,''),num=isFin?'→':(txt(h).match(/Часть\s+([IVX]+)/)||[])[1]||'';
  html+='<li class="rl-p" data-id="'+p.id+'"><a href="#'+p.id+'"><i>'+num+'</i>'+lab+'</a>';secs.push({id:p.id,el:p,part:p.id});
  if(!isFin){var ch='',n=p.nextElementSibling;
    while(n&&!n.classList.contains('part')&&!n.classList.contains('fin')){
      if(n.tagName==='SECTION'&&n.id){var sm=n.querySelector('.head .num small'),t=txt(sm)||txt(n.querySelector('.head h2'));
        ch+='<li data-id="'+n.id+'"><a href="#'+n.id+'">'+t+'</a></li>';secs.push({id:n.id,el:n,part:p.id})}
      n=n.nextElementSibling}
    if(ch)html+='<ol>'+ch+'</ol>'}
  html+='</li>'});
html+='</ol>';
var nav=document.createElement('nav');nav.className='rail';nav.setAttribute('aria-label','Разделы гайда');nav.innerHTML=html;(document.querySelector('.pg')||document.body).appendChild(nav);
if(inFrame)nav.classList.add('rl-inf');
var cur=null,curP=null;
function top(e){var y=0;while(e){y+=e.offsetTop;e=e.offsetParent}return y}
function upd(){
  var vt,vh;if(inFrame){if(!view)return;vt=view.top;vh=view.h}else{vt=window.scrollY;vh=window.innerHeight}
  var start=top(parts[0])-vh*.5,on=vt>start&&vt<document.documentElement.scrollHeight-vh*1.2;
  nav.classList.toggle('rl-vis',on);
  if(inFrame)nav.style.top=(vt+vh/2-(nav.offsetParent?top(nav.offsetParent):0))+'px';
  var a=null;for(var i=0;i<secs.length;i++){if(top(secs[i].el)<=vt+vh*.5)a=secs[i];else break}
  if(a&&a.id!==cur){cur=a.id;
    [].forEach.call(nav.querySelectorAll('li'),function(li){li.classList.toggle('rl-cur',li.dataset.id===a.id);li.classList.toggle('rl-open',li.dataset.id===a.part)})}
}
var raf=0;function sch(){if(!raf)raf=requestAnimationFrame(function(){raf=0;upd()})}
if(inFrame){addEventListener('message',function(e){if(e.data&&e.data.type==='pad-view'){view={top:+e.data.top||0,h:+e.data.h||800};nav.classList.add('rl-live');sch()}})}
else{addEventListener('scroll',sch,{passive:true})}
addEventListener('resize',sch);sch();
})();
