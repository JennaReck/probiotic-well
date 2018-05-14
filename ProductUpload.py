from Handler import *

class ProductUpload(Handler):
    def get(self):
        if self.user_check():
            upload_url = blobstore.create_upload_url('/product-upload-handler')
            self.render("product-upload.html",
                        pagetitle="Product Upload",
                        upload_url=upload_url)
        else:
            self.redirect("/back-login")

class ProductUploadHandler (blobstore_handlers.BlobstoreUploadHandler, Handler):    
    def post(self):
        if self.user_check():
            name = self.no_trailing_spaces(self.request.get('name'))
            brand_name = self.request.get('brand-name')
            large_image = self.get_uploads('large-image')
            slider_image = self.get_uploads('slider-image')
            thumbnail_image = self.get_uploads('thumbnail-image')
            delivery_method = self.request.get('delivery-method')
            strain_count = int(self.request.get('strain-count'))
            strains = self.request.get('strains')
            cfu = int(self.request.get('cfu'))
            cfu_quantity = self.request.get('cfu-quantity')
            refrigeration_required = self.to_bool(self.request.get('refrigeration-required'))
            stomach_acid_protection = self.to_bool(self.request.get('stomach-acid-protection'))
            vegetarian_or_vegan = self.request.get('vegetarian-or-vegan')
            recommended_for = self.request.get('recommended-for')
            price = float(self.request.get('price'))
            servings = int(self.request.get('servings'))
            serving_measure = self.request.get('serving-measure')
            price_per_serving = self.request.get('price-per-serving')
            review_link = self.request.get('review-link')
            buy_link = self.request.get('buy-link')
            seller = self.request.get('seller')
            seller_rating = float(self.request.get('seller-rating'))
            description = self.request.get('description')
            ingredients_and_allergy_info = self.request.get('ingredients-and-allergy-info')

            ranking = self.calculate_rank(float(price_per_serving), strain_count,
                                          cfu, delivery_method, refrigeration_required,
                                          stomach_acid_protection, seller_rating)
            
            large_blob_info = large_image[0]
            slider_blob_info = slider_image[0]
            thumbnail_blob_info = thumbnail_image[0]
     
            large_image_url = images.get_serving_url(large_blob_info)
            slider_image_url = images.get_serving_url(slider_blob_info)
            thumbnail_image_url = images.get_serving_url(thumbnail_blob_info)
            blob_keys = [large_blob_info.key(),
                         slider_blob_info.key(),
                         thumbnail_blob_info.key()]

            productdata = ProductDB(name=name,
                                    brand_name=brand_name,
                                    large_image=large_image_url,
                                    slider_image=slider_image_url,
                                    thumbnail_image=thumbnail_image_url,
                                    delivery_method=delivery_method,
                                    strain_count=strain_count,
                                    strains=strains,
                                    cfu=cfu,
                                    cfu_quantity=cfu_quantity,
                                    refrigeration_required=refrigeration_required,
                                    stomach_acid_protection=stomach_acid_protection,
                                    vegetarian_or_vegan=vegetarian_or_vegan,
                                    recommended_for=recommended_for,
                                    price=price,
                                    servings=servings,
                                    serving_measure=serving_measure,
                                    price_per_serving=price_per_serving,
                                    review_link=review_link,
                                    buy_link=buy_link,
                                    seller=seller,
                                    ranking=ranking,
                                    description=description,
                                    ingredients_and_allergy_info=ingredients_and_allergy_info,
                                    blob_keys=blob_keys)
            
            product_id = productdata.put().id()
            self.add_brand(brand_name)
            self.add_delivery_method(delivery_method)
            
            url_name = self.safe_url_name(name)
            link = "/product/" + str(product_id) + "/" + url_name
            productdata.link = link
            productdata.put()
            
            #updating product caches
            self.update_caches(productdata, "product")
            
            self.redirect(link)
            
        else:
            self.redirect("/back-login")
