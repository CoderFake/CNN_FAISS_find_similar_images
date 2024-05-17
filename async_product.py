import os
import csv
import aiohttp
import asyncio
import aiomysql

# Ensure you have a directory to save the images
os.makedirs('product_images', exist_ok=True)

async def fetch_image(session, image_url, product_id):
    if not isinstance(image_url, str):
        print(f'Invalid URL for product_id {product_id}: {image_url}')
        return product_id, None

    try:
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_path = os.path.join('product_images', f'{product_id}.jpg')
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_data)
                print(f'Saved image {product_id}.jpg')
                return product_id, f'{product_id}.jpg'
            else:
                print(f'Failed to fetch image {product_id}.jpg, status code: {response.status}')
                return product_id, None
    except Exception as e:
        print(f'Error fetching image for product_id {product_id}: {e}')
        return product_id, None
async def fetch_images_and_save_csv():
    # Database connection details
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'db': 'htttql2024',
    }

    conn = await aiomysql.connect(**db_config)
    async with conn.cursor() as cur:
        await cur.execute("SELECT product_id, image_url FROM store_productimage WHERE image_type='default'")
        images = await cur.fetchall()
    
    await conn.ensure_closed()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for image in images:
            product_id, image_url = image
            tasks.append(fetch_image(session, image_url, product_id))
        results = await asyncio.gather(*tasks)
    
    with open('image_filenames.csv', mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['product_id', 'filename'])
        for result in results:
            product_id, filename = result
            if filename:
                csv_writer.writerow([product_id, filename])
            else:
                csv_writer.writerow([product_id, 'failed'])

if __name__ == '__main__':
    asyncio.run(fetch_images_and_save_csv())
