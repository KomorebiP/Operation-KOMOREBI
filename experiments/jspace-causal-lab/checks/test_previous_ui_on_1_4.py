"""Run the unchanged earlier browser assertions on the current delivered HTML.
Only the input HTML and output locations are redirected; assertions are unchanged.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name,out in [('test_legacy_browser_on_1_3.py','legacy'),('test_challenge_browser.py','previous_challenge')]:
    (ROOT/'checks/relay'/out).mkdir(exist_ok=True)
    source=(ROOT/'checks'/name).read_text().replace('Komorebi_JSpace_Causal_Lab_v1_3.html','Komorebi_JSpace_Causal_Lab_v1_4.html')
    if name.startswith('test_legacy'):
        source=source.replace('checks/robustness/','checks/relay/legacy/')
    else:
        source=source.replace("loc=ROOT/'checks/robustness'","loc=ROOT/'checks/relay/previous_challenge'")
    exec(compile(source,str(ROOT/'checks'/name),'exec'),{'__file__':str(ROOT/'checks'/name),'__name__':'__main__'})
