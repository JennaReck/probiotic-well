from Handler import *

class ReviewImageUpload(Handler):
    def get(self):
        if self.user_check():
            upload_url = blobstore.create_upload_url('/review-image-upload-handler')
            self.render("review-image-upload.html",
                        pagetitle="Review Image Upload",
                        upload_url=upload_url)
        else:
            self.redirect("/back-login")


class ReviewImageUploadHandler(Handler, blobstore_handlers.BlobstoreUploadHandler):    
    def post(self):
        if self.user_check():
            uploaded_image = self.get_uploads('image')
            blob_info = uploaded_image[0]
            product_id = int(self.request.get('product-id'))
            imagedata = ReviewImageDB(product_id=product_id,
                                      image=images.get_serving_url(blob_info),
                                      blob_key=blob_info.key())
            imagedata.put()
            time.sleep(5)
            self.redirect("/review-images/" + str(product_id))
        else:
            self.redirect("/back-login")

class ReviewImagesDisplay(Handler):
    def get(self, resource):
        if self.user_check():
            images = self.get_review_images(int(resource[1:]))
            if images:
                self.render("review-image-display.html",
                            images=images,
                            product_id=resource[1:])
            else:
                error = "No images by that product ID here!"
                self.render("review-image-display.html",
                            product_id=resource[1:],
                            error=error)
        else:
            self.redirect("/back-login")
