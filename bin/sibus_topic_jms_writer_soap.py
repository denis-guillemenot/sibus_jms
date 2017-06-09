# ===========================================
# ./wsadmin.sh -lang jython -host <dmgr_host> -port <dmgr_port> -f sibus_jms_topic_writer_soap.py
#   version 1.1
# ===========================================
script_name = "sibus_topic_jms_writer_soap.py"

import sys

# default user and password and port
was_user = 'wasadmin'
was_pswd = 'admin'
was_port = 2811

def print_usage():
  print('\nUsage: wsadmin.sh -conntype SOAP -lang jython -f <%s>  <ConnectionFactory> <TopicName> [message]' % script_name)
  print('\n          ConnectionFactory:  as in JNDI jms/ConnectionFactory')  
  print('\n          TopicName: as in JNDI jms/TopicName')
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
      print
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
      print
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
    print
    f = open( 'sibus_conf.py', 'w')
    f.write( "\nwas_user = \'%s\'" % was_user)
    f.write( "\nwas_pswd = \'%s\'" % was_pswd)
    f.write( "\n\n# BOOTSTRAP_ADDRESS")
    f.write( "\nwas_port = %s" % was_port)
    f.close()
    sys.exit(1)

def topic_writer( *argv):
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
  print
  if len( argv) >= 2:
    cf_name = argv[0]
    topic_name = argv[1]
    if len( argv) >= 3: 
      topic_message = ' '.join( argv[2:])
    else:
      topic_message = "TOPIC: Just a test with Jython"
    print('Writing message to [jms/%s]' % topic_name)
    print('Message is: %s ' % topic_message)
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
  session = connection.createSession( java.lang.Boolean('false'), javax.jms.Session.AUTO_ACKNOWLEDGE)

  connection.start()

  # write message to topic
  tsender = session.createProducer( tdestination)
  tsender.send( session.createTextMessage( '%s' % topic_message))

  tsender.close()
  session.close()
  connection.close()
  
  print( "\nFinished.")
  
# =======================================================================================================================
# for WAS 6: __name__ == "main"
if __name__ == "__main__" or __name__ == "main":
  topic_writer( *sys.argv)
  # sys.exit()
else:
  try:
    import AdminConfig, AdminControl, AdminApp, AdminTask, Help
    import lineSeparator
    import java
  except ImportError:
    pass
 
