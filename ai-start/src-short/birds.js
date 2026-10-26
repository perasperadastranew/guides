/* «Одной птицей проект не взять»: две сцены — одна птица против стаи со скиллами */
(function(){
var root=document.getElementById('pg-birds');if(!root)return;
var NS='http://www.w3.org/2000/svg',still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function el(t,a,p){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
var GROUND=230,SX=62,SY=166;
var BL={b1:[252,170,12,60],b2:[338,170,12,60],b3:[244,158,114,12],b4:[266,110,12,48],b5:[324,110,12,48],b6:[258,98,86,12]};
function scene(svg,id){
  var d=el('defs',{},svg),pt=el('pattern',{id:'dt'+id,width:4,height:4,patternUnits:'userSpaceOnUse'},d);el('circle',{cx:2,cy:2,r:1.15,'class':'dtc'},pt);
  el('line',{x1:0,y1:GROUND,x2:400,y2:GROUND,'class':'gr'},svg);
  /* рогатка */
  el('path',{d:'M60 '+GROUND+' L60 192 L50 166 M60 192 L70 166','class':'sl'},svg);
  var fort=el('g',{'class':'fort'},svg),B={};
  Object.keys(BL).forEach(function(k){var b=BL[k],g=el('g',{},fort);el('rect',{x:b[0],y:b[1],width:b[2],height:b[3],rx:2,fill:'url(#dt'+id+')','class':'bk'},g);B[k]={g:g,cx:b[0]+b[2]/2,cy:b[1]+b[3]/2,s:[0,0,0],e:[0,0,0],t0:0,t1:0}});
  var rg=el('g',{},fort);el('polygon',{points:'268,98 301,70 334,98',fill:'url(#dt'+id+')','class':'bk'},rg);el('line',{x1:301,y1:70,x2:301,y2:46,'class':'pole'},rg);el('path',{d:'M301 46 L322 52 L301 58 Z','class':'flag'},rg);
  B.roof={g:rg,cx:301,cy:84,s:[0,0,0],e:[0,0,0],t0:0,t1:0};
  var cg=el('g',{},fort);el('rect',{x:288,y:134,width:26,height:24,rx:3,'class':'core'},cg);B.core={g:cg,cx:301,cy:146,s:[0,0,0],e:[0,0,0],t0:0,t1:0};
  var fx=el('g',{},svg),txt=el('text',{x:200,y:28,'text-anchor':'middle','class':'cap'},svg);
  return {svg:svg,B:B,fort:fort,fx:fx,txt:txt};
}
function bird(p,kind,cls){
  var g=el('g',{'class':'bird '+cls},p.svg),r=kind==='heavy'?13:kind==='scout'?6:kind==='mini'?5:9;
  if(kind==='drill'){el('path',{d:'M-9 -7 Q4 -10 14 0 Q4 10 -9 7 Q-12 0 -9 -7 Z','class':'bb'},g)}else el('circle',{r:r,'class':'bb'},g);
  el('circle',{cx:r*.35,cy:-r*.3,r:Math.max(1.8,r*.28),'class':'ey'},g);el('circle',{cx:r*.45,cy:-r*.3,r:Math.max(.9,r*.13),'class':'pu'},g);
  el('path',{d:'M'+(r*.8)+' '+(-r*.05)+' l'+(r*.55)+' '+(r*.18)+' l'+(-r*.55)+' '+(r*.2)+' Z','class':'bk2'},g);
  if(kind==='split'){el('circle',{cx:-r*.4,cy:r*.45,r:1.6,'class':'ey'},g);el('circle',{cx:0,cy:r*.55,r:1.6,'class':'ey'},g)}
  g.style.opacity=0;return g}
function put(g,x,y,rot,op){g.setAttribute('transform','translate('+x+' '+y+') rotate('+(rot||0)+')');if(op!=null)g.style.opacity=op}
function arc(t,a,b,h){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t-4*h*t*(1-t)]}
function ease(t){return t<0?0:t>1?1:1-Math.pow(1-t,3)}
function fall(t){return t<0?0:t>1?1:t*t}
function setB(blk,t){var k=blk.t1>blk.t0?fall((t-blk.t0)/(blk.t1-blk.t0)):(t>=blk.t0?1:0);var s=blk.s,e=blk.e;
  var dx=s[0]+(e[0]-s[0])*k,dy=s[1]+(e[1]-s[1])*k,r=s[2]+(e[2]-s[2])*k;
  blk.g.setAttribute('transform','translate('+dx+' '+dy+') rotate('+r+' '+blk.cx+' '+blk.cy+')')}
function hit(B,k,t0,dur,e){var b=B[k];b.s=b.e.slice?b.e.slice():[0,0,0];b.s=[b.cur?b.cur[0]:b.e[0],b.cur?b.cur[1]:b.e[1],b.cur?b.cur[2]:b.e[2]];b.e=e;b.t0=t0;b.t1=t0+dur}
function ring(p,x,y,t,t0){var c=p._rings||(p._rings={}),key=x+'_'+y;if(!c[key])c[key]=el('circle',{cx:x,cy:y,r:6,'class':'ring'},p.fx);var k=(t-t0);c[key].style.opacity=k<0?0:Math.max(0,.9-((k%1.2)/1.2)*.6);c[key].setAttribute('r',6+((k>0?k:0)%1.2)*8)}

/* ---------- сцена А: одна птица */
function A(svg){var p=scene(svg,'a'),b=bird(p,'round','g');var D=8.6;
  p.draw=function(t){var tries=[0,2.4,4.8],shown=false;
    tries.forEach(function(t0){var k=t-t0;if(k<0||shown&&k>2.4)return;
      if(k>=0&&k<1){var q=arc(ease(k),[SX,SY],[244,196],70);put(b,q[0],q[1],k*200,1);shown=true}
      else if(k>=1&&k<2.2){var j=(k-1)/1.2;put(b,244-j*40,196+Math.min(1,j*1.6)*25,200-j*300,1-j*.2);shown=true;
        p.fort.setAttribute('transform','translate('+(k<1.25?Math.sin(k*60)*1.6:0)+' 0)')}});
    if(!shown)put(b,SX,SY,0,t<7.2?1:1);
    p.txt.textContent=t<1?'':t<7.2?'Попытка '+Math.min(3,1+Math.floor(t/2.4))+' — снова та же птица':'Проект стоит. Одной птицей его не взять';
    p.txt.setAttribute('class','cap'+(t>=7.2?' end':''))};
  p.D=D;return p}

/* ---------- сцена Б: стая со скиллами */
function Bscene(svg){var p=scene(svg,'b'),B=p.B,D=9.2;
  var sc=bird(p,'scout','s'),sp=bird(p,'split','r'),m=[bird(p,'mini','r'),bird(p,'mini','r'),bird(p,'mini','r')],dr=bird(p,'drill','r'),hv=bird(p,'heavy','r');
  var path=el('path',{d:'','class':'trail'},p.fx);
  /* сценарий разрушения: [время, длительность, dx, dy, поворот] */
  var plan={b6:[3.0,.9,46,118,78],roof:[3.0,1.0,72,118,115],core:[6.45,.7,-6,72,8],b1:[4.6,.6,-42,26,-90],b3:[6.4,.8,18,64,-10],b4:[6.45,.8,-34,92,-90],b5:[6.5,.8,42,92,90],b2:[6.6,.8,30,26,90]};
  var sag={b3:[4.7,.4,0,8,-7]};
  p.draw=function(t){
    /* блоки */
    Object.keys(B).forEach(function(k){var b=B[k],pl=plan[k],sg=sag[k],cur=[0,0,0];
      if(sg&&t>=sg[0]){var q=fall((t-sg[0])/sg[1]);cur=[sg[2]*q,sg[3]*q,sg[4]*q]}
      if(t>=pl[0]){var q2=fall((t-pl[0])/pl[1]);var s0=cur.slice();cur=[s0[0]+(pl[2]-s0[0])*q2,s0[1]+(pl[3]-s0[1])*q2,s0[2]+(pl[4]-s0[2])*q2]}
      b.g.setAttribute('transform','translate('+cur[0]+' '+cur[1]+') rotate('+cur[2]+' '+b.cx+' '+b.cy+')')});
    /* 1. разведчик: пролетает над крепостью, оставляет пунктир, отмечает слабые места */
    if(t<1.6){var q=arc(ease(t/1.4),[SX,SY],[390,120],110);put(sc,q[0],q[1],0,t<1.4?1:0)}else put(sc,0,0,0,0);
    var pts=[];for(var i=0;i<=24;i++){var u=i/24;if(u>Math.min(1,t/1.4))break;var r=arc(ease(u),[SX,SY],[390,120],110);pts.push(r[0].toFixed(1)+' '+r[1].toFixed(1))}
    path.setAttribute('d',pts.length>1?'M'+pts.join(' L'):'');path.style.opacity=t<6.8?.9:Math.max(0,1-(t-6.8));
    if(t>1.2&&t<3)ring(p,301,104,t,1.2);else ring(p,301,104,-1,0);
    if(t>1.2&&t<4.6)ring(p,258,214,t,1.3);else ring(p,258,214,-1,0);
    /* 2. «стиль»: летит и делится на три */
    if(t>=1.8&&t<2.5){var q3=arc(ease((t-1.8)/.9),[SX,SY],[230,80],80);put(sp,q3[0],q3[1],0,1)}else put(sp,0,0,0,0);
    var tg=[[300,100],[290,82],[320,96]];
    m.forEach(function(b,i){if(t>=2.5&&t<3.1){var k=(t-2.5)/.5,st=arc(ease(.7/.9),[SX,SY],[230,80],80);var q4=[st[0]+(tg[i][0]-st[0])*k,st[1]+(tg[i][1]-st[1])*k+(i-1)*14*Math.sin(k*Math.PI)];put(b,q4[0],q4[1],k*180,1)}else if(t>=3.1&&t<4){var j=(t-3.1)/.9;put(b,tg[i][0]+j*30,tg[i][1]+fall(j)*(GROUND-6-tg[i][1]),j*300,1-j)}else put(b,0,0,0,0)});
    /* 3. «точность»: низко и точно в левую опору */
    if(t>=3.8&&t<4.6){var q5=arc(ease((t-3.8)/.8),[SX,SY],[252,206],18);put(dr,q5[0],q5[1],8,1)}else if(t>=4.6&&t<5.4){var j2=(t-4.6)/.8;put(dr,252-j2*20,206+fall(j2)*18,40*j2,1-j2)}else put(dr,0,0,0,0);
    /* 4. «тяжёлый»: финальный удар в центр */
    if(t>=5.4&&t<6.4){var q6=arc(ease((t-5.4)/1),[SX,SY],[300,160],60);put(hv,q6[0],q6[1],(t-5.4)*120,1)}else if(t>=6.4&&t<7.4){var j3=(t-6.4);put(hv,300+j3*20,160+fall(j3)*57,120+j3*90,1)}else if(t>=7.4){put(hv,320,217,210,1)}else put(hv,0,0,0,0);
    p.txt.textContent=t<1.6?'Разведка: где слабое место':t<3.6?'Стиль: бьёт сразу в трёх местах':t<5.4?'Точность: одна опора — и всё шатается':t<7.2?'Сила: финальный удар':'Проект взят';
    p.txt.setAttribute('class','cap'+(t>=7.2?' end ok':''))};
  p.D=D;return p}

var sa=A(root.querySelector('.ab-a svg')),sb=Bscene(root.querySelector('.ab-b svg'));
var t0=null,raf=null,run=false;
function frame(ts){if(t0===null)t0=ts;var t=(ts-t0)/1000;sa.draw(Math.min(t,sa.D));sb.draw(Math.min(t,sb.D));if(t<Math.max(sa.D,sb.D))raf=requestAnimationFrame(frame);else run=false}
function play(){if(raf)cancelAnimationFrame(raf);t0=null;run=true;raf=requestAnimationFrame(frame)}
function end(){sa.draw(sa.D);sb.draw(sb.D)}
sa.draw(0);sb.draw(0);
root.querySelector('.ab-re').addEventListener('click',function(){still?end():play()});
if(still||!('IntersectionObserver' in window)){end()}else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){play();io.disconnect()}})},{threshold:.45});io.observe(root)}
})();
