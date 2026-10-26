/* «Проект раньше и сейчас»: две башни из одного спрайта, каждая в своей рамке, 12 кадров в секунду */
(function(){
var root=document.getElementById('pg-tw');if(!root)return;
var d=root.querySelector('.twd'),N=+d.dataset.n,cvs=[].slice.call(root.querySelectorAll('canvas')),im=new Image(),ok=false,W=480,H=270,still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function draw(i){if(!ok)return;cvs.forEach(function(cv){var x=cv.getContext('2d'),sx=+cv.dataset.x,w=cv.width;x.clearRect(0,0,w,H);x.imageSmoothingEnabled=false;x.drawImage(im,(i%12)*W+sx,Math.floor(i/12)*H,w,H,0,0,w,H)});root.classList.toggle('big',i>12)}
im.onload=function(){ok=true;draw(still?N-1:0)};im.src=d.dataset.src;
var raf,t0;function fr(ts){if(!t0)t0=ts;var i=Math.min(N-1,Math.floor((ts-t0)/1000*12));draw(i);if(i<N-1)raf=requestAnimationFrame(fr)}
function play(){cancelAnimationFrame(raf);t0=0;raf=requestAnimationFrame(fr)}
root.querySelector('.ab-re').addEventListener('click',function(){still?draw(N-1):play()});
if(still||!('IntersectionObserver' in window))return;
var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){var go=function(){ok?play():setTimeout(go,150)};go();io.disconnect()}},{threshold:.5});io.observe(root);
})();
