from Handler import *

class DeletePanel(Handler):
    def get(self):
        if self.user_check():
            products = self.sort_products("a-to-z")
            articles = self.get_articles_by_date()
            reviews = self.get_reviews_by_date()
            resources = self.get_all_resources()
            ads = self.get_all_ads()

            success = self.request.get("success")
            content_type = self.request.get("content-type")
            content_id = self.request.get("content")
            content = []    #initially set to empty list in case no
                            #content is selected for viewing

            if content_type and content_id:
                try:
                    int(content_id)
                except:
                    self.redirect("/delete-panel?success=n")
                    return
                content_id = int(content_id)
                if content_type == "product":
                    content = ProductDB.get_by_id(content_id)
                if content_type == "article":
                    content = ArticleDB.get_by_id(content_id)
                if content_type == "review":
                    content = ReviewDB.get_by_id(content_id)
                if content_type == "resource":
                    content = ResourcesDB.get_by_id(content_id)
                if content_type == "ad":
                    content = AdDB.get_by_id(content_id)
                if not content:
                    self.redirect("/delete-panel?success=n")
                    return

            self.render("delete-panel.html",
                        pagetitle="Delete Panel",
                        success=success,
                        products=products,
                        articles=articles,
                        reviews=reviews,
                        resources=resources,
                        ads=ads,
                        content_type=content_type,
                        content=content)
            
        else:
            self.redirect("/back-login")

    def post(self):
        if self.user_check():
            view_product = self.request.get("products")
            view_article = self.request.get("articles")
            view_review = self.request.get("reviews")
            view_resource = self.request.get("resources")
            view_ad = self.request.get("ads")

            content_to_delete_id = self.request.get("content-to-delete")
            content_to_delete_type = self.request.get("content-to-delete-type")
            if content_to_delete_id:
                try:
                    int(content_to_delete_id)
                except:
                    self.redirect("/delete-panel?success=n")
                    return
                content_to_delete_id = int(content_to_delete_id)

                if content_to_delete_type == "product":
                    content = ProductDB.get_by_id(content_to_delete_id)
                    blob_keys = content.blob_keys

                    #deleting brand from BrandsDB if ProductDB doesn't contain any others by that brand
                    self.add_brand(content.brand_name, True)
                    
                    #subtracting delivery method from DeliveryMethodsDB count or deleting it if count is only 1
                    self.add_delivery_method(content.delivery_method, True)

                    memcache.delete("related_products:" + str(content.key.id()))

                if content_to_delete_type == "article":
                    content = ArticleDB.get_by_id(content_to_delete_id)
                    blob_keys = content.blob_keys
                    
                    #subtracting article from ArticleCategories database
                    self.update_article_count(content.category, True)
                    
                    article_counters = ArticleCounters.query(ArticleCounters.article_id ==
                                                             content.key.id()).fetch()
                    counter_keys = []
                    for counter in article_counters:
                        counter_keys.append(counter.key)
                    if counter_keys:
                        #deleting article counters for the specific article
                        ndb.delete_multi(counter_keys)
                    memcache.delete("article_pageviews:" + str(content.key.id()))
                    
                if content_to_delete_type == "review":
                    content = ReviewDB.get_by_id(content_to_delete_id)
                    all_images = ReviewImageDB.query(ReviewImageDB.product_id == content.product_id).fetch()
                    blob_keys = []
                    image_keys = []
                    for image in all_images:
                        blob_keys.append(image.blob_key)
                        image_keys.append(image.key)
                    if image_keys:
                        #deleting ReviewImageDB content related to review
                        ndb.delete_multi(image_keys)
                    memcache.delete("review:" + str(content.product_id))
                    memcache.delete("related_reviews:" + str(content.product_id))
                        
                    #deleting review link from product
                    product = ProductDB.get_by_id(content.product_id)
                    product.review_link = ""
                    product.put()

                    #subtracting from ReviewCategories database and updating categories cache
                    self.update_review_count(content.categories, True)
                    
                if content_to_delete_type == "resource":
                    content = ResourcesDB.get_by_id(content_to_delete_id)
                    blob_keys = []
                    
                if content_to_delete_type == "ad":
                    content = AdDB.get_by_id(content_to_delete_id)
                    blob_keys = content.blob_key

                #deleting ndb content and blobstore content
                content.key.delete()
                if blob_keys:
                    if isinstance(blob_keys, list):
                        for key in blob_keys:
                            blobstore.delete(key)
                            images.delete_serving_url(key)
                    else:
                        blobstore.delete(blob_keys)
                        images.delete_serving_url(blob_keys)

                #updating caches to remove deleted content
                self.update_caches(content, content_to_delete_type, True)
                if content_to_delete_type in ["product", "article", "review"]: 
                    self.check_and_update_featured_caches(content, content_to_delete_type)
                if content_to_delete_type == "article":
                    self.get_article_lists(True)

                self.redirect("/delete-panel?success=y")
                return
            
            view_list = [[view_product, "product"],
                         [view_article, "article"],
                         [view_review, "review"],
                         [view_resource, "resource"],
                         [view_ad, "ad"]]
            for item in view_list:
                if item[0]:
                    self.redirect("/delete-panel?content-type=" + item[1] +
                                  "&content=" + item[0])
                    return
                
        else:
            self.redirect("/back-login")
