/* «Почему одних нейросетей мало»: две 3D-сцены в дизеринге, кадры из спрайтов 12×9 по 480×270, 12 кадров в секунду */
(function(){
var root=document.getElementById('pg-birds');if(!root)return;
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,N=108,COLS=12,W=480,H=270,FPS=12;
function capA(f){return f>=196?'Проект стоит. Одним навыком его не взять':'Попытка '+(f<72?1:f<144?2:3)+' — снова только генерация'}
function capB(f){return f<40?'Насмотренность: видит, куда бить':f<88?'База дизайна: бьёт сразу по трём фронтам':f<128?'Работа с заказчиком: точно в главное':f<176?'Нейросети: быстро добивают':'Проект взят'}
var S=[['a',capA],['b',capB]].map(function(d){var box=root.querySelector('.ab-'+d[0]),cv=box.querySelector('canvas'),cap=box.querySelector('.cap'),im=new Image(),s={cv:cv,x:cv.getContext('2d'),cap:cap,im:im,ok:false,fn:d[1],box:box};im.onload=function(){s.ok=true;draw(s,still?N-1:0)};im.src=cv.dataset.src;return s});
function draw(s,i){if(!s.ok)return;s.x.clearRect(0,0,W,H);s.x.imageSmoothingEnabled=false;s.x.drawImage(s.im,(i%COLS)*W,Math.floor(i/COLS)*H,W,H,0,0,W,H);var f=1+2*i;s.cap.textContent=s.fn(f);s.box.classList.toggle('end',i>=N-12)}
var raf=null,t0=0;
function frame(ts){if(!t0)t0=ts;var i=Math.min(N-1,Math.floor((ts-t0)/1000*FPS));S.forEach(function(s){draw(s,i)});if(i<N-1)raf=requestAnimationFrame(frame)}
function play(){if(raf)cancelAnimationFrame(raf);t0=0;raf=requestAnimationFrame(frame)}
root.querySelector('.ab-re').addEventListener('click',function(){still?S.forEach(function(s){draw(s,N-1)}):play()});
if(still||!('IntersectionObserver' in window)){S.forEach(function(s){draw(s,N-1)})}else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var go=function(){if(S.every(function(s){return s.ok}))play();else setTimeout(go,150)};go();io.disconnect()}})},{threshold:.45});io.observe(root)}
})();
