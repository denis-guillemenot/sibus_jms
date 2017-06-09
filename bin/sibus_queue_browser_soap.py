# ===========================================
# ./wsadmin.sh -lang jython -host <dmgr_host> -port <dmgr_port> -f sibus_jms_queue_browser_soap.py
#   version 1.1
# ===========================================
script_name = "sibus_queue_browser_soap.py"

import sys

def print_usage():
  print('\nUsage: wsadmin.sh -conntype SOAP -lang jython -f <%s>  <BusName> <QueueName>' % script_name)
  print('\n                    BusName:  the SIBus name')
  print('\n                  QueueName:  the SIBus destination QueueName (not the JNDI)')
  print
  return

def queue_browser( *argv):
  # first check if we are really connected: AdminTask should be available
  try:
    cellName = AdminControl.getCell()
  except:
    print('\nWARNING: Not connected')
    print_usage()
    # sys.exit()
    return

  # test parameter
  print "#" + "-" * 30
  if len( argv) >= 2:
    bus_name   = argv[0]
    queue_name = argv[1]
    print('Browsing messages from SIBus Queue destination [%s:%s]' % ( bus_name, queue_name))
  else:
    print_usage()
    return

  sibqueue = AdminControl.queryNames( 'type=SIBQueuePoint,name=%s,SIBus=%s,*' % ( queue_name, bus_name))
  # print( '\nsibqueue: ' + str( sibqueue))
  # print( sibqueue)
  if sibqueue:
    sibqueue_depth  = AdminControl.getAttribute( sibqueue, 'depth')
    sibqueue_engine = AdminControl.makeObjectName( sibqueue).getKeyProperty( 'SIBMessagingEngine')
    print( '\n%s message(s) available' % sibqueue_depth)

    sibqueue_id = AdminControl.getAttribute( sibqueue, 'id')
    sibme = AdminControl.queryNames( 'type=SIBMessagingEngine,name=%s,*' % sibqueue_engine)
    sibme_obj = AdminControl.makeObjectName( sibme)

    messages = AdminControl.invoke_jmx( sibme_obj, 'getQueuePointMessages', [sibqueue_id], ['java.lang.String'])
    for msg in messages:
      msg_id = msg.getId()
      msg_sysid = msg.getSystemMessageId()
      msg_length = msg.getApproximateLength()
      msg_detail = AdminControl.invoke_jmx( sibme_obj, 'getQueuePointMessageData',[sibqueue_id, msg_id, 100], ['java.lang.String','java.lang.String', 'java.lang.Integer'])
      print( '-'*10 )
      print( '    id: %s' % msg_id)
      print( ' sysid: %s' % msg_sysid)
      print( 'length: %d' % msg_length)
      # print( 'Hexa: %s' % ':'.join( [ format( x, '02x') for x in msg_detail]))
      print( '  hexa: %s' % ':'.join( [ '%02x' % x for x in msg_detail]))
      print( ' ascii: %s' % ''.join( [ chr(x) for x in msg_detail]))

  else:
    print( 'Queue %s not found' % queue_name)

  print( "\nFinished.")

# =======================================================================================================================
# for WAS 6: __name__ == "main"
if __name__ == "__main__" or __name__ == "main":
  queue_browser( *sys.argv)
  # sys.exit()
else:
  try:
    import AdminConfig, AdminControl, AdminApp, AdminTask, Help
    import lineSeparator
  except ImportError:
    pass
 
