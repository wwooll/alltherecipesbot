from atproto import Client, models
import os
import httpx
from datetime import datetime

def get_image_data(url, http_client):
	r = http_client.get(url, timeout=12.0)
	return r.content

def upload_image_get_model(client, url, alt, http_client):
	upload = client.com.atproto.repo.upload_blob(get_image_data(url, http_client))
	return models.AppBskyEmbedImages.Image(alt=alt, image=upload.blob)

def post_to_bsky(text, link, images):
	bsky = Client()
	bsky.login(os.environ['BSKY_HANDLE'], os.environ['BSKY_PASSWORD'])

	with httpx.Client() as http_client:
		image_models = [upload_image_get_model(bsky, x[0], x[1], http_client) for x in images]

	text = text + '\n'
	combined_text = text + link
	link_idx_start = len(text.encode('UTF-8'))
	link_idx_end = link_idx_start + len(link.encode('UTF-8'))

	facets = [
		models.AppBskyRichtextFacet.Main(
			features = [models.AppBskyRichtextFacet.Link(uri=link)],
			index=models.AppBskyRichtextFacet.ByteSlice(byte_start=link_idx_start, byte_end=link_idx_end)
			)
	]

	bsky.post(
		langs=["English"],
		text=combined_text,
		facets=facets,
		embed=models.AppBskyEmbedImages.Main(images=image_models)
		)


	return

def frow_up():
	bsky = Client()
	bsky.login(os.environ['BSKY_HANDLE'], os.environ['BSKY_PASSWORD'])
	bsky.send_post(text="i frew up 🤮")	
	
	return
