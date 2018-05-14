from Handler import *

class DisclaimerPage(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        ads = self.chose_ads("disclaimer")
        self.render("disclaimer.html",
                    pagetitle="Probiotic Well | Disclaimer",
                    ads=ads)
