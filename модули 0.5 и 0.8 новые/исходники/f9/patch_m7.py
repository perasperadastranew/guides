import json,copy
K='/tmp/claude-0/-home-claude/3981ddd0-ce36-5aaf-8023-3267c13b1a2b/scratchpad/kv/'
src=json.load(open(K+'f9/l9_4_new.json',encoding='utf-8'));S={x['id']:x for x in src['sections']}
prod=json.load(open(K+'m7/m7_product.json',encoding='utf-8'))
ad=json.load(open(K+'m7/m7_ad.json',encoding='utf-8'))
bl=S['bity']['blocks']; beats=[bl[0],bl[1],bl[3],bl[4],bl[5]]
new=[{'id':'bity','nav':'Биты','title':'Пять битов ролика на 10–15 секунд','blocks':beats},
     {'id':'produkt','nav':'Продукт','title':'Как сохранить продукт неизменным','blocks':S['produkt']['blocks']},
     {'id':'tochnoe','nav':'Движение','title':'Точное движение: сначала простая анимация','blocks':S['3d']['blocks']}]
secs=[]
for x in prod['sections']:
    if x['id']=='pokaz':
        x['blocks']=[b for b in x['blocks'] if not(b['type']=='note' and b.get('title')=='Продукт не генерируется')]
    if x['id']=='proverka': secs+=copy.deepcopy(new)
    secs.append(x)
prod['sections']=secs
for x in ad['sections']:
    if x['id']=='reklama':
        for b in x['blocks']:
            if b['type']=='note' and b.get('title')=='Продукт не генерируется':
                b['text']='Какой бы приём ты ни выбрал, продукт приходит в ролик референсом реальной съёмки или карточкой продукта. Творчество — в мире вокруг. Правила и пять битов ролика — в статье <a href="#/m7_product">Продуктовое видео</a>.'
json.dump(prod,open(K+'m7/m7_product_new.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(ad,open(K+'m7/m7_ad_new.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print([x['title'] for x in prod['sections']])
