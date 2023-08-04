import httpx
import random
import re
from bs4 import BeautifulSoup

ALLRECIPES_ALL_URL="https://www.allrecipes.com/recipes-a-z-6735880"
recipe_link_re = re.compile('com\/recipe\/')

def has_enough_ratings(soup):
	rating_count = soup.find("div", class_="recipe-card-meta__rating-count-number")
	if rating_count:
		rating_count = rating_count.text.strip()
		rating_count = rating_count.split("\n\n")[0]
		rating_count = rating_count.replace(",", "")

		rating_count = int(rating_count)
		if rating_count > 20:
			return True

	return False

def get_random_recipe():
	r = httpx.get(ALLRECIPES_ALL_URL)
	soup = BeautifulSoup(r.text, "lxml")

	categories = soup.find(id="alphabetical-list_1-0").find_all("a")

	r = httpx.get(random.choice(categories)["href"])
	soup = BeautifulSoup(r.text, "lxml")

	recipes = soup.find("div", class_="loc fixedContent").find_all("a", class_="mntl-card-list-items")
	recipes = [a['href'] for a in recipes if (recipe_link_re.search(a['href']) and has_enough_ratings(a))]
	recipe = random.choice(recipes)

	return recipe

def number_of_photos(soup):
	photos_string = soup.find(id="recipe-review-bar__photo-count_1-0").text
	match = re.search(r'(\d+) Photos', photos_string)
	return int(match.group(1))

def get_useful_recipe(recursion=5):
	if recursion==0:
		raise RuntimeError("Couldn't find a good recipe")

	recipe = get_random_recipe()

	r = httpx.get(recipe)
	soup = BeautifulSoup(r.text, "lxml")

	try:
		photo_count = number_of_photos(soup)
		if photo_count > 9:
			return (recipe, soup, photo_count)
	except:
		pass

	#Fallback recurse
	return get_useful_recipe(recursion - 1)

def get_recipe_text(soup):
	title = soup.find("title").text.strip()
	rating = soup.find("div", id="mntl-recipe-review-bar__rating_1-0").text.strip()

	return (title, rating)

def get_photos(recipe, soup, photo_count):
	raw_photo_htmls = ""

	if photo_count > 40:
		photo_count = 40

	for x in range(0, photo_count // 10):
		param = ""
		if x>0:
			param = "?offset=" + str(x * 10)
		r = httpx.post(recipe + param, data={"cr": "photo-dialog__page_1"})
		raw_photo_htmls = raw_photo_htmls + r.json()["photo-dialog__page_1"]['html']

	soup = BeautifulSoup(raw_photo_htmls, "lxml")
	img_tags = soup.find_all("img")
	photo_imgs = []
	for img in img_tags:
		photo_imgs.append((img['data-src'], img['alt']))
		
	selected_imgs = random.sample(photo_imgs, 4)

	return selected_imgs

def get_random_recipe_and_photos():
	(recipe, soup, photo_count) = get_useful_recipe()
	photos = get_photos(recipe, soup, photo_count)

	(title, rating) = get_recipe_text(soup)

	return (title, rating, recipe, photos)