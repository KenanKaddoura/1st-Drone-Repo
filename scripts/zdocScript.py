import asyncio
from mavsdk import System
 
"""""
This script contains the commands used related to drone software. 
The script should not be excuted. 
"""""

async def run():

    drone = System()  # Initialize Drone
    await drone.connect(system_address="udpin://127.0.0.1:14540") # Connect Drone

    await drone.action.arm() # Arm Drone
    drone.action.disarm() # Disarm Drone
    
    await drone.action.set_takeoff_altitude(50.0) # Takeoff: set alt
    await drone.action.takeoff() # Takeoff Drone
    
    await drone.action.land() # Land Drone

    async for in_air in drone.telemetry.in_air(): # Check "in air" Drone Status
        if not in_air:
            print("-- Landed confirmed")
            break

    await asyncio.sleep(2) #  Wait; After (Arm, Takeoff, ...)
    

    # Monitor drone connection state - connect
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"[Drone] --- CONNECTED! ---")
            break


    # Monitor altitude - takeoff
    async for position in drone.telemetry.position():
        alt = position.relative_altitude_m
        
        if alt >= target_altitude * 0.95:
            print(f"[Drone Reached Target Altitude!")
            return
    
    # Monito landing - land
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print(f"[Drone -- Landed confirmed")
            break
    

    # Define tasks and run them simultaneously for a swarm
    tasks = [
        swarm[0].arm_and_takeoff(50.0),
        swarm[1].arm_and_takeoff(30.0)
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Run the async loop
    asyncio.run(run())



    # user_polygon = [
    #     (26.308079, 50.146278), # Bottom-Left (Home)
    #     (26.308642, 50.147220), # Bottom-Right (East + ~100m)
    #     (26.309173, 50.146842), # Top-Right  (North + ~100m, East + ~100m)
    #     (26.308620, 50.145891)  # Top-Left   (North + ~100m)
    # ]
    # home = (26.308343, 50.146416)