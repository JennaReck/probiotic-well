from Handler import *

class Product(Handler):
    def get(self, product_id, url):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
        product = self.get_content(product_id[1:], "product")
        if product:
            if url[1:] != self.safe_url_name(product.name):
                self.redirect(product.link)
                return
            else:
                related_products = self.get_related_products(product)
                compare_link = self.make_compare_link(product)
                ads = self.chose_ads("product")
                self.render("product.html",
                            pagetitle=product.name,
                            product=product,
                            compare_link=compare_link,
                            related_products=related_products,
                            ads=ads)
        else:
            self.redirect("/404")
