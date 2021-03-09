import requests
from bs4 import BeautifulSoup
import sqlite3
import random, string

db = 'posts.db'
url = 'https://vmolab.tistory.com/?page={}'


password = input('Input guest password: ')
cookies = {
	'GUEST_PASSWORD': password
}

conn = sqlite3.connect(db)

c = conn.cursor()

try:
	c.execute('CREATE TABLE `posts`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `date` DATETIME, `title` TEXT, `content` TEXT);')
except:
	pass
conn.commit()

try:
	c.execute('CREATE TABLE `files`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `filename` TEXT, `filename_saved` TEXT, `postid` INTEGER);')
except:
	pass
conn.commit()

def create_random_path(length=20):
	path = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
	return path

for i in range(1, 64):
	r = requests.get(url.format(i), cookies=cookies)
	resp = r.text
	soup = BeautifulSoup(resp, 'html.parser')
	posts = soup.find_all(class_='entry')
	for j in posts:
		date = j.find(class_='imgdate').get_text()
		title = j.find('a').get_text()
		content = j.find(class_='tt_article_useless_p_margin')
		content = str(content).replace('</p><p>', '\n').split('<span')[0]
		content = BeautifulSoup(content, 'html.parser').get_text()
		files = j.find_all(class_='imageblock')

		c.execute('INSERT INTO `posts`(`date`, `title`, `content`) VALUES (date("now"), ?, ?);', (title, content))
		conn.commit()
		c.execute('SELECT * FROM POSTS ORDER BY `id` DESC;')
		one = c.fetchone()
		id_recent = one[0]

		for k in files:
			filename = k.find('a').get_text()
			fileurl = k.find('a').get('href')
			fileurl_new = create_random_path(10)
			
			r = requests.get(fileurl, allow_redirects=True, cookies=cookies)
			open('./files/{}'.format(fileurl_new), 'wb').write(r.content)

			c.execute('INSERT INTO `files`(`filename`, `filename_saved`, `postid`) VALUES (?, ?, ?);', (filename, fileurl_new, one[0]))
			conn.commit()
		print(title)
