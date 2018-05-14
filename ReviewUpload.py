from Handler import *

class ReviewUpload(Handler):
    def get(self):
        if self.user_check():
            self.render("review-upload.html",
                        pagetitle="Review Upload")
        else:
            self.redirect("/back-login")

    def post(self):
        if self.user_check():
            product_id = int(self.request.get("product-id"))
            rating = self.request.get("rating")
            categories = self.request.get_all("categories")
            body = self.request.get("body")

            product = self.get_content(product_id, "product")
            name = self.safe_url_name(product.name)
            link = "/review/" + str(product_id) + "/" + name
            reviewdata = ReviewDB(product_id=product_id,
                                  rating=rating,
                                  categories=categories,
                                  body=body,
                                  link=link,
                                  product=product)
            reviewdata.put()
            self.update_review_count(categories)
            product.review_link = link
            product.put()

            #updating review caches
            self.update_caches(reviewdata, "review")
            
            self.redirect(link)
            
        else:
            self.redirect("/back-login")
