This repo is for testing and learning dorne scripts. 

The main files are scripts & GCS; others are auto generated while running the drones and scripts. 

You can test missions using these commands: 
```
sim_vehicle.py -v Copter -I0 -L KFUPM --sysid 1 --out=udp:127.0.0.1:14540 --out=udp:172.30.224.1:14550 --no-rebuild -w
```
```
sim_vehicle.py -v Copter -I1 -L KFUPM --sysid 2 --out=udp:127.0.0.1:14541 --out=udp:172.30.224.1:14550 --no-rebuild -w
```
```
sim_vehicle.py -v Copter -I2 -L KFUPM --sysid 3 --out=udp:127.0.0.1:14542 --out=udp:172.30.224.1:14550 --no-rebuild -w
```
```
sim_vehicle.py -v Copter -I3 -L KFUPM --sysid 4 --out=udp:127.0.0.1:14543 --out=udp:172.30.224.1:14550 --no-rebuild -w
```
Note: Most probabily, current scripts wouldnot with running less than 4 drones at the same time. 

