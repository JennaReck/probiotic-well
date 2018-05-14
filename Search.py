from Handler import *

class Search(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        ads = self.chose_ads("search")
        q = self.request.get("q")
        if not q:
            pagetitle = "Probiotic Well | Search"
        else:
            pagetitle = "Probiotic Well | " + q[:40].rsplit(" ", 1)[0]
        
        self.render("search.html",
                    pagetitle=pagetitle,
                    ads=ads)

    def post(self):
        ads = self.chose_ads("search")
        q = self.request.get("q")
        self.redirect("/search?q=" + q)
