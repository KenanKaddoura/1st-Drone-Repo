import asyncio
import math
from mavsdk import System

# --- Simple helpers (kept minimal) ---
R_EARTH_M = 6378137.0

def meters_east_to_lon_delta_deg(east_m: float, lat_deg: float) -> float:
    lat_rad = math.radians(lat_deg)
    return (east_m / (R_EARTH_M * math.cos(lat_rad))) * (180.0 / math.pi)

def distance_m(lat1, lon1, lat2, lon2) -> float:
    # Haversine (small and sufficient)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return R_EARTH_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def run():
    drone = System()

    # Connect to SITL (your current setup: sim_vehicle ... --out=udp:127.0.0.1:14540)
    await drone.connect(system_address="udpin://127.0.0.1:14540")

    # Wait until we have global + home position (needed for goto_location reliability)
    print("Waiting for global position + home position...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Position OK")
            break

    # Read home position once
    print("Reading home (from current position)...")
    async for pos in drone.telemetry.position():
        home_lat = pos.latitude_deg
        home_lon = pos.longitude_deg
        home_abs_alt = pos.absolute_altitude_m
        print(f"Home: {home_lat:.7f}, {home_lon:.7f}, abs_alt={home_abs_alt:.1f} m")
        break

    # Arm
    print("-- Arming")
    await drone.action.arm()
    await asyncio.sleep(2)

    # Takeoff
    takeoff_alt_rel = 5.0
    print(f"-- Takeoff to {takeoff_alt_rel} m")
    await drone.action.set_takeoff_altitude(takeoff_alt_rel)
    await drone.action.takeoff()

    # Wait a bit for climb (simple style)
    await asyncio.sleep(8)

    # Go 100m East (same altitude, using absolute altitude for goto_location)
    east_m = 100.0
    target_lat = home_lat
    target_lon = home_lon + meters_east_to_lon_delta_deg(east_m, home_lat)
    target_abs_alt = home_abs_alt + takeoff_alt_rel

    print("-- Going 100m East")
    await drone.action.goto_location(target_lat, target_lon, target_abs_alt, yaw_deg=0.0)

    # Wait until close to target (simple loop, no extra structure)
    async for pos in drone.telemetry.position():
        d = distance_m(pos.latitude_deg, pos.longitude_deg, target_lat, target_lon)
        if d <= 3.0:
            print(f"-- Reached East point (error {d:.2f} m)")
            break

    await asyncio.sleep(3)

    # Return home (go-to home)
    print("-- Returning Home")
    await drone.action.goto_location(home_lat, home_lon, target_abs_alt, yaw_deg=0.0)

    async for pos in drone.telemetry.position():
        d = distance_m(pos.latitude_deg, pos.longitude_deg, home_lat, home_lon)
        if d <= 3.0:
            print(f"-- Reached Home (error {d:.2f} m)")
            break

    await asyncio.sleep(2)

    # Land
    print("-- Landing")
    await drone.action.land()

    # Wait until landed
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("-- Landed confirmed")
            break

    # Disarm
    print("-- Disarming")
    await drone.action.disarm()


if __name__ == "__main__":
    asyncio.run(run())
