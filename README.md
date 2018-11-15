# Items List Generator

Creates static html items list with photos, prices and descriptions.


## Usage

### Items directory
- items
  - `category`
    - `single_item`.jpg
    - `single_item`.txt
    - `items_pack`\#`price`
      - `item1`.jpg
      - `item1`.txt
      - `item2`.jpg
      - `item2`.txt

### Item description - `item`.txt
!`sub-category1` `sub-category2`

title: `item`  
price: `price`  
`info1`: `val1`  
`info2`: `val2`  
  
\#\#  
`optional multiline description`

### Generate - www-auto.py
Check path to ImageMagic and parameter names used in `item`.txt for price and title.
```
IM         = 'ImageMagick/convert.exe '
ITEMS_DIR  = 'items/'
WWW_DIR    = 'www-auto/'
PRICE_TXT  = 'price'
TITLE_TXT  = 'title'
```

Items List will be saved to www-auto directory.