import pymap3d as pm


def get_sub_sector_centers(area_width=100, area_height=100, n_rows=2, n_cols=2):
    """
    Divides a rectangular area into a grid and calculates the center (x, y) 
    of each sub-sector.
    
    Assumes the "Origin" (0,0) is the Bottom-Left corner of the area.
    
    Args:
        area_width (float): Total width of the area in meters (East-West).
        area_height (float): Total height of the area in meters (North-South).
        n_rows (int): Number of horizontal divisions.
        n_cols (int): Number of vertical divisions.
        
    Returns:
        list of tuples: A list containing (center_x, center_y) for each sector.
    """
    
    # 1. Calculate the size of each small sector
    sector_width = area_width / n_cols
    sector_height = area_height / n_rows
    
    centers = []
    
    print(f"--- Partitioning {area_width}x{area_height}m Area ---")
    print(f"Grid: {n_rows}x{n_cols}")
    print(f"Sector Size: {sector_width}x{sector_height}m\n")

    # 2. Loop through rows and columns to find centers
    # We iterate i (row) and j (column)
    for row in range(n_rows):
        for col in range(n_cols):
            # Calculate the Bottom-Left corner of this specific sector
            x_min = col * sector_width
            y_min = row * sector_height
            
            # The center is the Bottom-Left + half the size
            center_x = x_min + (sector_width / 2)
            center_y = y_min + (sector_height / 2)
            
            centers.append((center_x, center_y))
            
            # Labeling for clarity (0,0 is bottom-left, 0,1 is bottom-right, etc.)
            print(f"Sector [{row},{col}] Center: X={center_x:.1f}m, Y={center_y:.1f}m")
            
    return centers


def get_ned_distance(target_lat, target_lon, target_alt, origin_lat, origin_lon, origin_alt):
    """
    Converts a global GPS target into local meters (North, East) relative to an origin.
    
    Args:
        target_lat, target_lon, target_alt: Coordinates of the point you want to measure.
        origin_lat, origin_lon, origin_alt: Coordinates of your 'Home' (0,0,0).
        
    Returns:
        north_m: Distance North in meters (X axis).
        east_m: Distance East in meters (Y axis).
    """
    
    # geodetic2ned converts Geodetic (lat/lon/alt) to North-East-Down (meters)
    # Observer/Origin is the second set of arguments
    north_m, east_m, down_m = pm.geodetic2ned(
        target_lat, target_lon, target_alt,
        origin_lat, origin_lon, origin_alt
    )
    
    return north_m, east_m



if __name__ == "__main__":
    # Run the logic for the "Sky Guards" scenario
    # 100x100m area, divided into 4 sectors (2x2 grid)
    waypoints = get_sub_sector_centers(100, 100, 2, 2)
    
    print("\nThese are the local (NED) targets for your 4 drones:")
    print(waypoints)