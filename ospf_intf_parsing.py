# Python program to parse output from Cisco CLI command "show ip ospf interface"

'''
Usage:
    This program uses PyParsing library mostly.

Args:
    None

Result:
    Prints a dictionary with data-structure as follows:

    {interface:
       {ip: ip_prefix,
        area: ospf_area,
        interface_type: ospf_interface_type,
        cost: ospf_interface_metric,
        hello: ospf_hello_timer,
        dead: ospf_dead_timer}
    }

'''


from pyparsing import *
import re

ipField = Word(nums, max=3)
ipAddr = Combine(ipField + "." + ipField + "." + ipField + "." + ipField)
prefix = Combine(ipAddr + Literal("/") + Word(nums,max=2))
ospf1 = Combine(Word(alphanums) + Optional(Literal("/") + Word(nums)) + Optional(Literal(".") + Word(nums)))
ospf2 = Suppress(Word(alphas)*2) + prefix + Suppress(Literal(",") + Word(alphas)) + Word(nums)
ospf3 = Suppress(Word(alphas)*2 + Word(nums) + Literal(",") + Word(alphas)*2 + ipAddr + Literal(",") + Word(alphas)*2) + Combine(Word(alphas) + Optional(Literal("_") + Word(alphas) + Literal("_") + Word(alphas))) + Suppress(Literal(",") + Word(alphas+":")) + Word(nums)
ospf4 = Suppress(Word(alphas)*3 + Literal(",") + Word(alphas)) + Word(nums) + Suppress(Literal(",") + Word(alphas)) + Word(nums)


# This function is copied from the code provided by Kirk Byers in his class
# Python Fundamentals for Network Engineers

# This function is used to split interface data into a list
def separate_interface_data(ospf_data):

    # Split the data based on 'is up, line protocol is up' but retain this string
    ospf_data = re.split(r'(.+ is up, line protocol is up)', ospf_data)

    # Dump any data before the first 'is up, line protocol is up'
    ospf_data.pop(0)

    ospf_list = []

    while True:
        if len(ospf_data) >= 2:
            intf = ospf_data.pop(0)
            section = ospf_data.pop(0)

            # reunify because it was split up in the re.split
            ospf_string = intf + section
            ospf_list.append(ospf_string)

        else:
            break

    return ospf_list


def ospf_parser(section):
    l = section.splitlines()
    
    intf = ospf1.parseString(l[0])[0]
    ip = ospf2.parseString(l[1])[0]
    area = ospf2.parseString(l[1])[1]
    intf_type = ospf3.parseString(l[2])[0]
    cost = ospf3.parseString(l[2])[1]
    if intf_type == "POINT_TO_POINT":
        hello = ospf4.parseString(l[6])[0]
        dead = ospf4.parseString(l[6])[1]
    elif intf_type == "LOOPBACK":
        hello = 'NA'
        dead = 'NA'
    else:
        hello = ospf4.parseString(l[8])[0]
        dead = ospf4.parseString(l[8])[1]

    return intf,ip,area,intf_type,cost,hello,dead

    
if __name__ == "__main__":

    d = dict()
    with open('C:\python33\ospf_data.txt','r') as f:
        ospf = f.read()
        ospf_data_sections = separate_interface_data(ospf)
        
        for section in ospf_data_sections:
            intf,ip,area,intf_type,cost,hello,dead = ospf_parser(section)

            d[intf] = {'ip':ip,'area':area,'intf_type':intf_type,'cost':cost,'hello':hello,'dead':dead}

        print(d)
            
