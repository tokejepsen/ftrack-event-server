**Goal**

To ease the usage of Ftracks event plugins.

**Motivation**

Currently you can write event plugins, and run them individually, which can be difficult to manage.
Along with having to manage the execution of each plugin, feedback are scattering over multiple terminals.

**Setup**

If you are running the old ftrack API, and your login name matches you ftrack login name, you won't need to setup anything. If this is not the case you'll need to configure these environment variables; ```FTRACK_SERVER```, ```FTRACK_API_USER```, ```LOGNAME``` and ```FTRACK_API_KEY```.

You can either configure these environment variables prior to launching the ```server.py```, or you can create a ```config.py``` next to ```server.py```.
The ```config.py``` structure looks like this;
```python
server_url = 'http://mycompany.ftrackapp.com'
api_key = '7545384e-a653-11e1-a82c-f22c11dd25eq'
api_user = 'martin'
```

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

**Examples**

https://github.com/tokejepsen/ftrack-event-plugins
