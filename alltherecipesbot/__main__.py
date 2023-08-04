import allrecipes
import bsky

def main():
	try:
		(title, rating, recipe, photos) = allrecipes.get_random_recipe_and_photos()

		text = title + "\n" + rating + "⭐"
		bsky.post_to_bsky(text, recipe, photos)
	except RuntimeError:
		bsky.frow_up()

if __name__ == "__main__":
	main()