import pymap3d as pm

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

