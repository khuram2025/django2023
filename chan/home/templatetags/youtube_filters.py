from django import template
import re

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """
    Converts a YouTube URL into an embeddable video URL.
    """
    # Extract the video ID from the URL
    video_id = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url).group(1)
    return f'https://www.youtube.com/embed/{video_id}'
