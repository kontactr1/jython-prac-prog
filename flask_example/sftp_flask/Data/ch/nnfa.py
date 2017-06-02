def nullcloser(ds,sym):
 l = [str(sym)]
 k = []
 #string  = str(sym) + " "
 #if "^" in ds[sym]:
 #   for  k in ds[sym]["^"]:
 #       string += k + " "
 #string = string.strip(" ")
 #string = string.split(" ")
 while len(l) != 0:
     val = l.pop(0)
     k.append(val)
     string = ""
     if "^" in ds[val]:
         for  k1 in ds[val]["^"]:
             string += k1 + " "
         string = string.strip(" ")
         string = string.split(" ")
         for lo in string:
             if (lo not in l) and (lo not in k):
                 l.append(lo)
 return set(k)

def statetransition(ds,st_1,sym_1):
    string  = ""
    if sym_1 in ds[st_1]:
        string += ds[st_1][sym_1] + " "
    string = string.strip(" ")
    string = string.split(" ")
    return set(string)


state = int(input("Enter total state number: "))
symbol = int(input("Enter total symobl number: "))

ds = {}
l = {None}
l.pop()
for s_co in range(state):
    state_name = input("Enter "+str(s_co)+" state name: ")
    ds[state_name] = {}
    
    
    for symbol_count in range(int(input("howmany symbol you want to enter: "))):
        #example a -> s1,s2,s3
        symbol_entry = input("Enter symbol and state (one to many): ").split("->")
        print (symbol_entry)
        for k in range(len(symbol_entry)):
            symbol_entry[k] = symbol_entry[k].strip()
        l.add(symbol_entry[0])
        if symbol_entry[0] in ds[state_name]:
          val1 = ds[state_name][symbol_entry[0]]
          ds[state_name][symbol_entry[0]] = val1.union(set(symbol_entry[1].split(",")))
        else:
            ds[state_name][symbol_entry[0]] = set(symbol_entry[1].split(","))


se = input("Enter ini and final state: ").split(" ")
start = se[0]
se[0] = set((se[0]).split(","))
se[1] = set((se[1]).split(","))
un = se[0].intersection(se[1])
#print (se)
#print (un)
print (l)
print (ds)



ds_nnfa = {}
ds_nsym = l - {"^"}
for k in ds.keys():
    ds_nnfa[k] = {}

print (ds_nnfa)

for k in ds_nsym:
    for st in ds.keys():
        string = ""
        set_null = nullcloser(ds,st)
        for set_closer in set_null:
            if k in ds[set_closer]:
                for lk in ds[set_closer][k]:
                    string += lk + " "
        string = string.strip(" ")
        string = string.split(" ")
        if '' not in string:
           string_closer = set()
            
           for lk_cl in (set(string)):
                string_closer = string_closer.union(nullcloser(ds,lk_cl))
            #string_closer = string_closer.strip(" ")
            #string_closer = string_closer.split(" ")
           print (k+" "+st+"  set:",string_closer)
           ds_nnfa[st][k] = set(string_closer)

print (ds_nnfa)
#print (nullcloser(ds,"A"))
