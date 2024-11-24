from apify_client import ApifyClient
import ast
from skimage import io
import requests

def scrap_asos(query, maxItems = 1):
    """ Data scraper from asos.
    Inputs: 
        query (str): search query
        maxItems (int): number of items to scrap
    
    Returns:
        Items (list): list of dictionaries containing the following keys:
            name (str): name of the item
            brandName (str): brand name of the item
            price (str): price of the item
            image (np.array): image of the item
            url (str): url of the item
            gender (str): gender of the item
    """
    
    client = ApifyClient("apify_api_zHwEmmY3hZNab6L57n4NiebpEJDQy42PNRGq")
    
    run_input = {
        "search": query,
        "maxItems": maxItems,
        "endPage": 1,
        "extendOutputFunction": "($) => { return {} }",
        "customMapFunction": "(object) => { return {...object} }",
        "proxy": { "useApifyProxy": True },
    }
    
    run = client.actor("epctex/asos-scraper").call(run_input=run_input)
    
    Items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        try :
            # Certains articles n'ont pas de prix d'où la gestion d'erreur
            price = item["variants"][0]["pricing"]["price"]["current"]["text"]
            
            Items.append({
                "name" : item["name"],
                "brandName" : item["brandName"],
                "price" : price,
                "imageUrl" : item["images"][0]["url"],
                "gender" : item["gender"],
                "url" : item["url"]
            })
        except:
            pass
        
    return Items

def scrap_asos_outfit(queries, maxItems=3):
    queries = ast.literal_eval(queries)
    outfit = []
    for i, query in enumerate(queries):
        clothe = scrap_asos(query, maxItems)
        outfit += clothe
    return outfit

def request_asos(query, maxItems=3):
    
	url = "https://asos2.p.rapidapi.com/products/v2/list"

	querystring = {"store":"US","offset":"0","q": query,"limit": str(maxItems), "country":"US","sort":"freshness","currency":"USD","sizeSchema":"US","lang":"en-US"}

	headers = {
		"x-rapidapi-key": "7c2a2e3244msh805418e285d23cbp1faaa8jsn691342a23625",
		"x-rapidapi-host": "asos2.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)

	response = response.json()
	response = response["products"]

	list_keys = ["name", "url", "price", "imageUrl", "brandName", "price"]
	processed_response = []
	for product in response:
		processed_product = {}
		for key in list_keys:
			processed_product[key] = product[key]
		processed_product["price"] = processed_product["price"]["current"]["text"]
		processed_response.append(processed_product)
	return processed_response

def request_asos_outfit(queries, maxItems=3):
    queries = ast.literal_eval(queries)
    outfit = []
    for i, query in enumerate(queries):
        clothe = request_asos(query, maxItems)
        outfit += clothe
    return outfit