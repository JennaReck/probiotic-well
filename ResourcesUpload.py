from Handler import *

class ResourcesUpload(Handler):
    def get(self):
        if self.user_check():
            success = self.request.get('success')
            self.render("resources-upload.html",
                        pagetitle="Resources Upload",
                        success=success)
        else:
            self.redirect("/back-login")

    def post(self):
        if self.user_check():
            resource_type = self.request.get('resource-type')
            link = self.request.get('link')
            title = self.request.get('title')

            resourcedata = ResourcesDB(resource_type=resource_type,
                                       link=link,
                                       title=title)
            resourcedata.put()

            #updating resource caches
            self.update_caches(resourcedata, "resource")
            
            self.redirect("/resources-upload?success=yes")
        else:
            self.redirect("/back-login")
