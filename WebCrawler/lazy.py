import urllib2
urlOpener = urllib2.build_opener()
urlOpener.addheaders = [('User-Agent', 'Mozilla/5.0')]
popularPrefix = 'https://www.thingiverse.com/explore/popular/page:' # a number goes after this
populars = list()
for pageNumber in range(5):
	url = popularPrefix + str(1 + pageNumber) #1 not 101
	page = urlOpener.open(url)
	html = page.read()
	x = 0
	while x!= -1:
		x = html.find('href="/thing:', x + 1)
		if x != -1:
			if html.find('#comments', x + 1) > html.find('"', x + 8):
				populars.append(html[x+7:html.find('"', x + 8)])
print(populars)
for url in populars:
	realURL = 'https://www.thingiverse.com/' + url
	p = urlOpener.open(realURL)
	html = p.read()
	if html.find('retraction') != -1 or html.find('Retraction') != -1:
		print(realURL)
