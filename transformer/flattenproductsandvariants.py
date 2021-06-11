import copy
import sys
import requests
import marshal
import json

totalcount=0
base_url="https://hg4epjdj0g.execute-api.us-east-1.amazonaws.com/prod?"

def copy(object):
  bytes = marshal.dumps(object)
  redata = marshal.loads(bytes)
  return redata
  
def parse_variants(product, products_and_variants,key_variant):
  variants = []
  #make a deep copy of the current product
  orig_product = copy(product)#copy.deepcopy(product)
  #remove variants
  del orig_product[key_variant]
  #parse all variants from product
  for variant in product[key_variant]:
    new_product = copy(orig_product)
    new_product[key_variant]=copy(variant)
    products_and_variants.append(new_product)
  return products_and_variants


def parse_products(products,key_variant):
  global totalcount
  products_and_variants = []
  for p in products:
    #We are expecting always at least 1 variant!
    products_and_variants= parse_variants(p,products_and_variants,key_variant)
    
  totalcount=len(products_and_variants)
  return products_and_variants

def returnvalue(key,products,key_nextpage, nextpage):
  prod={}
  prod[key] = products
  prod[key_nextpage] = nextpage
  return prod


def process(url, name,key_product, key_variant, products_url, key_limit,key_page, limit, page, key_nextpage):
  global base_url
  print(f'getting Products: {key_product} with variants: {key_variant} from "{products_url}"')

  products = []
  nextpage = ''

  idx = 1
  try:
    addurl=''
    if not (limit==''):
      addurl = key_limit+'='+limit;
    if not (page==''):
      #increase nextpage with 1
      pagenr = int(page)
      pagenr = pagenr+1
      nexturl = addurl+'&'+key_page+'='+str(pagenr)
      addurl = addurl+'&'+key_page+'='+page
      nextpage = f'{url}{nexturl}'
      print(f'Nextpage: {nextpage}"')
    else:
      pagenr = 2
      nexturl = addurl+'&'+key_page+'='+str(pagenr)
      nextpage = f'{url}{nexturl}'
      print(f'Nextpage: {nextpage}"')

    print(f'URL: {products_url}&{addurl}')
    r = requests.get(f'{products_url}&{addurl}')
    p = r.json()[key_product]

    products.extend(p)
  except Exception as e:
    print("OOPS!! General Error")
    print(str(e))
    return returnvalue(key_product,products,key_nextpage, nextpage)

  print(f'Got {len(products)} products')

  products_and_variants = parse_products(products,key_variant)
  if (len(products_and_variants)==0):
    nextpage=''
  print(f'Got {len(products_and_variants)} products with variants')
  #json_dump(products_and_variants, f'{name}.json', None)

  return returnvalue(key_product,products_and_variants,key_nextpage, nextpage)

def lambda_handler(event, context):
    global totalcount
    global base_url
    
    print(f"qs: {json.dumps(event['params']['querystring'])}")
    products_url = event['params']['querystring']['url']
    print(f'products_url: {products_url} ')
    name = event['params']['querystring']['name']
    key_product = event['params']['querystring']['product']
    key_variant = event['params']['querystring']['variant']
    key_limit = event['params']['querystring']['key_limit']
    key_page = event['params']['querystring']['key_page']
    key_nextpage = event['params']['querystring']['key_nextpage']
    url = f'{base_url}name={name}&url={products_url}&product={key_product}&variant={key_variant}&key_limit={key_limit}&key_page={key_page}&key_nextpage={key_nextpage}&'
    print(f'url: {url} ')
    limit = ''
    page=''
    if ('limit' in event['params']['querystring']):
      limit = event['params']['querystring']['limit']
    if ('page' in event['params']['querystring']):
      page = event['params']['querystring']['page']
    print (products_url)

    return {#process(name,key_product, key_variant, products_url, key_limit,key_page, limit, page)#{ #{
        'statusCode': 200,
        'body': process(url,name,key_product, key_variant, products_url, key_limit,key_page, limit, page,key_nextpage),
        "headers": {
          "Content-Type": "application/json",
          "totalCount": totalcount
      }    
    }
#print(process('yellow','products','variants',"https://www.yellowshoes.com/fr/products.json?","limit","page","200","20","nextpage"))
#https://hg4epjdj0g.execute-api.us-east-1.amazonaws.com/prod?https://www.yellowshoes.com/fr/products.json?&limit=2&page=2