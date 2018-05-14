from Handler import *

class ReviewPage(Handler):
    def get(self, product_id, url):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        review = self.get_content(product_id[1:], "review")
        if review:
            if url[1:] != self.safe_url_name(review.product.name):
                self.redirect(review.link)
                return
            else:
                pagetitle = "Review of " + review.product.name
                related_reviews = self.get_related_reviews(review)
                review_count = self.get_review_count()
                ads = self.chose_ads("review")
                self.render("review.html",
                            pagetitle=pagetitle,
                            ads=ads,
                            review_count=review_count,
                            review=review,
                            related_reviews=related_reviews)
        else:
            self.redirect("/404")
        
