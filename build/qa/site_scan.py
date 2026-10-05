import re,glob,html,os,sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','site'))
bad=['[','**','관심 분야:','Google Forms)','내부','미래의료','JK','위드미','솜씨','삼성중앙','정강','한바이오','STC','BHC','최고','완벽','보장합','\\','(MEDICAL)','(ABOUT)','차병원','차바이오','수한방','부평','PRIVÉ','연세','세브란스','여성 의료진','효과 보장','안전 보장','바이오텍','nEPS','KHC','IFC']
for f in sorted(glob.glob('*.html')):
    t=open(f,encoding='utf-8').read()
    t=re.sub(r'<script[\s\S]*?</script>','',t); t=re.sub(r'<style[\s\S]*?</style>','',t); t=re.sub(r'<title[\s\S]*?</title>','',t)
    t=re.sub(r'<svg[\s\S]*?</svg>','',t)
    txt=html.unescape(re.sub(r'<[^>]+>','\n',t))
    lines=[l.strip() for l in txt.split('\n') if l.strip()]
    hits=[]
    for l in lines:
        if re.search(r'\d[\d,]*\s*(원|만원|USD|\$)',l): hits.append(('가격?',l[:80]))
        for b in bad:
            if b in l: hits.append((b,l[:90]))
    print(f, len(lines), hits[:12])
