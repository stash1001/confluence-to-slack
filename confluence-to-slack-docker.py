from confluence import Api
from bs4 import BeautifulSoup
import requests
import json
import collections
import time
import re
import os


def post_to_slack(attachment, slack_url, slack_channel):
    headers = {'Content-Type': 'application/json'}
    payload = {"channel": slack_channel, "username": "confluence",
               "attachments": attachment, "icon_emoji": ":ghost:"}
    requests.post(slack_url, data=json.dumps(payload), headers=headers)


def get_string(s):
    """Return True if this string is the only child of its parent tag."""
    return (s == s.parent.string)


def get_confluence(wiki_url, page, project, conf_user, conf_pass):
    api = Api(wiki_url, conf_user, conf_pass)
    pages = api.getpage(page, project)
    soup = BeautifulSoup(pages['content'], 'html.parser')
    tasks = collections.OrderedDict()
    for a in soup.find_all('ac:task-list'):
        for item in a:
            if item.name == "ac:task":
                for taskitem in item:
                    if taskitem.name == "ac:task-body":
                        task = taskitem.find_all(string=get_string)
                    if taskitem.name == "ac:task-status":
                        status = taskitem.find_all(string=get_string)
                if task and status:
                    tasks[task[0]] = status[0]
    return tasks


def main():
    conf_pass = os.environ['conf_pass']
    conf_user = os.environ['conf_user']
    wiki_url = os.environ['wiki_url']
    polling_frequency = os.environ['polling_frequency']
    slack_url = os.environ['slack_url']
    slack_channel = os.environ['slack_channel']
    page = os.environ['page']
    project = os.environ['project']
    tasks = get_confluence(wiki_url, page, project, conf_user, conf_pass)
    oldvalues = tasks
    duration = 0.0
    while True:
        duration = 0.0
        messages = []
        incomplete_duration = 0.0
        for task, status in tasks.iteritems():
            result = re.search("\((\d+) min[s]*\)", task)
            if result:
                duration += int((result.group(1)))
                if status == "incomplete":
                    incomplete_duration += int((result.group(1)))
                if status != oldvalues.get(task):
                    messages.append((status, task))
        time_remaining = (time.strftime(
            '%H:%M:%S', time.gmtime(incomplete_duration * 60)))
        time_to_finish = (time.strftime('%H:%M:%S', time.gmtime(
            time.time() + int(incomplete_duration * 60))))
        pct_complete = (
            100 - (100 * (float(incomplete_duration / float(duration)))))
        if messages:
            fields = []
            for status, task in messages:
                fields.append({
                    "title": task,
                    "value": status,
                    "short": False
                })
            attachment = [
                {
                    "fallback": "%s %s" % (task, status),
                    "color": "#36a64f",
                    "title": page,
                    "text": "Time Remaining: %s \nFinish Time: %s \nPercentage Complete: %d%%\n\n" % (time_remaining, time_to_finish, int(pct_complete)),
                    "title_link": wiki_url + "/display/" + project + "/" + page,
                    "fields": fields,
                    "ts": time.time()
                }
            ]
            post_to_slack(attachment, slack_url, slack_channel)

        time.sleep(float(polling_frequency))
        oldvalues = tasks
        tasks = get_confluence(wiki_url, page, project, conf_user, conf_pass)


main()
