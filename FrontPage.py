from Handler import *

class FrontPage(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
        ads = self.chose_ads("front")
        featured_article = self.get_featured_content("article", "F")
        if not featured_article:
            featured_article = ArticleDB.query().order(ArticleDB.date).get()
        products = self.get_slider_featured_content("products")
        if not products:
            products = ProductDB.query().order(ProductDB.ranking).fetch(15)
        reviews = self.get_slider_featured_content("reviews")
        if not reviews:
            reviews = ReviewDB.query().order(ReviewDB.date).fetch(15)
        
        self.render("front.html",
                    pagetitle="Probiotic Well",
                    ads=ads,
                    featured_article=featured_article,
                    products=products,
                    reviews=reviews)
