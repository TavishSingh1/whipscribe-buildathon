import os
import httpx

class SlackClient:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    def send_notification(self, title: str, summary: str, clips: list, social_posts: dict) -> str:
        """Sends a rich Block Kit message to Slack."""
        if not self.webhook_url:
            return "Slack webhook not configured in .env"
            
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎙️ New Episode Processed: {title}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary[:300]}..."
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add clips
        if clips:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎬 Top Viral Clips Generated:*"
                }
            })
            for i, clip in enumerate(clips):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{i+1}. {clip.get('title', 'Clip')}*\n_\"{clip.get('why', '')}\"_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Watch MP4"
                        },
                        "url": clip.get('video_url', 'https://whipscribe.com'),
                        "action_id": f"button-action-{i}"
                    }
                })
        
        # Add social snippet
        if social_posts.get('twitter'):
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🐦 X / Twitter Draft:*\n```{social_posts.get('twitter')}```"
                }
            })

        payload = {"blocks": blocks}
        
        try:
            with httpx.Client() as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
            return "Successfully sent Slack notification!"
        except Exception as e:
            return f"Error sending Slack notification: {e}"

