import os
import string
import random

# make Admin modules available to following imports
sys.modules['AdminConfig'] = AdminConfig
sys.modules['AdminControl'] = AdminControl
sys.modules['AdminApp'] = AdminApp
sys.modules['AdminTask'] = AdminTask
sys.modules['Help'] = Help
sys.modules['lineSeparator'] = lineSeparator

# import utilities modules
import   sibus_topic_jms_durable_subscriber_soap as tsubscriber
import             sibus_destinations_depth_soap as depth
import               sibus_queue_jms_writer_soap as qwriter
import               sibus_queue_jms_reader_soap as qreader
import               sibus_topic_jms_writer_soap as twriter
import               sibus_topic_jms_reader_soap as treader

# to generate random ID
def id_generator( size=6, chars= string.uppercase + string.digits):
  r = [ random.choice( chars) for _ in range( size)]
  return ''.join( r)

# varibales
bus_name   = 'myBus'
cf_name    = 'myConnectionFactory'
queue_name = 'myQueue'
topic_name = 'myTopic'
topic_id   = 'id.' + id_generator()
topic_sub  = 'sub.' + id_generator()
iteration  = 1

# create temporary durable subscriber
print
print( 'topic_id: %s    topic_sub: %s' % ( topic_id, topic_sub))
tsubscriber.durable_subscriber( cf_name, topic_name, topic_id, topic_sub, 'create')

# write messages to Queue and Topic
depth.show_depth( )

# os._exit()

# send N=iteration messages to queue and topic
print
for i in range( iteration):
  print( 'Writing message %d' % i)
  qwriter.queue_writer( cf_name, queue_name, 'Queue: test message %d' % i)
  twriter.topic_writer( cf_name, topic_name, 'publisher', 'Topic: test message %d' % i)

# read all messages from Queue and Topic
depth.show_depth( )

print
for i in range( iteration):
  print( 'Reading messages %d' % i)
  qreader.queue_reader( cf_name, queue_name, 'all')
  treader.topic_reader( cf_name, topic_name, topic_id, topic_sub, 'all')

# check Queue and Topic depth
depth.show_depth( )

# delete temporary durable subscriber
tsubscriber.durable_subscriber( cf_name, topic_name, topic_id, topic_sub, 'delete')
