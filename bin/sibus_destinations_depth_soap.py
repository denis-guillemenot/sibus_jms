# ===========================================
# ./wsadmin.sh -lang jython -host <dmgr_host> -port <dmgr_port> -f sibus_destinations_depth_soap.py
#   version 1.2
# ===========================================
script_name = "sibus_destinations_depth_soap.py"

import sys

def print_usage():
  print('\nUsage: wsadmin.sh -conntype SOAP -lang jython -f <%s>' % script_name)
  print
  return


def show_depth( *argv):
  """
    Display J2CConnectionFactory connections factories to SIBus
    Display J2CAdminObject Queues and Topics depths
  """
  # first check if we are really connected: AdminTask should be available
  try:
    cellName = AdminControl.getCell()
  except:
    print('\nWARNING: Not connected')
    print_usage()
    # sys.exit()
    return

  # get all J2CConnectionFactory to link (JNDI) to (SIBus)
  j2c_cf = AdminConfig.list( "J2CConnectionFactory").split( lineSeparator)
  cf_to_sibus = {}
  for c in j2c_cf:
    c_name = AdminConfig.showAttribute( c, 'name')
    c_jndi = AdminConfig.showAttribute( c, 'jndiName')
    cf_to_sibus[ c_name] = {}
    cf_to_sibus[ c_name][ 'jndi'] = c_jndi
    c_props = AdminConfig.showAttribute( c, 'propertySet')
    if c_props:
      c_def_props = AdminConfig.showAttribute( c_props,  'resourceProperties')[1:-1].split()
      c_sibus = ''
      for p in c_def_props:
        p_name  = AdminConfig.showAttribute( p, 'name')
        p_value = AdminConfig.showAttribute( p, 'value')
        if ( p_name.lower() == 'busname') and ( len( p_value)): c_sibus = p_value
    cf_to_sibus[ c_name][ 'sibus'] = c_sibus

  # reverse dictionnary
  sibus_to_cf = {}
  # print cf_to_sibus
  print
  for j in cf_to_sibus.keys():
    sibus_name = cf_to_sibus[ j][ 'sibus']
    if len( sibus_name):
      if sibus_to_cf.has_key( sibus_name) : sibus_to_cf[ sibus_name].append( j)
      else : sibus_to_cf[ sibus_name] = [ j]

  # print SIBus connection factories
  print( "\n%s %s\n" % ( "#--- JMS Connections to SIBus", "-" * 30))
  for s in sibus_to_cf.keys():
    sibus_name = s
    print( "\n      %d to %s \n" % ( int( len( sibus_to_cf[ s])), sibus_name))
    # print connections factories
    for c in sibus_to_cf[ s]:
      c_jndi = cf_to_sibus[ c][ 'jndi']
      print( "        %s (%s)" %( c, c_jndi))

  # get all J2CAdminObject to link (JNDI) JMS Queue and Topic to (SIBus) Destination
  j2c = AdminConfig.list( "J2CAdminObject").split( lineSeparator)
  jms_to_dest = {}
  for i in j2c:
    jndi_name = AdminConfig.showAttribute( i, 'jndiName')
    jms_to_dest[ jndi_name] = {}
    for j in AdminConfig.showAttribute( i, 'properties')[1:-1].split():
      prop_name = AdminConfig.showAttribute( j, 'name')
      prop_value = AdminConfig.showAttribute( j, 'value')
      jms_to_dest[ jndi_name][ prop_name] = prop_value

  dest_to_jms = {}
  for k, v in jms_to_dest.items():
    bus_name = jms_to_dest[ k][ 'BusName']
    if jms_to_dest[ k].has_key( 'QueueName'): 
      dest_name = 'Queue:' + jms_to_dest[ k][ 'QueueName']
    else:
      # TopicName : JMS Topic name,   TopicSpace: SIBus Topic name
      dest_name = 'Topic:' + jms_to_dest[ k][ 'TopicSpace']
    dest_to_jms[ bus_name + ':' + dest_name] = k

  # check queue depth
  print( "\n%s %s\n" % ( "#--- SIBus Queue(s) Depth -- [SIBus:queue_name (JMS JNDI)]", "-" * 30))
  sibqueuepoints = AdminControl.queryNames('type=SIBQueuePoint,*').split( lineSeparator)
  for d in sibqueuepoints:
    if d != '':
      # sibus_name = AdminControl.makeObjectName( sibqueuepoints[0]).getKeyProperty( 'SIBus')
      sibus_name = AdminControl.makeObjectName( d).getKeyProperty( 'SIBus')
      queue_name = AdminControl.getAttribute(d, 'identifier')
      queue_depth= AdminControl.getAttribute(d, 'depth')
      if dest_to_jms.has_key( sibus_name + ':Queue:' + queue_name):
        jms_name = '(%s)' % dest_to_jms[ sibus_name + ':Queue:' + queue_name]
      else:
        jms_name = ''
      print( "  %5d messages in %s:%s %s" %( int( queue_depth), sibus_name, queue_name, jms_name))

  # check topic depth
  print( "\n%s %s\n" % ( "#--- SIBus Topic(s) Depth -- [SIBus:topicspace_name (JMS JNDI)]", "-" * 30))
  sibpubpoints = AdminControl.queryNames('type=SIBPublicationPoint,*').split( lineSeparator)
  if sibpubpoints: 
    for d in sibpubpoints:
      if d != '':
        # sibus_name = AdminControl.makeObjectName( sibqueuepoints[0]).getKeyProperty( 'SIBus')
        sibus_name = AdminControl.makeObjectName( d).getKeyProperty( 'SIBus')
        topic_name = AdminControl.getAttribute(d, 'identifier')
        topic_depth= AdminControl.getAttribute(d, 'depth')
        if dest_to_jms.has_key( sibus_name + ':Topic:' + topic_name):
          jms_name = '(%s)' % dest_to_jms[ sibus_name + ':Topic:' + topic_name]
        else:
          jms_name = ''
        print( "  %5d messages in %s:%s %s" % ( int( topic_depth), sibus_name, topic_name, jms_name))
        # check all subscribers depth
        subs = AdminControl.invoke_jmx( AdminControl.makeObjectName( d), 'getSubscriptions', [], [])
        for s in subs:
          print( "    %5d messages for subscriber %s" % ( int( s.getDepth()), s.getSubscriberId()))
        if (len(subs) > 0): print

# =======================================================================================================================
# for WAS 6: __name__ == "main"
if __name__ == "__main__" or __name__ == "main":
  show_depth( *sys.argv)
  # sys.exit()
else:
  try:
    import AdminConfig, AdminControl, AdminApp, AdminTask, Help
    import lineSeparator
  except ImportError:
    pass
