# Sync

Sync command provides one-way content synchronisation from source to replica. Both folders are identical afterward.

⚠️ **Warning:** All folders which are located only in the replica will be deleted during synchronisation run.

## Usage

To select the source and the replica folder for the sync, you can run the following command:

```
filderflux --log-file <name-of-log-file> sync [-h] -s SOURCE -r REPLICA [-i INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
  -r REPLICA, --replica REPLICA
  -i INTERVAL, --interval INTERVAL
```
The interval between synchronisation runs is set to a value 1 s and can be changed.

Example output:

```
2024-06-09 20:05:59,711 - INFO - sync.py:Source is src.  Replica is rpl. Interval is 1.
```

## Graceful shut-down

For graceful shut-down please use `Ctrl-C` (SIGINT). After sending SIGINT the programme will perform the last iteration of synchronisation and gracefully end.

Please send just one SIGINT (hit `Ctrl-C` just once). Multiple SIGINTs are not handled.

## Eventual consistency

It is possible due to I/O operations in the source or replica folder the state will be inconsistence for a while (after synchronisation the files might not be identical copies), however eventual consistency is guaranteed. This behaviour is inherent because the source and the replica folders are not locked during synchronisation. I.e. consistency is guaranteed one iteration after the last I/O operation in the source or the replica folder.

## Algorithm

1. Create a set of all files and folders in the source folder.

2. Delete entities exclusive to the replica folder.

3. Compare checksums for files in the source and replica folders

4. Copy files with differing checksums or missing files in the source folder.

5. Recursively apply the algorithm to subfolders.

