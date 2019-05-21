pyPluribus
=====
Python library to interact with Pluribus devices.

This library has been deprecated.

Install
=======
pyPluribus is available on PyPi and can be easily installed using the following command:

```
pip install pyPluribus
```

Documentation
=============
### Open a connection with the device:
```python
>>> from pyPluribus import PluribusDevice
>>> my_lovely_pluribus = PluribusDevice(hostname='sw50.jnb01', username='fake', password='!L0v3Pl00ribu$', port=22, timeout=60, keepalive=900)
>>> my_lovely_pluribus.open()
```
The communication channel with the device is established via SSH.

### Send basic show commands:
There are two ways to execute show-type conmmands:
* using cli() and must specifiy the command in the Pluribus-specific format ([CONFIG-STANZA]-show)
* using show() and the command can be sent in human-readable format
```python
>>> my_lovely_pluribus.cli('running-config-show')  # will return the Running Configuration
>>> my_lovely_pluribus.show('running config')  # again, will return the running configuration
>>> my_lovely_pluribus.cli('switch-poweroff')
```

### Load configuration:
One single command can be loaded using the same method cli()
```python
>>> my_lovely_pluribus.cli('port-storm-control-modify port 39 speed 10g')
```
A whole configuration part can be loaded using the method load_candidate_config()
```python
>>> my_config_file = '/path/to/config/file'
>>> my_lovely_pluribus.config.load_candidate(filename=my_config_file)
```
or
```python
>>> my_custom_config = '''
.
.  [MUCH CONFIG CONTENT]
.
. '''
>>> my_lovely_pluribus.config.load_candidate(config=my_custom_config)
```

### Compare configuration
Returns the difference between the configuration since last commit (initial configuration -- if not commit issued since the connection was open) and the running config.
```python
>>> my_lovely_pluribus.config.compare()
@@ -79 +79 @@

-port-storm-control-modify port 39 speed 1g
+port-storm-control-modify port 39 speed 10g
```

### Commit changes
```python
>>> my_lovely_pluribus.config.commit()
```

### Rollback
Rollbacks the configuration a number of steps.
```python
>>> my_lovely_pluribus.config.rollback(7)
```

### Close connection
```
>>> my_lovely_pluribus.close()
```

NAPALM
======
Beginning with release 0.60, pyPluribus is used by [NAPALM](https://github.com/napalm-automation/napalm).


License
======
Copyright 2016 CloudFlare, Inc.

Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
