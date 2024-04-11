import json
import re

class Validation:
    @staticmethod
    def is_valid_product_data(product_data):
        """
        Validate the structure of product data JSON.
        """
        if not isinstance(product_data, dict):
            return False
        
        required_keys = ['brand', 'title', 'product_id','url','retail_price','image','category']
        for key in required_keys:
            if key not in product_data:
                return False
        
        return True

    @staticmethod
    def validate_product_data_schema(product_data):
        """
        Validate the schema of product data.
        """
        expected_structure = {
            'brand': str,
            'title': str,
            'description' : str,
            'image' : str,
            'images': list,
            'retail_price': str,
            'final_price': str,
            'url': str,
            'product_id': int,
            'category': str,
            'sales_size': str,
            'availability' : str,
            'Buzzwords': list,
            'nutrition': (dict, type(None)),
            'ingredients' : (list, type(None)),
            'country_of_origin':(str, type(None)),
        }
        
        validation_errors = []  
        
        for key, value in expected_structure.items():
            if key not in product_data:
                validation_errors.append(f"Missing key '{key}' in product data.")
            elif not isinstance(product_data[key], value):
                validation_errors.append(f"Key '{key}' has incorrect type. Expected type: {value}, Actual type: {type(product_data[key])}")
        
        if validation_errors:
            return False, validation_errors 
        
        return True, "Product data schema is valid."  

    
    @staticmethod
    def validate_selling_price(product_data):
        """
        Validate that selling_price <= original_price
        """
        selling_price = product_data.get('selling_price')
        original_price = product_data.get('original_price')
        if selling_price is not None and original_price is not None:
            if selling_price <= original_price:
                return True
            else:
                return False
        return True
    
    @staticmethod
    def validate_image_data(product_data):
        """
        Validate that the 'images' list contains at least one URL and image key value cannot be null.
        """
        if product_data.get('image') is None:
            return False, "Image key cannot be null"
        images = product_data.get('images')
        if not images or not any(isinstance(img, str) and img.startswith('http') for img in images):
            return False, "Images list should contain at least one URL"
        return True, ""  
    
    @staticmethod
    def validate_url_format(product_data):
        """
        Validate that the 'url' is in a standardized format.
        """
        url = product_data.get('url')
        if url is not None:
            url_pattern = re.compile(r'^https?://\S+$')
            if not url_pattern.match(url):
                return False, "URL should be in standardized format (e.g., http://example.com)"
        
        return True, ""
    
    @staticmethod
    def validate_product_id_uniqueness(product_data, product_ids):
        """
        Validate the uniqueness of product_id across all products.
        """
        product_id = product_data.get('product_id')
        if product_id in product_ids:
            return False, f"Duplicate product_id: {product_id}"
        else:
            product_ids.add(product_id)
            return True, ""
        
    @staticmethod
    def validate_duplicate_images(product_data):
        """
        Validate for duplicate images within the 'images' list.
        """
        images = product_data.get('images')
        if images:
            unique_images = set()
            for image_url in images:
                if image_url in unique_images:
                    return False, f"Duplicate image URL: {image_url}"
                else:
                    unique_images.add(image_url)
        return True, ""

    @staticmethod
    def validate_pdp_data(json_data):
        """
        Validate the JSON data fetched from the PDP API.
        """
        try:
            product_data = json_data
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        
        if not Validation.is_valid_product_data(product_data):
            return False, "Invalid product data structure"
        
        is_valid_url, message = Validation.validate_product_data_schema(product_data)
        if not is_valid_url:
            return False, message        
        
        is_valid_images, message = Validation.validate_image_data(product_data)
        if not is_valid_images:
            return False, message

        is_valid_url, message = Validation.validate_url_format(product_data)
        if not is_valid_url:
            return False, message

        # # Validate uniqueness of product_id
        global product_ids
        is_valid_id, id_message = Validation.validate_product_id_uniqueness(product_data, product_ids)
        if not is_valid_id:
            return False, id_message

        is_valid_images, message = Validation.validate_duplicate_images(product_data)
        if not is_valid_images:
            return False, message

        return True, "Product data is valid"

if __name__ == "__main__":
    invalid_data_details = []
    product_ids = set()
    with open(r'Output\traderjoes.json', 'r') as f:
        pdp_list = json.load(f)

    for index, pdp_data in enumerate(pdp_list, start=1):
        is_valid, message = Validation.validate_pdp_data(pdp_data)
        if not is_valid:
            invalid_data_details.append(f"Product data at index {index} is not valid: {message}")

    if not invalid_data_details:
        print("All product data is valid")
    else:
        print("Some product data is not valid:")
        for detail in invalid_data_details:
            print(detail)
