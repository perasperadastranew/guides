import json,sys
d=json.load(open(sys.argv[1]+'.json',encoding='utf-8'))
sk=set(sys.argv[2].split(',')) if len(sys.argv)>2 else set()
print(d['lead']);print(d['stage'])
for s in d['sections']:
    if s['id'] in sk: continue
    print('\n##',s['id'],s['title'])
    for b in s['blocks']:
        t=b['type']
        if t=='task': print(' [task] stuck=',b.get('stuck'));continue
        print(' -',t,json.dumps({k:v for k,v in b.items() if k!='type'},ensure_ascii=False)[:520])
print('\nQUIZ')
for q in d['quiz']:print(q['q'],[ (o['t'],o['ok']) for o in q['opts']])
