from random import choice

LINK_MSG = [
    "Click this shit for files, i am very lazy.",
    "linky linky",
    "this is a link",
    "3=====D~~",
    "Follow the rabbit hole to the files",
    "File access granted, click at your own risk",
    "The files are waiting for you, just one click away",
    "Get ready for the ride, files incoming",
    "The files are calling your name, answer the call",
    "Link to enlightenment (and files)",
    "It's not just a link, it's an adventure",
    "Links, files, and good times await",
    "You can't handle the link, or can you?",
    "It's a link to remember",
    "File me away, I'm ready to be clicked",
    "Buckle up, it's a wild link ride",
]


def get_link_msg():
    return choice(LINK_MSG)
