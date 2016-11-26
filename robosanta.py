
#######################################################################
#
#   RoboSanta - a Slack Bot for organising Secret Santa events.
#   Written with love by E. Locard
#   Twitter: @L0C4RD
#   Github: L0C4RD
#
#   Merry Christmas folks! :)
#
#######################################################################

import os, sys, time, random
from slackclient import SlackClient

#Fill in this list with the names of channels you'd like the bot to
#listen to.
target_sources = ["general", "random", "some_other_channel", "etc"]

#It's recommended that you set your OAuth token as an environment
#variable to avoid hardcoding it into your script (reduces the chance of
#you loloopsing your token into a public github or something.) If you
#don't care about that, you can hardcode it here. Up to you, though I'd
#recommend going the environment variable route.
OAuth_token = None
if (OAuth_token is None):
    OAuth_token = os.environ.get("SLACK_TOKEN")

#The persistence file is by default saved in the same directory as this
#script, but you can move it around by specifying a path here.
pfile = "./naughtylist.txt"

bot_name = "robosanta"


#the RoboSanta class basically does all the things.
class RoboSanta_class(object):
    
    def __init__(self, target_sources, destroy_list_on_generate = False, debug=False):
        
        #Sign into slack
        self.sc = SlackClient(OAuth_token)
        if (not self.sc.rtm_connect()):
            print "Could not sign into slack."
            sys.exit()
            
        self.botid = None
        self.sources = None
        self.atme = None
        self.userlist = None
        self.persistencefile = None
        self.debug = debug
        self.dlog = destroy_list_on_generate
        self.randerm = random.SystemRandom()
        
        #Get my own user ID (and everyone elses)
        api_call = self.sc.api_call("users.list")
        if api_call.get("ok"):
            users = api_call.get("members")
            self.userlist = users
            for user in users:
                if (("name" in user) and (user.get("name") == bot_name)):
                    self.botid = user.get("id")
                    self.atme = "<@" + self.botid + ">"

        if (self.botid is None):
            print "Could not get bot id."
            sys.exit()
        
        if (self.debug):
            print "My id number is " + str(self.botid)
        
        #Attempt to find target channels
        api_call = self.sc.api_call("channels.list")
        if api_call.get("ok"):
            channels = api_call.get("channels")
            
            self.sources = {}
            for channel in channels:
                if (("name" in channel) and (channel.get("name") in target_sources)):
                    self.sources[channel.get("name")] = channel.get("id")
        
        #Attempt to find private channels
        api_call = self.sc.api_call("groups.list")
        if api_call.get("ok"):
            groups = api_call.get("groups")

            for group in groups:
                if (("name" in group) and (group.get("name") in target_sources)):
                    self.sources[group.get("name")] = group.get("id")

        if (self.sources is None):
            print "Could not access list of channels."
            sys.exit()

        if (len(self.sources) < len(target_sources)):
            for t in target_sources:
                if t not in self.sources.keys():
                    print "Could not find \"" + t + "\""
            sys.exit()
        
        if (self.debug):
            print self.sources
        
        #Begin naughty list
        self.naughtylist = set()

        self.p = False
        try:
            self.persistencefile = open(pfile, "r")
        except IOError:
            print "Could not open naughtylist... starting without persistence."
        else:
            self.p = True
            for line in self.persistencefile:
                person = line.strip()
                if (len(person) > 0):
                    self.naughtylist.add(person)
            self.persistencefile.close()

        if (self.debug):
            raw_input("Secret Santa bot initialised. Press enter to start Secret Santa.")

        return

    
    def parse(self):
        output_list = self.sc.rtm_read()
        if ((output_list) and (len(output_list) > 0)):
            for msg in output_list:
                if (self.debug):
                    print msg
                if ((msg) and ("text" in msg) and ("channel" in msg) and (msg["channel"] in self.sources.values()) and (self.atme in msg["text"])):
                    self.respond(msg)

    def respond(self, msg):
        command = msg["text"].split(self.atme)[1].strip().lower()
        channel = msg["channel"]
        
        #Command select.
        #You can obviously add other commands to this, if you'd like.
        #For example: my team added some goofy commands to generate
        #links to random gifts on Amazon.

        #Add a user.
        if (command == "addme"):
            person = msg["user"]
            person_info = self.sc.api_call("users.info", user=person)
            if (person_info and person_info["ok"]):
                
                if (self.debug):
                    print "Received \"addme\" command from user " + str(msg["user"]) + "(" + str(person_info["user"]["name"]) + ")"
                
                self.naughtylist.add(str(msg["user"]))
                self.persist_add(str(msg["user"]))
                response = "Ho Ho Ho! Merry Christmas *@"+str(person_info["user"]["name"])+"*!"
                self.sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            else:
                response = "Bah Humbug!"
                self.sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

        #Remove a user.
        elif (command == "removeme"):
            person = msg["user"]
            person_info = self.sc.api_call("users.info", user=person)
            if (person_info and person_info["ok"]):
                
                if (self.debug):
                    print "Received \"removeme\" command from user " + str(msg["user"]) + "(" + str(person_info["user"]["name"]) + ")"
                
                if (str(msg["user"]) in self.naughtylist):
                    self.naughtylist.remove(str(msg["user"]))
                    self.persist_remove(str(msg["user"]))
                    response = "Ho Ho Ho! Only coal for you then, *@"+str(person_info["user"]["name"])+"*!"
                else:
                    response = "Ho Ho Ho! You weren't on my naughty list anyway, *@"+str(person_info["user"]["name"])+"*!"
                self.sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            else:
                response = "Bah Humbug!"
                self.sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

        #Print a list of participants.
        elif (command == "naughtylist"):

            if (self.debug):
                print "Received \"naughtylist\" command"
                
            response = "My naughty list this year:\n"
    
            if (len(self.naughtylist) == 0):
                response += "> _(no-one yet!)_"
            else:
                for naughty in self.naughtylist:
                    person_info = self.sc.api_call("users.info", user=naughty)
                    if (person_info and person_info["ok"]):
                        response += "> *@" + str(person_info["user"]["name"]) + "*\n"
                    #response += "> " + self.naughtylist[naughty] + "\n"
            self.sc.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

        #Assign gift givers to gift recipients, and send everyone a message.
        elif (command == "givegifts"):

            if (self.debug):
                print "Received \"givegifts\" command"

            pairings = {}
            suckers = list(self.naughtylist)
            
            #pick first person.
            first_sucker_index = self.randerm.randrange(len(suckers))
            first_sucker = suckers[first_sucker_index]
            del suckers[first_sucker_index]
            
            giver = first_sucker
            
            while (len(suckers) > 0):
                recipient_index = self.randerm.randrange(len(suckers))
                recipient = suckers[recipient_index]
                del suckers[recipient_index]
                pairings[giver] = recipient
                giver = recipient
            
            #finally, give the last person to the first.
            pairings[giver] = first_sucker
            
            if (self.debug):
                for i in pairings:
                    print "('" + i + "': '" + pairings[i] +"')"
            
            #send messages
            dmids = {}
            for i in pairings:
                api_call = self.sc.api_call("im.open", user=i, return_im=True)
                if (api_call.get("ok") and api_call.get("channel")["is_open"]):
                    if (self.debug):
                        print api_call.get("channel")
                        print ""
                    dmids[i] = api_call.get("channel")["id"]
            if (self.debug):
                print dmids
                print ""
            if (len(dmids) != len(pairings)):
                print "Could not open message channels to the following subscribed users:"
                for i in pairings:
                    if (i not in dmids):
                        person_info = self.sc.api_call("users.info", user=i)
                        if (person_info.get("ok")):
                            print "User *@" + str(person_info["user"]["name"]) + "* (" + i + ")"
                        else:
                            print "User " + i
            else:
                for i in pairings:
                    giver_info = self.sc.api_call("users.info", user=i)
                    recipient_info = self.sc.api_call("users.info", user=pairings[i])
                    response = "Ho Ho Ho, *@" + str(giver_info["user"]["name"]) + "*!"
                    self.sc.api_call("chat.postMessage", channel=dmids[i], text=response, as_user=True)
                    response = "You've been assigned user *@" + str(recipient_info["user"]["name"]) + "*!"
                    self.sc.api_call("chat.postMessage", channel=dmids[i], text=response, as_user=True)
                    response = "Be sure to get them something nice!"
                    self.sc.api_call("chat.postMessage", channel=dmids[i], text=response, as_user=True)
                    response = "Merry Christmas, *@" + str(giver_info["user"]["name"])+ "*!"
                    self.sc.api_call("chat.postMessage", channel=dmids[i], text=response, as_user=True)
                if (self.dlog):
                    self.naughtylist = set()
                    self.persistencefile = open(pfile, "w+")
                    self.persistencefile.close()

    #Add a user to the persistence file
    def persist_add(self, person):
        if (self.p):
            self.persistencefile = open(pfile, "r+")
            found = False
            for line in self.persistencefile:
                if (line.strip() == person):
                    found = True
            if (found == False):
                self.persistencefile.seek(0,2)
                self.persistencefile.write(person+"\n")
            self.persistencefile.close()

    #Remove a user from the persistence file
    def persist_remove(self, person):
        if (self.p):
            self.persistencefile = open(pfile, "r")
            lines = []
            for line in self.persistencefile:
                if (line.strip() != person):
                    lines.append(line.strip())
            self.persistencefile.close()
            self.persistencefile = open(pfile, "w")
            for line in lines:
                self.persistencefile.write(line + "\n")
            self.persistencefile.close()



#These lines just create a RoboSanta object, then tell it to go ahead
#and start parsing messages.
#You can turn on debug messages by adding "debug=True" as an argument to
#RoboSanta_class.
RoboSanta = RoboSanta_class(target_sources)

while (True):
    inbox = RoboSanta.parse()
    time.sleep(1)
