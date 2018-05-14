from Handler import *

class ResourcesPage(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        ads = self.chose_ads("resources")
        articles = self.get_resources("article")
        studies = self.get_resources("study")
        books = self.get_resources("book")
        blogs = self.get_resources("blog")
        websites = self.get_resources("website")
        
        self.render("resources.html",
                    pagetitle="Probiotic Well | Resources",
                    ads=ads,
                    articles=articles,
                    studies=studies,
                    books=books,
                    blogs=blogs,
                    websites=websites)
