from Handler import *

class ArticlePage(Handler):
    def get(self, article_id, url):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        article = self.get_content(article_id[1:], "article")
        if article:
            if url[1:] != self.safe_url_name(article.title):
                self.redirect(article.link)
                return
            else:
                self.update_pageviews(article_id[1:])
                popular_list = self.get_popular_articles()[:5]
                basic_list, shopping_list = self.get_article_lists()
                article_count = self.get_article_count()
                related_articles = self.get_articles_by_category(article.category)[:5]
                self.render("article.html",
                            pagetitle=article.title,
                            article=article,
                            popular_list=popular_list,
                            basic_list=basic_list,
                            shopping_list=shopping_list,
                            article_count=article_count,
                            related_articles=related_articles)
        else:
            self.redirect("/404")
