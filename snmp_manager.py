from pysnmp.hlapi import *

g = nextCmd(
    SnmpEngine(), 
    CommunityData('public', mpModel=1), 
    UdpTransportTarget(('localhost', 161)), 
    ContextData(), 
    ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
)

errorIndication, errorStatus, errorIndex, varBinds = next(g)

for varBind in varBinds:
    print(' = '.join([x.prettyPrint() for x in varBind]))