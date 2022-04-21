from pip._vendor import requests
from os import listdir
from os.path import isfile, join
from dotenv import dotenv_values
from PIL import Image as PILImage
import sys
import shutil
import mercantile
import warnings


# Import API key from .env file
keys = dotenv_values("keys.env")
mbAPIKey = keys["mapboxAPIKey"]

def initVariables(variables):
    delta = 0
    lat_lng = []

    for variable in variables:
        if variable == sys.argv[1]: lat_lng.append(float(variable)) # lat
        if variable == sys.argv[2]: lat_lng.append(float(variable)) # long
        if variable == sys.argv[3]: delta = float(variable) # delta

    return delta, lat_lng

def createTiles(x_tile_range, y_tile_range):

    # Enumerate for naming the files saved from request
    for i,x in enumerate(range(x_tile_range[0],x_tile_range[1]+1)):
        for j,y in enumerate(range(y_tile_range[0],y_tile_range[1]+1)):

            # Create request for elevation data image tiles
            # mbTerrainURL = f"https://api.mapbox.com/v4/mapbox.terrain-rgb/{str(z)}/{str(x)}/{str(y)}@2x.pngraw?access_token={mbAPIKey}"
            # response = requests.get(mbTerrainURL, stream=True)

            # # Write the raw content to img
            # with open(f'./elevation_images/{str(i)}.{str(j)}.png', "wb") as file:
            #     response.raw.decode_content = True
            #     shutil.copyfileobj(response.raw, file)


            # Create request for satellite elevation data image
            mbSatteliteURL = f"https://api.mapbox.com/v4/mapbox.satellite/{str(z)}/{str(x)}/{str(y)}@2x.pngraw?access_token={mbAPIKey}"
            response = requests.get(mbSatteliteURL, stream=True)

            # Write raw content
            with open(f'./satellite_images/{str(i)}.{str(j)}.png', "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)


def composeImages(x_tiles, y_tiles, lat_lng):
    for dir_name in ['satellite_images']:
            img_names = []
            for file in listdir(f'./{dir_name}'):
                if file.endswith('.png'):
                    img_names.append(f'{dir_name}/{file}')
            
            # Get raster size
            raster_length_width = x_tiles[1] - x_tiles[0] + 1
            raster_length_height = y_tiles[1] - y_tiles[0] + 1
            raster_length_width = max(1,raster_length_width)
            raster_length_height = max(1,raster_length_height)

            # calculate the total size of composite image
            images = [PILImage.open(x) for x in img_names]
            raster_width, raster_height = images[0].size
            total_width = raster_width*raster_length_width
            total_height = raster_height*raster_length_height

            # Create new composite image with given w/h
            composite = PILImage.new('RGB', (total_width, total_height))

            y_offset = 0
            for i in range(0,raster_length_width):
                x_offset = 0
                for j in range(0,raster_length_height):
                    print(raster_length_width, raster_length_height)
                    temp = PILImage.open(f"./{dir_name}/{str(i)}.{str(j)}.png")
                    composite.paste(temp, (y_offset, x_offset))
                    # For every raster in the first column, the next image pasted should be offset by the raster height
                    x_offset += raster_height
                # For every column finished, the next Y should be offset by raster width
                y_offset += raster_width
            
            composite.save(f"./composite_images/{dir_name}-{lat_lng[0]}-{lat_lng[1]}.png")



if __name__ == "__main__":

    # Program requires three arguments (delta, lat, lng)
    if len(sys.argv) > 3:
        delta, lat_lng = initVariables(sys.argv)
        print('running')

        # converting lat_lng to tilesets
        topLeft = [lat_lng[0]+delta, lat_lng[1]-delta*2]
        bottomRight = [lat_lng[0]-delta, lat_lng[1]+delta*2]
        z = 15 # Needs to be 0-15 where 15 is max resolution/zoom

        tl_tiles = mercantile.tile(topLeft[1],topLeft[0],z)
        br_tiles = mercantile.tile(bottomRight[1],bottomRight[0],z)
        
        x_tile_range =[tl_tiles.x,br_tiles.x]
        y_tile_range = [tl_tiles.y,br_tiles.y]

        print('Creating images...')
        createTiles(x_tile_range, y_tile_range)
        print('Got tiles from API.')

        print('Composing images...')
        composeImages(x_tile_range, y_tile_range, lat_lng)
        print('Composing done.')




    # If not enough arguments are passed in, exit the program
    else:
        print('Please provide arguments.')
        print('Usage: python app.py <lat> <long> <delta>')
        sys.exit()

    
