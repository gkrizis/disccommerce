# DiscCommerce
This project presents a simple way to update your woocommerce music store with your discogs store data or, in general, 
any discogs exported data.

## Example
In the *./example/* directory there are two csv files exported from **discogs** and **Woocommerce**, using the default 
formatting.

The discogs store is considered updated, while the woocommerce store is considered outdated.
During the execution of **main.py** two **.csv** files are created:
- *out_old.csv*
    * This file contains the products of the store that have not, yet, been sold. This .csv is the one to be populated 
      with the new products and be passed to the WooCommerce imported to update store
      
- *out_new.csv*
    * This file will update the discogs.csv with each release's artwork. The artwork is imported in the .csv file using
    the **Discogs OAuth Example**
      
## Execution

To run this example:

- *(optional)* Create a virtual environment
- pip install needed modules (oauth, pandas)
- Run main.py
- Follow console instructions