/* «Проект 2022 и проект 2026»: башни строятся по блокам, спрайт 12 колонок по 480×270, 12 кадров в секунду */
(function(){
var root=document.getElementById('pg-tw');if(!root)return;
var cv=root.querySelector('canvas'),x=cv.getContext('2d'),im=new Image(),N=+cv.dataset.n,still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,ok=false,W=480,H=270;
function draw(i){if(!ok)return;x.clearRect(0,0,W,H);x.imageSmoothingEnabled=false;x.drawImage(im,(i%12)*W,Math.floor(i/12)*H,W,H,0,0,W,H);root.classList.toggle('big',i>12)}
im.onload=function(){ok=true;draw(still?N-1:0)};im.src=cv.dataset.src;
var raf,t0;function fr(ts){if(!t0)t0=ts;var i=Math.min(N-1,Math.floor((ts-t0)/1000*12));draw(i);if(i<N-1)raf=requestAnimationFrame(fr)}
function play(){cancelAnimationFrame(raf);t0=0;raf=requestAnimationFrame(fr)}
root.querySelector('.ab-re').addEventListener('click',function(){still?draw(N-1):play()});
if(still||!('IntersectionObserver' in window))return;
var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){var go=function(){ok?play():setTimeout(go,150)};go();io.disconnect()}},{threshold:.5});io.observe(root);
})();
