import json,sys
TYPES={'p':['text'],'sub':['text'],'list':['items'],'quote':['text','who'],'formula':['parts'],'chain':['nodes'],'terms':['items'],'steps':['items'],'pairs':['groups'],'table':['head','rows'],'note':['title','text'],'two':['boxes'],'tree':['root','leaves'],'myths':['items'],'canvas':['columns'],'flow':['nodes'],'wire':['screens'],'shot':['img','title','text'],'case':['kind','title','steps'],'ai':['give','keep'],'task':['result','parts'],'check':['items'],'faq':['items'],'shots':['items'],'files':['items']}
SK={'big','ttl','lbl','text','field','item','btn','ghost','chips','tabs','map','img','blk','timer','row','stars','sp','fab','cols','grid','home','gap'}
def scr(bl,where,err):
    for b in bl:
        if b.get('k') not in SK: err.append(f'{where}: неизвестный блок экрана {b.get("k")}')
def check(path):
    err=[]; L=json.load(open(path))
    for k in ['id','title','lead','card','stage','sections','quiz']:
        if k not in L: err.append('нет поля '+k)
    for k in ['input','doing','output','next']:
        if k not in L.get('stage',{}): err.append('stage.'+k)
    ids=set(); types=set()
    for s in L.get('sections',[]):
        for k in ['id','nav','title','blocks']:
            if k not in s: err.append(f'section без {k}')
        if s.get('id') in ids: err.append('дубль id '+s['id'])
        ids.add(s.get('id'))
        for b in s.get('blocks',[]):
            ty=b.get('type'); types.add(ty)
            if ty not in TYPES: err.append(f'{s.get("id")}: неизвестный type {ty}'); continue
            for k in TYPES[ty]:
                if k not in b: err.append(f'{s.get("id")}/{ty}: нет {k}')
            if ty=='case':
                for i,st in enumerate(b.get('steps',[])):
                    for k in ['t','n','screen']:
                        if k not in st: err.append(f'case step {i}: нет {k}')
                    scr(st.get('screen',[]),f'case step {i}',err)
                    if i<len(b['steps'])-1 and not any(x.get('tap') for x in st.get('screen',[])): err.append(f'case «{b.get("title")}» step {i}: нет tap')
            if ty=='wire':
                for sc in b.get('screens',[]): scr(sc.get('blocks',[]),'wire',err)
            if ty=='canvas':
                for col in b['columns']:
                    if not isinstance(col,list): err.append('canvas: колонка должна быть списком ячеек')
            if ty=='pairs':
                for g in b['groups']:
                    if 'bad' not in g or 'good' not in g: err.append('pairs: нет bad/good')
            if ty=='table':
                for r in b['rows']:
                    if len(r)!=len(b['head']): err.append(f'{s.get("id")}/table: строка не той длины')
    for q in L.get('quiz',[]):
        if sum(1 for o in q['opts'] if o['ok'])!=1: err.append('quiz: ровно один верный: '+q['q'])
    need={'case','task','check','pairs','ai','steps'}
    miss=need-types
    if miss: err.append('нет обязательных блоков: '+', '.join(sorted(miss)))
    if len(L.get('quiz',[]))<6: err.append('в тесте меньше 6 вопросов')
    print(path.split('/')[-1],'OK' if not err else 'ОШИБКИ:\n  '+'\n  '.join(err), '| блоки:',len(types),'| знаков:',len(json.dumps(L,ensure_ascii=False)))
    return not err
if __name__=='__main__':
    ok=all([check(p) for p in sys.argv[1:]]); sys.exit(0 if ok else 1)
