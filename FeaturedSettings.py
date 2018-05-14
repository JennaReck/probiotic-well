from Handler import *

class FeaturedSettings(Handler):
    def get(self):
        if self.user_check():
            probiotics = self.sort_products("a-to-z")
            articles = self.get_articles_by_date()
            reviews = self.get_reviews_by_date()
            success = self.request.get("success")
            
            self.render("featured-settings.html",
                        pagetitle="Featured Settings",
                        probiotics=probiotics,
                        articles=articles,
                        reviews=reviews,
                        success=success)
        else:
            self.redirect("/back-login")

    def post(self):
        if self.user_check():
            probiotics = self.sort_products("a-to-z")
            articles = self.get_articles_by_date()
            reviews = self.get_reviews_by_date()

            featured_article = self.request.get("featured")
            side1_article = self.request.get("side1")
            side2_article = self.request.get("side2")
            side3_article = self.request.get("side3")

            featured1_review = self.request.get("featured1")
            featured2_review = self.request.get("featured2")
            featured3_review = self.request.get("featured3")
            
            featured_probiotic_list = []
            featured_review_list = []
            for probiotic in probiotics:
                featured_probiotic_list.append([probiotic.key.id(), self.request.get(str(probiotic.key.id()))])
            for review in reviews:
                featured_review_list.append([review.product_id, self.request.get(str(review.product_id))])

            for probiotic in featured_probiotic_list:
                product = self.get_content(probiotic[0], "product")
                if probiotic[1] == "y" and product.slider_featured == False:
                    product.slider_featured = True
                    product.put()
                elif probiotic[1] == "" and product.slider_featured == True:
                    product.slider_featured = False
                    product.put()

            for review in featured_review_list:
                current_review = self.get_content(review[0], "review")
                if review[1] == "y" and current_review.slider_featured == False:
                    current_review.slider_featured = True
                    current_review.put()
                elif review[1] == "" and current_review.slider_featured == True:
                    current_review.slider_featured = False
                    current_review.put()

            current_featured_article = ArticleDB.query(ArticleDB.featured == "F").get()
            current_side1_article = ArticleDB.query(ArticleDB.featured == "S1").get()
            current_side2_article = ArticleDB.query(ArticleDB.featured == "S2").get()
            current_side3_article = ArticleDB.query(ArticleDB.featured == "S3").get()

            self.check_and_replace_featured(featured_article, current_featured_article, "article", "F")
            self.check_and_replace_featured(side1_article, current_side1_article, "article", "S1")
            self.check_and_replace_featured(side2_article, current_side2_article, "article", "S2")
            self.check_and_replace_featured(side3_article, current_side3_article, "article", "S3")

            current_featured1_review = ReviewDB.query(ReviewDB.featured == "F1").get()
            current_featured2_review = ReviewDB.query(ReviewDB.featured == "F2").get()
            current_featured3_review = ReviewDB.query(ReviewDB.featured == "F3").get()

            self.check_and_replace_featured(featured1_review, current_featured1_review, "review", "F1")
            self.check_and_replace_featured(featured2_review, current_featured2_review, "review", "F2")
            self.check_and_replace_featured(featured3_review, current_featured3_review, "review", "F3")

            article_list_type = []
            for article in articles:
                article_list_type.append([article.key.id(), self.request.get(str(article.key.id()))])

            for article in article_list_type:
                current_article = self.get_content(article[0], "article")
                if article[1] != current_article.list_type:
                    current_article.list_type = article[1]
                    current_article.put()
                    
            time.sleep(5)
            #updating slider featured content cache and other content cache
            self.get_slider_featured_content("products", True)
            self.get_slider_featured_content("reviews", True)
            self.sort_products("a-to-z", True)
            articles = self.get_articles_by_date(True)
            reviews = self.get_reviews_by_date(True)
            
            #updating article list types ("basic" and "shopping") cache
            basic_list = ArticleDB.query(ArticleDB.list_type == "basic").fetch()
            memcache.set("article_list:basic", basic_list)
            
            shopping_list = ArticleDB.query(ArticleDB.list_type == "shopping").fetch()
            memcache.set("article_list:shopping", shopping_list)

            self.redirect("/featured-settings?success=yes")
            
        else:
            self.redirect("/back-login")
