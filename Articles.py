from Handler import *

class Articles(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        category = self.request.get('category')
        p = self.request.get('p')
        if category:
            if category == "general" or category == "shopping":
                url_parameters = "?category=" + category
                article_list = self.get_articles_by_category(category)
            else:
                self.redirect("/articles") #checks if category is valid, redirects if not
                return
        else:
            url_parameters = "" #no url parameters are needed if no category is selected
            article_list = self.get_articles_by_date()
        featured_article = [] #featured stuff is set to empty initially
        featured_side1 = []   #because it's not needed unless on first page
        featured_side2 = []   #and no category is selected
        featured_side3 = []
        general_category = []
        shopping_category = []
        popular_list = self.get_popular_articles()[:5]
        basic_list, shopping_list = self.get_article_lists()
        article_count = self.get_article_count()
        if not p and not category:
            pagination = self.make_pagination_by_date(p, "/articles", url_parameters,
                                                      article_list, "articles", True, 5)
            article_list = self.next_content(p, article_list, 5, True)  #uses offset

            featured_article = self.get_featured_content("article", "F")
            featured_side1 = self.get_featured_content("article", "S1")
            featured_side2 = self.get_featured_content("article", "S2")
            featured_side3 = self.get_featured_content("article", "S3")
            
            general_category = self.get_articles_by_category("general")[:5]
            shopping_category = self.get_articles_by_category("shopping")[:5]
            
        elif category:
            pagination = self.make_pagination_by_date(p, "/articles", url_parameters,
                                                      article_list, "articles", False, 5)
            article_list = self.next_content(p, article_list, 5, False) #doesn't use offset
        else:
            pagination = self.make_pagination_by_date(p, "/articles", url_parameters,
                                                      article_list, "articles", True, 5)
            article_list = self.next_content(p, article_list, 5, True) #uses offset            
        if not pagination or not article_list:
            self.redirect("/404")   #pagination and next_content return False if p is
            return                  #not a proper integer or too high, redirect if so
        self.render("articles.html",
                    pagetitle="Probiotic Well | Articles",
                    popular_list=popular_list,
                    basic_list=basic_list,
                    shopping_list=shopping_list,
                    article_count=article_count,
                    featured_article=featured_article,
                    featured_side1=featured_side1,
                    featured_side2=featured_side2,
                    featured_side3=featured_side3,
                    general_category=general_category,
                    shopping_category=shopping_category,
                    article_list=article_list,
                    p=p,
                    category=category,
                    pagination=pagination)
