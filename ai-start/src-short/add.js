(function(){
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
/* клетки 20/80: порядок появления */
document.querySelectorAll('.pg .cells i').forEach(function(c,k){c.style.setProperty('--d',(k%10)*28+Math.floor(k/10)*40)});
/* анимации запускаются, когда блок на экране (работает и во встроенном iframe) */
var els=[].slice.call(document.querySelectorAll('.pg .yt,.pg ol.cen,.pg .split,.pg .hp'));
if(still||!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('on')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}})},{threshold:.25});els.forEach(function(e){io.observe(e)})}
/* видео в карточках гайдов */
var vs=[].slice.call(document.querySelectorAll('.pg .gd video,.pg .gal video'));
function play(v,on){if(on){if(!v.src)v.src=v.dataset.src;if(!still){var p=v.play();if(p&&p.catch)p.catch(function(){})}}else v.pause()}
if('IntersectionObserver' in window){var vo=new IntersectionObserver(function(es){es.forEach(function(e){play(e.target,e.isIntersecting)})},{threshold:.4});vs.forEach(function(v){vo.observe(v)})}
})();
/* красная строка: первая строка абзаца встаёт под второе слово заголовка */
(function(){
function align(){document.querySelectorAll('.pg .head .txt').forEach(function(t){var h=t.querySelector('h2'),p=t.querySelector('p');if(!h||!p)return;
 var w=document.createTreeWalker(h,NodeFilter.SHOW_TEXT),n,first=true,r=document.createRange(),x=null,top=null,hr=h.getBoundingClientRect();
 while((n=w.nextNode())){var s=n.nodeValue,i=s.search(/\s\S/);if(i<0){continue}r.setStart(n,i+1);r.setEnd(n,i+2);var b=r.getBoundingClientRect();x=b.left-hr.left;top=b.top-hr.top;break}
 var pr=p.getBoundingClientRect(),lim=pr.width*.45;
 p.style.textIndent=(x!==null&&top<20&&x<lim)?Math.round(x)+'px':'0'})}
align();addEventListener('resize',align);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(align);
})();
