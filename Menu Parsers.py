# -*- coding: UTF-8 -*-
import requests
import bs4
import json

res = requests.get('https://www.e-food.gr/delivery/nea-smurni/peri-gyros')
###---https://www.e-food.gr/delivery/menu/pizza-fan

soup = bs4.BeautifulSoup(res.text, 'lxml')


###-----------------------Parsing the Category Names-----------------------###
names = []
for i in soup.find_all(class_ = "w-75 text-truncate h3 mb-0"):
    names.append(i.text)

category_names = []
for i in range(len(names)):
    category_names.append(names[i].replace('\n','').replace(' ','').replace('/', '-').replace('|', '-'))
    category_names[i] = category_names[i].upper()

del category_names[0]



###-----------------------Parsing the Items as Blocks (Name, Description, Price)-----------------------###
l = []
for i in soup.find_all(class_ = "shop-profile-menu-list-item--inner py-7 d-flex justify-content-between align-items-center"):
    l.append(i.text)

item_blocks = []
for i in range(len(l)):
    item_blocks.append(l[i].replace('\n\n','').replace(' \n','').replace('&','και').replace('Από ',''))


###-----------------------Parsing the number of dishes in each category-----------------------###
categ_no = []
for i in soup.find_all(class_ = "text-muted font-weight-normal ml-auto d-md-none"):
    categ_no.append(i.text)

no_of_dishes_per_categ = []
for i in range(len(categ_no)):
    no_of_dishes_per_categ.append(categ_no[i].replace('\n','').replace(' ',''))
    no_of_dishes_per_categ[i] = int(no_of_dishes_per_categ[i])


###-----------------------Connecting each category with its item blocks-----------------------###

joint_categs_items = []
cdef = {}

for (a,b) in zip(category_names,no_of_dishes_per_categ):
    joint_categs_items.append([a,b])

for pair in joint_categs_items:  
    cdef[pair[0]] = item_blocks[0:pair[1]]
    del item_blocks[0:pair[1]]
             
###-----------------------Splitting each item block to: name, description, price-----------------------###
for i in cdef:
    for j in range(len(cdef[i])):
        cdef[i][j] = cdef[i][j].splitlines()

for i in cdef:
    for j in cdef[i]:
        for z in j:
            if z.find('€') != -1:
                if z[z.index('€')-5].isdigit():
                    a,b = j[j.index(z)][:j[j.index(z)].index('€')-5], j[j.index(z)][j[j.index(z)].index('€')-5:].replace('€','').replace(',','.')
                    j[j.index(z)] = a
                    j.append(b)
                else:
                    a,b = j[j.index(z)][:j[j.index(z)].index('€')-4], j[j.index(z)][j[j.index(z)].index('€')-4:].replace('€','').replace(',','.')
                    j[j.index(z)] = a
                    j.append(b)

total_products = [len(cdef[i]) for i in cdef]
"""for z in cdef:
    for y in range(len(cdef[z])):
        if len(cdef[z][y]) == 2:
            cdef[z][y][1] = cdef[z][y][1].replace(' ','').replace('€','').replace(',','.')
        else:
            cdef[z][y][2] = cdef[z][y][2].replace(' ','').replace('€','').replace(',','.')"""


###-----------------------Creating the dict that will turn into the final json-----------------------###
null = "null"
true = "true"
false = "false"


default_dict = {
    "items": [
        {
            "additives": [],
            "alcohol_percentage": 0,
            "allergens": [],
            "availability_period": {
                "end": null,
                "start": null
            },
            "barcode_gtin": null,
            "baseprice": {
                "amount": "ΕΔΩ",
                "currency": "EUR"
            },
            "catalog_id": null,
            "courier_restrictions": [],
            "delivery_methods": [
                "eatin",
                "takeaway",
                "homedelivery"
            ],
            "description": [
                {
                    "lang": "el",
                    "value": "ΕΔΩ",
                    "verified": true
                }
            ],
            "discounted": null,
            "distributor_information": [],
            "enabled": true,
            "external_id": null,
            "forbidden_courier_capabilities": [],
            "id": null,
            "image": null,
            "image_blurhash": null,
            "ingredients": [],
            "is_bundle_offer": false,
            "merchant_sku": "",
            "name": [
                {
                    "lang": "el",
                    "value": "ΕΔΩ",
                    "verified": true
                }
            ],
            "nutrition_facts": [],
            "option_bindings": [],
            "producer_information": [],
            "product_category_id": null,
            "quantity_sold": null,
            "quantity_total": null,
            "required_courier_capabilities": [],
            "source": null,
            "user_requirements": [],
            "vat_percentage": null,
            "version": {},
            "weekly_availability": null,
            "weekly_visibility": null
        },
        
    ],
    "options": []
} 

default_list = [default_dict for i in range(sum(total_products))]

x = 0
while x < len(default_list):
    for i in cdef:
        for j in cdef[i]:
            if len(j) == 2:  ###add the 'no. of elements per item block' control
                default_list[x]['items'][0]['baseprice']['amount'] = j[1]
                default_list[x]['items'][0]['description'][0]['value'] = ""
                default_list[x]['items'][0]['name'][0]['value'] = j[0]
                x += 1
            else:
                default_list[x]['items'][0]['baseprice']['amount'] = j[2]
                default_list[x]['items'][0]['description'][0]['value'] = j[1]
                default_list[x]['items'][0]['name'][0]['value'] = j[0]
                x += 1


for pair in joint_categs_items:
    with open('{0}.json'.format(pair[0]), 'w') as fp:
        for i in range(pair[1]):
            json.dump(default_list[i], fp)
            del default_list[i]

print('Done')