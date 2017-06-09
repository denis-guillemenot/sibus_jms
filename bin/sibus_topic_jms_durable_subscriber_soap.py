# ===========================================
# ./wsadmin.sh -lang jython -host <dmgr_host> -port <dmgr_port> -f sibus_jms_topic_durable_subscriber_soap.py
#   version 1.1
# ===========================================
script_name = "sibus_topic_jms_durable_subscriber_soap.py"

import sys

# default user and password and port
was_user = 'wasadmin'
was_pswd = 'admin'
was_port = 2811

def print_usage():
  print('\nUsage: wsadmin.sh -conntype SOAP -lang jython -f <%s>  <ConnectionFactory> <TopicName> <client_id> <subscriber_id> <create | delete>' % script_name)
  print('\n          ConnectionFactory:  as in JNDI jms/ConnectionFactory')  
  print('\n                  TopicName:  as in JNDI jms/TopicName')
  print('\n                  client_id:  client identifier')  
  print('\n              subscriber_id:  for DURABLE subscription')
  print
  print('\n                     create:  create subscriber')
  print('\n                     delete:  delete subscriber')
  print
  return

def import_conf():
  """ import or generate 'sibus_conf.py'
      sibus_conf.py:
        was_user = 'wasadmin'
        was_pswd = 'admin'
        was_port = 2811          # (BOOTSTRAP_ADDRESS)
  """

  global was_user, was_pswd, was_port

  try:
    import sibus_conf
    try:
      was_user = sibus_conf.was_user
      was_pswd = sibus_conf.was_pswd
      was_port = sibus_conf.was_port
      print "\n#" + "-"*30
      print "INFO: Using WAS user '%s'and port '%s' defined in 'sibus_conf.py'..." % ( was_user, was_port)
      print "#" + "-"*30      
    except AttributeError, ex:
      print "\n#" + "-"*30
      print "ERROR: File 'sibus_conf.py' is invalid..."
      print "  " + str( ex)
      print "\nExample:"
      print "  sibus_conf.py: "
      print "      was_user = '%s'" % was_user
      print "      was_pswd = '%s'" % was_pswd
      print "      # (BOOTSTRAP_ADDRESS)"
      print "      was_port = %s  " % was_port
      print "#" + "-" * 30
      sys.exit(1)
  except ImportError:
    print "\n#" + "-"*30
    print "INFO: File 'sibus_conf.py' can be used to set 'was_user', 'was_pswd' and 'was_port'"
    print "      Generating one for you !"
    print ""
    print "  sibus_conf.py: "
    print "      was_user = '%s'" % was_user
    print "      was_pswd = '%s'" % was_pswd
    print "      # (BOOTSTRAP_ADDRESS)"
    print "      was_port = %s  " % was_port
    print "#" + "-" * 30  
    f = open( 'sibus_conf.py', 'w')
    f.write( "\nwas_user = \'%s\'" % was_user)
    f.write( "\nwas_pswd = \'%s\'" % was_pswd)
    f.write( "\n\n# BOOTSTRAP_ADDRESS")
    f.write( "\nwas_port = %s" % was_port)
    f.close()
    sys.exit(1)

def durable_subscriber( *argv):
  # first check if we are really connected: AdminTask should be available
  try:
    cellName = AdminControl.getCell()
  except:
    print('\nWARNING: Not connected')
    print_usage()
    # sys.exit()
    return

  try:
    import_conf()
  except SystemExit:
    return

  # test parameter
  print "\n#" + "-"*30
  # print( 'len( argv): %d' % len( argv))
  if len( argv) >= 5:
    cf_name        = argv[0]
    topic_name     = argv[1]
    client_id      = argv[2]
    subscriber_id  = argv[3]
    action         = argv[4]
    if (action.lower() in ['create', 'delete']):
      print('%s subscriber [%s##%s] for Topic [%s]' % ( action, client_id, subscriber_id, topic_name))
    else:
      print_usage()
      return
  else:
    print_usage()
    return

  # import JMS APIs
  import javax.naming
  import javax.jms
  import javax.naming.Context

  # initialize context
  h = java.util.Hashtable()
  h[ javax.naming.Context.INITIAL_CONTEXT_FACTORY] = "com.ibm.websphere.naming.WsnInitialContextFactory"
  h[ javax.naming.Context.PROVIDER_URL] = "corbaloc:iiop:localhost:%s" % was_port
  h[ javax.naming.Context.SECURITY_AUTHENTICATION] = "simple"
  h[ javax.naming.Context.SECURITY_PRINCIPAL] = was_user
  h[ javax.naming.Context.SECURITY_CREDENTIALS] = was_pswd
  initcontext = javax.naming.InitialContext( h)

  # search connection factory and queue
  factory = initcontext.lookup('jms/%s' % cf_name)
  tdestination = initcontext.lookup('jms/%s' % topic_name)
  # initialize JNDI context
  initcontext.close()

  # create connection and session for topic
  connection = factory.createConnection( was_user, was_pswd)

  # need to set client ID for Topic Space
  connection.setClientID('%s' % client_id)
  
  session = connection.createSession( java.lang.Boolean('false'), javax.jms.Session.AUTO_ACKNOWLEDGE)

  # read topic without waiting any available message
  if action.lower() == 'create':
    subscriber = session.createDurableSubscriber( tdestination, '%s' % subscriber_id)
  if action.lower() == 'delete':
    # unsubscribe from Topic
    session.unsubscribe( '%s' % subscriber_id)
  else:
    pass
  
  session.close()
  print( "\nFinished.")
  return 
  
# =======================================================================================================================
# for WAS 6: __name__ == "main"
if __name__ == "__main__" or __name__ == "main":
  durable_subscriber( *sys.argv)
  # sys.exit()
else:
  try:
    import AdminConfig, AdminControl, AdminApp, AdminTask, Help
    import lineSeparator
    import java
  except ImportError:
    pass 
