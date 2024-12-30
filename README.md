# address-maker
Generate real addresses in bulk for your project using a simple collection of Python scripts!

Have you ever needed addresses in particular cities, states, or zip codes? Do you need these addresses in bulk? Use my address maker suite!

These files allow you to generate addresses to your specification. Addressgen is used to generate based on particular zip codes, while citygen is used to generate based on city and state. You can choose to use the smarty API to validate your addresses, and additionally, you can filter to only residential addresses. If all you need is a *potentially* valid address, then the tool can also provide you with randomized addresses based on real street names and formatting in order to pass basic validators. 

ndownload - Helper file that downloads the needed edges files from the US census bureau website
addressgen - base file which hadnles tiger shapefiles, generates and validates addresses based on zip codes
citygen - extends addressgen to generate based on city and state rather than zipcode. 
