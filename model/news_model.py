class NewsModel:
    def __init__(self, source, title, content, publication_time, image_url, author, related_links):
        self.source = source
        self.title = title
        self.content = content
        self.image_url = image_url
        self.publication_time = publication_time
        self.author = author
        self.related_links = related_links

    def to_dict(self, news_id):
        return {
            "version": "1.0",
            "document": {
                "id": news_id,
                "title": self.title,
                "content": self.content,
                "metadata": {
                    "source": self.source,
                    "image_url": self.image_url,
                    "publication_time": self.publication_time,
                    "author": self.author,
                    "related_links": self.related_links,
                    "attachments": []
                }
            }
        }