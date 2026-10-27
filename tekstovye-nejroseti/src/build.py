import re,os,json
D=os.path.dirname(os.path.abspath(__file__))
nd=open(os.path.join(D,'..','..','nejroseti-dostup','index.html'),encoding='utf-8').read()
css='\n'.join(re.findall(r'<style[^>]*>(.*?)</style>',nd,re.S))
js=re.findall(r'<script(?![^>]*application/json)[^>]*>(.*?)</script>',nd,re.S)
copyquiz=[x for x in js if 'button.copy' in x][0]
body=open(os.path.join(D,'body.html'),encoding='utf-8').read()
quiz=open(os.path.join(D,'quiz.json'),encoding='utf-8').read();json.loads(quiz)
extra=open(os.path.join(D,'extra.css'),encoding='utf-8').read()
# неразрывные пробелы в тексте (не в тегах и не в pre)
SHORT='в|во|к|ко|с|со|и|а|о|об|у|по|на|не|ни|за|из|от|до|без|для|при|про|что|как|это|же|ли|бы|но|да|или|мы|ты|он|ее|её|их|все|всё'
def nb(t):
    t=re.sub(r'(?<![\wА-Яа-яЁё])('+SHORT+r') (?=\S)',lambda m:m.group(1)+' ',t,flags=re.I)
    t=re.sub(r' (—|–)',r' \1',t)
    return t
parts=re.split(r'(<pre.*?</pre>|<[^>]+>)',body,flags=re.S)
body=''.join(p if p.startswith('<') else nb(p) for p in parts)
out='''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow"><title>Claude и текстовые нейросети</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>'''+css+'\n'+extra+'''</style></head><body>
'''+body+'''
<script type="application/json" id="quiz-data">'''+quiz+'''</script>
<script>'''+copyquiz+'''</script>
</body></html>'''
open(os.path.join(D,'..','index.html'),'w',encoding='utf-8').write(out);print('ok',len(out))
