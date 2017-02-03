#!/usr/bin/python
import os, time, sqlite3
from slackclient import SlackClient
from secrets import SLACK_BOT_TOKEN, BOT_ID # <== Storing my authentication there

# constants
AT_BOT = "<@" + BOT_ID + ">"
WHAT_COMMAND = "what"
WILDART_COMMAND = "wild"
ALBUM_COMMAND = "album"
HELP_COMMAND = "help"
COUNT_COMMAND = "count"
DIE_COMMAND = "die"

# gets reset by @jazzbot die command  - to kill off bot so it can be restarted
Alive = True

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)


def handle_album(command):
    
    """
      Process the album command
    """
    conn = sqlite3.connect('myjazzalbums.sqlite')
    cur = conn.cursor()

    if command [-1] == "?": 
        album_name = command[5:-1].strip()
    else: 
        album_name = command[5:].strip()
    print "Album name = " + "'" + album_name +"'"

    cur.execute (" SELECT Artist.name FROM Album JOIN Artist ON Artist.id = Album.artist_id WHERE Album.title =?" , (album_name + "\n",) )
        
    count = 0
    response =  'Albums called ' + album_name + '\n'

    for row in cur :
        response += "Artist: " + row[0]
        count = count + 1
    response = "I have "+ str (count) +" " +  response
    return response
    cur.close()

        

def handle_count(command):

    """
      Process the handle command
    """

    conn = sqlite3.connect('myjazzalbums.sqlite')
    cur = conn.cursor()

    if command [-1] == "?": 
        artist_name = command[5:-1].strip().title()
    else: 
        artist_name = command[5:].strip().title()

    cur.execute (" SELECT Album.title FROM Album JOIN Artist ON Artist.id = Album.artist_id WHERE Artist.name =?" , (artist_name,) )
    #c.execute('SELECT * FROM stocks WHERE symbol=?', t)
    count = 0

    for row in cur :
        count = count + 1
    response = 'I have '+ str (count) + ' albums for ' + artist_name + ':\nIf you want to know the titles use the command *what* ' + artist_name
    return response
    cur.close()

def handle_wildartist(command):
    """
      Process the wildcard command
    """
    
    conn = sqlite3.connect('myjazzalbums.sqlite')
    cur = conn.cursor()

    if command [-1] == "?": 
        artist_name = "%"+command[5:-1].strip().title()+"%"
    else: 
        artist_name = "%"+command[5:].strip().title()+"%"

    cur.execute (" SELECT Artist.name, Album.title FROM Album JOIN Artist ON Artist.id = Album.artist_id WHERE Artist.name LIKE ?" , (artist_name,) )
    #c.execute('SELECT * FROM stocks WHERE symbol=?', t)
    count = 0
    response =  ''

    for row in cur :
        response += "*"+row[0]+ "*: "+ row[1]
        count = count + 1
    
    response = "I have "+ str(count) + " albums where the artist incudes " + artist_name.split("%")[1]+ "\n" + response
    return response
    cur.close()     


def handle_what(command):
    """
      Process the what command
    """
    
    conn = sqlite3.connect('myjazzalbums.sqlite')
    cur = conn.cursor()

    if command [-1] == "?": 
        artist_name = command[5:-1].strip().title()
    else: 
        artist_name = command[5:].strip().title()

    cur.execute (" SELECT Album.title FROM Album JOIN Artist ON Artist.id = Album.artist_id WHERE Artist.name =?" , (artist_name,) )
    #c.execute('SELECT * FROM stocks WHERE symbol=?', t)
    count = 0
    response =  'Albums for ' + artist_name + ':\n'

    for row in cur :
        response += row[0]
        count = count + 1
    response = "I have "+ str (count) +" " +  response
    return response
    cur.close()

def handle_help(commands):
    """
      Process the help command
    """
    # Place holder for any attachments we want to send
    
    response = "My capabilities are few, but generally well-executed. \nI find that when mistakes do happen it is not at my end. So, to keep you right, here are some pointers:\n"

    # Add help message for each command
    response += "*" + HELP_COMMAND + "* - shows this message\n"
    response += "*" + WHAT_COMMAND + "* - returns which albums I have by an artist\n \t e.g.: *'What Miles Davis?'*' will show what Miles Davis Albums I have \n"
    response += "*" + WILDART_COMMAND + "* - is a wildcard search which shows all albums where the artist name partially matches the query \n \t e.g *'Wild Sonny?'*' will match albums by Sonny Stitt or Sonny Rollins\n"
    response += "*" + COUNT_COMMAND + "* - shows you how many albums I have by an artist \n \t e.g. *'Count Count Basie?'*' will count how many Count Basie albums I have. \n"
    response += "*" + ALBUM_COMMAND + "* - shows which albums I have of that name\n \t e.g. *'Album Stardust?'* will show which albums I have named Stardust \n"
    response += "And in all queries the '?' is optional, as are capitals.\n"
    
    return response

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    
    if command.lower().startswith(WHAT_COMMAND):
        response = handle_what(command)
    if command.lower().startswith(WILDART_COMMAND):
        response = handle_wildartist(command)
    elif command.lower().startswith(ALBUM_COMMAND):
        response = handle_album(command)
    elif command.lower().startswith(COUNT_COMMAND):
        response = handle_count (command)
    elif command.lower().startswith(HELP_COMMAND):
        response = handle_help (command)
    elif command.lower().startswith(DIE_COMMAND):
        Alive = False
    else:
        response = "I'm not sure what you mean. Try *'@jazzbot help'* for more options."

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True and Alive :
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

