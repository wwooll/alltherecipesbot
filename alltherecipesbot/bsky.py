from atproto import Client, models
import os
import httpx
from datetime import datetime

def get_image_data(url):
	r = httpx.get(url)
	return r.content

def upload_image_get_model(client, url, alt):
	upload = client.com.atproto.repo.upload_blob(get_image_data(url))
	return models.AppBskyEmbedImages.Image(alt=alt, image=upload.blob)

def post_to_bsky(text, link, images):
	bsky = Client()
	bsky.login(os.environ['BSKY_HANDLE'], os.environ['BSKY_PASSWORD'])

	image_models = [upload_image_get_model(bsky, x[0], x[1]) for x in images]

	text = text + '\n'
	combined_text = text + link
	link_idx_start = len(text.encode('UTF-8'))
	link_idx_end = link_idx_start + len(link.encode('UTF-8'))

	facets = [
		models.AppBskyRichtextFacet.Main(
			features = [models.AppBskyRichtextFacet.Link(uri=link)],
			index=models.AppBskyRichtextFacet.ByteSlice(byteStart=link_idx_start, byteEnd=link_idx_end)
			)
	]

	bsky.com.atproto.repo.create_record(
		models.ComAtprotoRepoCreateRecord.Data(
			repo=bsky.me.did,
			collection=models.ids.AppBskyFeedPost,
			record=models.AppBskyFeedPost.Main(
				createdAt=datetime.now().isoformat(),
				text=combined_text,
				facets=facets,
				embed=models.AppBskyEmbedImages.Main(images=image_models)
				)
			)
		)

	return

def frow_up():
	bsky = Client()
	bsky.login(os.environ['BSKY_HANDLE'], os.environ['BSKY_PASSWORD'])
	bsky.send_post(text="i frew up 🤮")	
	
	return
