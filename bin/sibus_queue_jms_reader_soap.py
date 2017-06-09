# ===========================================
# ./wsadmin.sh -lang jython -host <dmgr_host> -port <dmgr_port> -f sibus_jms_queue_reader_soap.py
#   version 1.1
# ===========================================
script_name = "sibus_queue_jms_reader_soap.py"

import sys

# default user and password and port
was_user = 'wasadmin'
was_pswd = 'admin'
was_port = 2811

def print_usage():
  print('\nUsage: wsadmin.sh -conntype SOAP -lang jython -f <%s>  <ConnectionFactory> <QueueName> [all]' % script_name)
  print('\n          ConnectionFactory:  as in JNDI jms/ConnectionFactory')
  print('\n                  QueueName:  as in JNDI jms/QueueName')
  print('\n                        all:  read all available message')  
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


def queue_reader( *argv):
  """
    read one message or all messages from a JMS Queue
  """

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
  if len( argv) >= 2:
    read_all = 0
    cf_name = argv[0]
    queue_name = argv[1]
    print('Reading message from [jms/%s]' % queue_name)
    if len( argv) >= 3:
      read_all = 1
      print('Reading all messages')
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
  qdestination = initcontext.lookup('jms/%s' % queue_name)
  # initialize JNDI context
  initcontext.close()

  # create connection and session for queue
  connection = factory.createConnection( 'wasadmin', 'admin')
  session = connection.createSession( java.lang.Boolean('false'), javax.jms.Session.AUTO_ACKNOWLEDGE)

  connection.start()

  # read queue
  reader = session.createConsumer( qdestination)

  finished = 0
  read_count = 0
  while not finished:
    qmessage = reader.receiveNoWait()
    if qmessage:
      print( qmessage)
      print
      read_count += 1
      if not read_all:
        finished = 1
    else:
      finished = 1


  connection.close()
  session.close()

  print( "\nFinished.")

# =======================================================================================================================
# for WAS 6: __name__ == "main"
if __name__ == "__main__" or __name__ == "main":
  queue_reader( *sys.argv)
  # sys.exit()
else:
  try:
    import AdminConfig, AdminControl, AdminApp, AdminTask, Help
    import lineSeparator
    import java
  except ImportError:
    pass
 
