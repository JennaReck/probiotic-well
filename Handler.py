import webapp2
import jinja2
import os
import urllib
import time
import random
import re
import hashlib
import hmac
import cgi
from operator import itemgetter
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import urlfetch

jinja_environment = jinja2.Environment(extensions=['jinja2.ext.autoescape'],autoescape=True,
                                       loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                        'templates')))
secret = "Ab2jsI4jElN"

class Handler(webapp2.RequestHandler):

    def write(self, *a, **na):
        self.response.out.write(*a, **na)
    
    def render_str(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)
    
    def render(self, template, **na):
        self.write(self.render_str(template, **na))

    def get_review_images(self, productid):
        return ReviewImageDB.query(ReviewImageDB.product_id == productid).fetch()

    def get_content(self, content_id, content_type):
        try:
            int(content_id)
        except:
            return False
        content_id = int(content_id)
        if content_type == "product":
            content = ProductDB.get_by_id(content_id)
        elif content_type == "article":
            content = ArticleDB.get_by_id(content_id)
        elif content_type == "review":
            content = memcache.get("review:" + str(content_id))
            if not content:
                content = ReviewDB.query(ReviewDB.product_id == content_id).get()
                if content:
                    memcache.set("review:" + str(content_id), content)
        else:
            return False
        return content

    def get_ads(self, adtype, update=False):
        if update == False:
            ads = memcache.get("ads_by_type:" + adtype)
        if update == True or not ads:
            ads = AdDB.query(AdDB.ad_type == adtype).fetch()
            memcache.set("ads_by_type:" + adtype, ads)
        return ads

    def get_all_ads(self, update=False):
        if update == False:
            ads = memcache.get("all_ads")
        if update == True or not ads:
            ads = AdDB.query().fetch()
            memcache.set("all_ads", ads)
        return ads

    def chose_ads(self, page, update=False):
        if update == False:
            ads = memcache.get("ads:" + page)
        if update == True or not ads:
            ad_list = []
            settings = memcache.get("ad_settings:" + page)
            if not settings:
                settings = AdSettingsDB.query(AdSettingsDB.page == page).get()
                memcache.set("ad_settings:" + page, settings)
            if settings == "none":
                return ad_list
            article_ads = self.get_ads("article")
            product_ads = self.get_ads("product")
            for setting in settings.ad_settings:
                while True:
                    if setting == "article":
                        ad = random.choice(article_ads)
                        if ad not in ad_list:
                            ad_list.append(ad)
                            break
                    else:
                        ad = random.choice(product_ads)
                        if ad not in ad_list:
                            ad_list.append(ad)
                            break
            ads = self.build_ads(ad_list)
            memcache.set("ads:" + page, ads, 3600) #ads for a page stay in cache for 1 hour
        return ads

    def build_ads(self, ad_list):
        ad_html = []
        current_html = ""
        for ad in ad_list:
            cached_ad = memcache.get("ad:" + str(ad.key.id()))
            if cached_ad:
                ad_html.append(cached_ad)
            else:
                if ad.ad_type == "article":
                    current_html += ('<a href="' + ad.link_or_buy_link + '"><img class="sidebar-img" src="' + ad.image + '" alt="' +
                                     ad.title_or_name + '" title="' + ad.title_or_name + '" /></a>')
                else:
                    current_html += ('<a href="' + ad.link_or_buy_link +
                                     '" class="product-and-heading-links"><div class="sidebar-product-container"><img src="' +
                                     ad.image + '" alt="' + ad.title_or_name +
                                     '" class="sidebar-ad-img" /><div class="sidebar-product-info">' +
                                     ad.title_or_name + '<br />$' + ad.price + '</div></div></a>')
                ad_html.append(current_html)
                memcache.set("ad:" + str(ad.key.id()), current_html)
                current_html = ""
        return ad_html

    def get_resources(self, resource_type, update=False):
        if update == False:
            resources = memcache.get("resources:" + resource_type)
        if update == True or not resources:
            resources = ResourcesDB.query(ResourcesDB.resource_type == resource_type).fetch()
            memcache.set("resources:" + resource_type, resources)
        return resources

    def get_all_resources(self, update=False):
        if update == False:
            resources = memcache.get("all_resources")
        if update == True or not resources:
            resources = ResourcesDB.query().fetch()
            memcache.set("all_resources", resources)
        return resources
                
    def to_bool(self, value):
        if value == "y":
            return True
        else:
            return False

    def safe_url_name(self, name):
	character_list = ["'", '"', ",", ".", ";", ":", "!", "(", ")", "[", "]",
                          "~", "`", ">", "<", "*", "#", "$", "^", "&", "=", "?"]
	name = name.replace(" ", "-")
	for character in character_list:
		if character in name:
			name = name.replace(character, "")
	return urllib.quote(name.lower())

    def no_trailing_spaces(self, name):
        while True:
            if name[-1] == " ":
                name = name[:-1]
            else:
                break
        return name

    def add_brand(self, brand, delete=False):
        query = BrandsDB.query(BrandsDB.name == brand).get()
        if not query and delete == False:
            branddata = BrandsDB(name=brand)
            branddata.put()
        if delete == True:
            same_brand_products = ProductDB.query(ProductDB.brand_name == brand).fetch()
            if len(same_brand_products) == 1:
                brand_db = BrandsDB.query(BrandsDB.name == brand).get()
                if brand_db:
                    brand_db.key.delete()
        self.get_all_brands(True)

    def add_delivery_method(self, method, delete=False):
        query = DeliveryMethodsDB.query(DeliveryMethodsDB.delivery_method == method).get()
        if not query and delete == False:
            methoddata = DeliveryMethodsDB(delivery_method=method)
            methoddata.put()
        elif query and delete == False:
            query.count += 1
            query.put()
        elif query and delete == True:
            if query.count > 1:
                query.count -= 1
                query.put()
            else:
                query.key.delete()
        self.get_all_delivery_methods(True)

    def get_all_delivery_methods(self, update=False):
        delivery_methods = memcache.get("all_delivery_methods")
        if not delivery_methods or update == True:
            delivery_methods = DeliveryMethodsDB.query().fetch()
            memcache.set("all_delivery_methods", delivery_methods)
        return delivery_methods

    def get_all_brands(self, update=False):
        all_brands = memcache.get("all_brands")
        if not all_brands or update == True:
            all_brands = BrandsDB.query().order(BrandsDB.name).fetch()
            memcache.set("all_brands", all_brands)
        return all_brands

    def get_related_products(self, product, delete=False):
        if delete == True:
            memcache.delete("related_products:" + str(product.key.id()))
            return
        related_products = memcache.get("related_products:" + str(product.key.id()))
        if not related_products:
            related_products = ProductDB.query(ProductDB.delivery_method == product.delivery_method
                                                or ProductDB.brand_name == product.brand_name).fetch(15)
            memcache.set("related_products:" + str(product.key.id()),
                         related_products,
                         604800) #sets memcache expiration to one week
        return related_products

    def sort_products(self, sort, update=False):
        if update == False:
                sorted_products = memcache.get("sorted_products:" + sort)
                if sorted_products:
                    return sorted_products
        if sort == "a-to-z":
            sorted_products = ProductDB.query().order(ProductDB.name).fetch()
        if sort == "cheapest":
            sorted_products = ProductDB.query().order(ProductDB.price).fetch()
        if sort == "popular":
            sorted_products = ProductDB.query().order(-ProductDB.ranking).fetch()
        if not sort:
            sorted_products = ProductDB.query().order(-ProductDB.ranking).fetch()
        memcache.set("sorted_products:" + sort, sorted_products)
        return sorted_products

    def filter_products(self, delivery_method, strain_count, cfu, refrigeration_required,
                        brand_name, recommended_for, price, update=False):
        if delivery_method:
            if update == False:
                query1 = memcache.get("filter_products:delivery_method:" + delivery_method)
            if update == True or not query1:
                query1 = ProductDB.query(ProductDB.delivery_method == delivery_method).order(-ProductDB.ranking).fetch()
                memcache.set("filter_products:delivery_method:" + delivery_method, query1)
        else:
            query1 = False #Setting an unused query to false prevents it from counting the same as 'no products returned'.
        
        if strain_count:
            if update == False:
                query2 = memcache.get("filter_products:strain_count:" + strain_count)
            if update == True or not query2:
                if strain_count == "1-to-2":
                    query2 = ProductDB.query(ndb.OR(ProductDB.strain_count == 1,
                                                    ProductDB.strain_count == 2)).order(-ProductDB.ranking).fetch()
                if strain_count == "3-to-5":
                    query2 = ProductDB.query(ndb.OR(ProductDB.strain_count == 3,
                                                    ProductDB.strain_count == 4,
                                                    ProductDB.strain_count == 5)).order(-ProductDB.ranking).fetch()
                if strain_count == "6":
                    query2 = ProductDB.query(ProductDB.strain_count > 5).fetch()
                memcache.set("filter_products:strain_count:" + strain_count, query2)
        else:
            query2 = False
       
        if cfu:
            if update == False:
                query3 = memcache.get("filter_products:cfu:" + cfu)
            if update == True or not query3:
                if cfu == "1-to-4":
                    query3 = ProductDB.query(ndb.OR(ProductDB.cfu == 1,
                                                    ProductDB.cfu == 2,
                                                    ProductDB.cfu == 3,
                                                    ProductDB.cfu == 4)).order(-ProductDB.ranking).fetch()
                if cfu == "5-to-10":
                    query3 = ProductDB.query(ndb.OR(ProductDB.cfu == 5,
                                                    ProductDB.cfu == 6,
                                                    ProductDB.cfu == 7,
                                                    ProductDB.cfu == 8,
                                                    ProductDB.cfu == 9,
                                                    ProductDB.cfu == 10)).order(-ProductDB.ranking).fetch()
                if cfu == "11":
                    query3 = ProductDB.query(ProductDB.cfu > 10).fetch()
                memcache.set("filter_products:cfu:" + cfu, query3)
        else:
            query3 = False
            
        if refrigeration_required:
            if update == False:
                query4 = memcache.get("filter_products:refrigeration_required:" + refrigeration_required)
            if update == True or not query4:
                if refrigeration_required == "y":
                    query4 = ProductDB.query(ProductDB.refrigeration_required == True).order(-ProductDB.ranking).fetch()
                else:
                    query4 = ProductDB.query(ProductDB.refrigeration_required == False).order(-ProductDB.ranking).fetch()
                memcache.set("filter_products:refrigeration_required:" + refrigeration_required, query4)
        else:
            query4 = False

        if brand_name:
            if update == False:
                query5 = memcache.get("filter_products:brand_name:" + brand_name)
            if update == True or not query5:
                query5 = ProductDB.query(ProductDB.brand_name == brand_name).order(-ProductDB.ranking).fetch()
                memcache.set("filter_products:brand_name:" + brand_name, query5)
        else: query5 = False
            
        if recommended_for:
            if update == False:
                query6 = memcache.get("filter_products:recommended_for:" + recommended_for)
            if update == True or not query6:
                query6 = ProductDB.query(ProductDB.recommended_for == recommended_for).order(-ProductDB.ranking).fetch()
                memcache.set("filter_products:recommended_for:" + recommended_for, query6)
        else:
            query6 = False
            
        if price:
            if update == False:
                query7 = memcache.get("filter_products:price:" + price)
            if update == True or not query7:
                if price == "15":
                    query7 = ProductDB.query(ProductDB.price <= 15).fetch()
                if price == "16-20":
                    query7 = ProductDB.query(ProductDB.price > 15, ProductDB.price <= 20).fetch()
                if price == "21-30":
                    query7 = ProductDB.query(ProductDB.price > 20, ProductDB.price <= 30).fetch()
                if price == "31":
                    query7 = ProductDB.query(ProductDB.price > 30).fetch()
                memcache.set("filter_products:price:" + price, query7)
        else:
            query7 = False

        list_of_lists = []
        query_list = [query1, query2, query3, query4, query5, query6, query7]
        for query in query_list:
            if query != False:
                list_of_lists.append(query)
        product_list = list_of_lists[0]
        new_product_list = []
        for num in range(1, len(list_of_lists)):
            for product in product_list:
                if product in list_of_lists[num]:
                    new_product_list.append(product)
            product_list = new_product_list
            new_product_list = []
        return product_list

    def calculate_rank(self, price_per_serving, strain_count, cfu, delivery_method,
                       refrigeration_required, stomach_acid_protection, seller_rating):
        personal_rating = 0
        if price_per_serving <= 0.15:
            personal_rating += 10
        elif price_per_serving > 0.15 and price_per_serving <= 0.20:
            personal_rating += 9
        elif price_per_serving > 0.20 and price_per_serving <= 0.30:
            personal_rating += 8
        elif price_per_serving > 0.30 and price_per_serving <= 0.40:
            personal_rating += 7
        elif price_per_serving > 0.40 and price_per_serving <= 0.60:
            personal_rating += 6
        elif price_per_serving > 0.60 and price_per_serving <= 0.80:
            personal_rating += 5
        elif price_per_serving > 0.80:
            personal_rating += 4

        if strain_count == 1:
            personal_rating += 6
        elif strain_count == 2:
            personal_rating += 7
        elif strain_count == 3:
            personal_rating += 8
        elif strain_count == 4:
            personal_rating += 9
        elif strain_count >= 5:
            personal_rating += 10

        if cfu == 1:
            personal_rating += 6
        elif cfu == 2:
            personal_rating += 7
        elif cfu == 3:
            personal_rating += 8
        elif cfu == 4:
            personal_rating += 9
        elif cfu >= 5:
            personal_rating += 10

        if delivery_method == "pearls":
            personal_rating += 10
        elif delivery_method in ["capsules", "chewable tablets", "liquid"]:
            personal_rating += 8
        elif delivery_method == "powder":
            personal_rating += 7
        elif delivery_method == "pills":
            personal_rating += 6
        else:
            personal_rating += 5

        if refrigeration_required == True:
            personal_rating += 5
        else:
            personal_rating += 10

        if stomach_acid_protection == True:
            personal_rating += 10
        else:
            personal_rating += 5

        return ((seller_rating * 2) + (personal_rating/6.0)) / 2.0

    def make_url_parameters(self, *a):
        url_parameters = ""
        for parameter in a:
            if parameter[1]:
                if url_parameters != "":
                    url_parameters += "&"
                url_parameters += parameter[0] + "=" + parameter[1]
        return url_parameters

    def make_pagination(self, p, url_parameters, products, products_per_page):
	html = ""
        if not p:
            p = 1
        try:
	    int(p)
	except:
	    return False
	p = int(p)
        if len(products)%products_per_page != 0:
            all_pages = (len(products)/products_per_page) + 1
        else:
            all_pages = len(products)/products_per_page
        if all_pages < 1:
            all_pages = 1
	if p > all_pages:
            return False #checks if p is higher than all_pages, redirect to 404
	if not p or p == 1:
		html += "<div id='pagination'><span class='prev-next-unused'>prev</span> <span class='pagination-current'>1</span> "
		if all_pages > 1 and all_pages <= 5:
			for page_num in range(2, all_pages + 1):
				html += (" <a href='/brands?" + url_parameters + "&p=" + str(page_num) +
                                         "' class='pagination-noncurrent'>" + str(page_num) + "</a>")
				
			html += " <a href='/brands?" + url_parameters + "&p=2' class='prev-next-used'>next</a></div>"
		if all_pages == 1:
			html += " <span class='prev-next-unused'>next</span></div>"
		if all_pages > 5:
			for page_num in range(2, 6):
				html += (" <a href='/brands?" + url_parameters + "&p=" + str(page_num) +
                                         "' class='pagination-noncurrent'>" + str(page_num) + "</a>")
				
			html += (" <span class='pagination-ellipses'>...</span> <a href='/brands?" +
                                 url_parameters + "&p=2' class='prev-next-used'>next</a></div>")
	else:
		html += ("<div id='pagination'><a href='/brands?" + url_parameters +
                         "&p=" + str(p - 1) + "' class='prev-next-used'>prev</a>")
		if p <= 4:
			if all_pages <= 5:
				for page_num in range(1, all_pages + 1):
					if page_num == p:
						html += " <span class='pagination-current'>" + str(p) + "</span>"
					else:
						html += (" <a href='/brands?" + url_parameters + "&p=" + str(page_num) +
                                                         "' class='pagination-noncurrent'>" + str(page_num) + "</a>")
				if p == all_pages:
					html += " <span class='prev-next-unused'>next</span></div>"
				else:
					html += (" <a href='/brands?" + url_parameters + "&p=" + str(p + 1) +
                                                 "' class='prev-next-used'>next</a></div>")
			else:
				for page_num in range(1, 6):
					if page_num == p:
						html += " <span class='pagination-current'>" + str(p) + "</span>"
					else:
						html += (" <a href='/brands?" + url_parameters +
                                                         "&p=" + str(page_num) + "'>" + str(page_num) + "</a>")
						
				html += (" <span class='pagination-ellipses'>...</span> <a href='/brands?" +
                                         url_parameters + "&p=" + str(p + 1) +
                                         "' class='prev-next-used'>next</a></div>")
		else:
			html += (" <a href='/brands?" + url_parameters + "&p=" + str(p - 2) +
                                 "' class='pagination-noncurrent'>" + str(p - 2) + "</a>" +
                                 " <a href='/brands?" + url_parameters + "&p=" +
                                 str(p - 1) + "' class='pagination-noncurrent'>" +
                                 str(p - 1) + "</a>" + " <span class='pagination-current'>" +
                                 str(p) + "</span>")
			
			if all_pages > p + 2:
				for nextpage in [p + 1, p + 2]:
					html += (" <a href='/brands?" + url_parameters + "&p=" + str(nextpage) +
                                                 "' class='pagination-noncurrent'>" + str(nextpage) + "</a>")
				if p + 2 == all_pages:
					html += (" <a href='/brands?" + url_parameters + "&p=" + str(p + 1) +
                                                 "' class='prev-next-used'>next</a></div>")
				else:
					html += (" <span class='pagination-ellipses'>...</span> <a href='/brands?" +
                                                 url_parameters + "&p=" + str(p + 1) +
                                                 "' class='prev-next-used'>next</a></div>")
			if p + 1 == all_pages:
				html += (" <a href='/brands?" + url_parameters + "&p=" + str(p + 1) +
                                         "' class='pagination-current'>" + str(p + 1) +
                                         "</a> <a href='/brands?" + url_parameters + "&p=" + str(p + 1) +
                                         "' class='prev-next-used'>next</a></div>")
			if p == all_pages:
				html += " <span class='prev-next-unused'>next</span></div>"
	return html

    def next_content(self, p, content, items_per_page, offset):
	if not p or p == "1" or p == 1:
            if not offset:
		return content[:items_per_page]
	    else:
		return content[:3]
	
	try:
	    int(p)
	except:
	    return False
	p = int(p)
	
	if not offset:
	    if items_per_page * (p - 1) + 1 > len(content):
		return False
	    else:
		return content[(p - 1) * items_per_page:p * items_per_page]
	else:
	    if items_per_page * (p - 2) + 4 > len(content):
		return False
	    else:
		return content[(p - 1) * items_per_page - 2:p * items_per_page - 2]

    def update_pageviews(self, article_id):
	try:
	    int(article_id)
	except:
	    return
	article_id = int(article_id)
	shard = random.randint(1, 3)
	counter = ArticleCounters.query(ArticleCounters.article_id == article_id, ArticleCounters.shard == shard).get()
	if not counter:
	    counter = ArticleCounters(article_id=article_id,
                                      shard=shard,
                                      pageviews=0)
	counter.pageviews += 1
	counter.put()
	
    def get_pageviews(self, article_id):
        total = memcache.get("article_pageviews:" + article_id)
        if total:
            return total
	try:
	    int(article_id)
	except:
	    return
	article_id = int(article_id)
	total = 0
	counters = ArticleCounters.query(ArticleCounters.article_id == article_id).fetch()
	for counter in counters:
	    if counter:
                total += counter.pageviews
        memcache.set("article_pageviews:" + str(article_id), total, 86400)
	return total
	
    def get_popular_articles(self, update=False):
        if update == False:
            popular_articles = memcache.get("popular_articles")
	if update == True or not popular_articles:
            popular_articles = []
	    articles = ArticleDB.query().fetch()
	    combined_list = []
	    for article in articles:
	    	combined_list.append((article, self.get_pageviews(str(article.key.id()))))
            popular_sort = sorted(combined_list, key=itemgetter(1), reverse=True)
            for article in popular_sort:
                popular_articles.append(article[0]) #selecting only the article out of the combined article+pageview turple
            memcache.set("popular_articles", popular_articles, 604800)
	return popular_articles

    def update_article_count(self, category, delete=False):
        count = ArticleCategories.query().get()
        if not count:
            count = ArticleCategories(general=0,
                                      shopping=0)
        if category == "general":
            if delete == False:
                count.general += 1
            else:
                count.general -= 1
        if category == "shopping":
            if delete == False:
                count.shopping += 1
            else:
                count.shopping -= 1
        count.put()
        memcache.set("article_count", count)

    def get_articles_by_date(self, update=False):
        if update == False:
            article_list = memcache.get("articles:by_date")
        if update == True or not article_list:
            article_list = ArticleDB.query().order(-ArticleDB.date).fetch()
            memcache.set("articles:by_date", article_list)
        return article_list

    def get_articles_by_category(self, category, update=False):
        if update == False:
            article_list = memcache.get("articles:" + category)
        if update == True or not article_list:
            article_list = ArticleDB.query(ArticleDB.category == category).order(-ArticleDB.date).fetch()
            memcache.set("articles:" + category, article_list)
        return article_list

    def get_article_lists(self, update=False):
        if update == False:
            basic_list = memcache.get("article_list:basic")
            shopping_list = memcache.get("article_list:shopping")
            
        if update == True or not basic_list:
            basic_list = ArticleDB.query(ArticleDB.list_type == "basic").fetch()
            memcache.set("article_list:basic", basic_list)
        
        if update == True or not shopping_list:
            shopping_list = ArticleDB.query(ArticleDB.list_type == "shopping").fetch()
            memcache.set("article_list:shopping", shopping_list)
        return basic_list, shopping_list

    def get_article_count(self):
        article_count = memcache.get("article_count")
        if not article_count:
            article_count = ArticleCategories.query().get()
            memcache.set("article_count", article_count)
        return article_count

    def make_pagination_by_date(self, p, url, url_parameters,
                                content, content_type, offset, items_per_page):
	html = "<div id='pagination'>"
	unused_newest = ("<span class='pagination-unused pagination-newest-oldest' " +
                        "title='newest " + content_type + "'>newest</span> ")
	unused_earlier = ("<span class='pagination-unused pagination-earlier-later' " +
			"title='earlier " + content_type + "'>earlier</span> ")
	separator = "<span class='pagination-separator'>|</span> "
	unused_later = ("<span class='pagination-unused pagination-earlier-later' " +
			"title='later " + content_type + "'>later</a> ")
	unused_oldest = ("<span class='pagination-unused pagination-newest-oldest' " +
			"title='oldest " + content_type + "'>oldest</a>")
	if url_parameters:
            p_parameter = "&p="
        else:
            p_parameter = "?p="
	if not p:
            p = 1
	try:
            int(p)
	except:
	    return False    #p wasn't a number, check pagination before
                            #rendering html, redirect to 404 not found
	p = int(p)
	if offset:
            if len(content) > 3:
		if (len(content) - 3)%items_per_page != 0:
                    last_page = ((len(content) - 3)/5) + 2   #adds 2 pages because of subtracted
                                                            #offset page and to round up
		else:
		    last_page = ((len(content) - 3)/5) + 1    #adds 1 page because of subtracted
                                                            #offset page, no rounding needed
            else:
		last_page = False   #set to False because there isn't enough content
        else:                       #for a second page
            if len(content) > items_per_page:
                if len(content)%items_per_page != 0:
		    last_page = (len(content)/items_per_page) + 1
		else:
		    last_page = len(content)/items_per_page
            else:
		last_page = False
		
        if last_page == False:
            if p > 1:           #if p is greater than 1 and last_page is False,
		return False    #then the page count (p) is too high to be valid
        else:
            if p > last_page:   #if last_page isn't False (must be 2 or higher) and
		return False    #p is higher than it, then p is too high to be valid
	    
	if p == 1:
	    html += unused_newest + unused_earlier + separator 
	    if last_page != False:
		html += ("<a href='" + url + url_parameters + p_parameter +
                        "2' class='main-links pagination-earlier-later' " +
                        "title='later " + content_type + "'>later</a> <a href='" +
                        url + url_parameters + p_parameter + str(last_page) + 
                        "' class='main-links pagination-newest-oldest' " +
                        "title='oldest " + content_type + "'>oldest</a>")
	    else:
		html += unused_later + unused_oldest
			
	if p > 1:
	    html += ("<a href='" + url + url_parameters + 
                    "' class='main-links pagination-newest-oldest' " +
                    "title='newest " + content_type + "'>newest</a> <a href='" + 
                    url + url_parameters)
	    if p > 2:
		html += p_parameter + str(p - 1)
	    html += ("' class='main-links pagination-earlier-later' " +
		    "title='earlier " + content_type + "'>earlier</a> " + separator)
	    if p != last_page:
		html += ("<a href='" + url + url_parameters + p_parameter + str(p + 1) + 
                        "' class='main-links pagination-earlier-later' " +
                        "title='later " + content_type + "'>later</a> <a href='" +
                        url + url_parameters + p_parameter + str(last_page) +
                        "' class='main-links pagination-newest-oldest' " +
                        "title='oldest " + content_type + "'>oldest</a>")
	    else:
		html += unused_later + unused_oldest
	html += "</div>"
	return html

    def check_and_replace_featured(self, featured, current_featured, content_type, featured_type):
        if featured:
            if content_type == "article":
                if current_featured:
                    if int(featured) != current_featured.key.id():
                        new_featured_article = self.get_content(int(featured), "article")
                        new_featured_article.featured = featured_type
                        new_featured_article.put()
                        current_featured.featured = ""
                        current_featured.put()
                        memcache.set("featured_article:" + featured_type, new_featured_article)
                else:
                    new_featured_article = self.get_content(int(featured), "article")
                    new_featured_article.featured = featured_type
                    new_featured_article.put()
                    memcache.set("featured_article:" + featured_type, new_featured_article)
            if content_type == "review":
                if current_featured:
                    if int(featured) != current_featured.product_id:
                        new_featured_review = self.get_content(int(featured), "review")
                        new_featured_review.featured = featured_type
                        new_featured_review.put()
                        current_featured.featured = ""
                        current_featured.put()
                        memcache.set("featured_review:" + featured_type, new_featured_review)
                else:
                    new_featured_review = self.get_content(int(featured), "review")
                    new_featured_review.featured = featured_type
                    new_featured_review.put()
                    memcache.set("featured_review:" + featured_type, new_featured_review)

    def update_review_count(self, categories, delete=False):
        count = ReviewCategories.query().get()
        if not count:
            count = ReviewCategories()
        for category in categories:
            category = str(category)
            if category == "best-for-price":
                if delete == False:
                    count.price += 1
                else:
                    count.price -= 1
            if category == "most-popular":
                if delete == False:
                    count.popular += 1
                else:
                    count.popular -= 1
            if category == "most-strains-and-highest-cfu":
                if delete == False:
                    count.strains_and_cfu += 1
                else:
                    count.strains_and_cfu -= 1
            if category == "pearls":
                if delete == False:
                    count.pearls += 1
                else:
                    count.pearls -= 1
            if category == "chewable-and-liquid":
                if delete == False:
                    count.chewable_and_liquid += 1
                else:
                    count.chewable_and_liquid -= 1
            if category == "for-kids":
                if delete == False:
                    count.kids += 1
                else:
                    count.kids -= 1
        count.put()
        memcache.set("review_count", count)

    def get_reviews_by_date(self, update=False):
        if update == False:
            reviews = memcache.get("reviews:by_date")
        if update == True or not reviews:
            reviews = ReviewDB.query().order(-ReviewDB.date).fetch()
            memcache.set("reviews:by_date", reviews)
        return reviews

    def get_related_reviews(self, review):
        related_reviews = memcache.get("related_reviews:" +
                                       str(review.product_id))
        if not related_reviews:
            related_reviews = ReviewDB.query(ReviewDB.categories.IN(review.categories)).fetch()
            memcache.set("related_reviews:" +
                         str(review.product_id),
                         related_reviews,
                         604800) #sets memcache expiration to one week
        return related_reviews

    def get_review_count(self):
        review_count = memcache.get("review_count")
        if not review_count:
            review_count = ReviewCategories.query().get()
            memcache.set("review_count", review_count)
        return review_count

    def get_slider_featured_content(self, content_type, update=False):
        if update == False:
            content = memcache.get("slider_featured_" + content_type)
        if update == True or not content:
            if content_type == "products":
                content = ProductDB.query(ProductDB.slider_featured == True).fetch()
                memcache.set("slider_featured_products", content)
            if content_type == "reviews":
                content = ReviewDB.query(ReviewDB.slider_featured == True).fetch()
                memcache.set("slider_featured_reviews", content)
        return content

    def get_featured_content(self, content_type, featured_type, update=False):
        if update == False:
            content = memcache.get("featured_" + content_type + ":" + featured_type)
        if update == True or not content:
            if content_type == "article":
                content = ArticleDB.query(ArticleDB.featured == featured_type).get()
                memcache.set("featured_article:" + featured_type, content)
            if content_type == "review":
                content = ReviewDB.query(ReviewDB.featured == featured_type).get()
                memcache.set("featured_review:" + featured_type, content)
        return content

    def check_and_update_featured_caches(self, content, content_type):
        if content_type == "product":
            if content in self.get_slider_featured_content("products"):
                self.get_slider_featured_content("products", True)
		
        if content_type == "article":
            for featured_type in ["F", "S1", "S2", "S3"]:
                if content == self.get_featured_content("article", featured_type):
		    self.get_featured_content("article", featured_type, True)

        if content_type == "review":
            if content in self.get_slider_featured_content("reviews"):
                self.get_slider_featured_content("reviews", True)
            for featured_type in ["F1", "F2", "F3"]:
                if content == self.get_featured_content("review", featured_type):
                    self.get_featured_content("review", featured_type, True)

    def make_compare_link(self, probiotic):
        link = memcache.get("compare_link:" + str(probiotic.key.id()))
        if not link:
            link = "/compare?p1=" + str(probiotic.key.id())
            compare_products = []
            current_num = 2
            popular_products = self.sort_products("popular")[:5] #get one extra in case of duplicate
            for product in popular_products:
                if product.key.id() != probiotic.key.id(): #checking for duplicate of original probiotic
                    compare_products.append(product)
            compare_products = compare_products[:4] #make sure list is only 4 products long
            for product in compare_products:
                link += "&p" + str(current_num) + "=" + str(product.key.id())
                current_num += 1
            memcache.set("compare_link:" + str(probiotic.key.id()), link, 604800)
        return link

    def update_caches(self, content, content_type, delete=False):
        #time delay to make sure other database inserts or deletions are finished before updating
        time.sleep(5) 
        if content_type == "product":
            self.sort_products("a-to-z", True)
            self.sort_products("cheapest", True)
            self.sort_products("popular", True)
            self.sort_products("", True)
            
            #setting parameters for filter_products cache update
            if content.strain_count < 3:
                strain_count = "1-to-2"
            if content.strain_count > 2 and content.strain_count < 6:
                strain_count = "3-to-5"
            if content.strain_count > 5:
                strain_count = "6"
                
            if content.cfu < 5:
                cfu = "1-to-4"
            if content.cfu > 4 and content.cfu < 11:
                cfu = "5-to-10"
            if content.cfu > 10:
                cfu = "11"
                
            if content.refrigeration_required == True:
                refrigeration_required = "y"
            else:
                refrigeration_required = "n"
                
            if content.price <= 15:
                price = "15"
            if content.price > 15 and content.price <= 20:
                price = "16-20"
            if content.price > 20 and content.price <= 30:
                price = "21-30"
            if content.price > 30:
                price = "31"

            #updating filter_products cache    
            self.filter_products(content.delivery_method,
                                 strain_count,
                                 cfu,
                                 refrigeration_required,
                                 content.brand_name,
                                 content.recommended_for,
                                 price,
                                 True)
            if delete == False:
                self.get_related_products(content)
            else:
                self.get_related_products(content, True)
            
        if content_type == "article":
            self.get_popular_articles(True)
            self.get_articles_by_category(content.category, True)
            self.get_articles_by_date(True)

        if content_type == "review":
            for category in content.categories:
                reviews = ReviewDB.query(ReviewDB.categories == str(category)).fetch()
                memcache.set("reviews:" + str(category), reviews)
                
            self.get_reviews_by_date(True)

        if content_type == "resource":
            self.get_resources(content.resource_type, True)
            self.get_all_resources(True)

        if content_type == "ad":
            self.get_ads(content.ad_type, True)
            self.get_all_ads(True)
            if delete == False:
                self.build_ads([content])
            else:
                for page in ["front", "product", "reviews",
                             "review","about", "contact",
                             "resources", "disclaimer", "404"]:
                    self.chose_ads(page, True)
                memcache.delete("ad:" + str(content.key.id()))

    def make_cookie(self, admin):
	user_cookie = admin.key.id()
	hash_start = str(user_cookie)[:10]
	user_hash = hmac.new(secret, hash_start).hexdigest()
	return user_cookie, user_hash
	
    def make_salt(self):                                
            salt = ""
            for x in range(0,5):
                            salt += chr(random.randrange(97,123))
            return salt
            
    def make_pw_hash(self, name, pw, salt=None):
        if salt == None:
            salt = self.make_salt()
        h = hashlib.sha256(name + pw + salt).hexdigest()
        return '%s,%s' % (h, salt)
            
    def valid_password(self, username, password, h):
        salt = h.split(",")[1]
        return h == self.make_pw_hash(username, password, salt)

    def cookie_check(self, cookies):
	if len(cookies) > 5:
            cookie_user_id, cookie_user_hash = cookies.split("|")
            hash_start = str(cookie_user_id)[:10]
            cookie_username = AdminDB.get_by_id(int(cookie_user_id))
            if cookie_username == None:
                return False
            else:
                cookie_username = cookie_username.username
                if cookie_user_hash == hmac.new(secret, hash_start).hexdigest():
                    return True
                else:
                    return False
        else:
	    return False

    def user_check(self):
	cookies = self.request.cookies.get('username',"0|0")
	return self.cookie_check(cookies)

    def locked_out(self):
        lockout = memcache.get("lockout")
        if lockout:
            return True
        else:
            return False

    def update_failed_logins(self):
        failed_logins = memcache.get("failed_logins")
        if not failed_logins:
            #set memcache to expire in 1 hour, set current time in list.
            memcache.set("failed_logins", [1, time.time()], 3600)
        else:
            if failed_logins[0] + 1 >= 5:
                memcache.set("lockout", True, 3600) #set lockout to last 1 hour
            else:
                #set new expiration time based on time set minus
                #difference of time set and current time
                #(updating this makes sure it still expires in an hour)
                memcache.set("failed_logins",
                             [failed_logins[0] + 1,
                              failed_logins[1]],
                             3600 - (time.time() - failed_logins[1]))

    def truncate_and_strip_html(self, text, length):
        html_tags = ["<p>", "</p>", "<h3>", "</h3>"]
        for tag in html_tags:
            text = text.replace(tag, "")
        return text[:length].rsplit(" ", 1)[0] + "..."

    def sanitize_email_inputs(self, email="", email2="", subject="", message=""):
        sanitized_inputs = []
        if email:
            email = email.replace("\r", "")
            email = email.replace("\n", "")
            sanitized_inputs.append(email)

        if email2:
            email2 = email2.replace("\r", "")
            email2 = email2.replace("\n", "")
            sanitized_inputs.append(email2)
            
        if subject:
            subject = subject.replace("\r", " ")
            subject = subject.replace("\n", " ")
            subject = cgi.escape(subject, True)
            sanitized_inputs.append(subject)
            
        if message:
            message = message.replace("\r", " ")
            message = message.replace("\n", " ")
            message = cgi.escape(message, True)
            sanitized_inputs.append(message)

        return sanitized_inputs

    def domain_redirect(self, c_url):
        if c_url.find("probioticwell.appspot.com") != -1:
            #if domain is .appspot instead of custom domain, get redirect url
            start_pos = c_url.find("probioticwell.appspot.com")
            #separate out path from domain name, which is 25 characters long
            url_path = c_url[start_pos + 25:]
            if url_path == '':
                #if path is empty, set it to default homepage path
                url_path = "/"
            redirect_url = memcache.get("redirect:" + url_path)
            if not redirect_url:
                redirect_url = "http://www.probioticwell.com" + url_path
                if self.check_redirect_url(redirect_url) == False:
                    #set redirect_url to default homepage if invalid or broken
                    redirect_url = "http://www.probioticwell.com/"

                memcache.set("redirect:" + url_path, redirect_url)
            return redirect_url
            
        else:
            #domain is the correct custom domain, do nothing
            return False

    def check_redirect_url(self, redirect_url):
        try:
            response = urlfetch.fetch(redirect_url, allow_truncated=True, deadline=10)
            if response.status_code == 200:
                #checks if status code is success, allow redirect
                result = True
            else:
                #status code wasn't success, don't allow redirect to
                #current redirect url
                result = False
        except:
            #urlfetch raised an exception or it timed out
            result = False
            
        return result
                         
### TEMPLATE STUFF ###
def count_tags(text, tag):
    count = 0
    index = 0
    while True:
        index = text.find(tag, index)
        if index == -1:
            break
        else:
            index += 1
            count += 1
    return count

def close_p_tag(text):
    open_tag_count = count_tags(text, '<p>')
    close_tag_count = count_tags(text, '</p>')
    if open_tag_count != close_tag_count:
        return True
    else:
        return False
        
jinja_environment.tests['unclosed_p_tag'] = close_p_tag

def strip_p_tags(text):
    text = text.replace('<p>', '')
    text = text.replace('</p>', '')
    return text.lstrip()

jinja_environment.filters['strip_p_tags'] = strip_p_tags

def add_zero(num):
    str_num = str(num)
    pos = str_num.find(".")
    if pos != -1:
    	if len(str_num) - pos >= 3:
            return False
	else:
            return True
    return False

jinja_environment.tests['add_zero'] = add_zero

def review_category_filter(category):
    category_dict = {"best-for-price":"price",
                     "most-popular":"popular",
                     "most-strains-and-highest-cfu":"strains-cfu",
                     "pearls":"pearls",
                     "chewable-and-liquid":"chewable-liquid",
                     "for-kids":"kids"}
    return category_dict[category]

jinja_environment.filters['review_category_filter'] = review_category_filter

### DATABASES ###
class ProductDB(ndb.Model):
    name = ndb.StringProperty(required = True)
    link = ndb.StringProperty()
    brand_name = ndb.StringProperty(required = True)
    large_image =  ndb.StringProperty(required = True)
    slider_image = ndb.StringProperty(required = True)
    thumbnail_image = ndb.StringProperty(required = True)
    delivery_method = ndb.StringProperty(required = True)
    strain_count = ndb.IntegerProperty(required = True)
    strains = ndb.StringProperty(required = True)
    cfu = ndb.IntegerProperty(required = True)
    cfu_quantity = ndb.StringProperty(required = True)
    refrigeration_required = ndb.BooleanProperty(required = True)
    stomach_acid_protection = ndb.BooleanProperty(required = True)
    vegetarian_or_vegan = ndb.StringProperty(required = True)
    recommended_for = ndb.StringProperty(required = True)
    price = ndb.FloatProperty(required = True)
    servings = ndb.IntegerProperty(required = True)
    serving_measure = ndb.StringProperty(required = True)
    price_per_serving = ndb.StringProperty(required = True)
    review_link = ndb.StringProperty()
    buy_link = ndb.StringProperty(required = True)
    seller = ndb.StringProperty(required = True)
    ranking = ndb.FloatProperty(required = True)
    description = ndb.TextProperty(required = True)
    ingredients_and_allergy_info = ndb.TextProperty(required = True)
    slider_featured = ndb.BooleanProperty(default = False)
    blob_keys = ndb.BlobKeyProperty(repeated = True)

class ArticleDB(ndb.Model):
    title = ndb.StringProperty(required = True)
    category = ndb.StringProperty(required = True)
    image = ndb.StringProperty(required = True)
    thumbnail_image = ndb.StringProperty(required = True)
    image_alt = ndb.StringProperty(required = True)
    body = ndb.TextProperty(required = True)
    link = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add = True)
    featured = ndb.StringProperty(default = "")
    list_type = ndb.StringProperty(default = "")
    blob_keys = ndb.BlobKeyProperty(repeated = True)

class ReviewDB(ndb.Model):
    product_id = ndb.IntegerProperty(required = True)
    rating = ndb.StringProperty(required = True)
    categories = ndb.StringProperty(repeated = True)
    body = ndb.TextProperty(required = True)
    link = ndb.StringProperty(required = True)
    product = ndb.StructuredProperty(ProductDB, required = True)
    date = ndb.DateTimeProperty(auto_now_add = True)
    slider_featured = ndb.BooleanProperty(default = False)
    featured = ndb.StringProperty(default = "")

class AdDB(ndb.Model):
    ad_type = ndb.StringProperty(required = True)
    image = ndb.StringProperty (required = True)
    title_or_name = ndb.StringProperty(required = True)
    link_or_buy_link = ndb.StringProperty(required = True)
    price = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty(required = True)

class ReviewImageDB(ndb.Model):
    product_id = ndb.IntegerProperty(required = True)
    image = ndb.StringProperty(required = True)
    blob_key = ndb.BlobKeyProperty(required = True)

class AdSettingsDB(ndb.Model):
    page = ndb.StringProperty(required = True)
    ad_settings = ndb.StringProperty(repeated = True)

class ResourcesDB(ndb.Model):
    resource_type = ndb.StringProperty(required = True)
    link = ndb.StringProperty(required = True)
    title = ndb.StringProperty()
    
class DeliveryMethodsDB(ndb.Model):
    delivery_method = ndb.StringProperty(required = True)
    count = ndb.IntegerProperty(default = 1)

class BrandsDB(ndb.Model):
    name = ndb.StringProperty(required = True)

class ArticleCounters(ndb.Model):
    article_id = ndb.IntegerProperty(required = True)
    pageviews = ndb.IntegerProperty(default = 0)
    shard = ndb.IntegerProperty(required = True)

class ArticleCategories(ndb.Model):
    general = ndb.IntegerProperty(default = 0)
    shopping = ndb.IntegerProperty(default = 0)

class ReviewCategories(ndb.Model):
    price = ndb.IntegerProperty(default = 0)
    popular = ndb.IntegerProperty(default = 0)
    strains_and_cfu = ndb.IntegerProperty(default = 0)
    pearls = ndb.IntegerProperty(default = 0)
    chewable_and_liquid = ndb.IntegerProperty(default = 0)
    kids = ndb.IntegerProperty(default = 0)

class AdminDB(ndb.Model):
    username = ndb.StringProperty(required = True)
    password = ndb.StringProperty(required = True)
    
