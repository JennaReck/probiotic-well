from Handler import *

class ArticleUpload(Handler):
    def get(self):
        if self.user_check():
            upload_url = blobstore.create_upload_url('/article-upload-handler')
            self.render("article-upload.html",
                        pagetitle="Article Upload",
                        upload_url=upload_url)
        else:
            self.redirect("/back-login")


class ArticleUploadHandler (blobstore_handlers.BlobstoreUploadHandler, Handler):    
    def post(self):
        if self.user_check():
            title = self.no_trailing_spaces(self.request.get('title'))
            category = self.request.get('category')
            image = self.get_uploads('image')
            thumbnail_image = self.get_uploads('thumbnail-image')
            image_alt = self.request.get('alt')
            body = self.request.get('body')
            
            image_blob_info = image[0]
            thumbnail_blob_info = thumbnail_image[0]

            image_url = images.get_serving_url(image_blob_info)
            thumbnail_image_url = images.get_serving_url(thumbnail_blob_info)
            blob_keys = [image_blob_info.key(),
                         thumbnail_blob_info.key()]

            articledata = ArticleDB(title=title,
                                    category=category,
                                    image=image_url,
                                    thumbnail_image=thumbnail_image_url,
                                    image_alt=image_alt,
                                    body=body,
                                    blob_keys=blob_keys)
            
            article_id = articledata.put().id()
            self.update_article_count(category)
            url_name = self.safe_url_name(title)
            link = "/article/" + str(article_id) + "/" + url_name
            articledata.link = link
            articledata.put()

            #updating article caches
            self.update_caches(articledata, "article")
            
            self.redirect(link)
            
        else:
            self.redirect("/back-login")
