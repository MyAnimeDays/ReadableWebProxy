#TODO:
 - Figure out how to selectively preserve some classes (I want to allow fontawesome content)
 - Search for proximate words.
 - "https://xxjohnsmithxx.wordpress.com", parser
 
tsvector column not up to date
handle leading decimals numeric

delete series
rules comditionally disable tld permutatiom
text/plain mimetype freaking shit out

 FIXED:
 ## - If series have > 5 chapters and < 20% of chapters have no numbering, do basic chronological numbering.
 ## - wattpad requires login for some things?
 ## - Show two digits for all fragment numbers.
 ## - Add last updated field for most recent release
 ## - Removing items does not work.
 ## - WattPad metadata filter.
 ## - Rule-caching is not working.
 ## - Multithreaded server fails because DB interface is shared across threads.
 ## - Validate unmatched keys in rules so that key-typos don't silently break things.
 ## - funky tables outlines
