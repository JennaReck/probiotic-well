from Handler import *

class AboutPage(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        ads = self.chose_ads("about")
        self.render("about.html",
                    pagetitle="Probiotic Well | About",
                    ads=ads)
