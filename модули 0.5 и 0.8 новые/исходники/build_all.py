import sys, json, base64, os, re
S='/home/claude/perasperadastranew/guides/ai-metodichki/src/'
K='/tmp/claude-0/-home-claude/3981ddd0-ce36-5aaf-8023-3267c13b1a2b/scratchpad/kv/'
sys.path.insert(0,S)
import build

MODS=[ # (имя модуля в meta, номер, about, [(id, путь json, num)])
 ('Старт','00','<b>Введение в профессию и инструменты.</b> Что заказывают AI-креатору, как устроены нейросети и текстовые агенты, из каких шести этапов состоит дизайн-процесс. Помогает понять, из чего состоит работа, до выбора инструментов.',
   [('l0_1',K+'m0/m0_1.json','01'),('l0_2',K+'m0/m0_2.json','02'),('l0_3',K+'m0/m0_3.json','03'),('l0_4',K+'m0/m0_4.json','04')]),
 ('Сервисы и оплата','СЕРВИСЫ','<b>Как подключить и оплатить нейросети из России.</b> Тарифы, способы оплаты, что брать и на чём не переплатить, на чём сэкономить.',
   [('pay_budget',K+'pay/pay_budget_new.json','01'),('pay_agg',K+'pay/pay_agg_new.json','02'),('pay_video',K+'pay/pay_video_new.json','03'),('pay_text',K+'pay/pay_text_new.json','04'),('pay_mj',K+'pay/pay_mj_new.json','05')]),
 ('Проекты курса','ПРОЕКТЫ','<b>Проекты, из которых собирается портфолио.</b> О каждом кратко: что это за работа, кто её заказывает, какие бывают темы и из чего собирается проект.',
   [('pr_photo',K+'pr/pr_photo_new.json','01'),('pr_product',K+'pr/pr_product_new.json','02'),('pr_illu',K+'pr/pr_illu_new.json','03'),('pr_video',K+'pr/pr_video_new.json','04')]),
 ('Фундамент визуала','01','<b>Основные принципы и правила дизайна.</b> Они помогают заранее видеть, почему кадр работает: иерархия, композиция, ракурсы, свет и цвет, стиль, сюжет кадра.',
   [('l1_1',K+'f1/l1_1_new.json','01'),('l1_2',K+'f1/l1_2_new.json','02'),('l1_3',K+'f1/l1_3_new.json','03'),('l1_4',K+'f1/l1_4_new.json','04'),('l1_style',K+'f1/l1_style_new.json','05'),('l1_5',K+'f1/l1_5_new.json','06')]),
 ('Midjourney и стиль','02','<b>Как устроена работа в Midjourney.</b> Интерфейс и тарифы, формула промпта, мудборды и sref. Для каких проектов он подходит и как редактировать в нём картинки.',
   [('l2_1',K+'f2/l2_1_new.json','01'),('l2_2',K+'f2/l2_2_new.json','02'),('l2_3',K+'f2/l2_3_new.json','03'),('l2_4',K+'f2/l2_4_new.json','04')]),
 ('Nano Banana и финализация','03','<b>Как устроена работа в Nano Banana и GPT.</b> Для каких проектов они подходят, как редактировать готовые картинки и собирать кадр и серию из референсов.',
   [('m3_nano',K+'m3/m3_1.json','01'),('m3_edits',K+'m3/m3_2.json','02'),('m3_refs',K+'m3/m3_3.json','03')]),
 ('Съёмка с моделью','05','<b>Пайплайн двух типов проектов с людьми и продуктом.</b> Фотосессия с моделью и съёмка продукта: инструкция по шагам и примеры.',
   [('m5_model',K+'m5/m5_model.json','01'),('m5_product',K+'m5/m5_product.json','02')]),
 ('Графика и key visual','06','<b>Пайплайны проектов на графику бренда.</b> 2D и 3D key visual, маскот, мокапы, упаковка и мерч: инструкция по шагам и примеры.',
   [('l6_2',K+'l6_2_new.json','01'),('l6_3',K+'l6_3_new.json','02'),('l6_mascot',None,None),('l6_5',K+'l6_5_new.json','04')]),
 ('Концепция видео','07','<b>Сначала теория, потом проекты.</b> Первая статья — как устроен любой ролик. Затем типы видеопроектов (продуктовое, рекламное, креативное): как они устроены и на какие темы делаются, с инструкцией по шагам.',
   [('m7_base',K+'m7/m7_base.json','01'),('m7_product',K+'m7/m7_product.json','02'),('m7_ad',K+'m7/m7_ad.json','03'),('m7_creative',K+'m7/m7_creative.json','04')]),
 ('Препродакшн','08','<b>Подготовка всех материалов, необходимых до создания визуального ряда.</b> Персонаж, локация и раскадровка.',
   [('l8_1',K+'m8/l8_1.json','01'),('l8_2',K+'m8/l8_2.json','02'),('l8_3',K+'m8/l8_3.json','03')]),
]
NUMS=[m[1] for m in MODS]
orig=build.data
def data():
    m=orig(); mods=[]; L={}; titles={}
    for name,num,about,items in MODS:
        x=[z for z in m['modules'] if z['name']==name][0]
        x['lessons']=[i[0] for i in items]; x['about']=about; mods.append(x)
        if num=='03': x['name']='Nano Banana и GPT'; x['short']='Nano Banana и GPT'
        if num=='01': x['name']='Фундамент дизайна'; x['short']='Фундамент дизайна'
        for id_,path,n in items:
            if path:
                v=json.load(open(path,encoding='utf-8')); v['num']=n; v['sections']=[z for z in v['sections'] if z['id']!='zadanie']; v['lead']=re.sub(r'\s*После (?:статьи|урока) у тебя будет.*$','',v['lead'],flags=re.S); v=json.loads(json.dumps(v,ensure_ascii=False).replace('Для задания это не страшно','Для учебной работы это не страшно').replace(' на кадр в задании.',' на кадр.')); L[id_]=v; titles[id_]=v['title']
            else: titles[id_]='Маскот'
    names=[z['name'] for z in mods]
    ST=[('Старт','Профессия, нейросети, сервисы и оплата, проекты курса','Старт'),('Изображение','Основы дизайна, работа в Midjourney и Nano Banana, съёмка с моделью, графика и key visual','Фундамент дизайна'),('Видео','Теория и типы видеопроектов, подготовка материалов','Концепция видео'),('Кейс и деньги','Упаковка кейса, продвижение, цены','')]
    m['stages']=[{'n':i+1,'name':a,'what':b,'mod':(names.index(c) if c else -1)} for i,(a,b,c) in enumerate(ST)]
    SM={'Старт':1,'Сервисы и оплата':1,'Проекты курса':1,'Фундамент дизайна':2,'Midjourney и стиль':2,'Nano Banana и GPT':2,'Съёмка с моделью':2,'Графика и key visual':2,'Концепция видео':3,'Препродакшн':3}
    for z in mods: z['stage']=SM[z['name']]
    m['modules']=mods; m['lessons']=L; m['titles']=titles; m['short']={}
    return m
build.data=data
g=build.page()

def sub(old,new,s,regex=False):
    n=(re.subn(old,new,s,count=1,flags=re.S) if regex else (s.replace(old,new,1),1 if old in s else 0))
    assert n[1]==1, 'no match: '+old[:70]
    return n[0]

g=sub("function t(s){return typo(esc(s)).replace(/&lt;(\\/?)(b|i)&gt;/g,'<$1$2>')}","function t(s){return typo(esc(s)).replace(/&lt;(\\/?)(b|i)&gt;/g,'<$1$2>').replace(/&lt;a href=&quot;(#\\/m7_[a-z]+)&quot;&gt;(.*?)&lt;\\/a&gt;/g,'<a class=\"inlink\" href=\"$1\">$2</a>')}",g)
g=sub("var secs=[{id:'gde',nav:'Где мы',title:'Где мы сейчас',html:where(L)}];","var secs=[];",g)
g=sub(r'<nav aria-label="Разделы">\'\+secs\.map.*?\'</nav>',"",g,True)
g=sub(r'<a href="#/">← Все методички</a><span class="eyebrow">.*?</span></div>','<a href="#/">← К списку статей</a></div>',g,True)
g=sub("corner('МОДУЛЬ «'+m.name.toUpperCase()+'»','МЕТОДИЧКА К УРОКУ')","corner('МОДУЛЬ «'+m.name.toUpperCase()+'»','БЛОК '+m.stage+' · '+D.stages[m.stage-1].name.toUpperCase())",g)
g=sub("prev=ORDER[k-1], next=ORDER[k+1];","prev=ORDER.slice(0,k).filter(function(x){return D.lessons[x]}).pop(), next=ORDER.slice(k+1).filter(function(x){return D.lessons[x]})[0];",g)
g=sub("← Предыдущий урок","← Предыдущая статья",g); g=sub("Следующий урок →","Следующая статья →",g)
g=sub("← Оглавление<b>Все методички</b>","← К списку статей<b>Mission to AI</b>",g)
g=sub("Оглавление →<b>Все методички</b>","К списку статей →<b>Mission to AI</b>",g)
HEAD="var h='<header>'+corner('PERASPERADASTRA','MISSION TO AI')+'<span class=\"kicker\">Методички курса</span><h1 class=\"brand\">Mission<br>to AI</h1><p class=\"lead\"><b>Практический курс по созданию изображений и видео с помощью нейросетей.</b> Он учит собирать рабочий процесс: от идеи и референсов до готового кадра и ролика. Из проектов курса складывается портфолио.</p><div style=\"display:flex;gap:8px;flex-wrap:wrap\"><span class=\"save\">Сохрани, чтобы не потерять</span></div></header>';"
g=sub(r"var h='<header>'\+corner\('PERASPERADASTRA','МЕТОДИЧКИ К УРОКАМ'\).*?</header>';",HEAD.replace('\\','\\\\'),g,True)
PLATE="h+='<section>'+corner('КАРТА КУРСА')+'<h2>Четыре блока курса</h2><p>Курс разделён на четыре блока: старт, изображение, видео, кейс и деньги. Нажми на блок, чтобы перейти к его модулям.</p><div class=\"stagebar\">'+D.stages.map(function(x){if(x.mod<0)return '<div><i>блок '+x.n+'</i><b>'+t(x.name)+'</b><small>'+t(x.what)+'</small><small>готовится</small></div>';return '<a class=\"stg\" href=\"#/\" data-go=\"mod-'+x.mod+'\"><i>блок '+x.n+'</i><b>'+t(x.name)+'</b><small>'+t(x.what)+'</small><em>к модулям →</em></a>'}).join('')+'</div></section>';"
g=sub(r"h\+='<section>'\+corner\('КАРТА КУРСА'\).*?</section>';",PLATE.replace('\\','\\\\'),g,True)
g=sub("h+='<section>'+corner(m.code||('МОДУЛЬ '+('0'+mi).slice(-2)),'БЛОК '+m.stage)","h+='<section id=\"mod-'+mi+'\">'+corner(("+json.dumps(NUMS)+"[mi].length<=2?'МОДУЛЬ '+"+json.dumps(NUMS)+"[mi]:m.name.toUpperCase()),'БЛОК '+m.stage+' · '+D.stages[m.stage-1].name.toUpperCase())",g)
#"corner('МОДУЛЬ '+"+json.dumps(NUMS)+"[mi],'СТАТЬИ ПО ПРОЕКТАМ')",g)
g=sub("document.title='Методички курса'","app.querySelectorAll('[data-go]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();var el=document.getElementById(a.getAttribute('data-go'));if(el)el.scrollIntoView({behavior:'smooth',block:'start'})})});document.title='Mission to AI'",g)
g=g.replace("document.title='Mission to AI';","document.title='Новая методичка Mission to AI';");g=g.replace('<title>Методички курса Mission to AI</title>','<title>Новая методичка Mission to AI</title>',1)
g=g.replace('</style>','a.stg{background:var(--card);border:1px solid var(--stroke);border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:6px;min-width:0;color:inherit;text-decoration:none;cursor:pointer;transition:border-color .15s,transform .15s}a.stg:hover{border-color:var(--ink);transform:translateY(-2px)}a.stg i{font-style:normal;font-family:var(--mono);font-size:11px;color:var(--faint)}a.stg b{font-weight:400;font-size:15px;line-height:1.15}a.stg small{font-size:12px;line-height:1.3}a.stg em{font-style:normal;font-family:var(--mono);font-size:11px;color:var(--faint);margin-top:auto}.stagebar a.stg:hover em{color:var(--ink)}a.inlink{color:inherit;font-weight:700;text-decoration:underline;text-underline-offset:3px}a.inlink:hover{opacity:.7}</style>',1)
g=sub("note:function(b){","baselink:function(b){return '<div class=\"baselink\"><div><b>'+t(b.title)+'</b><p>'+t(b.text)+'</p></div><a href=\"'+esc(b.href)+'\">'+t(b.button)+'</a></div>'},note:function(b){",g)
g=g.replace('</style>','.baselink{background:var(--accent);color:var(--accent-ink);border-radius:14px;padding:18px 20px;margin:0 0 20px;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}.baselink b{display:block;font-weight:700;color:var(--accent-ink)}.baselink p{margin:4px 0 0;color:var(--accent-ink);max-width:60ch}.baselink a{background:var(--accent-ink);color:var(--ink);padding:12px 20px;border-radius:10px;text-decoration:none;white-space:nowrap}.baselink a:hover{opacity:.85}</style>',1)

imgs=set(re.findall(r'"img":\s*"([^"]+)"', json.dumps(build.data()['lessons'],ensure_ascii=False)))
IM={}
for n in imgs:
    p=S+'../img/'+n+'.webp'
    if os.path.exists(p): IM[n]='data:image/webp;base64,'+base64.b64encode(open(p,'rb').read()).decode()
    else: print('missing',n)
g=sub("IMG={}","IMG="+json.dumps(IM),g)
g=g.replace("(window.IMGBASE||'img/')+x.img+'.webp'","(IMG[x.img]||(window.IMGBASE||'img/')+x.img+'.webp')")
g=g.replace("(window.IMGBASE||'img/')+s.img+'.webp'","(IMG[s.img]||(window.IMGBASE||'img/')+s.img+'.webp')")
open(K+'mission-to-ai-metodichki-moduli-05-08.html','w',encoding='utf-8').write(g)
print(len(IM),'images',len(g)//1024,'KB')
