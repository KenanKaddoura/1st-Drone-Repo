import asyncio

import sys
import os

# 1. Get the absolute path to the current file's folder (swarm_mission)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the parent folder (missions)
parent_dir = os.path.dirname(current_dir)

# 3. Add the parent folder to the system path
sys.path.append(parent_dir)

from drone_agent import DroneAgent  # Your drone class
from mission_manager import MissionManager # Your math brain

async def run_sky_guards_mission():
    print("--- 🛡️ SKY GUARDS MISSION START 🛡️ ---")

    # 1. Setup the Mission Manager (The Brain)
    #    We set Home to KFUPM Stadium
    kfupm_home = (26.308079, 50.146278)
    manager = MissionManager(kfupm_home[0], kfupm_home[1])

    # 2. Define the Area to Protect (The User Input)
    #    In a real app, this comes from mouse clicks. 
    #    Here, we simulate a 100x100m box.
    area_polygon = [
        (26.308079, 50.146278), # Bottom-Left (Home)
        (26.308642, 50.147220), # Bottom-Right (East + ~100m)
        (26.309173, 50.146842), # Top-Right  (North + ~100m, East + ~100m)
        (26.308620, 50.145891)  # Top-Left   (North + ~100m)
    ]

    # 3. Calculate Targets (The Math)
    #    This now returns GPS coordinates thanks to your update
    print("\n[Manager] Calculating Sector Targets...")
    targets_gps = manager.process_area(area_polygon)
    
    # 4. Initialize the Swarm (The Hardware)
    print("\n[Swarm] Connecting to 4 Drones...")
    swarm = [
        # Sector 1: Bottom-Left
        DroneAgent(1, "udpin://127.0.0.1:14540", mavsdk_port=50051),
        
        # Sector 2: Bottom-Right
        DroneAgent(2, "udpin://127.0.0.1:14541", mavsdk_port=50052),
        
        # Sector 3: Top-Right
        DroneAgent(3, "udpin://127.0.0.1:14542", mavsdk_port=50053),
        
        # Sector 4: Top-Left
        DroneAgent(4, "udpin://127.0.0.1:14543", mavsdk_port=50054)
    ]
        
    # Connect to all 4 simultaneously
    await asyncio.gather(*[d.connect() for d in swarm])

    # 5. EXECUTION: Assign Targets to Drones
    print("\n[Mission] Deploying Swarm to Protection Sectors...")
    
    tasks = []
    
    # Loop through our drones and assign each one a target
    for i, drone in enumerate(swarm):
        # Safety check: Do we have enough targets?
        if i < len(targets_gps):
            target_lat, target_lon = targets_gps[i]
            
            print(f" -> Assigning Drone {drone.id} to Sector {i+1}")
            print(f"    Target: Lat {target_lat:.6f}, Lon {target_lon:.6f}")
            
            # Create a task for this drone to fly to that GPS spot
            # We assume you added 'fly_to_gps' to DroneAgent!
            tasks.append(drone.fly_to_gps(target_lat, target_lon, altitude=25))
            
    # Execute all flights simultaneously
    await asyncio.gather(*tasks)
    
    print("\n--- Mission Accomplished: Drones are holding position ---")
    # Keep the script running so we can watch them hover
    await asyncio.sleep(20)
    
    # Optional: Land everyone at the end
    print("--- Returning to Base (Landing) ---")
    await asyncio.gather(*[d.land() for d in swarm])

if __name__ == "__main__":

    asyncio.run(run_sky_guards_mission())



    