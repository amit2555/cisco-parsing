### Python code to parse output of Cisco IOS CLI command "show ip bgp | begin Network"

from pyparsing import *

'''
Explanation:
    This script takes as input of Cisco IOS CLI command "show ip bgp | begin Network".
    It extracts the status code and prefix using string slicing.
    Other BGP attributes are extracted using PyParsing.

Args:
    None

Result:
    Result is a dict of the form -
    {prefix: {next-hop: {status: dict, med: int, locprf: int, path: list, origin: string}},
             {next-hop: {status: dict, med: int, locprf: int, path: list, origin: string}}}
    
          1         2         3         4         5         6
0123456789012345678901234567890123456789012345678901234567890123456789
*>i10.1.1.0/24      1.1.1.1                  0    100      0 200 i
'''

def mustMatchCols(startloc,endloc):
    def pa(s,l,t):
        if not startloc <= col(l,s) <= endloc:
            raise ParseException(s,l,"text not in expected column")
    return pa

def bgpAttribute(expr,colstart,colend):
    return Optional(expr.copy().addParseAction(mustMatchCols(colstart,colend)))
    
def parse_bgp_ios(response):
    ipField = Word(nums, max=3)
    ipAddr = Combine(ipField + "." + ipField + "." + ipField + "." + ipField)
    nextHop = ipAddr('next_hop')
    metric = Word(nums).setParseAction(lambda t: int(t[0]))('med')
    local_pref = Word(nums).setParseAction(lambda t: int(t[0]))('locprf')
    wt = Word(nums).setParseAction(lambda t: int(t[0]))('weight')
    as_path = Group(ZeroOrMore(Word(nums)))('path')
    o = oneOf("i e ?")('origin')

    grammer = nextHop + bgpAttribute(metric,17,26) + bgpAttribute(local_pref,27,33) + wt + as_path + o
    
    status_code = {'s':'suppressed','d':'damped','h':'history','*':'valid','>':'best','i':'internal','r':'RIB-failure'}
    origin_code = {'i':'IGP','e':'EGP','?':'incomplete'}
    result = dict()
    

    lines = response.splitlines()
    header = lines[0]
    for line in lines[1:]:
        status = dict()
        status['code'] = {}
        
        if any(line.startswith(item) for item in list(status_code.keys())):
            code = line[:3].strip()
            for v in code:
                status['code'].update({v:status_code[v]})
            _pstart = header.index('Network')
            _pend = header.index('Next Hop') - header.index('Network')
            prefix_extracted = line[_pstart:_pend].strip()
            
            rest_of_line = line[20:]
            rol = grammer.parseString(rest_of_line)

            next_hop = rol['next_hop']
           
            try:
                med = rol['med']
            except KeyError:
                med = 0
            try:
                locprf = rol['locprf']
            except KeyError:
                locprf = 0

            weight = rol['weight']
            path = list(rol['path'])
            origin = origin_code[rol['origin']]

            if prefix_extracted is not '':
                prefix = prefix_extracted
                result[prefix] = {next_hop : {'status':status,'med':med,'locprf':locprf,'weight':weight,'path':path,'origin':origin}}
            else:
                result[prefix].update({next_hop : {'status':code,'med':med,'locprf':locprf,'weight':weight,'path':path,'origin':origin}})
                
    return result

    
