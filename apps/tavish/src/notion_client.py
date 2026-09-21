import os
from notion_client import Client

class NotionClient:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if self.api_key and self.database_id:
            self.client = Client(auth=self.api_key)
        else:
            self.client = None

    def push_episode(self, title: str, summary: str, chapters: list, social_posts: dict, clips: list) -> str:
        """Creates a rich Notion page for the episode."""
        if not self.client:
            return "Notion not configured in .env"
            
        try:
            # Create the blocks for the page body
            children = []
            
            # Summary
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Episode Summary"}}]}})
            children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": summary}}]}})
            
            # Chapters
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Chapters"}}]}})
            for c in chapters:
                chapter_text = f"{c.get('timestamp_s', 0)}s: {c.get('title', '')} - {c.get('summary', '')}"
                children.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": chapter_text}}]}})
            
            # Clips
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Viral Clips"}}]}})
            for clip in clips:
                children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": clip.get('title', 'Clip'), "link": {"url": clip.get('video_url', '')}}}]}})

            # Social Posts
            children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Social Media Posts"}}]}})
            
            for platform, post in social_posts.items():
                children.append({"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": platform.capitalize()}}]}})
                children.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": post}}]}})

            new_page = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": "Draft"
                        }
                    }
                },
                "children": children
            }
            
            response = self.client.pages.create(**new_page)
            return f"Successfully pushed to Notion! Page ID: {response['id']}"
        except Exception as e:
            return f"Error pushing to Notion: {e}"

