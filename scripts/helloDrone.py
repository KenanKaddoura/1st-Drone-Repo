import asyncio
from mavsdk import System

async def run():

    # Connect drone
    drone = System()
    await drone.connect(system_address="udpin://127.0.0.1:14540")

    # Arm & Wait
    await drone.action.arm()
    await asyncio.sleep(2)

    # Takeoff
    await drone.action.set_takeoff_altitude(50.0)
    await drone.action.takeoff()

    # Hover for 10 seconds
    await asyncio.sleep(100)

    # Land
    await drone.action.land()

    # Wait until the drone is actually on the ground
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("-- Landed confirmed")
            break

    # Disarm
    drone.action.disarm()

    # # 1. Connect to the Drone
    # # In SITL, the drone usually exposes port 14540 for MAVSDK apps.
    # drone = System()
    # print("Waiting for drone to connect...")
    # await drone.connect(system_address="udpin://127.0.0.1:14540")

    # # 2. Check Connection State
    # print("Waiting for drone to have a global position estimate...")
    # async for health in drone.telemetry.health():
    #     if health.is_global_position_ok and health.is_home_position_ok:
    #         print("-- Global position estimate OK")
    #         break

    # # 3. Arm the Drone
    # print("-- Arming")
    # try:
    #     await drone.action.arm()
    # except Exception as e:
    #     print(f"Arming failed: {e}")
    #     return
    
    # # --- ADD THIS BLOCK ---
    # print("-- Waiting for motors to spin up...")
    # await asyncio.sleep(2)

    # # 4. Takeoff
    # print("-- Taking off")
    # try:
    #     await drone.action.set_takeoff_altitude(5.0) # Set target altitude to 5m
    #     await drone.action.takeoff()
    # except Exception as e:
    #     print(f"Takeoff failed: {e}")
    #     return

    # # 5. Hover for 10 seconds (Simulate a mission)
    # print("-- Hovering for 10 seconds...")
    # await asyncio.sleep(10)

    # # 6. Land
    # print("-- Landing")
    # await drone.action.land()

    # # Wait until the drone is actually on the ground
    # async for in_air in drone.telemetry.in_air():
    #     if not in_air:
    #         print("-- Landed confirmed")
    #         break

    # # 7. Disarm (Optional, usually auto-disarms on land, but good practice)
    # # print("-- Disarming")
    # # await drone.action.disarm()

if __name__ == "__main__":
    # Run the async loop
    asyncio.run(run())