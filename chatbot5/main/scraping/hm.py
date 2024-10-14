import requests
from bs4 import BeautifulSoup

# URL trang chủ của H&M Men
base_url = 'https://www2.hm.com'
category_url = 'https://www2.hm.com/en_us/men.html'

# Gửi yêu cầu đến trang
response = requests.get(category_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Tìm tất cả các categories liên quan đến sản phẩm Men
categories = soup.find_all('a', class_='menu__super-link')

# Duyệt qua từng category và crawl sản phẩm trong đó
for category in categories:
    category_name = category.text.strip()
    category_link = base_url + category['href']
    
    print(f"Crawling category: {category_name}")
    print(f"URL: {category_link}")
    
    # Gửi yêu cầu đến trang danh mục để lấy sản phẩm
    category_response = requests.get(category_link)
    category_soup = BeautifulSoup(category_response.text, 'html.parser')
    
    # Lấy danh sách sản phẩm trong danh mục
    products = category_soup.find_all('article', class_='hm-product-item')
    
    # Duyệt qua từng sản phẩm trong danh mục
    for product in products:
        product_name = product.find('a', class_='link').text.strip()
        product_price = product.find('span', class_='price regular').text.strip()
        image_url = product.find('img', class_='item-image')['src']
        
        print(f'Product Name: {product_name}')
        print(f'Price: {product_price}')
        print(f'Image URL: {image_url}')
        print('-' * 40)