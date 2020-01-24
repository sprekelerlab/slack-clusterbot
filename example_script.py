import time
from clusterbot import ClusterBot, activate_logger

# Print confirmation about sent Slack messages
activate_logger()
# Debug mode
#activate_logger('DEBUG')

# Send a message to the default user specified in you config files.
cb = ClusterBot()
message_id = cb.send("Starting example script.")
# Reply to the default user message from above (open a ne Thread).
cb.reply(message_id, "Waiting for 5s.")
# Wait 5 seconds.
time.sleep(5)
# Reply again.
cb.reply(message_id, "5s have passed.")

# Send a message to someone else (not default user)
message_id = cb.send("Hi Denis. I started using ClusterBot :tada:",
                     user_name="Denis Alevi")
# Reply to that message (message_id has to belong to a message exchanged with
# ``user_name``)
cb.reply(message_id, "And I ran the example script!", user_name="Denis Alevi")
