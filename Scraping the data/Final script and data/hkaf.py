def sortings(s):
    lst=[0]*9
    for i in range(0,s.length()):
        if(s[i].isdigit()):
            lst[s[i]-'0']+=1
    ans=""
    for i in range(0,lst.length()):
        if(lst[i]%2!=0):
            ans+=chr(i)*lst[i]

    for i in range(0, s.length()):
        if(lst[s[i]-'0']%2==0):
            ans+=s[i]

    print(ans)