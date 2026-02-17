#!/bin/bash

# Function to kill all background processes when you press Ctrl+C
cleanup() {
    echo "Stopping all swarm instances..."
    kill 0
}

# Trap the interrupt signal (Ctrl+C)
trap cleanup SIGINT

echo "Starting Swarm..."

# Drone 1 (Instance 0)
sim_vehicle.py -v Copter --console -I0 -L KFUPM --sysid 1 --out=udp:127.0.0.1:14540 --out=udp:172.30.224.1:14550 --no-rebuild &

# Drone 2 (Instance 1)
sim_vehicle.py -v Copter --console -I1 -L KFUPM --sysid 2 --out=udp:127.0.0.1:14541 --out=udp:172.30.224.1:14551 --no-rebuild &

# Drone 3 (Instance 2)
sim_vehicle.py -v Copter --console -I2 -L KFUPM --sysid 3 --out=udp:127.0.0.1:14542 --out=udp:172.30.224.1:14552 --no-rebuild &

# Drone 4 (Instance 3)
sim_vehicle.py -v Copter --console -I3 -L KFUPM --sysid 4 --out=udp:127.0.0.1:14543 --out=udp:172.30.224.1:14553 --no-rebuild &

# Keep the script running to maintain the processes
wait


