from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asynsock.dgram import udp
import platform

snmpEngine = engine.SnmpEngine()

print('Конфигурация агента...')

# Transport setup UDP over IPv4
IP = '127.0.0.1'
PORT = 1234

config.addSocketTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode((IP, PORT))
)

# SNMPv1/2c setup
# SecurityName <-> CommunityName mapping
config.addV1System(snmpEngine, 'my-area', 'public')

# SNMPv3/USM setup 
# user: usr-md5-des, auth: MD5, priv DES
config.addV3User(
    snmpEngine, 'usr-md5-des',
    config.usmHMACMD5AuthProtocol, 'authkey1',
    config.usmDESPrivProtocol, 'privkey1'
)

# user: usr-none-none, auth: NONE, priv NONE
config.addV3User(
    snmpEngine, 'usr-none-none'
)

# user: usr-md5-none, auth: MD5, priv NONE
config.addV3User(
    snmpEngine, 'usr-md5-none',
    config.usmHMACMD5AuthProtocol, 'authkey1'
)

# user: usr-sha-aes128, auth: SHA, priv AES
config.addV3User(
    snmpEngine, 'usr-sha-aes128',
    config.usmHMACSHAAuthProtocol, 'authkey1',
    config.usmAesCfb128Protocol, 'privkey1'
)

# Access control (VACM) setup
# allow full MIB access for each user
config.addVacmUser(snmpEngine, 2, 'my-area', 'noAuthNoPriv', (1,3,6), (1,3,6)) 
config.addVacmUser(snmpEngine, 3, 'usr-md5-des', 'authPriv', (1,3,6), (1,3,6)) 
config.addVacmUser(snmpEngine, 3, 'usr-none-none', 'noAuthNoPriv', (1,3,6), (1,3,6)) 
config.addVacmUser(snmpEngine, 3, 'usr-md5-none', 'authNoPriv', (1,3,6), (1,3,6)) 
config.addVacmUser(snmpEngine, 3, 'usr-sha-aes128', 'authPriv', (1,3,6), (1,3,6)) 

#
# CommandResponder could serve multiple independent MIB trees
# selected by ContextName parameter. The default ContextName is
# an empty string, this is where SNMP engine's LCD also lives.
#
snmpContext = context.SnmpContext(snmpEngine)

# Add our own Managed Object to default MIB tree
# Get a reference to defautl MIB tree instrumentation
mibInstrumController = snmpContext.getMibInstrum('')

# Create and put on-line my managed object
u=platform.uname()
sysDescr, = mibInstrumController.mibBuilder.importSymbols('SNMPv2-MIB', 'sysDescr')
MibScalarInstance, = mibInstrumController.mibBuilder.importSymbols('SNMPv2-SMI', 'MibScalarInstance')
sysDescrInstance = MibScalarInstance(sysDescr.name, (0,), sysDescr.syntax.clone(u.system+' '+u.node+' '+u.release+' '+u.version+' '+u.processor))
mibInstrumController.mibBuilder.exportSymbols('PYSNMP-EXAMPLE-MIB', sysDescrInstance)  # add anonymous Managed Object Instance

# Register SNMP Applications at the SNMP engine
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

print('Конфигурация агента прошла успешно.')
print('Агент запущен по ip-адресу {} на порту {}.'.format(IP, PORT))

snmpEngine.transportDispatcher.jobStarted(1) 

# Run I/O dispatcher which would receive queries and send responses
try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    print('\nАгент остановлен')