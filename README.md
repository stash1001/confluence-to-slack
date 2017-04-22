# confluence-to-slack #

This is an integration between Confluence and Slack.

The integration scrapes the task object with in a page and reports if that task is complete and the total remaining time for all other tasks on the page.

Tasks need to be in the following format.

■ Task one do something (2 mins)


### How to run ###
```
export conf_user="Confluence Username"
export conf_pass="Confluence Password"
docker run -it --rm \
 -e conf_user \
 -e conf_pass \
 -e wiki_url="https://ConfluenceWIKIURL/wiki" \
 -e page="Page Name" \
 -e project="Project Name" \
 -e polling_frequency="10" \
 -e slack_url="Slack Webhook URL" \
 -e slack_channel="#Slack Channel to send to" \
stash1001/confluence-to-slack
```