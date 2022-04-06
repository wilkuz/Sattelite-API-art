from os import listdir

for dir_name in ['elevation_images', 'satellite_images']:
            img_names = []
            for file in listdir(f'./{dir_name}'):
                img_names.append(f'{dir_name}/{file}')
            print(img_names)