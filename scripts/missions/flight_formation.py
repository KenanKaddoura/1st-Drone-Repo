import asyncio
from mavsdk import System

    


class DroneAgent:
    def __init__(self, drone_id, address, mavsdk_port):
        """
        Args:
            mavsdk_port (int): Unique internal port for MAVSDK server (50051, 50052, etc.)
        """
        self.id = drone_id
        self.address = address
        # CRITICAL FIX: We assign a unique port for the mavsdk_server
        # self.drone = System(mavsdk_server_address="localhost", port=mavsdk_port)
        self.drone = System(port=mavsdk_port)


    async def connect(self):
        print(f"[Drone {self.id}] Connecting to {self.address}...")
        await self.drone.connect(system_address=self.address)

        print(f"[Drone {self.id}] Waiting for heartbeat...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print(f"[Drone {self.id}] --- CONNECTED! ---")
                break

    async def arm_and_takeoff(self, target_altitude):
        print(f"[Drone {self.id}] Checking Global Position...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print(f"[Drone {self.id}] GPS is good.")
                break

        print(f"[Drone {self.id}] Arming...")
        await self.drone.action.arm()
        
        await asyncio.sleep(2)
        
        print(f"[Drone {self.id}] Taking off to {target_altitude}m...")
        await self.drone.action.set_takeoff_altitude(target_altitude)
        await self.drone.action.takeoff()

        # Monitor altitude
        async for position in self.drone.telemetry.position():
            alt = position.relative_altitude_m
            print(f"[Drone {self.id}] Climbing... Current Alt: {alt:.1f}m")
            if alt >= target_altitude * 0.95:
                print(f"[Drone {self.id}] Reached Target Altitude!")
                return
            
    async def land(self):
        print(f"[Drone {self.id}] Landing...")
        await self.drone.action.land()
        async for in_air in self.drone.telemetry.in_air():
            if not in_air:
                print(f"[Drone {self.id}] -- Landed confirmed")
                break
        await self.drone.action.disarm()
        print(f"[Drone {self.id}] -- Disarmed")

    async def fly_to_gps(self, lat, lon, altitude):
        """Commands the drone to fly to a specific GPS coordinate."""
        print(f"[Drone {self.id}] Taking off...")
        await self.arm_and_takeoff(altitude)
        
        print(f"[Drone {self.id}] Moving to Lat:{lat:.6f}, Lon:{lon:.6f}...")
        
        # The MAVSDK command to fly to a coordinate
        # yaw_deg=0 means face North
        await self.drone.action.goto_location(lat, lon, altitude, 0)


async def main():
    # 1. Define Swarm with UDP ports AND unique MAVSDK server ports
    swarm = [
        # Drone 1: Listens on UDP 14540, uses internal Server Port 50051
        DroneAgent(drone_id=1, address="udpin://127.0.0.1:14540", mavsdk_port=50051),
        
        # Drone 2: Listens on UDP 14550, uses internal Server Port 50052 (NO CONFLICT!)
        DroneAgent(drone_id=2, address="udpin://127.0.0.1:14550", mavsdk_port=50052)
    ]
    
    print("--- Swarm Connecting ---")
    await asyncio.gather(*[agent.connect() for agent in swarm])
    
    print("\n--- Starting Formation Takeoff ---")
    tasks = [
        swarm[0].arm_and_takeoff(50.0),
        swarm[1].arm_and_takeoff(30.0)
    ]
    await asyncio.gather(*tasks)
    
    print("\n--- Formation Complete (Hovering 10s) ---")
    await asyncio.sleep(10)

    print("\n--- Landing Swarm ---")
    endTask = [
        swarm[0].land(),
        swarm[1].land()
    ]
    await asyncio.gather(*endTask)

if __name__ == "__main__":
    asyncio.run(main())