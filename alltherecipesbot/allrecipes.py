import httpx
import random
import re
from bs4 import BeautifulSoup

ALLRECIPES_ALL_URL="https://www.allrecipes.com/recipes-a-z-6735880"
recipe_link_re = re.compile('com\/recipe\/')
number_photos_re = re.compile('(\d+) Photos')

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

def get_random_recipe(http_client):
	r = http_client.get(ALLRECIPES_ALL_URL)
	soup = BeautifulSoup(r.text, "lxml")

	categories = soup.find(id="alphabetical-list_1-0").find_all("a")

	r = http_client.get(random.choice(categories)["href"])
	soup = BeautifulSoup(r.text, "lxml")

	recipes = soup.find("div", class_="loc fixedContent").find_all("a", class_="mntl-card-list-items")
	recipes = [a['href'] for a in recipes if (recipe_link_re.search(a['href']) and has_enough_ratings(a))]
	recipe = random.choice(recipes)

	return recipe

def number_of_photos(soup):
	photos_string = soup.find(id="recipe-review-bar__photo-count_1-0").text
	match = number_photos_re.search(photos_string)
	return int(match.group(1))

def get_useful_recipe(http_client, recursion=5):
	if recursion==0:
		raise RuntimeError("Couldn't find a good recipe")

	recipe = get_random_recipe(http_client)

	r = http_client.get(recipe)
	soup = BeautifulSoup(r.text, "lxml")

	try:
		photo_count = number_of_photos(soup)
		if photo_count > 9:
			return (recipe, soup, photo_count)
	except:
		pass

	#Fallback recurse
	return get_useful_recipe(http_client, recursion - 1)

def get_recipe_text(soup, http_client):
	title = soup.find("meta", property="og:title")["content"].strip()
	rating = soup.find("div", id="mntl-recipe-review-bar__rating_1-0").text.strip()

	return (title, rating)

def random_alt_tag():
	return random.choice([
			"An enticing photograph of {0}",
			"A delectable photo of {0}",
			"A photo of {0}",
			"A well-lit photo of {0}",
			"A photo of {0}, probably perfectly framed and looking great"
		])

def get_photos(recipe, soup, photo_count, title, http_client):
	raw_photo_htmls = ""

	if photo_count > 40:
		photo_count = 40

	for x in range(0, photo_count // 10):
		param = ""
		if x>0:
			param = "?offset=" + str(x * 10)
		r = http_client.post(recipe + param, data={"cr": "photo-dialog__page_1"})
		raw_photo_htmls = raw_photo_htmls + r.json()["photo-dialog__page_1"]['html']

	soup = BeautifulSoup(raw_photo_htmls, "lxml")
	img_tags = soup.find_all("img")
	photo_imgs = []
	for img in img_tags:
		backup_alt = random_alt_tag().format(title)
		alt = img.get("alt", False)
		if not alt:
			alt = backup_alt

		photo_imgs.append((img['data-src'], alt))
		
	selected_imgs = random.sample(photo_imgs, 4)

	return selected_imgs

def get_random_recipe_and_photos():
	http_client = httpx.Client()
	(recipe, soup, photo_count) = get_useful_recipe(http_client)
	(title, rating) = get_recipe_text(soup, http_client)
	photos = get_photos(recipe, soup, photo_count, title, http_client)

	return (title, rating, recipe, photos)