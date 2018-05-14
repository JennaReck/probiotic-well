from Handler import *

class Error404(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        ads = self.chose_ads("404")
        self.render("404.html",
                    pagetitle="Probiotic Well | 404",
                    ads=ads)
