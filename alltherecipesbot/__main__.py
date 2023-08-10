import allrecipes
import bsky
import os

def main():
	try:
		(title, rating, recipe, photos) = allrecipes.get_random_recipe_and_photos()

		text = title + "\n" + rating + "⭐"
		if (os.getenv("PY_ENV", "prod") == "dev"):
			print(title)
			print(rating)
			print(recipe)
			print(photos)
		else:
			bsky.post_to_bsky(text, recipe, photos)

	except RuntimeError:
		if (os.getenv("PY_ENV", "prod") == "prod"):
			bsky.frow_up()

if __name__ == "__main__":
	main()