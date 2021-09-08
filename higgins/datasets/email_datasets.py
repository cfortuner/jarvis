SEND_EMAIL_DATASET_TRAIN = [
    {
        "query": "Send an email to mom and let her know I'm coming home for Christmas",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "mom",
                    "subject": "Christmas plans",
                    "body": "I'm coming home for Christmas",
                }
            },
        ]
    },
    {
        "query": "email Brian jennings and ask if I can tour the apartment tomorrow",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "Brian jennings",
                    "subject": "Apartment visit",
                    "body": "Can I tour the apartment tomorrow?",
                }
            },
        ]
    },
    {
        "query": "email support@mattressfirm.com Return my order for a full refund",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "support@mattressfirm.com",
                    "subject": "Return Order",
                    "body": "I would like to schedule a return and receive a full refund",
                }
            },
        ]
    },
    {
        "query": "email Sally can we push our meeting to tomorrow at 9am?",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "Sally",
                    "subject": "Raincheck meeting",
                    "body": "Can we push our meeting to tomorrow at 9am?",
                }
            },
        ]
    },
    {
        "query": "Cancel membership support at netflix.com",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "support@netflix.com",
                    "subject": "Cancel membership",
                    "body": "Can you cancel my membership?",
                }
            },
        ]
    },
]

SEND_EMAIL_DATASET_TEST = [
    {
        "query": "Email Dad and ask if my tennis rackets arrived",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "Dad",
                    "subject": "Tennis rackets",
                    "body": "Have my tennis rackets arrived?",
                }
            },
        ]
    },
    {
        "query": "email mission@bodyrok.edu cancel membership",
        "actions": [
            {
                "action": "SendEmail",
                "params": {
                    "to": "mission@bodyrok.edu",
                    "subject": "Cancel membership",
                    "body": "Can you cancel my membership?",
                }
            },
        ]
    },
]

SEARCH_EMAIL_DATASET_TRAIN = [
    {
        "query": "Get unread emails newer than 1 month old with labels finance and Betterment",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "???",
                    "unread": "True",
                    "labels": "finance AND Betterment",
                    "exact_phrase": "???",
                    "newer_than": "1 month",
                    # "older_than": "???",
                    # "before": "2/10/2020",
                    # "after": "???",
                    # "has_attachment": "???",
                    # "attachment_spec": "???",
                }
            },
        ]
    },
    {
        "query": "Find emails with the subject Hello Brendan",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "Hello Brendan",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Get emails from Dad",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "Dad",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Search for emails from Erin Fortuner sent in the last 30 days",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "Erin Fortuner",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "30 days",
                }
            },
        ]
    },
    {
        "query": "Find emails sent to cfortuner@gmail.com",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "cfortuner@gmail.com",
                    "from": "???",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Get all unread emails sent in the last 2 days",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "???",
                    "unread": "True",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "2 day",
                }
            },
        ]
    },
    {
        "query": "Find emails which contain the phrase fizzy bottle",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "fizzy bottle",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "search for emails from nari.kourian@getcruise.ai",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "nari.kourian@getcruise.ai",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
]

SEARCH_EMAIL_DATASET_TEST = [
    {
        "query": "Get emails from Jackie First",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "Jackie First",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Get emails sent by York Mather in the last month",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "York Mather",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "1 month"
                }
            },
        ]
    },
    {
        "query": "Find emails titled My first email",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "My first email",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Get all emails from Colin sent in the last week",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "Colin",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "7 day",
                }
            },
        ]
    },
    {
        "query": "Get all unread emails received in the last 5 days",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "???",
                    "unread": "True",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "5 day",
                }
            },
        ]
    },
    {
        "query": "Get all unread emails with the labels tennis OR Federer",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "???",
                    "unread": "True",
                    "labels": "tennis OR Federer",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Get emails with the phrase Yoon Manivanh",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "???",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "Yoon Manivanh",
                    "newer_than": "???",
                }
            },
        ]
    },
    {
        "query": "Get emails from Yoon Manivanh",
        "actions": [
            {
                "action": "SearchEmail",
                "params": {
                    "to": "???",
                    "from": "Yoon Manivanh",
                    "subject": "???",
                    "unread": "???",
                    "labels": "???",
                    "exact_phrase": "???",
                    "newer_than": "???",
                }
            },
        ]
    },
]

EMAIL_DATASETS_TRAIN = []
EMAIL_DATASETS_TRAIN += SEND_EMAIL_DATASET_TRAIN
EMAIL_DATASETS_TRAIN += SEARCH_EMAIL_DATASET_TRAIN

EMAIL_DATASETS_TEST = []
EMAIL_DATASETS_TEST += SEND_EMAIL_DATASET_TEST
EMAIL_DATASETS_TEST += SEARCH_EMAIL_DATASET_TEST
