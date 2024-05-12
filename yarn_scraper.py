from bs4 import BeautifulSoup, Tag
from urllib.parse import urlencode
from urllib.request import urlopen
import sys

URL = "https://www.yarn.com/categories/yarn-by-type?%s"



class Listing():
    def __init__(self, name, description, price, product_link, sale):
        self.name = name
        self.price = float(price.strip("$"))
        self.product_link = product_link
        self.sale = sale
        self.materials = self.get_material(description)
        self.thickness = self.get_thickness(description)
        (self.length, self.mass) = self.get_dimensions(description)
        # Rate: price per 100g
        self.rate = self.get_rate()
    
    # Return String
    def __str__(self):
        return "%s,\n %s,\n \t%s,\n \t%s weight,\n \t%im, \t%ig, \t$%.2f, \t$%.2f/100g,\t%s" % (self.name, self.product_link, self.materials, self.thickness, self.length, self.mass, self.price, self.rate, self.sale)


    # Return Tuple:Float dimensions: len (meters) and mass (100 grams) 
    def get_dimensions(self, description):
        listed_description = description.split(",")
        length="" # meters
        mass="" # 100 grams

        if not len(listed_description) > 1:
            return (None, None)

        dimensions = listed_description[1].split("/")

        if not len(dimensions) > 1:
            return (None, None)

        record = False
        dim_lens = dimensions[0]
        for i in range(len(dim_lens)):
            if dim_lens[i]=="(":
                record=True
                continue
            if record and not (dim_lens[i]=="m"):
                dim_lens[i]
                length += dim_lens[i]
            elif (dim_lens[i]=="m"):
                record=False
                break

        dim_mass = dimensions[1]
        for i in range(len(dim_mass)):
            if dim_mass[i]=="g":
                break
            else:
                mass += dim_mass[i]

        return (float(length), float(mass))
    
    # Return String Thickness
    def get_thickness(self, description):
        thickness = description.split(",")
        if len(thickness) < 3:
            return "Unknown Thickness"
        return thickness[2].strip()

    # Return String material
    def get_material(self, description):
        material = description.split(",")
        return material[0].strip()
    
    # Return Float rate (price_per_100g)
    def get_rate(self):
        rate = 0
        if not(self.mass==0 or self.mass is None):
            rate = 100*self.price/(self.mass)
        
        return rate


# Scrape web, return pages variable
def getPages(materials, weights):

    filters = []
    # URL parameters associeted with args
    params = {"wool":["Wool", "Virgin Wool"],"merino wool":["Merino Wool"],
              "specialty wool":["Baby Alpaca", "Alpaca", "Cashmere", "Mohair", "Angora", "Llama"],"silk":["Silk"],
              "acrylic/synthetic":["Acrylic", "Viscose", "Nylon", "Polyester", "Polyalamide", "Lyocell", "Modal", "Rayon", "Synthetic"],
              "cotton": ["Cotton"], "linen": ["Linen"], "bamboo":["Bamboo"], "lace":["Lace | 2 Ply", "Light Fingering"], "superfine":["Fingering"],
              "fine":["Sport"], "light":["DK | Light Worsted"], "medium":["Worsted", "Aran"], "bulky":["Bulky", "Heavy Worsted"], "superbulky":["Super Bulky", "Super Bulky | Super Chunky"]}

    if materials is not ["all"]:
        for material in materials: 
            for value in params[material]:
                filters.append(("filter-fibers.en-US", value))
    if weights is not ["all"]:
        for weight in weights: 
            for value in params[weight]:
                filters.append(("filter-yarnWeight.en-US", value))
    
    filters.append(())
    pages = []
    i = 1
    while True:
        try:
            filters[-1] = ("page", str(i))
            params = urlencode(filters).replace("+", "%20")
            with urlopen(URL % params) as response:
                soup = BeautifulSoup(response, "html.parser")
                products_grid = soup.find(class_="products__grid")
                if products_grid is None:
                    break
                else:
                    pages.append(products_grid)
        except (Exception) as error:
            print(error.__str__())
            break
            
        i += 1

    return pages

# Return array of Listing objects
def getListings(materials, weights):

    # pages is bs object products grid
    pages = getPages(materials, weights)

    listings = []

    for page in pages:
        # Iterate all products in grid
        for listing_tag in page.children:
            if type(listing_tag)==Tag:

                # Product Listing
                if listing_tag["data-testid"]=="product-card":
                    attributes = {"name":"", "description":"", "price":"", "product_link":"", "sale":False}

                    # Get product attributes 
                    for tag in listing_tag.children:
                        if type(tag)==Tag:

                            # Get name, product_link, description
                            if (tag.name=="a" and "data-testid" in tag.attrs):
                                if tag["data-testid"]=="product-link":
                                    # Link
                                    attributes["product_link"]=tag["href"]
                                    for child_tag in tag.children:
                                        if type(child_tag)==Tag:

                                            if ("class" in child_tag.attrs):
                                                # Name
                                                if child_tag.name=="h2":
                                                    if child_tag["class"]==["product-card__title"]:
                                                        attributes["name"]=child_tag.string.strip()
                                                # Description
                                                elif child_tag.name=="p":
                                                    if child_tag["class"]==["product-card__subtitle"]:
                                                        attributes["description"]=child_tag.string.strip()
                            
                            # Get price and sale
                            elif (tag.name=="div" and "class" in tag.attrs):
                                if "product-price" in tag["class"]:
                                    for child_tag in tag.descendants:
                                        if type(child_tag)==Tag:

                                            # get price and sale
                                            if (child_tag.name=="span" or child_tag.name=="ins") and ("class" in child_tag.attrs):

                                                if (child_tag["class"]==["lc-price__regular"]):
                                                    attributes["price"]=child_tag.text.strip()
                                                    if "From\n" in attributes["price"]:
                                                        attributes["price"] = attributes["price"].replace("From\n", "").strip()
                                                elif  (child_tag["class"]==["lc-price__special"]):
                                                    attributes["price"]=child_tag.contents[0].text.strip().replace("From ", "")
                                                    
                                                attributes["sale"]=(child_tag["class"]==["lc-price__special"])

            # Create new listing
            newListing = Listing(attributes["name"], attributes["description"], attributes["price"], attributes["product_link"], attributes["sale"])
            if not((newListing.length is None) or (newListing.mass is None)):
                listings.append(newListing)

    return listings


# Return [amount] array of listing objects, sorted by lowest rate
def getTopListings(amount, material, weight):
    matches = getListings(material, weight)
    topListings = [None] * amount

    # Find match with lowest price rate, sort [amount] matches within ascending order
    lowest_rate = 25.0
    i=0
    # For each entry in top listings
    while i < amount:
        
        # In the case "amount" > len matches
        if len(matches)==0:
            return topListings
        # Iterate matches to find match with lowest rate 
        for match in matches:
            if match.rate < lowest_rate:
                topListings[i] = match
                lowest_rate = match.rate
            
        # Remove entry from matches, increment topLIstings
        if topListings[i] in matches:
            matches.remove(topListings[i])
        lowest_rate = 25.0
        i += 1


    return topListings
    


        

'''
    System args:
        0: program name
        1: int amount of listings to display (top listings with best price rate)
            (one number) 1-100
        2: str material [wool-merinowool-specialtywool-silk-acrylic/synthetic-cotton-linen-bamboo]
            (delim: - ) w-mw-sw-s-a-c-l-b
        3: str weight (thickness) [lace-superfine-fine-light-medium-bulky-superbulky]
            (delim: - ) 0-1-2-3-4-5-6
'''
if __name__=="__main__":
    printHelp = False
    amount = 0
    material_key = {"all":"all","w":"wool", "mw":"merino wool", "sw":"specialty wool", "s":"silk", "a":"acrylic/synthetic", "c":"cotton", "l":"linen", "b":"bamboo"}
    weight_key = {"all":"all", "0":"lace", "1":"superfine", "2":"fine", "3":"light", "4":"medium", "5":"bulky", "6":"superbulky"}
            
    
    arg2 = []
    arg3 = []
    for i in range(1, len(sys.argv)):
        if i == 1:
            try:
                amount = int(sys.argv[i])
                if amount > 100:
                    amount = 100
                elif amount < 1:
                    amount = 1
            except ValueError:
                printHelp = ((amount == "--help") or (amount == "--h"))                    
        elif i == 2:    
            arg2 = sys.argv[i].split("-")
        elif i ==3:
            arg3 = sys.argv[i].split("-")

    if not printHelp:
        materials = []
        weights = []
        for entry in arg2:
            if entry in material_key.keys():
                materials.append(material_key[entry])
        for entry in arg3:
            if entry in weight_key.keys():
                weights.append(weight_key[entry])

        # Get [amount] listings which fit condition, sorted by best rate. 
        topListings = getTopListings(amount, materials, weights)
        
        # Print formatted listings
        for listing in topListings:
            if listing is not None:
                print(listing.__str__())
    else:
        print("Three optional args: \nFirst arg amount: integer 1-100")
        print("Second arg material (fiber): ")
        for i, (key, value) in enumerate(material_key.items()):
            print("%s: %s", key, value)
        print("Third arg thickness (weight): ")
        for i, (key, value) in enumerate(weight_key.items()):
            print("%s: %s", key, value)
