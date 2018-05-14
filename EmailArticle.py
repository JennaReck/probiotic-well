from Handler import *
from google.appengine.api import mail

class EmailArticle(Handler):
    def post(self):
        from_email = self.request.get("from")
        to_email = self.request.get("to")
        message = self.request.get("message")
        if not message:
            message = "None"
        from_email, to_email, message = self.sanitize_email_inputs(email=from_email,
                                            email2=to_email,
                                            message=message)
        escaped_from_email = cgi.escape(from_email, True)
        
        article_id = self.request.get("article-id")
        article = self.get_content(article_id, "article")
        html_email_content = "<p>Your friend, " + escaped_from_email + ", has sent you this article.</p>"
        plain_email_content = "Your friend, " + escaped_from_email + ", has sent you this article.\r\n"
        if message != "None":
            html_email_content += "<p>Their message:<br />" + message + "</p>"
            plain_email_content += "Their message:\r\n" + message + "\r\n"
        if article:
            truncated_body = self.truncate_and_strip_html(article.body, 131)
            html_email_content += ("<a href='http://probioticwell.appspot.com/" + article.link +
                                   "'><img alt='Probiotic Well logo'" +
                                    "title='Click here to view this article on probioticwell.com'" +
                                    "src='http://probioticwell.appspot.com/images/PWlogo.png' /></a><h3>" +
                                    article.title + "</h3><p>" + truncated_body +
                                    "<a href='http://probioticwell.appspot.com/" + article.link +
                                    "'>Read the rest of the article at probioticwell.com</a></p>")
            plain_email_content += (article.title + "\r\n" + truncated_body +
                                    "\r\n" + "Read the rest of the article at http://probioticwell.appspot.com/"
                                    + article.link)
            mail.send_mail(sender = "alerts@probioticwell.com",
                           reply_to = from_email,
                           to = to_email,
                           subject = article.title,
                           body = plain_email_content,
                           html = html_email_content)
