import json,sys,re
for l in sys.argv[1:]:
    d=json.load(open(l+'.json',encoding='utf-8'));S={x['id']:x for x in d['sections']}
    print('=====',l,d['title']);print('LEAD',d['lead'][:400]);print('STAGE',json.dumps(d['stage'],ensure_ascii=False)[:1400])
    for b in S['glavnoe']['blocks']:
        if b['type'] in('p','note'): print(' G',b['type'],b.get('title',''),b.get('text','')[:420])
    ai=S['ai']['blocks'][0];print('AIgive',ai['give']);print('AIkeep',ai['keep']);print('AImistake',ai['mistake'])
    print('STEPS',[b['title'] for b in S['ai']['blocks'] if b['type']=='prompt'])
    t=[b for b in S['zadanie']['blocks'] if b['type']=='task'][0];print('STUCK',json.dumps(t.get('stuck'),ensure_ascii=False))
    print('FAQ',json.dumps(S['faq']['blocks'][0]['items'],ensure_ascii=False)[:1500])
    for q in d['quiz']:print('Q',q['q'],[(o['t'],o['ok']) for o in q['opts']])
