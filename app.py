from dotenv import dotenv_values
from pip._vendor import requests
from os import listdir
from os.path import isfile, join
import sys
import shutil
import mercantile
import PIL
import math


# Import API key from .env file
keys = dotenv_values("keys.env")
mbAPIKey = keys["mapboxAPIKey"]

def initVariables(variables):
    delta = 0
    lat_lng = []

    for variable in variables:
        if variable == sys.argv[1]: lat_lng.append(float(variable))
        if variable == sys.argv[2]: lat_lng.append(float(variable))
        if variable == sys.argv[3]: delta = float(variable)

    return delta, lat_lng

def createTiles(x_tile_range, y_tile_range):
    for i,x in enumerate(range(x_tile_range[0],x_tile_range[1]+1)):
        for j,y in enumerate(range(y_tile_range[0],y_tile_range[1]+1)):

            # Create request for image tiles
            mbTerrainURL = f"https://api.mapbox.com/v4/mapbox.terrain-rgb/{str(z)}/{str(x)}/{str(y)}@2x.pngraw?access_token={mbAPIKey}"
            response = requests.get(mbTerrainURL, stream=True)

            # Write the raw content to img
            with open(f'./elevation_images/{str(i)}.{str(j)}.png', "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)

            # Create request for satellite data
            mbSatteliteURL = f"https://api.mapbox.com/v4/mapbox.satellite/{str(z)}/{str(x)}/{str(y)}@2x.pngraw?access_token={mbAPIKey}"
            response = requests.get(mbSatteliteURL, stream=True)

            # Write raw content
            with open(f'./satellite_images/{str(i)}.{str(j)}.png', "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)

def composeImages():
    for dir_name in ['elevation_images', 'satellite_images']:
            img_names = []
            for file in listdir(f'./{dir_name}'):
                img_names.append(f'{dir_name}/{file}')
            
            images = [PIL.Image.open(x) for x in img_names]


if __name__ == "__main__":

    # Program requires three arguments (delta, lat, lng)
    if len(sys.argv) > 3:
        delta, lat_lng = initVariables(sys.argv)

        # converting lat_lng to tilesets
        topLeft = [lat_lng[0]+delta, lat_lng[1]-delta]
        bottomRight = [lat_lng[0]-delta, lat_lng[1]+delta]
        z = 15 # Max resolution/zoom

        tl_tiles = mercantile.tile(topLeft[1],topLeft[0],z)
        br_tiles = mercantile.tile(bottomRight[1],bottomRight[0],z)
        
        x_tile_range =[tl_tiles.x,br_tiles.x]
        y_tile_range = [tl_tiles.y,br_tiles.y]

        print('Creating images...')
        createTiles(x_tile_range, y_tile_range)
        print('Got tiles from API.')

        print('Composing images...')
        composeImages()
        print('Composing done.')




    # If not enough arguments are passed in, exit the program
    else:
        print('Please provide arguments.')
        print('Usage: python app.py <lat> <long> <delta>')
        sys.exit()

    