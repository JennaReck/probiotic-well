from Handler import *

class Compare(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        products = self.sort_products("a-to-z")
        sort = self.request.get('sort')
        if sort not in ["popular", "pearls", "strain-count", "cfu", ""]:
            self.redirect("/compare")
            return
        probiotic_list = []
        compare_products = []
        probiotic_keys = []
        probiotic_list.append(self.request.get('p1'))
        probiotic_list.append(self.request.get('p2'))
        probiotic_list.append(self.request.get('p3'))
        probiotic_list.append(self.request.get('p4'))
        probiotic_list.append(self.request.get('p5'))
        for probiotic in probiotic_list:
            if probiotic:
                try:
                    int(probiotic)
                except:
                    self.redirect("/404")
                    return
                current_probiotic = self.get_content(int(probiotic), "product")
                if current_probiotic:
                    compare_products.append(current_probiotic)
                probiotic_keys.append(int(probiotic))
            else:
                probiotic_keys.append("")
        if (not sort or sort == "popular") and compare_products == []:
            #Checking to see if any probiotics were selected and
            #if sort was selected or not
            compare_products = self.sort_products("popular")
        if sort == "pearls":
            compare_products = self.filter_products("pearls", "", "", "", "", "", "")
        if sort == "strain-count":
            compare_products = memcache.get("compare_products:sort:strain_count")
            if not compare_products:
                compare_products = ProductDB.query().order(-ProductDB.strain_count).fetch(5)
                memcache.set("compare_products:sort:strain_count",
                             compare_products,
                             604800) #sets memcache expiration to one week
        if sort == "cfu":
            compare_products = memcache.get("compare_products:sort:cfu")
            if not compare_products:
                compare_products = ProductDB.query().order(-ProductDB.cfu).fetch(5)
                memcache.set("compare_products:sort:cfu",
                             compare_products,
                             604800) #sets memcache expiration to one week
        if len(compare_products) > 0:
            product1 = compare_products[0]
        else:
            product1 = []
        if len(compare_products) > 1:
            product2 = compare_products[1]
        else:
            product2 = []
        if len(compare_products) > 2:
            product3 = compare_products[2]
        else:
            product3 = []
        if len(compare_products) > 3:
            product4 = compare_products[3]
        else:
            product4 = []
        if len(compare_products) > 4:
            product5 = compare_products[4]
        else:
            product5 = []
        self.render("compare.html",
                    pagetitle="Probiotic Well | Compare",
                    products=products,
                    product1=product1,
                    product2=product2,
                    product3=product3,
                    product4=product4,
                    product5=product5,
                    sort=sort,
                    probiotic_keys=probiotic_keys)

    def post(self):
        sort = self.request.get('compare-sort-dropdown')
        probiotic1 = self.request.get('probiotic1')
        probiotic2 = self.request.get('probiotic2')
        probiotic3 = self.request.get('probiotic3')
        probiotic4 = self.request.get('probiotic4')
        probiotic5 = self.request.get('probiotic5')

        if sort:
            self.redirect("/compare?" + "sort=" + sort)
            return
        else:
            url_parameters = self.make_url_parameters(["p1", probiotic1], ["p2", probiotic2],
                                                      ["p3", probiotic3], ["p4", probiotic4],
                                                      ["p5", probiotic5])
            self.redirect("/compare?" + url_parameters)
