#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from FrontPage import *
from Brands import *
from Product import *
from Compare import *
from Articles import *
from ArticlePage import *
from Reviews import *
from ReviewPage import *
from AboutPage import *
from ContactPage import *
from ResourcesPage import *
from DisclaimerPage import *
from Error404 import *
from ReviewImageUpload import *
from ProductUpload import *
from ReviewUpload import *
from ArticleUpload import *
from AdUpload import *
from ResourcesUpload import *
from FeaturedSettings import *
from Login import *
from DeletePanel import *
from GetRank import *
from EmailArticle import *
from EmailSubscribe import *
from Search import *

page_re = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
num_re = r'(/[0-9]+/?)'

app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/brands', Brands),
    ('/product' +  num_re + page_re, Product),
    ('/compare', Compare),
    ('/articles', Articles),
    ('/article' + num_re + page_re, ArticlePage),
    ('/reviews', Reviews),
    ('/review' + num_re + page_re, ReviewPage),
    ('/about', AboutPage),
    ('/contact', ContactPage),
    ('/resources', ResourcesPage),
    ('/disclaimer', DisclaimerPage),
    ('/404', Error404),
    ('/review-image-upload', ReviewImageUpload),
    ('/review-image-upload-handler', ReviewImageUploadHandler),
    ('/review-images' + num_re, ReviewImagesDisplay),
    ('/product-upload', ProductUpload),
    ('/product-upload-handler', ProductUploadHandler),
    ('/review-upload', ReviewUpload),
    ('/article-upload', ArticleUpload),
    ('/article-upload-handler', ArticleUploadHandler),
    ('/ad-upload', AdUpload),
    ('/ad-upload-handler', AdUploadHandler),
    ('/ad-settings', AdSettings),
    ('/resources-upload', ResourcesUpload),
    ('/featured-settings', FeaturedSettings),
    ('/back-login', Login),
    ('/logout', Logout),
    ('/admin-panel', AdminPanel),
    ('/delete-panel', DeletePanel),
    ('/get-rank', GetRank),
    ('/pass-email', EmailArticle),
    ('/email-alert-settings', EmailSubscribe),
    ('/search', Search)
], debug=True)
