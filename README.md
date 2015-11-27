**Goal**

To ease the usage of Ftracks event plugins.

**Motivation**

Currently you can write event plugins, and run them individually, which can be difficult to manage.
Along with having to manage the execution of each plugin, feedback are scattering over multiple terminals.

**Usage**

You can write the event plugins exactly how Ftrack documents you to do; http://ftrack-python-api.rtd.ftrack.com/en/latest/handling_events.html

You can test your plugin by just running it individually. When you have collect two or more plugins that you want to run at the same time, you have two options.

- Pass the directories of the plugins.
```
python ftrack-event-server/server.py PATH/TO/A/PLUGIN PATH/TO/OTHER/PLUGINS
```
 - ftrack-event-server will look for all python scripts in a directory, and execute them.
 - You can either pass in a directory or the file path.


- Setup ```FTRACK_EVENT_SERVER_PLUGINS``` to the directories of the plugins.
```
set FTRACK_EVENT_SERVER_PLUGINS=PATH/TO/A/PLUGIN;PATH/TO/OTHER/PLUGINS
python ftrack-event-server/server.py
```
