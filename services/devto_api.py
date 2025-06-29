import os
import textwrap
import requests


def publish_to_devto(
    api_key, title, content, image_path=None, published=False, tags=""
):
    """
    Publish the blog to dev.to

    :param api_key: Your DEV.to API key
    :param title: Title of the article
    :param content: Markdown content of the article
    :param image_path: Optional local path to a main image
    :param published: Whether to publish immediately
    :param tags: Comma-separated string of tags
    :return: API response JSON if successful
    """
    try:
        # Get the API key
        final_api_key = api_key or os.getenv("DEV_TO_API_KEY")
        if not final_api_key:
            raise ValueError(
                "No API key provided and DEV_TO_API_KEY environment variable not set"
            )

        # If image_path is provided, try uploading the image using imgbb or a similar image hosting API
        image_url = None
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                imgbb_api_key = os.getenv(
                    "IMGBB_API_KEY"
                )  # Store your imgbb key as an env var
                if not imgbb_api_key:
                    raise ValueError("IMGBB_API_KEY environment variable not set")

                upload_response = requests.post(
                    "https://api.imgbb.com/1/upload",
                    params={"key": imgbb_api_key},
                    files={"image": f},
                )
                if upload_response.status_code == 200:
                    image_url = upload_response.json()["data"]["url"]
                else:
                    print(f"Image upload failed: {upload_response.text}")
        cleaned_content = textwrap.dedent(content).strip()

        article_data = {
            "article": {
                "title": title,
                "body_markdown": cleaned_content,
                "published": published,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "main_image": image_url,
            }
        }

        headers = {"api-key": final_api_key, "Content-Type": "application/json"}

        response = requests.post(
            "https://dev.to/api/articles",
            headers=headers,
            json=article_data,
        )

        if response.status_code == 201:
            print("✅ Blog published successfully!")
            return response.json()
        else:
            error_msg = f"❌ Failed to publish to dev.to: {response.status_code} - {response.text}"
            print(error_msg)
            raise Exception(error_msg)

    except Exception as e:
        print(f"🚨 Error publishing to dev.to: {str(e)}")
        raise
