from Handler import *

class GetRank(Handler):
    def get(self):
        product_id = self.request.get("product-id")
        product = self.get_content(product_id, "product")
        if not product:
            self.write("error")
            return
        self.write(product.ranking)
        return
