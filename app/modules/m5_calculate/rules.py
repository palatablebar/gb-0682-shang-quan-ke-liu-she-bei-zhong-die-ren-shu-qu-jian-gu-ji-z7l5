from app.errors import DomainError

def bounds(model):
    zones=model['zones'];keys=sorted(zones);pairs=model['pairs'];values=[zones[k] for k in keys]
    if len(keys)==1:return values[0],values[0],0,0
    if len(keys)==2:
        common=pairs.get('|'.join(keys))
        return (sum(values)-common,sum(values)-common,common,common) if common is not None else (max(values),sum(values),0,min(values))
    a,b,c=keys;ab=pairs['|'.join([a,b])];ac=pairs['|'.join([a,c])];bc=pairs['|'.join([b,c])]
    low=max(0,ab+ac-zones[a],ab+bc-zones[b],ac+bc-zones[c]);high=min(ab,ac,bc)
    if model.get('triple') is not None:low=max(low,model['triple']);high=min(high,model['triple'])
    if low>high:raise DomainError('CONSTRAINT','三方观测不存在可行人数')
    base=sum(values)-ab-ac-bc
    return base+low,base+high,low,high

def apply(state):
    results=[];bad=set()
    for i,item in enumerate(state['models']):
        try:
            low,high,tlo,thi=bounds(item['model']);results.append({'id':item['bucket'],'line':item['line'],'lower':low,'upper':high,'width':high-low,'triple_lower':tlo,'triple_upper':thi,'code':'EXACT' if low==high else 'INTERVAL'})
        except DomainError as e:
            bad.add(item['bucket'])
            for r in state['rows']:
                if r['bucket']==item['bucket']:state['quarantine'].append({'line':r['_line'],'id':r['id'],'code':e.code,'raw':r['_raw']})
    state['rows']=[r for r in state['rows'] if r['bucket'] not in bad]
    state['calculations']=results;state['business']={'total':sum(r['lower'] for r in results),'upper_total':sum(r['upper'] for r in results),'buckets':len(results),'unit':'客次'};return state
