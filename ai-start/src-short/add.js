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
