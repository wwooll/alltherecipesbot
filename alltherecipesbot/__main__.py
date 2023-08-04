import allrecipes
import bsky

def main():
	#TODO: Add try/except, fallback to a "I frew up" post
	(title, rating, recipe, photos) = allrecipes.get_random_recipe_and_photos()

	text = title + "\n" + rating + "⭐"
	bsky.post_to_bsky(text, recipe, photos)

if __name__ == "__main__":
	main()