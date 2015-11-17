## Readable-Web Proxy

Reading long-form content on the internet is a shitty experience.   
This is a web-proxy that tries to make it better.

This is a *rewriting proxy*. In other words, it proxies arbitrary web
content, while allowing the rewriting of the remote content as driven
by a set of rule-files. The goal is to effectively allow the complete
customization of any existing web-sites as driven by predefined rules.

Functionally, it's used for extracting just the actual content body
of a site and reproducing it in a clean layout. It also modifies
all links on the page to point to internal addresses, so following a
link points to the proxied version of the file, rather then the original.


---

Quick installation overview:

 - Install Postgresql **>= 9.5.** This is alpha, you will have to build from source.
     (This is because this project uses the new `ON CONFLICT` clause)
 - Build the community extensions for Postgresql.
 - Create a database for the project.
 - In the project database, install the `pg_trgm` and `citext` extensions.
 - Copy `settings.example.py` to `settings.py`.
 - Setup virtualhost by rinning `build-venv.sh`
 - Activate vhost: `source flask/bin/activate`
 - Bootstrap DB: `create_db.sh`
 - (Potentially) disable wattpad login system by editing the content of `INIT_CALLS` in 
     `activePlugins.py`.
 - Run server: `python3 run.py`