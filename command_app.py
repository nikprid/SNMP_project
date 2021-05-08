from pysnmp.hlapi import *

iterator = getCmd(
    SnmpEngine(),
    CommunityData('public', mpModel=1),
    UdpTransportTarget(('127.0.0.1', 1234)),
    ContextData(),
    ObjectType(ObjectIdentity('1.3.6.1.2.1.1.2.0'))
)

for errorIndication, errorStatus, errorIndex, varBinds in iterator:

    if errorIndication:
        print(errorIndication)
        break

    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        break

    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))

