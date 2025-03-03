# Waffle

A discord bot for my friends and I. A constant work-in-progress but very stable these days.

Some commands are prefixed and some are slash commands. If they require no options, then I tend to leave them as a prefix command. 
## Features:
- Randomly pulls a phrase from a phrase list. Chatters can add to the list with /addphrase
    
    - *Phrases are managed by a little flask api.*

- Commands to search completely and totally legal torrents and some utility commands.

    - *!search \<query>*: searches a local Jackett server for query, sorts results by uploaders, returns the top 10. User can pick one and its sent to an Alldebrid account. A valid link is returned or the torrent is queued and the id is sent to `queue.txt` and `tasks.debrid_check()` checks for a complete download every 30 seconds or removes it from the list if it failed.
    - */magnet \<magnet>*: directly adds a magnet link and follows the same logic as !search
    - *!ready*: return the total number of cached torrents on the Alldebrid account
    - *!deletetorrents \<num>*: clears out `num` cached torrents. Useful if the Alldebrid account hits the limit.
    - *!status*: get status of active downloads
    - */m3u \<url>*: Returns a `.m3u` for a streaming folder. A testy command, use wisely.

    *Note: These commands are mixture of prefix and slash because a couple of my friends are not tech-savvy. The prefix sticks around for them and my sanity.*

- Misc commands:
    
    - *!inspireme*: returns an image from the inspirobot API.
    - *!waffle*: Namesake and first command 3 years ago. Returns a random image from the waffleimages dump.
    - */hltb \<game>*: get stats about `game` from HowLongToBeat.
    - */roll \<num> \<sides>*: roll dice.