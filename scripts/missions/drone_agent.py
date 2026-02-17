import asyncio
from mavsdk import System
from mavsdk.action import ActionError # Import this to catch errors

class DroneAgent:
    def __init__(self, drone_id, address, mavsdk_port):
        self.id = drone_id
        self.address = address
        # Port for the MAVSDK server instance
        self.drone = System(port=mavsdk_port)

    async def connect(self):
        print(f"[Drone {self.id}] Connecting to {self.address}...")
        await self.drone.connect(system_address=self.address)

        print(f"[Drone {self.id}] Waiting for connection...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print(f"[Drone {self.id}] --- CONNECTED! ---")
                break
        
        # We wait for GPS here to ensure the drone knows where it is before we ask anything else
        print(f"[Drone {self.id}] Waiting for GPS Lock...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print(f"[Drone {self.id}] GPS Locked.")
                break

    async def arm_and_takeoff(self, target_altitude):
        # 1. CRITICAL: Wait until the drone says it is "Armable"
        #    (Prevents "ActionError: Failed" if Gyros are still calibrating)
        print(f"[Drone {self.id}] Waiting for system to be armable...")
        async for health in self.drone.telemetry.health():
            if health.is_armable:
                print(f"[Drone {self.id}] System is ready to arm.")
                break
            await asyncio.sleep(1)

        # 2. Arm
        print(f"[Drone {self.id}] Arming...")
        try:
            await self.drone.action.arm()
        except ActionError as e:
            print(f"[Drone {self.id}] ARMING FAILED: {e}")
            return

        await asyncio.sleep(2) # 3. Wait for motors to spin up (The "Lag" fix)
        
        # 4. Takeoff
        print(f"[Drone {self.id}] Taking off to {target_altitude}m...")
        try:
            await self.drone.action.set_takeoff_altitude(target_altitude)
            await self.drone.action.takeoff()
        except ActionError as e:
            print(f"[Drone {self.id}] TAKEOFF FAILED: {e}")
            return

        # 5. Monitor altitude
        async for position in self.drone.telemetry.position():
            alt = position.relative_altitude_m
            
            if int(alt) % 5 == 0:  # Print every 5 meters roughly to reduce spam
                 print(f"[Drone {self.id}] Climbing... Alt: {alt:.1f}m")
            
            if alt >= target_altitude * 0.99:
                print(f"[Drone {self.id}] Reached Target Altitude!")
                break 
            
    async def land(self):
        print(f"[Drone {self.id}] Landing...")
        await self.drone.action.land()
        async for in_air in self.drone.telemetry.in_air():
            if not in_air:
                print(f"[Drone {self.id}] -- Landed confirmed")
                break
        await self.drone.action.disarm()
        print(f"[Drone {self.id}] -- Disarmed")

    async def fly_to_gps(self, lat, lon, altitude, yaw): 
        """Commands the drone to fly to a specific GPS coordinate."""
       
        await self.arm_and_takeoff(altitude)  # This calls the robust arm_and_takeoff function defined above
        
        print(f"[Drone {self.id}] Moving to Lat:{lat:.6f}, Lon:{lon:.6f}...")
        
        try:
            await self.drone.action.goto_location(lat, lon, altitude, yaw) # yaw_deg=0 means face North
        except ActionError as e:
            print(f"[Drone {self.id}] MOVE FAILED: {e}")