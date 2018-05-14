from Handler import *

class Reviews(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        category = self.request.get('category')
        p = self.request.get('p')
        if category:
            if category in ["price", "popular", "strains-cfu",
                            "pearls", "chewable-liquid", "kids"]:
                url_parameters = "?category=" + category
                category = {"price":"best-for-price", "popular":"most-popular",
                            "strains-cfu":"most-strains-and-highest-cfu",
                            "pearls":"pearls", "chewable-liquid":"chewable-and-liquid",
                            "kids":"for-kids"}[category] #changes url category slug to proper category for searching
                reviews = memcache.get("reviews:" + category)
                if not reviews:
                    reviews = ReviewDB.query(ReviewDB.categories == category).fetch()
                    memcache.set("reviews:" + category, reviews)
            else:
                self.redirect("/reviews") #checks if category is valid, redirects if not
                return
        else:
            url_parameters = "" #no url parameters needed if no category is selected
            reviews = self.get_reviews_by_date()
        review_count = self.get_review_count()
        featured_review1 = [] #featured stuff is set to empty initially
        featured_review2 = [] #because it's not needed unless on first page
        featured_review3 = []
        ads = self.chose_ads("reviews")
        if not p and not category:
            pagination = self.make_pagination_by_date(p, "/reviews", url_parameters,
                                                      reviews, "reviews", True, 5)
            reviews = self.next_content(p, reviews, 5, True) #uses offset
            featured_review1 = self.get_featured_content("review", "F1")
            featured_review2 = self.get_featured_content("review", "F2")
            featured_review3 = self.get_featured_content("review", "F3")
        elif category:
            pagination = self.make_pagination_by_date(p, "/reviews", url_parameters,
                                                      reviews, "reviews", False, 5)
            reviews = self.next_content(p, reviews, 5, False) #doesn't use offset
        else:
            pagination = self.make_pagination_by_date(p, "/reviews", url_parameters,
                                                      reviews, "reviews", True, 5)
            reviews = self.next_content(p, reviews, 5, True) #uses offset
        if not pagination or not reviews:
            self.redirect("/404") #pagination and next_content return False if p is
            return                                             #not a proper integer or too high, redirect if so
        self.render("reviews.html",
                    pagetitle="Probiotic Well | Reviews",
                    review_count=review_count,
                    ads=ads,
                    featured_review1=featured_review1,
                    featured_review2=featured_review2,
                    featured_review3=featured_review3,
                    reviews=reviews,
                    p=p,
                    category=category,
                    pagination=pagination)
