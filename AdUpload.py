from Handler import *

class AdUpload(Handler):
    def get(self):
        if self.user_check():
            upload_url = blobstore.create_upload_url('/ad-upload-handler')
            self.render("ad-upload.html",
                        pagetitle="Ad Upload",
                        upload_url=upload_url)
        else:
            self.redirect("/back-login")

class AdUploadHandler (blobstore_handlers.BlobstoreUploadHandler, Handler):    
    def post(self):
        if self.user_check():
            ad_type = self.request.get('ad-type')
            image = self.get_uploads('image')
            title_or_name = self.request.get('title-or-name')
            link_or_buy_link = self.request.get('link-or-buy-link')
            price = self.request.get('price')
            
            image_blob_info = image[0]

            image_url = images.get_serving_url(image_blob_info)

            addata = AdDB(ad_type=ad_type,
                          image=image_url,
                          title_or_name=title_or_name,
                          link_or_buy_link=link_or_buy_link,
                          price=price,
                          blob_key=image_blob_info.key())
            addata.put()

            #updating ad caches
            self.update_caches(addata, "ad")
            
            self.redirect("/ad-settings")
        else:
            self.redirect("/back-login")

class AdSettings(Handler):
    def get(self):
        if self.user_check():
            article_ads = self.get_ads("article")
            product_ads = self.get_ads("product")
            success = self.request.get("success")
            
            self.render("ad-settings.html",
                        pagetitle="Ad Settings",
                        article_ads=article_ads,
                        product_ads=product_ads,
                        success=success)
        else:
            self.redirect("/back-login")

    def post(self):
        if self.user_check():
            page = self.request.get('page')
            ad_settings = self.request.get('ad-style').split("-")
            settingsdata = AdSettingsDB.query(AdSettingsDB.page == page).get()
            if not settingsdata:
                settingsdata = AdSettingsDB(page=page,
                                            ad_settings=ad_settings)
            else:
                settingsdata.ad_settings = ad_settings
            settingsdata.put()

            #updating ad settings cache
            memcache.set("ad_settings:" + page, settingsdata)
            
            self.redirect("ad-settings?success=yes")
            
        else:
            self.redirect("/back-login")
        
