# Indexing Shopify Using the Generic REST API Connector

## Use Case
This shows how to index Shopify products. Every website running the Shopify platform exposes a public api called `products.json`.
This public api exposes all the products, including (as childs) the variants.

## Prerequisites
To fully understand how to use this example, you must:
1. Have a Coveo Platform organization.
2. Learn about [Coveo Connectivity](https://docs.coveo.com/en/1702/).
3. Learn [how to configure a Generic REST API source](https://docs.coveo.com/en/1896/).

## Instructions
1. [Create a Generic REST API Source](https://docs.coveo.com/en/1896/). 
2. Change the [ProductAndVariantConfig.json](https://github.com/coveooss/connectivity-library/blob/master/Shopify/index/ProductAndVariantConfig.json).
  * You have two endpoints defined. The first is the (temporary) proxy to format multiple variants into single ones. The second is indexing the products directly.
  * The first endpoint points to the target url: `"url": "https://www.yellowshoes.com/fr/products.json?"`. Change it to your website. Make sure to end with the `?`.
  * The second endpoint points to the original url: `"Url": "https://www.yellowshoes.com/",`. Change it to your website.
  * The second endpoint uses the following path: `"Path": "fr/products.json",`. Change it to your specific path.
3. Add the (changed) [ProductAndVariantConfig.json](https://github.com/coveooss/connectivity-library/blob/master/Shopify/index/ProductAndVariantConfig.json). 
4. Make sure you've changed all placeholders in the configuration with your own values.
5. [Create the appropiate fields and mappings](https://docs.coveo.com/en/1896/#completion).

## Content indexed
* Products
* Variants

## Temporary proxy
Because the current REST Connector does not support `Subitems` on nested objects, we need to create a 1:1 JSON with Products & Variants. Shopify responds with 1:many Products & Variants, so we need a a temporary solution to fix this.
We created an Amazon AWS REST service which takes care of this. 

Available here: [Amazon proxy url](https://hg4epjdj0g.execute-api.us-east-1.amazonaws.com/prod)

Example call here: [Example](https://hg4epjdj0g.execute-api.us-east-1.amazonaws.com/prod?url=https://www.yellowshoes.com/fr/products.json?&name=yellow&product=products&variant=variants&key_limit=limit&key_page=page&limit=10&key_nextpage=nextpage)

### Parameters
| Parameter | Contents |
| --- |--- |
| url | The URL to index (must end with ?)|
| name | Name |
| product | JSON key for the products |
| variant | JSON key for the variants |
| key_limit | The url parameter key to use for the limit (for the url specified above) |
| key_page | The url parameter key to use for the paging (for the url specified above) |
| key_nextpage | The JSON key to use for the nextpage which will be used as paging parameter in the Generic REST |

### Custom fields
The following custom fields must be created:
| Field        | Type           | Features  |
| ------------- |-------------|-----|
| ec_brand | String | Facet |
| ec_category | String | Facet |
| ec_name | String | Free Text, Ranking, Stemming |
| ec_images | String | |
| ec_price | Decimal | |
| ec_promo_price| Decimal | |
| ec_item_group_id | String | |
| ec_in_stock | String | |
| ec_slug| String | |
| ec_tags| String | Multi value facet |
| sku| String | |
| ec_image| String ||
| ec_size | String ||
| ec_product_color | String ||

### AWS deployment
1. Create an AWS Lambda Python function with the code from [requestspackage.zip](https://github.com/coveooss/connectivity-library/blob/master/Shopify/transformer/requestspackage.zip). 
  * If you want to create the zip yourselves:
    * create a new directory
    * `pip install requests -t .`
    * copy `flattenproductsandvariants.py` in that directory
    * zip everything in that directory
    * upload that zip to your lambda function
2. Set the timeout of this function to 30 seconds.
3. Create an AWS REST API
  * GET Integration Request
  * Integration type: Lambda function
  * Use Lambda Proxy Integration: false
  * Lambda Function: (the above)
  * Mapping Template: Use the passthrough template
  * GET Integration Response
  * Mapping Template: application/json, with Template:
```
$input.json("$.body")
#set($counter = "$input.json('$.totalCount')")
#set($context.responseOverride.header.totalCount = $counter)
```





## Security indexed
No Security is indexed


## Reference
https://shopify.dev/docs

## Version
1.1 June 2021, Wim Nijmeijer
    Fixed Global url
1.0 May 2021, Wim Nijmeijer

