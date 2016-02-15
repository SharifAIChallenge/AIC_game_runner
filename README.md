# AIC_game_runner
Run games scheduled by AIC_mezzanine_site
# Management commands
## Redis initialization commands
### init_redis
You need to run this command before using a redis db for CPU management. This command takes one positional argument ``db`` which is the redis db number. You may also pass available cores using ``--cores`` optional argument which must be followed by a list of available cores' indices.
### add_cores
After you have initialized a database you may use this command to add available cores. This commands takes a list of available cores' indices.
