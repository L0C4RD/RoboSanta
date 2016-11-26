# RoboSanta
A Slack Bot for organising Secret Santa events.

## Easy Setup

~ 3 minutes.

1. Register a new bot user for your team. Go to `<your_team>.slack.com/apps/build/custom-integration`, and click on "Bots." Name your bot "robosanta," then click "Add bot integration" (i.e. the massive green button.)

2. Get your API token. It's the thing at the top of the page. You'll need it later. There's a bunch of other customisation options here too; you can fill them in now, or come back and do it later.

3. Add your new bot to the channels you'd like it to listen to.

4. Clone the repo:

	```bash
	git clone git@github.com:L0C4RD/RoboSanta.git
	```

5. Install the slackclient module for python:

	```bash
	pip install slackclient
	```

6. Find the file `robosanta.py` in your newly-cloned repo.

7. Edit the `target_sources` variable such that it is a list containing the names of the channels you'd like the bot to listen to.

8. Run the bot, passing your API token (from step 2) as an environment variable:

	```bash
	SLACK_TOKEN=<your_api_token> python ./robosanta.py
	```



## Interacting with the bot

Anyone on your team can interact with the bot by sending it commands in a channel to which it is listening.

To use a command, just type `@robosanta <command>`. A list of commands is given here:

 - `addme`: registers the user for the event.
 - `removeme`: removes the user from the list of users registered for the event.
 - `naughtylist`: prints a list of users currently registered for the event.
 - `givegifts`: Messages all registered users with a notification telling them to whom they need to give a gift.

##Disclaimer

This is just a bit of Python I hacked together on a Friday afternoon. As such, it is provided as-is, and comes with absolutely no guarantees whatsoever, and I cannot accept responsibility for any interaction between you, it, your users, Slack, or any combination thereof.

I've tested it on my end and it seems pretty robust - my team had a jolly good stab at breaking it and weren't able to cause it to do anything awful.

###Merry Christmas!

```

                            _
                         __{_}_
                       .'______'-.
                     _:-'      `'-:
                _   /   _______    `\
             .-' \  \.-'       `'--./
           .'  \  \ /  () ___ ()    \
           \ \\\#  ||    (___)      |
            \  #\\_||   '.___.'     |
             \___|\  \_________.--./
                  \\ |         \   \--.
                   \\/_________/   /   `\       ,
                   .\\        /`--;`-.   `-.__.'/
                  / _\\   ,_.'   _/ \ \        /
                 |    `\   \   /`    | '.___.-'
                  \____/\   '--\____/
                 /      \\           \
                |        \\           |
                |         \\          |
                |          \\         |
                \           \\        /::.:::..
                 '.___..-.__.\\__.__.':::::::'''''

```


