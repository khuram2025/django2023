from django import template
import re

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """
    Converts a YouTube URL into an embeddable video URL.
    """
    # Extract the video ID from the URL
    match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
    if match:
        video_id = match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    else:
        # Handle the case where no match is found
        # Perhaps return an empty string or a default YouTube URL
        return ""
