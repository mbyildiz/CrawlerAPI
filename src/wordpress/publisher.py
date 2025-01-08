from ..config import WP_URL, WP_USERNAME, WP_PASSWORD
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

class WordPressPublisher:
    def __init__(self):
        self.client = Client(f'{WP_URL}/xmlrpc.php', WP_USERNAME, WP_PASSWORD)
    
    def publish_post(self, title, content, categories=None):
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = 'draft'  # Önce taslak olarak kaydet
        
        return self.client.call(NewPost(post)) 