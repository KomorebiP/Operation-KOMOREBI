def without_comments(s: str) -> str:
    # Preserve newlines and support nested Lean comments and quoted strings.
    out=[]; i=0; depth=0; string=False
    while i<len(s):
        if depth:
            if s.startswith('/-',i): depth+=1;i+=2
            elif s.startswith('-/',i): depth-=1;i+=2
            else:
                out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif string:
            if s[i]=='\\': i+=2
            elif s[i]=='"': string=False;i+=1
            else:out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif s.startswith('/-',i):depth=1;i+=2
        elif s.startswith('--',i):
            j=s.find('\n',i);i=len(s) if j<0 else j
        elif s[i]=='"':string=True;i+=1
        else:out.append(s[i]);i+=1
    if depth or string:raise ValueError('Unterminated source comment/string')
    return ''.join(out)

