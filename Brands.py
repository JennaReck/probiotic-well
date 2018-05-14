from Handler import *

class Brands(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        delivery_methods = self.get_all_delivery_methods()
        brand_names = self.get_all_brands()
        
        sort = self.request.get('sort')
        if sort not in ["cheapest", "popular", "a-to-z", ""]:
            self.redirect("/brands")
            return #if sort is not valid input, redirect to main brands page

        delivery_method = self.request.get('deliverymethod')
        strain_count = self.request.get('straincount')
        cfu = self.request.get('cfucount')
        refrigeration_required = self.request.get('refrigerationrequired')
        brand_name = self.request.get('brandname')
        recommended_for = self.request.get('recommendedfor')
        price = self.request.get('priceamount')

        if delivery_method or strain_count or cfu or refrigeration_required or brand_name or recommended_for or price:
            products = self.filter_products(delivery_method, strain_count,
                                            cfu, refrigeration_required,
                                            brand_name, recommended_for,
                                            price)
        else:
            products = self.sort_products(sort)
        
        url_parameters = self.make_url_parameters(["sort", sort],
                                                  ["deliverymethod", delivery_method],
                                                  ["straincount", strain_count],
                                                  ["cfucount", cfu],
                                                  ["refrigerationrequired", refrigeration_required],
                                                  ["brandname", brand_name],
                                                  ["recommendedfor", recommended_for],
                                                  ["priceamount", price])
        
        p = self.request.get('p')
        pagination = self.make_pagination(p, url_parameters, products, 10)
        if not pagination:
            self.redirect("/404") #pagination returns false if p is not
                                  #a proper integer or too high, redirect if so
        current_products = self.next_content(p, products, 10, False)
        self.render("brands.html",
                    pagetitle="Probiotic Well | Brands",
                    delivery_methods=delivery_methods,
                    brand_names=brand_names,
                    products=current_products,
                    pagination=pagination,
                    sort=sort,
                    delivery_method=delivery_method,
                    strain_count=strain_count,
                    cfu=cfu,
                    refrigeration_required=refrigeration_required,
                    brand_name=brand_name,
                    recommended_for=recommended_for,
                    price=price)
        
    def post(self):
        sort = self.request.get('brands-sort-dropdown')
        if sort:
            self.redirect('/brands?sort=' + sort)
        else:
            delivery_method = self.request.get('delivery-method')
            strain_count = self.request.get('strain-count')
            cfu = self.request.get('cfu')
            refrigeration_required = self.request.get('refrigeration-required')
            brand_name = self.request.get('brand-name')
            recommended_for = self.request.get('recommended-for')
            price = self.request.get('price')
            url_parameters = self.make_url_parameters(["deliverymethod", delivery_method],
                                                      ["straincount", strain_count],
                                                      ["cfucount", cfu],
                                                      ["refrigerationrequired", refrigeration_required],
                                                      ["brandname", brand_name],
                                                      ["recommendedfor", recommended_for],
                                                      ["priceamount", price])
            self.redirect('/brands?' + url_parameters)
