import time
from clusterbot import ClusterBot, activate_logger

# Print confirmation about sent Slack messages
activate_logger()
# Debug mode
# activate_logger('DEBUG')

# Send a message to the default user specified in you config files.
bot = ClusterBot()
message_id = bot.send("Starting example script.")
# Reply to the default user message from above (open a ne Thread).
bot.reply(message_id, "Waiting for 5s.")
# Wait 5 seconds.
time.sleep(5)
# Reply again.
bot.reply(message_id, "5s have passed.")

# Send a message to someone else (not default user)
message_id = bot.send(
    "Hi Denis. I started using ClusterBot :tada:", user_name="Denis Alevi"
)
# Reply to that message (message_id has to belong to a message exchanged with
# ``user_name``)
bot.reply(message_id, "And I ran the example script!", user_name="Denis Alevi")

# Upload a file to your slack chat
message_id = bot.upload(
    file_name="README.md", message="Upload of README.md", user_name="Denis Alevi"
)

# Update/edit a previously send message
message_id = bot.reply(message_id, "An answer to this file", user_name="Denis Alevi")
bot.update(message_id, "An updated answer to this figure.", user_name="Denis Alevi")

# Initialize and update a progress bar
bot.init_pbar(10)
for i in range(10):
    message_new = bot.update_pbar()
    time.sleep(1)
