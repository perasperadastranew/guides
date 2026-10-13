/* Маскот для разбора: порт «стенда движений» (claude.ai/artifact/PV7GyEcSwrXC6uwJEsMsWM) в координаты постера 1080×1530.
   Детерминированная симуляция с шагом 1/60 — MASCOT.render(t) можно вызывать для любого t. */
window.MASCOT=(function(){
var NS='http://www.w3.org/2000/svg',ZS=1.38,M=1.45*ZS*0.9,VIO='#6f5cff';
function mk(t,a,p){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);p.appendChild(e);return e}
function cl(x){return Math.max(0,Math.min(1,x))}function lerp(a,b,k){return a+(b-a)*k}
function bez(x1,y1,x2,y2){return function(x){x=cl(x);var t=x;for(var i=0;i<6;i++){var cx=3*x1*t*(1-t)*(1-t)+3*x2*t*t*(1-t)+t*t*t-x,d=3*x1*(1-t)*(1-3*t)+3*x2*t*(2-3*t)+3*t*t;if(Math.abs(d)<1e-6)break;t-=cx/d}t=cl(t);return 3*y1*t*(1-t)*(1-t)+3*y2*t*t*(1-t)+t*t*t}}
var E={travel:bez(.65,0,.2,1),out:bez(.16,1,.3,1),outBack:bez(.2,1.45,.35,1),in:bez(.7,0,.84,0),inOut:bez(.65,0,.35,1),arrive:bez(.1,.9,.2,1)};
var OFF={blob:[[0,0,46],[-22,12,30],[22,12,30],[0,-16,30],[-13,-30,12],[13,-30,12],[0,20,34]],saucer:[[0,-16,34],[-14,-10,22],[14,-10,22],[0,-26,22],[0,-6,20],[-8,-4,18],[8,-4,18]]};
['blob','saucer'].forEach(function(k){OFF[k]=OFF[k].map(function(o){return [o[0]*M,o[1]*M,o[2]*M]})});
var el={},drops=[],P=[],V=[],lights=[],HP=[],EW,PP,GL,built=false;
var S,Q=[],cur=null,T=0,SCHED=[],si=0,K={jelly:.32,ant:.5},EV=[];function ev(n,d){EV.push([+T.toFixed(3),n,d||0])}
// формы из конструктора маскота (claude.ai/artifact/H8rShzgneTCSWyafAmWZ9P): раскладка капель, место и масштаб глаз, якорь роста
var FORMS=[{c:[[0,0,70],[-30,-30,50],[30,-30,50],[-30,30,50],[30,30,50],[0,0,50],[0,0,40]],eye:[0,-24],es:1,a:[0,0]},
 {c:[[-22,-6,34],[-22,-30,30],[-22,20,30],[-30,-50,24],[-10,10,26],[-22,-6,22],[-22,-6,22]],eye:[-22,-22],es:.72,a:[-10,0]},
 {c:[[0,-76,24],[-50,-76,22],[50,-76,22],[0,-30,24],[0,10,24],[0,50,24],[0,80,22]],eye:[0,-76],es:.7,a:[0,-76]}];
var MOODS={neutral:[1,1],curious:[1.1,1.04],focus:[1,1.08],happy:[1.06,1.16],effort:[.96,.9],wow:[1.2,.68],sleep:[.94,1]};
(function(){var o={};for(var m in MOODS)o[m]={lt:m=='sleep'?1:0,lb:0,tl:0,sc:MOODS[m][0],pr:MOODS[m][1]};o.angry={lt:.3,lb:.04,tl:20,sc:1.02,pr:.92};MOODS=o})();
function resetState(){S={x:1500,y:-400,px:1500,py:-400,vis:0,sau:1,sauT:1,tilt:0,tiltV:0,fr:{x:0,y:0,w:0,h:0,p:0,mp:null},beam:0,beamW:0,bt:null,look:[0,1],el:[0,1],stA:0,stD:[1,0],sz:1,szT:1,mood:'neutral',
  ey:{lt:0,lb:0,tl:0,sc:1,pr:1},bk:-9,ring:0,ringAt:[0,0],pen:0,penR:0,tip:[0,0],inkP:0,inkOn:0,inkA:0,bar:{x1:0,y1:0,x2:0,y2:0,p:0},grid:0,gridL:[],gaze:0,tool:{k:-1,on:0,c:[540,765],g:1},tk:[0,0,0],kick:0,kickT:0,an:[0,0,1],core:0,win:{x:0,y:0,w:0,h:0,s:0},wind:0,scanA:0,scanY:0,poi:null,idleN:0,MS:[]};
  Q=[];cur=null;T=0;si=0;EV.length=0;for(var i=0;i<7;i++){P[i]=[1500,-400];V[i]=[0,0]}if(built){el.gaze.setAttribute('d','');el.ink.setAttribute('opacity',0);el.meas.innerHTML=''}}
function step(d,f,init){return {d:d,f:f||function(){},init:init,t:0}}
function hold(d){return step(d)}
function mood(m){return step(0.001,null,function(){S.mood=m})}
function arc(a,b,p,hgt){var dx=b[0]-a[0],dy=b[1]-a[1],l=Math.hypot(dx,dy)||1,s=Math.sin(Math.PI*p)*hgt;return [lerp(a[0],b[0],p)-dy/l*s,lerp(a[1],b[1],p)+dx/l*s]}
function lookAt(x,y){var dx=x-S.x,dy=y-S.y,l=Math.hypot(dx,dy)||1;S.look=[dx/l,dy/l]}
function frameOut(){var f0;return step(0.2,function(p){S.fr.p=f0*(1-E.in(p))},function(){f0=S.fr.p})}
function beamOff(){var b0;return step(0.22,function(p){S.beamW=b0*(1-E.in(p));if(p>=1)S.beam=0},function(){b0=S.beamW})}
function tidy(keepGrid){var v;return step(0.2,function(p){var k=1-E.in(p);S.bar.p=v.b*k;if(!keepGrid)S.grid=v.g*k;S.gaze=v.z*k;S.inkA=v.i*k;S.MS.forEach(function(m){m.o=k});if(p>=1){S.inkOn=0;S.MS=[];el.meas.innerHTML='';if(S.gaze<.01)el.gaze.setAttribute('d','')}},function(){v={b:S.bar.p,g:S.grid,z:S.gaze,i:S.inkA}})}
function winOut(){var a,b;return step(0.2,function(p){var k=1-E.in(p);S.win.s=a*k;S.wind=b*k},function(){a=S.win.s;b=S.wind})}
function pre(keepGrid){var r=[];if(S.pen>0.01){var p0;r.push(step(0.12,function(p){S.pen=p0*(1-p)},function(){p0=S.pen}))}if(S.core>0.01){var c0;r.push(step(0.15,function(p){S.core=c0*(1-p)},function(){c0=S.core}))}if(S.win.s>0)r.push(winOut());if(S.beam)r.push(beamOff());if(S.fr.p>0)r.push(frameOut());if(S.bar.p>0||(!keepGrid&&S.grid>0)||S.gaze>0||S.inkOn||S.MS.length)r.push(tidy(keepGrid));return r}
// перемещение — исчезнуть, вспышка-кольцо на новом месте, появиться с открывающимися глазами
function travel(to,asSaucer,lookTo,size){var v0;return [
  step(0.11,function(p){S.vis=v0*(1-E.in(p))},function(){v0=S.vis;lookAt(to[0],to[1])}),
  step(0.12,function(p){S.ring=Math.sin(Math.PI*E.out(p))},function(){ev('blink');S.x=to[0];S.y=to[1];S.px=to[0];S.py=to[1];S.ringAt=[to[0],to[1]];for(var i=0;i<7;i++){P[i]=[to[0],to[1]];V[i]=[0,0]}S.sauT=asSaucer?1:0;S.sau=S.sauT;S.szT=size||(asSaucer?.8:.62);S.sz=S.szT;S.tilt=0;S.tiltV=0;S.mood=asSaucer?'neutral':'focus';S.ey.lt=1;if(lookTo){S.look=lookTo.slice();S.el=lookTo.slice()}}),
  step(0.18,function(p){S.vis=E.out(p);S.ring=0})]}
function hide(){var v0;return pre().concat([step(0.14,function(p){S.vis=v0*(1-E.in(p))},function(){v0=S.vis})])}
function markerPts(w,h,seed){var r=Math.min(18*ZS,w/4,h/4),A=[],i,a;function add(x,y){A.push([x,y])}
  for(i=0;i<=10;i++)add(lerp(r,w-r,i/10),0);for(i=1;i<=6;i++){a=-Math.PI/2+i/6*Math.PI/2;add(w-r+Math.cos(a)*r,r+Math.sin(a)*r)}
  for(i=1;i<=8;i++)add(w,lerp(r,h-r,i/8));for(i=1;i<=6;i++){a=i/6*Math.PI/2;add(w-r+Math.cos(a)*r,h-r+Math.sin(a)*r)}
  for(i=1;i<=10;i++)add(lerp(w-r,r,i/10),h);for(i=1;i<=6;i++){a=Math.PI/2+i/6*Math.PI/2;add(r+Math.cos(a)*r,h-r+Math.sin(a)*r)}
  for(i=1;i<=8;i++)add(0,lerp(h-r,r,i/8));for(i=1;i<=6;i++){a=Math.PI+i/6*Math.PI/2;add(r+Math.cos(a)*r,r+Math.sin(a)*r)}
  for(i=1;i<=4;i++)add(r+i/4*Math.min(60,w*0.16),-2-i*1.2);
  return A.map(function(q,k){var t=k/A.length*6.2832;return [q[0]+Math.sin(t*3.1+seed)*3+Math.sin(t*8.3+seed*1.7)*1.5,q[1]+Math.cos(t*2.7+seed*0.6)*3+Math.sin(t*9.1+seed)*1.4]})}
// рамка-маркер вокруг блока: он садится в левый верхний угол, линия выходит из него
function frameRect(r,dur){var res=pre();res=res.concat(travel([r[0]+2,r[1]+2],false,[0.72,0.7]));
  res.push(step(dur||0.42,function(p){S.fr.p=E.out(p)},function(){ev('frame');S.fr={x:r[0],y:r[1],w:r[2],h:r[3],p:0,mp:markerPts(r[2],r[3],r[0]*0.37+r[1]*0.11)};S.look=[0.72,0.7];S.mood='focus'}));
  res.push(mood('happy'));res.push(hold(0.4));res.push(mood('focus'));return res}
function ellPts(cx,cy,rx,ry){var pts=[];for(var i=0;i<=90;i++){var k=i/90,a=-2.5+k*6.283*1.12,w=1+0.05*Math.sin(k*17)+0.06*(k-0.5);pts.push([cx+Math.cos(a)*rx*w+Math.sin(k*23)*4,cy+Math.sin(a)*ry*w+Math.cos(k*19)*4])}return pts}
function setPath(e,pts,p){var n=Math.max(2,Math.ceil(pts.length*p)),d='';for(var i=0;i<n;i++)d+=(i?'L':'M')+pts[i][0].toFixed(1)+' '+pts[i][1].toFixed(1);e.setAttribute('d',d)}
// обводит карандашом
function writePts(pts,dur,keepGrid){var HO=[-44*ZS,-56*ZS],res=pre(keepGrid);res=res.concat(travel([pts[0][0]+HO[0],pts[0][1]+HO[1]],false,[0.62,0.78]));
  res.push(step(0.3,function(p){S.pen=E.outBack(p);S.penR=(1-E.out(p))*-260},function(){ev('pen',dur||1.1);S.pts=pts;S.tip=pts[0].slice();S.mood='focus';S.inkOn=1;S.inkA=1;S.inkP=0;setPath(el.ink,pts,0)}));
  res.push(step(dur||1.1,function(p){var e=E.inOut(p),f=e*(pts.length-1),i=Math.min(pts.length-2,Math.floor(f)),k=f-i;S.tip=[lerp(pts[i][0],pts[i+1][0],k),lerp(pts[i][1],pts[i+1][1],k)];S.x=S.tip[0]+HO[0];S.y=S.tip[1]+HO[1];S.inkP=e;setPath(el.ink,pts,e);S.look=[0.62,0.78]}));
  res.push(step(0.22,function(p){S.pen=1-E.in(p);S.penR=E.in(p)*200}));res.push(mood('happy'));return res}
// маленькая тарелка пролетает маршрут, за ней остаётся тонкий след
function trailPts(pts,dur,size){var HO=[0,-52*ZS],res=pre();res=res.concat(travel([pts[0][0]+HO[0],pts[0][1]+HO[1]],true,[0,1],size||.58));
  res.push(step(0.01,null,function(){ev('fly',dur);S.mood='focus';S.gaze=1;S.gpts=pts;el.gaze.setAttribute('d','')}));
  res.push(step(dur,function(p){var e=E.inOut(p),f=e*(pts.length-1),i=Math.min(pts.length-2,Math.floor(f)),k=f-i,x=lerp(pts[i][0],pts[i+1][0],k),y=lerp(pts[i][1],pts[i+1][1],k);S.x=x+HO[0];S.y=y+HO[1];S.look=[0,1];
    var d='';for(var q=0;q<=i;q++)d+=(q?'L':'M')+pts[q][0].toFixed(1)+' '+pts[q][1].toFixed(1);d+='L'+x.toFixed(1)+' '+y.toFixed(1);el.gaze.setAttribute('d',d)}));
  var v0;res.push(step(0.16,function(p){S.vis=v0*(1-E.in(p))},function(){v0=S.vis}));return res}
function spline(G,n){var pts=[];for(var i=0;i<G.length-1;i++){var p0=G[Math.max(0,i-1)],p1=G[i],p2=G[i+1],p3=G[Math.min(G.length-1,i+2)];for(var j=0;j<n;j++){var t=j/n,t2=t*t,t3=t2*t;pts.push([0.5*(2*p1[0]+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3),0.5*(2*p1[1]+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)])}}pts.push(G[G.length-1]);return pts}
function circPts(cx,cy,r,a0,turn){var n=Math.ceil(r*6.283*turn/14),o=[];for(var i=0;i<=n;i++){var a=a0+turn*6.2832*i/n;o.push([cx+Math.cos(a)*r,cy+Math.sin(a)*r])}return o}
// сетка: он схлопывается в точку и разлетается направляющими — ни тела, ни глаз
function gridBurst(lines,at){var res=pre(),v0;res=res.concat(travel(at,false,[0,0.3]));
  res.push(step(0.16,function(p){S.vis=v0*(1-E.in(p))},function(){ev('grid');v0=S.vis;S.mood='sleep';S.gridL=lines;el.grid.innerHTML='';lines.forEach(function(){mk('path',{},el.grid)})}));
  res.push(step(0.6,function(p){S.grid=p}));return res}
// размерные линии с числом
function measure(defs){var res=[];defs.forEach(function(m){var mx=(m.a[0]+m.b[0])/2,my=(m.a[1]+m.b[1])/2;res=res.concat(travel([mx+(m.hx||0),my+(m.hy||-110)],false,[m.a[0]<540?-0.4:0.4,0.9]));
  res.push(step(0.3,function(p){m.p=E.out(p)},function(){ev('meas');m.p=0;m.o=1;m.c=VIO;m.g=mk('g',{},el.meas);S.MS.push(m);S.mood='focus'}));res.push(hold(0.12))});return res}
function measColor(c,md){return step(0.3,null,function(){ev('ok');S.MS.forEach(function(m){m.c=c});S.mood=md||'happy'})}
function beamRect(b){var to=[b[0]+b[2]/2,b[1]-250],res=pre();res=res.concat(travel(to,true,[0,1],.9));
  res.push(step(0.12,function(p){S.beam=1;S.beamW=0.05*E.out(p)},function(){S.bt=b;S.look=[0,1];S.mood='effort'}));
  res.push(step(0.4,function(p){S.beamW=lerp(0.05,1,E.outBack(p))}));return res}
// «окно» из конструктора: вкладка с глазами + большая рамка, внутри течёт воздух
function windowAir(r){var TW=200,TH=112,res=pre();res=res.concat(travel([r[0]+TW/2,r[1]-TH/2+10],false,[0.55,0.83],.5));
  res.push(step(0.4,function(p){S.win.s=E.outBack(p)},function(){S.win={x:r[0],y:r[1],w:r[2],h:r[3],s:0};S.mood='focus';
    el.winB.setAttribute('x',r[0]);el.winB.setAttribute('y',r[1]);el.winB.setAttribute('width',r[2]);el.winB.setAttribute('height',r[3]);
    el.winT.setAttribute('x',r[0]-8);el.winT.setAttribute('y',r[1]-TH+8);el.winT.setAttribute('width',TW);el.winT.setAttribute('height',TH);
    var n=el.windP.length;el.windP.forEach(function(e,j){var y=r[1]+r[3]*(0.24+0.26*j),x0=r[0]+r[2]*(j==1?0.1:0.2),x1=r[0]+r[2]*(j==1?0.82:0.66),rr=j==1?40:30;
      e.setAttribute('d','M'+x0+' '+y+'H'+x1+(j==2?'a'+rr+' '+rr+' 0 1 1 '+(-rr)+' '+rr:'a'+rr+' '+rr+' 0 1 0 '+(-rr)+' '+(-rr)))})}));
  res.push(step(0.35,function(p){S.wind=p}));return res}
function arriveScan(to,scanDur){var from=[1330,-330];return [step(0.01,null,function(){S.vis=1;S.sauT=1;S.sau=1;S.szT=.95;S.sz=.95;S.mood='curious';S.x=from[0];S.y=from[1];S.px=from[0];S.py=from[1];for(var i=0;i<7;i++){P[i]=[from[0],from[1]];V[i]=[0,0]}S.look=[-0.5,0.85]}),
  step(0.95,function(p){var e=E.arrive(p),q=arc(from,to,e,150);S.x=q[0];S.y=q[1]}),
  step(0.22,function(p){S.scanA=E.out(p);S.scanY=0},function(){ev('scan',scanDur);S.mood='effort';S.look=[0,1]}),
  step(scanDur,function(p){S.scanY=1530*p;S.look=[0.35*Math.sin(p*9),1]}),
  step(0.22,function(p){S.scanA=1-E.in(p)}),mood('happy'),hold(0.35),mood('neutral')]}
function leave(){var a,f,res=pre();
  res.push(step(0.24,function(p){var k=Math.sin(Math.PI*0.5*E.out(p));S.x=a[0]-34*k*K.ant;S.y=a[1]+22*k*K.ant},function(){a=[S.x,S.y];S.sauT=1;S.szT=.9;S.mood='neutral';S.look=[0.8,-0.6]}));
  res.push(step(0.5,function(p){var e=E.in(p);S.x=lerp(f[0],1500,e);S.y=lerp(f[1],f[1]-700,e*e)},function(){f=[S.x,S.y]}));res.push(step(0.01,function(){S.vis=0}));return res}
// финальная заставка: он по очереди становится фреймом, кривой и курсором
var TLOOK=[[.3,.5],[.5,.6],[0,.8]];
// финал: тарелка между постерами → обычный комочек → фрейм, дальше он глазами обходит постеры
function toolSeq(c,g,sz,looks){var res=[];res.push(step(0.01,null,function(){S.x=c[0];S.y=c[1];S.px=c[0];S.py=c[1];for(var i=0;i<7;i++){P[i]=[c[0],c[1]];V[i]=[0,0]}S.sauT=1;S.sau=1;S.szT=sz*1.25;S.sz=sz*1.25;S.vis=0;S.mood='happy';S.look=[0,-1];S.tool={k:-1,on:1,c:c,g:g};S.tk=[0,0,0];S.ringAt=c}));
  res.push(step(0.3,function(p){S.vis=E.outBack(p)}));res.push(hold(0.3));
  res.push(step(0.001,null,function(){ev('morph');S.sauT=0;S.szT=sz*1.5;S.kick=.7;S.kickT=T;S.mood='neutral';S.look=[0,-.6]}));res.push(hold(0.5));
  res.push(step(0.001,null,function(){ev('morph');S.tool.k=0;S.kick=1;S.kickT=T;S.mood='happy';S.look=[0,.3]}));res.push(hold(0.5));
  (looks||[]).forEach(function(v){res.push(step(0.33,null,function(){S.mood='neutral';S.look=v}))});
  res.push(step(0.001,null,function(){S.look=[0,0];S.mood='happy'}));return res}
function coreOn(d){var z0;return [step(0.36,function(p){S.core=E.outBack(p)},function(){ev('idea');z0=S.szT;S.szT=1.18;S.mood='happy'}),hold(d),step(0.2,function(p){S.core=1-E.in(p)},function(){S.szT=z0})]}
function look(seq){return step(seq.d,function(p){var v=seq.f(p);S.look=v},function(){if(seq.mood)S.mood=seq.mood})}
function build(){built=true;var po=document.getElementById('poster'),svg=mk('svg',{id:'msvg',width:1080,height:1530,viewBox:'0 0 1080 1530'},po);svg.style.cssText='position:absolute;left:0;top:0;overflow:visible;z-index:6;pointer-events:none';
  var df=mk('defs',{},svg),f=mk('filter',{id:'goo','color-interpolation-filters':'sRGB',filterUnits:'userSpaceOnUse',x:-400,y:-600,width:1900,height:2700},df);
  mk('feGaussianBlur',{in:'SourceGraphic',stdDeviation:11,result:'b'},f);mk('feColorMatrix',{in:'b',values:'1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10',result:'g'},f);mk('feGaussianBlur',{in:'g',stdDeviation:8,result:'b2'},f);mk('feColorMatrix',{in:'b2',values:'0 0 0 0 .07  0 0 0 0 .05  0 0 0 0 .2  0 0 0 26 -22.4',result:'c'},f);mk('feGaussianBlur',{in:'c',stdDeviation:3,result:'cs'},f);var fm=mk('feMerge',{},f);mk('feMergeNode',{in:'g'},fm);mk('feMergeNode',{in:'cs'},fm);
  var h=mk('filter',{id:'halo',filterUnits:'userSpaceOnUse',x:-400,y:-600,width:1900,height:2700},df);mk('feGaussianBlur',{stdDeviation:32},h);el.fGoo=f;el.fHalo=h;
  var sf=mk('filter',{id:'msoft',filterUnits:'userSpaceOnUse',x:-300,y:-700,width:1700,height:2700},df);mk('feGaussianBlur',{stdDeviation:13},sf);
  var g1=mk('linearGradient',{id:'mbg1',gradientUnits:'userSpaceOnUse',x1:0,y1:0,x2:0,y2:100},df);mk('stop',{offset:0,'stop-color':'#7dff6a','stop-opacity':.85},g1);mk('stop',{offset:.55,'stop-color':'#5dff9a','stop-opacity':.4},g1);mk('stop',{offset:1,'stop-color':'#5dff9a','stop-opacity':0},g1);el.g1=g1;
  var g2=mk('linearGradient',{id:'mbg2',gradientUnits:'userSpaceOnUse',x1:0,y1:0,x2:0,y2:100},df);mk('stop',{offset:0,'stop-color':'#7dff6a','stop-opacity':.6},g2);mk('stop',{offset:1,'stop-color':'#7dff6a','stop-opacity':.12},g2);el.g2=g2;
  var g3=mk('linearGradient',{id:'mbg3',gradientUnits:'userSpaceOnUse',x1:0,y1:0,x2:0,y2:100},df);mk('stop',{offset:0,'stop-color':'#7dff6a','stop-opacity':0},g3);mk('stop',{offset:1,'stop-color':'#7dff6a','stop-opacity':.3},g3);el.g3=g3;
  el.scan=mk('g',{},svg);el.scan.style.mixBlendMode='screen';el.cone=mk('path',{fill:'url(#mbg2)',filter:'url(#msoft)'},el.scan);el.strail=mk('rect',{fill:'url(#mbg3)',x:0,width:1080},el.scan);el.band=mk('rect',{fill:'#9dff5a',filter:'url(#msoft)',x:-14,width:1108,height:26},el.scan);el.core=mk('rect',{fill:'#eaffd8',x:0,width:1080,height:4,opacity:.85},el.scan);
  el.grid=mk('g',{stroke:VIO,'stroke-width':4,'stroke-linecap':'round'},svg);
  el.gaze=mk('path',{fill:'none',stroke:VIO,'stroke-width':5.5,'stroke-linecap':'round','stroke-linejoin':'round'},svg);
  el.meas=mk('g',{},svg);
  el.ink=mk('path',{fill:'none',stroke:VIO,'stroke-width':9,'stroke-linecap':'round','stroke-linejoin':'round',opacity:0},svg);
  el.fm1=mk('path',{fill:'none',stroke:VIO,'stroke-width':9,'stroke-linecap':'round','stroke-linejoin':'round',opacity:0},svg);el.fm2=mk('path',{fill:'none',stroke:'#8f80ff','stroke-width':4,'stroke-linecap':'round','stroke-linejoin':'round',opacity:0},svg);
  el.beamG=mk('g',{opacity:0},svg);el.beams=[.45,.4,.4].map(function(o){return mk('polygon',{fill:'url(#mbg1)',opacity:o},el.beamG)});
  el.hp=mk('g',{fill:'#fff',stroke:VIO,'stroke-width':4},svg);
  el.wind=mk('g',{fill:'none',stroke:'#7a68ff','stroke-width':12,'stroke-linecap':'round',opacity:0},svg);el.windP=[0,1,2].map(function(){return mk('path',{pathLength:1,'stroke-dasharray':'0.85 2'},el.wind)});
  var gg=el.gg=mk('g',{id:'mgoo',filter:'url(#goo)',fill:VIO,stroke:VIO},svg);el.body=mk('g',{id:'mbody'},gg);
  el.halo=mk('use',{href:'#mbody',filter:'url(#halo)',opacity:.45,fill:VIO,stroke:VIO},svg);svg.insertBefore(el.halo,gg);
  el.bar=mk('path',{fill:'none','stroke-width':34,'stroke-linecap':'round'},el.body);
  el.tools=[mk('rect',{x:-84,y:-84,width:168,height:168,rx:6,stroke:'none'},el.body),
    mk('path',{d:'M-60 -112L-60 82L-18 46L12 114L52 98L22 32L84 32Z','stroke-width':6,'stroke-linejoin':'round'},el.body),
    mk('path',{d:'M-96 -104H96V-48H30V104H-30V-48H-96Z','stroke-width':4,'stroke-linejoin':'round'},el.body)];
  el.winG=mk('g',{},el.body);el.winB=mk('rect',{rx:8,fill:'none','stroke-width':16},el.winG);el.winT=mk('rect',{rx:8,stroke:'none'},el.winG);el.disc=mk('ellipse',{stroke:'none'},el.body);var dg=mk('g',{stroke:'none'},el.body);
  for(var i=0;i<7;i++)drops.push(mk('circle',{},dg));
  el.lights=mk('g',{fill:'#7dff6a'},svg);for(var i=0;i<5;i++)lights.push(mk('circle',{r:6},el.lights));
  el.pencil=mk('g',{opacity:0},svg);el.penIn=mk('g',{transform:'rotate(-122)'},el.pencil);
  mk('polygon',{points:'0,0 18,-7 18,7',fill:'#14110f'},el.penIn);mk('polygon',{points:'18,-7 30,-8 30,8 18,7',fill:'#f0d9b0'},el.penIn);mk('rect',{x:30,y:-8,width:64,height:16,fill:'#7dff6a'},el.penIn);mk('rect',{x:94,y:-8,width:8,height:16,fill:'#cfd3da'},el.penIn);mk('rect',{x:102,y:-8,width:12,height:16,rx:4,fill:'#ff8fb0'},el.penIn);
  el.tov=mk('g',{},svg);[[-84,-84],[84,-84],[-84,84],[84,84]].forEach(function(q){mk('rect',{x:q[0]-7,y:q[1]-7,width:14,height:14,fill:'#fff',stroke:VIO,'stroke-width':3},el.tov)});
  mk('rect',{x:-42,y:104,width:84,height:24,rx:6,fill:VIO},el.tov);mk('text',{x:0,y:121,'text-anchor':'middle','font-size':13,'font-weight':600,fill:'#fff',style:'font-family:Onest,sans-serif'},el.tov).textContent='168 × 168';
  el.dots=mk('g',{},svg);
  var lg=mk('linearGradient',{id:'mcore',x1:0,y1:0,x2:0,y2:1},df);mk('stop',{offset:0,'stop-color':'#fff7a8'},lg);mk('stop',{offset:1,'stop-color':'#ffc24d'},lg);var gf=mk('filter',{id:'mglow',x:'-100%',y:'-100%',width:'300%',height:'300%'},df);mk('feGaussianBlur',{stdDeviation:7},gf);
  var cp=mk('clipPath',{id:'mclip'},df);el.clipC=[0,1,2,3,4,5,6].map(function(){return mk('circle',{},cp)});el.coreW=mk('g',{'clip-path':'url(#mclip)'},svg);el.coreG=mk('g',{},el.coreW);var BULB='<path d="M-11 15C-11 5 -23 1 -23 -13A23 23 0 1 1 23 -13C23 1 11 5 11 15Z" fill="url(#mcore)"/><path d="M-9 22H9M-6 29H6" stroke="#ffd66b" stroke-width="4.5" stroke-linecap="round" fill="none"/>';el.coreG.innerHTML='<g filter="url(#mglow)" opacity=".9">'+BULB+'</g>'+BULB;
  el.ring=mk('circle',{fill:'none',stroke:VIO,'stroke-width':6,opacity:0},svg);
  el.eyes=mk('g',{},svg);EW=[];PP=[];GL=[];for(var i=0;i<2;i++){EW.push(mk('path',{fill:'#fff'},el.eyes));PP.push(mk('ellipse',{fill:'#0b0a14'},el.eyes));GL.push(mk('circle',{r:1.7,fill:'#fff'},el.eyes))}
  resetState()}
function addDot(x,y,n,t0,t1){var g=mk('g',{},el.dots);mk('circle',{cx:x,cy:y,r:17,fill:VIO},g);var tx=mk('text',{x:x,y:y+7,'text-anchor':'middle','font-size':20,'font-weight':700,fill:'#fff',style:'font-family:Onest,sans-serif'},g);tx.textContent=n;g.style.transformBox='fill-box';g.style.transformOrigin='center';HP.push({g:g,t0:t0,t1:t1})}
function addHandle(x,y,t0,t1){var g=mk('rect',{x:x-11,y:y-11,width:22,height:22},el.hp);g.style.transformBox='fill-box';g.style.transformOrigin='center';HP.push({g:g,t0:t0,t1:t1})}
function tick(dt){T+=dt;
  while(si<SCHED.length&&SCHED[si][0]<=T){if(window.MPREEMPT){Q=[];cur=null}Q=Q.concat(SCHED[si][1]());si++}
  if(!cur&&Q.length){cur=Q.shift();cur.t=0;if(cur.init)cur.init()}
  if(cur){cur.t+=dt;var p=cl(cur.t/cur.d);cur.f(p);if(p>=1)cur=null}
  // когда он ничего не делает — смотрит по точкам интереса
  if(!cur&&!Q.length&&S.vis>.9&&S.poi&&S.fr.p<.5&&!S.beam){var n=Math.floor(T/0.8);if(n!==S.idleN){S.idleN=n;var q=S.poi[n%S.poi.length];lookAt(q[0],q[1])}}
  var vx=(S.x-S.px)/dt,vy=(S.y-S.py)/dt,sp=Math.hypot(vx,vy);S.px=S.x;S.py=S.y;
  S.sau+=(S.sauT-S.sau)*Math.min(1,dt*9);
  var tt=Math.max(-0.4,Math.min(0.4,vx*0.0004))*S.sau;S.tiltV+=(tt-S.tilt)*dt*70;S.tiltV*=Math.pow(0.00002,dt);S.tilt+=S.tiltV*dt*8;
  var hover=S.sau*(Math.sin(T*2.3)*8+Math.sin(T*3.7)*3),hx=S.sau*Math.sin(T*1.4)*6;
  S.sz+=(S.szT-S.sz)*Math.min(1,dt*8);var idle=S.fr.p>0.5?0.35:1;
  // растяжение по скорости держим маленьким
  var st=Math.min(0.12,sp/9000)*K.jelly*2+S.stA,d=sp>20?[vx/sp,vy/sp]:S.stD,ct=Math.cos(S.tilt),sn=Math.sin(S.tilt);
  for(var i=0;i<7;i++){var a=OFF.blob[i],b=OFF.saucer[i],ox=lerp(a[0],b[0],S.sau)*S.sz,oy=lerp(a[1],b[1],S.sau)*S.sz,r=lerp(a[2],b[2],S.sau)*S.sz;
    var al=ox*d[0]+oy*d[1],pr=-ox*d[1]+oy*d[0];al*=1+st;pr*=1-st*0.5;ox=al*d[0]-pr*d[1];oy=al*d[1]+pr*d[0];
    var tx=S.x+hx+ox*ct-oy*sn+Math.sin(T*2.1+i*1.7)*3*idle,ty=S.y+hover+ox*sn+oy*ct+Math.cos(T*1.8+i*2.3)*3*idle;
    if(S.tool.on){if(S.tool.k>=0){var Fc=FORMS[S.tool.k].c[i];tx=S.tool.c[0]+Fc[0]*S.tool.g;ty=S.tool.c[1]+Fc[1]*S.tool.g;r=Fc[2]*S.tool.g}var kq=1-Math.pow(1-(0.07+0.018*i),dt*60);P[i][0]+=(tx-P[i][0])*kq;P[i][1]+=(ty-P[i][1])*kq;V[i]=[0,0];S.dr=S.dr||[];S.dr[i]=(S.dr[i]||r)+(r-(S.dr[i]||r))*kq;continue}
    var k=lerp(1,(0.55+i*0.06),K.jelly),stf=900*k,ns=2,hh=dt/ns,dm=Math.pow(lerp(1e-12,0.000004,K.jelly),hh);
    for(var q2=0;q2<ns;q2++){V[i][0]=(V[i][0]+(tx-P[i][0])*stf*hh)*dm;V[i][1]=(V[i][1]+(ty-P[i][1])*stf*hh)*dm;P[i][0]+=V[i][0]*hh;P[i][1]+=V[i][1]*hh}
    // капли не отстают от головы дальше своего места в теле — без длинных «хвостов»
    var ddx=P[i][0]-tx,ddy=P[i][1]-ty,dl=Math.hypot(ddx,ddy),mxd=16*M*S.sz;if(dl>mxd){P[i][0]=tx+ddx/dl*mxd;P[i][1]=ty+ddy/dl*mxd}
    S.dr=S.dr||[];S.dr[i]=r}
  S.sp=sp;var ey=S.ey,mo=MOODS[S.mood]||MOODS.neutral,kk=Math.min(1,dt*11);for(var q in mo)ey[q]+=(mo[q]-ey[q])*(q=='lt'?Math.min(1,dt*20):kk);
  if(S.fr.p>0.9&&S.vis>0.9&&!S.beam){var fi=Math.floor(T/0.62),fr1=Math.abs(Math.sin(fi*12.9898)*43758.5453)%1,fr2=Math.abs(Math.sin(fi*78.233)*12543.123)%1,ga=lerp(0.3,1.25,fr1*0.6+fr2*0.4);S.look=[Math.cos(ga),Math.sin(ga)]}
  if(S.beam&&S.bt&&S.beamW>0.9)S.look=[0.45*Math.sin(T*1.6),1];
  S.el[0]+=(S.look[0]-S.el[0])*Math.min(1,dt*18);S.el[1]+=(S.look[1]-S.el[1])*Math.min(1,dt*18);
  var k12=1-Math.pow(0.88,dt*60);for(var j=0;j<3;j++)S.tk[j]+=((S.tool.on&&S.tool.k===j?1:0)-S.tk[j])*k12;S.kick*=Math.pow(0.9,dt*60);
  var et=[P[0][0]+S.el[0]*9*S.sz*ZS,P[0][1]-2+S.el[1]*8*S.sz*ZS-S.core*13*M*S.sz,lerp(0.95,0.82,S.sau)*M*S.sz*S.ey.sc];
  if(S.tool.on){if(S.tool.k>=0){var F=FORMS[S.tool.k],g=S.tool.g;et=[S.tool.c[0]+(F.eye[0]+S.el[0]*16)*g,S.tool.c[1]+(F.eye[1]+S.el[1]*12)*g,1.25*g*F.es*S.ey.sc]}for(var j=0;j<3;j++)S.an[j]+=(et[j]-S.an[j])*k12}else S.an=et;}
function draw(){var ct=Math.cos(S.tilt),sn=Math.sin(S.tilt),i;
  for(i=0;i<7;i++){drops[i].setAttribute('cx',P[i][0].toFixed(1));drops[i].setAttribute('cy',P[i][1].toFixed(1));drops[i].setAttribute('r',Math.max(0,((S.dr?S.dr[i]:0)+Math.sin(T*2.6+i)*2)*S.vis).toFixed(1))}
  var hd=P[0],dc=[hd[0]-16*M*S.sz*sn*S.sau,hd[1]+16*M*S.sz*ct*S.sau];
  el.disc.setAttribute('cx',dc[0].toFixed(1));el.disc.setAttribute('cy',dc[1].toFixed(1));el.disc.setAttribute('rx',(96*M*S.sz*S.sau*S.vis).toFixed(1));el.disc.setAttribute('ry',(19*M*S.sz*S.sau*S.vis).toFixed(1));el.disc.setAttribute('transform','rotate('+(S.tilt*57.3).toFixed(2)+' '+dc[0].toFixed(1)+' '+dc[1].toFixed(1)+')');
  lights.forEach(function(l,i){var a=T*1.5+i*1.2566,lx=Math.cos(a)*78*M*S.sz,z=Math.sin(a),x=dc[0]+lx*ct,y=dc[1]+lx*sn+3;l.setAttribute('cx',x.toFixed(1));l.setAttribute('cy',y.toFixed(1));l.setAttribute('r',((3+1.8*(z+1)/2)*S.sz).toFixed(1));l.setAttribute('opacity',(S.sau*S.vis*(z>-0.2?0.2+0.35*(z+0.2)/1.2:0)).toFixed(2))});
  var f=S.fr;if(f.mp&&f.p>0.002){var n3=Math.max(2,Math.ceil(f.mp.length*f.p)),dm='',dn='';for(var q4=0;q4<n3;q4++){dm+=(q4?'L':'M')+(f.x+f.mp[q4][0]).toFixed(1)+' '+(f.y+f.mp[q4][1]).toFixed(1);dn+=(q4?'L':'M')+(f.x+f.mp[q4][0]+Math.sin(q4*0.9)*2.2).toFixed(1)+' '+(f.y+f.mp[q4][1]+3.2+Math.cos(q4*0.7)*1.9).toFixed(1)}
    el.fm1.setAttribute('d',dm);el.fm2.setAttribute('d',dn);el.fm1.setAttribute('opacity',1);el.fm2.setAttribute('opacity',0.6)}else{el.fm1.setAttribute('opacity',0);el.fm2.setAttribute('opacity',0)}
  if(S.beam&&S.bt){var b=S.bt,w=S.beamW,by=b[1]+b[3]+70,bx=b[0]+b[2]/2,bw=(b[2]+50)/2*w,tw=40*Math.min(1,w*6);[1.12,0.9,0.66].forEach(function(k,j){el.beams[j].setAttribute('points',(dc[0]-tw*k)+','+(dc[1]+10)+' '+(dc[0]+tw*k)+','+(dc[1]+10)+' '+(bx+bw*k)+','+by+' '+(bx-bw*k)+','+by)});
    el.g1.setAttribute('y1',dc[1]);el.g1.setAttribute('y2',by+90);el.beamG.setAttribute('opacity',(S.vis*(0.96+0.04*Math.sin(T*9))).toFixed(2))}else el.beamG.setAttribute('opacity',0);
  if(S.scanA>0.01){var ys=S.scanY,sy=dc[1]+12,a=S.scanA;el.scan.style.display='';el.g2.setAttribute('y1',sy);el.g2.setAttribute('y2',Math.max(sy+10,ys));el.cone.setAttribute('d','M'+(dc[0]-34)+' '+sy+'L'+(dc[0]+34)+' '+sy+'L1090 '+ys.toFixed(1)+'L-10 '+ys.toFixed(1)+'Z');el.cone.setAttribute('opacity',(a*(.85+.15*Math.sin(T*31))).toFixed(3));
    var th=Math.min(260,ys);el.g3.setAttribute('y1',ys-th);el.g3.setAttribute('y2',ys);el.strail.setAttribute('y',(ys-th).toFixed(1));el.strail.setAttribute('height',Math.max(0,th).toFixed(1));el.strail.setAttribute('opacity',a.toFixed(3));el.band.setAttribute('y',(ys-13).toFixed(1));el.band.setAttribute('opacity',a.toFixed(3));el.core.setAttribute('y',(ys-2).toFixed(1));el.core.setAttribute('opacity',(a*.85).toFixed(3))}else el.scan.style.display='none';
  var B=S.bar;el.bar.setAttribute('d','M'+B.x1.toFixed(1)+' '+B.y1.toFixed(1)+'L'+lerp(B.x1,B.x2,B.p).toFixed(1)+' '+lerp(B.y1,B.y2,B.p).toFixed(1));el.bar.setAttribute('opacity',B.p>0.01?1:0);
  var TL=S.tool;el.tools.forEach(function(e,k){var s=S.tk[k],on=s>0.01,a=FORMS[k].a;e.style.display=on?'':'none';if(on)e.setAttribute('transform','translate('+TL.c[0]+' '+TL.c[1]+') scale('+TL.g+') translate('+a[0]+' '+a[1]+') scale('+s.toFixed(3)+') translate('+(-a[0])+' '+(-a[1])+')')});
  var sq=TL.on?S.kick*Math.sin((T-S.kickT)/0.055)*0.09:0;el.gg.setAttribute('transform',TL.on?'translate('+TL.c[0]+' '+TL.c[1]+') scale('+(1+sq).toFixed(4)+' '+(1-sq).toFixed(4)+') translate('+(-TL.c[0])+' '+(-TL.c[1])+')':'');
  var ov=S.tk[0]>0.02;el.tov.style.display=ov?'':'none';if(ov){el.tov.setAttribute('transform','translate('+TL.c[0]+' '+TL.c[1]+') scale('+(TL.g*lerp(.6,1,S.tk[0])).toFixed(3)+')');el.tov.setAttribute('opacity',cl(S.tk[0]*1.6-.5).toFixed(2))}
  var W=S.win;el.winG.style.display=W.s>0.01?'':'none';if(W.s>0.01){var wx=W.x+90,wy=W.y-40;el.winG.setAttribute('transform','translate('+wx+' '+wy+') scale('+W.s.toFixed(3)+') translate('+(-wx)+' '+(-wy)+')')}
  el.wind.setAttribute('opacity',(S.wind*.85).toFixed(2));if(S.wind>0.01)el.windP.forEach(function(e,j){var ph=((T*0.36+j*0.31)%1);e.setAttribute('stroke-dashoffset',(0.85-1.85*ph).toFixed(3))});
  var gp=el.grid.childNodes;S.gridL.forEach(function(L,i){if(!gp[i])return;var k=E.out(cl(S.grid*1.4-i*0.08)),mx=(L[0]+L[2])/2,my=(L[1]+L[3])/2;gp[i].setAttribute('d','M'+lerp(mx,L[0],k).toFixed(1)+' '+lerp(my,L[1],k).toFixed(1)+'L'+lerp(mx,L[2],k).toFixed(1)+' '+lerp(my,L[3],k).toFixed(1));gp[i].setAttribute('visibility',k>0.005?'visible':'hidden')});
  el.gaze.setAttribute('opacity',(S.gaze*.9).toFixed(2));el.ink.setAttribute('opacity',S.inkOn?S.inkA.toFixed(2):0);
  S.MS.forEach(function(m){if(!m.g)return;var e=m.p,xe=lerp(m.a[0],m.b[0],e),ye=lerp(m.a[1],m.b[1],e),hz=m.a[1]===m.b[1],t1=hz?'M'+m.a[0]+' '+(m.a[1]-18)+'v36':'M'+(m.a[0]-18)+' '+m.a[1]+'h36',t2=hz?'M'+m.b[0]+' '+(m.b[1]-18)+'v36':'M'+(m.b[0]-18)+' '+m.b[1]+'h36';
    m.g.setAttribute('opacity',m.o);m.g.innerHTML='<path d="M'+m.a[0]+' '+m.a[1]+'L'+xe.toFixed(1)+' '+ye.toFixed(1)+t1+(e>0.98?t2:'')+'" stroke="'+m.c+'" stroke-width="6" stroke-linecap="round" fill="none"/>'+(e>0.6?'<g transform="translate('+((m.a[0]+m.b[0])/2+(m.lx||0)).toFixed(1)+' '+((m.a[1]+m.b[1])/2+(m.ly==null?-58:m.ly)).toFixed(1)+') scale('+cl((e-0.6)/0.4).toFixed(2)+')"><rect x="-46" y="-28" width="92" height="52" rx="10" fill="'+m.c+'"/><text y="11" text-anchor="middle" font-size="34" font-weight="700" fill="#fff" style="font-family:Onest,sans-serif">'+m.label+'</text></g>':'')});
  HP.forEach(function(h){var p=cl((T-h.t0)/.3),o=cl((h.t1-T)/.2);h.g.style.opacity=T<h.t0?0:cl(p*2)*o;h.g.style.transform='scale('+E.outBack(p).toFixed(3)+')'});
  var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(i=0;i<7;i++){x0=Math.min(x0,P[i][0]);y0=Math.min(y0,P[i][1]);x1=Math.max(x1,P[i][0]);y1=Math.max(y1,P[i][1])}var mg=260;x0-=mg;y0-=mg;x1+=mg;y1+=mg;if(B.p>0.01){x0=-200;y0=-400;x1=1300;y1=1900}if(S.tool.on){x0=S.tool.c[0]-1400;y0=S.tool.c[1]-1400;x1=S.tool.c[0]+1400;y1=S.tool.c[1]+1400}if(S.win.s>0.01){x0=-200;y0=-200;x1=1300;y1=1750}
  [el.fGoo,el.fHalo].forEach(function(e){e.setAttribute('x',x0.toFixed(0));e.setAttribute('y',y0.toFixed(0));e.setAttribute('width',(x1-x0).toFixed(0));e.setAttribute('height',(y1-y0).toFixed(0))});
  var ey=S.ey,since=T-S.bk,auto=(T%3.4),bl=since<0.16?Math.sin(Math.PI*since/0.16):((auto<0.11&&S.sau<0.5)?Math.sin(Math.PI*auto/0.11):0),lt=Math.min(1,ey.lt+bl*(1-ey.lt));
  var es=S.an[2]*S.vis;
  el.eyes.setAttribute('transform','translate('+S.an[0].toFixed(1)+' '+S.an[1].toFixed(1)+') rotate('+(S.tilt*57.3).toFixed(1)+') scale('+es.toFixed(3)+')');
  for(i=0;i<2;i++){var cxe=i?12:-12,RX=9.5,RY=12.5,yT=-RY+lt*2*RY,yB=RY-ey.lb*2*RY,d='',TS=Math.tan((ey.tl||0)*(i?-1:1)*Math.PI/180)*(1-bl);
    if(yB-yT<1.2){d='M'+(cxe-RX)+' '+((yT+yB)/2-0.9)+'h'+(2*RX)+'v1.8h'+(-2*RX)+'z'}else{for(var k=0;k<28;k++){var an=k/28*6.2832,ex=cxe+Math.cos(an)*RX,eyy=Math.max(yT+(ex-cxe)*TS,Math.min(yB,Math.sin(an)*RY));d+=(k?'L':'M')+ex.toFixed(2)+' '+eyy.toFixed(2)}d+='Z'}
    EW[i].setAttribute('d',d);var open=Math.max(0,yB-yT),pry=Math.min(6.2*ey.pr,open/2),pcx=cxe+S.el[0]*3.6,pcy=Math.max(yT+pry,Math.min(yB-pry,1+S.el[1]*4.6));
    PP[i].setAttribute('cx',pcx.toFixed(2));PP[i].setAttribute('cy',pcy.toFixed(2));PP[i].setAttribute('rx',(5*ey.pr*Math.min(1,open/8)).toFixed(2));PP[i].setAttribute('ry',pry.toFixed(2));
    GL[i].setAttribute('cx',(pcx+1.8).toFixed(2));GL[i].setAttribute('cy',(pcy-2.2).toFixed(2));GL[i].setAttribute('opacity',open>7?1:0)}
  el.pencil.setAttribute('opacity',cl(S.pen*S.vis).toFixed(2));el.pencil.setAttribute('transform','translate('+S.tip[0].toFixed(1)+' '+S.tip[1].toFixed(1)+') rotate('+(Math.sin(T*26)*2.5*(S.inkP>0&&S.inkP<1?1:0)).toFixed(2)+') scale('+Math.max(0.01,S.pen*0.68*ZS).toFixed(3)+')');el.penIn.setAttribute('transform','rotate('+(-122+(S.penR||0)).toFixed(1)+')');
  var cs=S.core*0.62*M*S.sz*S.vis;el.coreG.style.display=S.core>0.01?'':'none';if(S.core>0.01)for(var ci=0;ci<7;ci++){el.clipC[ci].setAttribute('cx',P[ci][0].toFixed(1));el.clipC[ci].setAttribute('cy',P[ci][1].toFixed(1));el.clipC[ci].setAttribute('r',Math.max(0,(S.dr?S.dr[ci]:0)-5).toFixed(1))}
  if(S.core>0.01)el.coreG.setAttribute('transform','translate('+hd[0].toFixed(1)+' '+(hd[1]+35*M*S.sz).toFixed(1)+') rotate('+((1-Math.min(1,S.core))*-40).toFixed(1)+') scale('+cs.toFixed(3)+')');
  el.ring.setAttribute('cx',S.ringAt[0]);el.ring.setAttribute('cy',S.ringAt[1]);el.ring.setAttribute('r',(5+S.ring*34).toFixed(1));el.ring.setAttribute('opacity',S.ring.toFixed(2));}
return {
  api:{step:step,hold:hold,mood:mood,travel:travel,hide:hide,frameRect:frameRect,ellPts:ellPts,writePts:writePts,trailPts:trailPts,spline:spline,circPts:circPts,gridBurst:gridBurst,measure:measure,measColor:measColor,beamRect:beamRect,arriveScan:arriveScan,leave:leave,look:look,pre:pre,tidy:tidy,addHandle:addHandle,addDot:addDot,toolSeq:toolSeq,windowAir:windowAir,coreOn:coreOn,state:function(){return S},lookAt:lookAt,E:E},
  events:function(){return EV},time:function(){return [T,si,Q.length,cur?cur.d:-1,SCHED.length]},schedule:function(list){SCHED=list.slice().sort(function(a,b){return a[0]-b[0]})},
  render:function(t){if(!built)build();if(t<T-1e-6)resetState();var n=0;while(T+1/120<t&&n<20000){tick(1/60);n++}draw()},
  build:function(){if(!built)build()}};
})();
