#!/usr/bin/python
import os, time
from slackclient import SlackClient
from secrets import SLACK_BOT_TOKEN, BOT_ID # <== Storing my authentication there
response = ""

# constants
AT_BOT = "<@" + BOT_ID + ">"
WHAT_COMMAND = "what"
ALBUM_COMMAND = "album"
HELP_COMMAND = "help"
HOWMANY_COMMAND = "how"

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

def handle_album(commands):
    """
      Process the album command
    """
    response = "Fake response - a place holder for real DB query response\n\n"
    response += "I have 2 albums called '*So What*'. These are by\n"
    response += "*Al Cohn*\n"
    response += "*Zoot Sims*\n"
    return response

def handle_howmany(commands):
    """
      Process the how_many command
    """
    # Place holder for real DB query response
    response = "Fake response - a place holder for real DB query response\n\n"
    response += "I have 5 albums by Charlie Parker. These are \n"
    response += "to list these ask 'What Charlie Parker?'"

    return response

def handle_what(commands):
    """
      Process the what command
    """
    # Place holder for real DB query response
    response = "Fake response - a place holder for real DB query response\n\n"
    response += "I have 3 albums by Miles Davis. These are \n"
    response += "*Bitches Brew*\n"
    response += "*Miles Ahead*\n"
    response += "*Filles De Kilamanjairo*"

    return response

def handle_help(commands):
    """
      Process the help command
    """
    # Place holder for any attachments we want to send
    
    response = "I'm just a collection of 1s and 0s so the famous phrase 'garbage in, garbage out' applies to me.\n So far I've evolved to understand\n"

    # Add help message for each command
    response += "*" + HELP_COMMAND + "* - shows this message\n"
    response += "*" + WHAT_COMMAND + "* - returns which ablbums I have by an artist\n \t e.g.: 'What Miles Davis?' will show what Miles Davis Albums I have \n"
    response += "*" + HOWMANY_COMMAND + "* - shows you how many albums I have by an artist \n \t e.g. 'How many Charlie Parker?' will count how many Charlie Parker albums I have. \n"
    response += "*" + ALBUM_COMMAND + "* - shows which albums I have of that name\n \t e.g. 'Album Stardust?'' will show which albums I have named Stardust \n"

    return response

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    commands = command.split()


    if commands[0].lower() == WHAT_COMMAND:
        response = handle_what(commands)
    elif commands[0].lower() == ALBUM_COMMAND:
        response = handle_album(commands)
    elif commands[0].lower() == HOWMANY_COMMAND and commands[1].lower() == 'many':
        response = handle_howmany (commands)
    elif commands[0].lower() == HELP_COMMAND:
        response = handle_help (commands)
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
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")