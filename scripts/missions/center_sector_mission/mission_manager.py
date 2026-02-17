import pymap3d as pm
import sys
import os

# 1. Get the absolute path to the current file's folder (center_sector_mission)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the parent folder (missions)
parent_dir = os.path.dirname(current_dir)

# 3. Add the parent folder to the system path
sys.path.append(parent_dir)

from partition_func import get_ned_distance, get_sub_sector_centers

class MissionManager:
    def __init__(self, home_lat, home_lon, home_alt=0):
        self.home_lat = home_lat
        self.home_lon = home_lon
        self.home_alt = home_alt
        self.swarm_targets = [] 

    def process_area(self, corners_gps):
        """
        1. Converts GPS Polygon -> Local Meters
        2. Divides area into sectors
        3. Converts Sector Centers -> Back to GPS for the drones
        """
        print(f"--- Processing Mission Area ---")
        
        # 1. Convert GPS Polygon corners to Local Meters (NED)
        bl_lat, bl_lon = corners_gps[0]
        tr_lat, tr_lon = corners_gps[2]
        
        x_min, y_min = get_ned_distance(bl_lat, bl_lon, 0, self.home_lat, self.home_lon, self.home_alt)
        x_max, y_max = get_ned_distance(tr_lat, tr_lon, 0, self.home_lat, self.home_lon, self.home_alt)
        
        width_meters = y_max - y_min
        height_meters = x_max - x_min
        
        print(f"Area Dimensions: {width_meters:.1f}m Wide x {height_meters:.1f}m High")

        # 2. Partition Logic
        local_centers = get_sub_sector_centers(width_meters, height_meters, n_rows=2, n_cols=2)
        
        # 3. Convert Centers BACK to GPS (The new part)
        self.swarm_targets = []
        for (cx, cy) in local_centers:
            # Calculate absolute distance from Home
            abs_n = x_min + cx 
            abs_e = y_min + cy
            
            # Convert Cnters Meters -> Lat/Lon
            t_lat, t_lon, t_alt = pm.ned2geodetic(
                abs_n, abs_e, 0, # North, East, Down (0)
                self.home_lat, self.home_lon, self.home_alt
            )
            
            self.swarm_targets.append((t_lat, t_lon))
            
        print("\n--- Mission Targets Calculated (GPS) ---")
        for i, (lat, lon) in enumerate(self.swarm_targets):
            print(f"Target {i+1}: Lat={lat:.6f}, Lon={lon:.6f}")
            
        return self.swarm_targets
    
