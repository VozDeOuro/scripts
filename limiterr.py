#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this was edited from https://github.com/blacktwin/JBOPS killstream script 
# this was edited as a Workaround to Quick fix my needs so its not the best code

from __future__ import print_function
from __future__ import unicode_literals

from builtins import range
import requests
import argparse
from datetime import datetime, timedelta
import sys
import os
from plexapi.server import PlexServer
from time import time as ttime
from time import sleep

TAUTULLI_URL = 'https://TAUTULLI_URL.com.br'
TAUTULLI_APIKEY = 'TAUTULLI_APIKEY'
PLEX_URL = 'http://192.168.0.10:32400'
PLEX_TOKEN = 'PLEX_TOKEN'

# Environmental Variables
PLEX_URL = os.getenv('PLEX_URL', PLEX_URL)
PLEX_TOKEN = os.getenv('PLEX_TOKEN', PLEX_TOKEN)
TAUTULLI_URL = os.getenv('TAUTULLI_URL', TAUTULLI_URL)
TAUTULLI_APIKEY = os.getenv('TAUTULLI_APIKEY', TAUTULLI_APIKEY)
TAUTULLI_ENCODING = os.getenv('TAUTULLI_ENCODING', 'UTF-8')

SUBJECT_TEXT = "Tautulli has killed a stream."
BODY_TEXT = "Killed session ID '{id}'. Reason: {message}"
BODY_TEXT_USER = "Killed {user}'s stream. Reason: {message}."
LIMIT_MESSAGE = 'Are you still watching or are you asleep? ' \
                'If not please wait ~{delay} seconds and try again.'

sess = requests.Session()
# Ignore verifying the SSL certificate
sess.verify = False  # '/path/to/certfile'
# If verify is set to a path to a directory,
# the directory must have been processed using the c_rehash utility supplied
# with OpenSSL.
if sess.verify is False:
    # Disable the warning that the request is insecure, we know that...
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=sess)
lib_dict = {x.title: x.key for x in plex.library.sections()}


SELECTOR = ['watch', 'plays', 'time', 'limit']
ENABLE_LAST_KILL = ['yes', 'no']
ENABLE_WATCHED = ['yes', 'no']
TODAY = datetime.now()
TODAY_FORMATED = TODAY.strftime("%Y-%m-%d %H:%M")
unix_time = int(ttime())
LAST_KILL_FILE = f"last_killed.txt"


def send_notification(subject_text, body_text, notifier_id):
    """Send a notification through Tautulli

    Parameters
    ----------
    subject_text : str
        The text to use for the subject line of the message.
    body_text : str
        The text to use for the body of the notification.
    notifier_id : int
        Tautulli Notification Agent ID to send the notification to.
    """
    payload = {'apikey': TAUTULLI_APIKEY,
               'cmd': 'notify',
               'notifier_id': notifier_id,
               'subject': subject_text,
               'body': body_text}

    try:
        req = sess.post(TAUTULLI_URL.rstrip('/') + '/api/v2', params=payload)
        response = req.json()

        if response['response']['result'] == 'success':
            sys.stdout.write("Successfully sent Tautulli notification.\n")
        else:
            raise Exception(response['response']['message'])
    except Exception as e:
        sys.stderr.write(
            "Tautulli API 'notify' request failed: {0}.\n".format(e))
        return None


def get_activity(session_id=None):
    """Get the current activity on the PMS.

    Returns
    -------
    list
        The current active sessions on the Plex server.
    """
    payload = {'apikey': TAUTULLI_APIKEY,
               'cmd': 'get_activity'}
    if session_id:
        payload['session_id'] = session_id

    try:
        req = sess.get(TAUTULLI_URL.rstrip('/') + '/api/v2', params=payload)
        response = req.json()

        if session_id:
            res_data = response['response']['data']
        else:
            res_data = response['response']['data']['sessions']
        return res_data

    except Exception as e:
        sys.stderr.write(
            "Tautulli API 'get_activity' request failed: {0}.\n".format(e))
        pass


def get_history(username, start_date=None, section_id=None):
    """Get the Tautulli history.

    Parameters
    ----------
    username : str
        The username to gather history from.

    Optional
    ----------
    start_date : list ["YYYY-MM-DD", ...]
        The date in history to search.
    section_id : int
        The libraries numeric identifier

    Returns
    -------
    dict
        The total number of watches, plays, or total playtime.
    """
    payload = {'apikey': TAUTULLI_APIKEY,
               'cmd': 'get_history',
               'user': username}

    if start_date:
        payload['start_date'] = start_date

    if section_id:
        payload['section_id '] = section_id

    try:
        req = sess.get(TAUTULLI_URL.rstrip('/') + '/api/v2', params=payload)
        response = req.json()

        res_data = response['response']['data']
        #print(res_data)
        return res_data

    except Exception as e:
        sys.stderr.write("Tautulli API 'get_history' request failed: {0}.".format(e))


def terminate_session(session_id, message, notifier=None, username=None):
    """Stop a streaming session.

    Parameters
    ----------
    session_id : str
        The session ID of the stream to terminate.
    message : str
        The message to display to the user when terminating a stream.
    notifier : int
        Notification agent ID to send a message to (the default is None).
    username : str
        The username for the terminated session (the default is None).
    """
    payload = {'apikey': TAUTULLI_APIKEY,
               'cmd': 'terminate_session',
               'session_id': session_id,
               'message': message}

    try:
        req = sess.post(TAUTULLI_URL.rstrip('/') + '/api/v2', params=payload)
        response = req.json()

        if response['response']['result'] == 'success':
            sys.stdout.write(
                "Successfully killed Plex session: {0}.\n".format(session_id))
            reset_last_kill()
            if notifier:
                if username:
                    body = BODY_TEXT_USER.format(user=username,
                                                 message=message)
                else:
                    body = BODY_TEXT.format(id=session_id, message=message)
                send_notification(SUBJECT_TEXT, body, notifier)
        else:
            raise Exception(response['response']['message'])
    except Exception as e:
        sys.stderr.write(
            "Tautulli API 'terminate_session' request failed: {0}.".format(e))
        return None


def arg_decoding(arg):
    return arg.decode(TAUTULLI_ENCODING).encode('UTF-8')


def session_file():
        if not os.path.exists(LAST_KILL_FILE):
            print(f"File created")
            with open(LAST_KILL_FILE, 'w') as file:
                pass 

def count_user_in_file():
    count_user = 0
    if os.path.exists(LAST_KILL_FILE):
        with open(LAST_KILL_FILE, 'r') as f:
            lines = f.readlines()

        # Iterate through each line and check for the username
        for line in lines:
            clean_line = line.strip()  # Strip leading/trailing whitespace
            if clean_line:  # Ensure the line isn't empty
                parts = clean_line.split('|')  # Split the line into all parts (username, number, etc.)
                #print(f"Comparing parts: {parts}")
                # Compare the username and grandparent_rating_key as strings
                if len(parts) >= 2 and parts[0] == opts.username and parts[1] == str(opts.grandparent_rating_key):
                    count_user += 1  # Increment the counter if the username and rating key match

    print(f"{opts.username} appears {count_user} time(s) in the file with ID {opts.grandparent_rating_key} limit is set to {total_limit}.")
    return count_user

def add_user():
    time_last_kill = TODAY_FORMATED  # Assuming TODAY_FORMATED is the current date/time
    ep_watched = count_user_in_file()

    with open(LAST_KILL_FILE, 'a') as file:
        file.write(f"{opts.username}|{opts.grandparent_rating_key}|{time_last_kill}|{ep_watched}|{total_limit}\n")
    print("User added to file fineshed watched.")
        
def check_file_last_5h():
    five_hours_ago = datetime.now() - timedelta(hours=5)  # Current time minus 5 hours
    new_lines = []

    if os.path.exists(LAST_KILL_FILE):
        with open(LAST_KILL_FILE, 'r') as f:
            lines = f.readlines()

        for line in lines:
            clean_line = line.strip()
            if clean_line:
                parts = clean_line.split('|')  # Assuming the timestamp is the third field
                if len(parts) >= 3:
                    try:
                        # Assuming the timestamp format is '2024-09-14 15:04'
                        entry_time = datetime.strptime(parts[2], '%Y-%m-%d %H:%M')
                        
                        # Compare the time
                        if entry_time >= five_hours_ago:
                            new_lines.append(line)  # Keep the line if it's within the last 5 hours
                        else:
                            print(f"Deleting entry older than 5 hours: {parts}")

                    except ValueError:
                        print(f"Error parsing date: {parts[2]}")  # Handle incorrect date formats

        # Write back only the lines that are not older than 5 hours
        with open(LAST_KILL_FILE, 'w') as f:
            f.writelines(new_lines)

        print(f"Updated file with entries within the last 5 hours.")
    else:
        print(f"No file named {LAST_KILL_FILE} exists.")
    

def reset_last_kill():
    if os.path.exists(LAST_KILL_FILE):
        with open(LAST_KILL_FILE, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            clean_line = line.strip()  # Strip leading/trailing whitespace
            #print(f"Processing line: '{clean_line}'")  # Debug: Show the processed line

            if clean_line:  # Ensure the line isn't empty after stripping
                parts = clean_line.split('|')  # Split at the first space
                # Compare username exactly and only append if it's different
                if parts[0] != opts.username:
                    new_lines.append(line)  # Keep lines with different usernames
                #else:
                    #print(f"Line with username '{opts.username}' found and will be deleted.")  # Debug
            #else:
                #print("Empty or whitespace-only line encountered and skipped.")  # Debug

        # Ensure we write the new lines back to the file
        with open(LAST_KILL_FILE, 'w') as file:
            file.writelines(new_lines)
            file.flush()  # Ensure all data is written to the file
            os.fsync(file.fileno())  # Force writing to disk

        print(f"{opts.username} reset successfully probably is active")
    else:
        print(f"No file named {LAST_KILL_FILE} exists to reset.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Limiting Plex users by plays, watches, or total time from Tautulli.")
    parser.add_argument('--jbop', required=True, choices=SELECTOR,
                        help='Limit selector.\nChoices: (%(choices)s)')
    parser.add_argument('--username', required=True,
                        help='The username of the person streaming.')
    parser.add_argument('--sessionId', required=True,
                        help='The unique identifier for the stream.')
    parser.add_argument('--notify', type=int,
                        help='Notification Agent ID number to Agent to send '
                             'notification.')
    parser.add_argument('--limit', action='append', type=lambda kv: kv.split("="),
                        help='The limit related to the limit selector chosen.')
    parser.add_argument('--grandparent_rating_key', type=int,
                        help='The unique identifier for the TV show or artist.')
    parser.add_argument('--delay', type=int, default=60,
                        help='The seconds to wait in order to deem user is active.')
    parser.add_argument('--killMessage', nargs='+',
                        help='Message to send to user whose stream is killed.')
    parser.add_argument('--section', default=False, choices=lib_dict.keys(), metavar='',
                        help='Space separated list of case sensitive names to process. Allowed names are: \n'
                             '(choices: %(choices)s)')
    parser.add_argument('--days', type=int, default=0, nargs='?',
                        help='Search history limit. \n'
                             'Default: %(default)s day(s) (today).')
    parser.add_argument('--duration', type=int, default=0,
                        help='Duration of item that triggered script agent.')
    parser.add_argument('--save_last_kill', type=str, choices=ENABLE_LAST_KILL, default="no", 
                        help="Whether to save the last killed user to a file, so it will reset the counter.")
    parser.add_argument('--watch', type=str, choices=ENABLE_WATCHED, default="no",
                        help="Whether the user has watched the ep")
    parser.add_argument('--flush', type=str, choices=ENABLE_WATCHED, default="no",
                        help="Delete all the user data of the file.")

    opts = parser.parse_args()

    history_lst = []
    total_limit = 0
    total_jbop = 0
    duration = 0
    dates = []
    delta = timedelta(days=opts.days)

    if opts.flush == "yes":
        reset_last_kill()
        check_file_last_5h()

    for i in range(delta.days + 1):
        day = TODAY + timedelta(days=-i)
        dates.append(day.strftime('%Y-%m-%d'))

    if opts.limit:
        limit = dict(opts.limit)

        for key, value in limit.items():
            if key == 'days':
                total_limit += int(value) * (24 * 60 * 60)
            elif key == 'hours':
                total_limit += int(value) * (60 * 60)
            elif key == 'minutes':
                total_limit += int(value) * 60
            elif key == 'plays':
                total_limit = int(value)

    if not opts.sessionId:
        sys.stderr.write("No sessionId provided! Is this synced content?\n")
        sys.exit(1)

    if opts.duration:
        # If duration is used convert to seconds from minutes
        duration = opts.duration * 60

    if opts.killMessage:
        message = ' '.join(opts.killMessage)
    else:
        message = ''

    for date in dates:
        if opts.section:
            section_id = lib_dict[opts.section]
            history = get_history(username=opts.username, section_id=section_id, start_date=date)
        else:
            history = get_history(username=opts.username, start_date=date)
        history_lst.append(history)

    # todo-me need more flexibility for pulling history
    # limit work requires gp_rating_key only? Needs more options.
    if opts.save_last_kill == "yes":
        session_file()
        check_file_last_5h()
    if opts.watch == "yes":
        add_user()

    if opts.jbop == 'limit' and opts.grandparent_rating_key:
        ep_watched = []
        stopped_time = []
        paused_time = []
        for date in dates:
            history_lst.append(get_history(username=opts.username, start_date=date))
        # If message is not already defined use default message
        if not message:
            message = LIMIT_MESSAGE.format(delay=opts.delay)
        for history in history_lst:
            ep_watched += [data['watched_status'] for data in history['data']
                          if data['grandparent_rating_key'] == opts.grandparent_rating_key and
                          data['watched_status'] == 1]
            
            stopped_time += [data['stopped'] for data in history['data']
                            if data['grandparent_rating_key'] == opts.grandparent_rating_key and
                            data['watched_status'] == 1]
        
            #print(f"history{history}")

        # If show episode have not been stopped (completed?) then use current time.
        # Last stopped time is needed to test against auto play timer
        if opts.save_last_kill == "yes":

            time_last_kill = TODAY_FORMATED
            ep_watched_list = count_user_in_file()
            ep_sum = ep_watched_list
            if ep_watched_list >= total_limit:
                #print("{}'s limit is {} and has watched {} episodes of this show.".format(
                    #opts.username, total_limit, ep_watched))
                terminate_session(opts.sessionId, message, opts.notify, opts.username)  

            else:
                print("{}'s limit is {} but has only watched {} episodes of this show.".format(
                    opts.username, total_limit, ep_sum))
