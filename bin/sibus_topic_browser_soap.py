# ===========================================
# ./wsadmin.sh -lang jython -host <dmgr_host> -port <dmgr_port> -f sibus_jms_topic_browser_soap.py
#   version 1.1
# ===========================================
script_name = "sibus_topic_browser_soap.py"

import sys

def print_usage():
  print('\nUsage: wsadmin.sh -conntype SOAP -lang jython -f <%s>  <BusName> <TopicName>' % script_name)
  print('\n                    BusName:  the SIBus name')
  print('\n                  TopicName:  the SIBus destination TopicName (not the JNDI)')
  print
  return

def topic_browser( *argv):
  # first check if we are really connected: AdminTask should be available
  try:
    cellName = AdminControl.getCell()
  except:
    print('\nWARNING: Not connected')
    print_usage()
    # sys.exit()
    return

  # test parameter
  print "\n#" + "-"*30
  if len( argv) >= 2:
    bus_name   = argv[0]
    topic_name = argv[1]
    print('Browing message(s) from SIBus Topic destination [%s:%s]' % ( bus_name, topic_name))
  else:
    print_usage()
    return

  sibtopic = AdminControl.queryNames( 'type=SIBPublicationPoint,name=%s,SIBus=%s,*' % ( topic_name, bus_name))
  # print( '\nsibtopic: ' + str( sibtopic))
  # print( sibqueue)
  if sibtopic:
    sibtopic_obj = AdminControl.makeObjectName( sibtopic)
    sibtopic_depth = AdminControl.getAttribute( sibtopic, 'depth')
    print( '\n%s message(s) available' % sibtopic_depth)
    # sibtopic_depth = AdminControl.invoke( sibtopic, 'getDepth')

    sibtopic_id = AdminControl.getAttribute( sibtopic, 'id')

    #get topic subscriptions
    # subs = AdminControl.invoke( sibtopic, 'getSubscriptions').split( lineSeparator)
    subs_obj = AdminControl.invoke_jmx( sibtopic_obj, 'getSubscriptions', [], [])

    for sub in subs_obj:
      print( '\nsubscriber: %s## %s (depth: %s)' % ( sub.getIdentifier(), sub.getSubscriberId(), sub.getDepth()))
      # for m in sub.getClass().getMethods(): print m
      # print
      messages = AdminControl.invoke_jmx( sibtopic_obj, 'getSubscriptionMessages', [sub.getId()], ['java.lang.String'])
      for msg in messages:
        msg_id = msg.getId()
        msg_sysid = msg.getSystemMessageId()
        msg_length = msg.getApproximateLength()
        msg_detail = AdminControl.invoke_jmx( sibtopic_obj, 'getSubscriptionMessageData',[sub.getId(),msg.getId(),100], ['java.lang.String','java.lang.String', 'java.lang.Integer'])
        print( '-'*11 )
        print( '        id: %s' % msg_id)
        print( '     sysid: %s' % msg_sysid)
        print( '    length: %d' % msg_length)
        print( '      hexa: %s' % ':'.join( [ '%02x' % x for x in msg_detail]))
        print( '     ascii: %s' % ''.join( [ chr(x) for x in msg_detail]))


  else:
    print( 'Topic %s not found' % topic_name)

  print( "\nFinished.")

# =======================================================================================================================
# for WAS 6: __name__ == "main"
if __name__ == "__main__" or __name__ == "main":
  topic_browser( *sys.argv)
  # sys.exit()
else:
  try:
    import AdminConfig, AdminControl, AdminApp, AdminTask, Help
    import lineSeparator
  except ImportError:
    pass
 
