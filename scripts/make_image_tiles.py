import sys
import os
sys.path.append(os.path.dirname("config.py"))
import extract_map_images
if __name__ == "__main__":
    map_id = "0018035"
    extract_map_images.download_map_image(map_id)
    extract_map_images.make_tiles_from_image("map_images/" + map_id + ".jp2", 6, 8)