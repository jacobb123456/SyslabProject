import urllib2
import datetime
#import pickle

startTime = datetime.datetime.now()
urlOpener = urllib2.build_opener()
urlOpener.addheaders = [('User-Agent', 'Mozilla/5.0')]
popularPrefix = 'https://www.thingiverse.com/explore/popular/page:' # a number goes after this
populars = list()
for pageNumber in range(5):
	url = popularPrefix + str(101 + pageNumber) #1 not 101
	page = urlOpener.open(url)
	html = page.read()
	x = 0
	while x!= -1:
		x = html.find('href="/thing:', x + 1)
		if x != -1:
			if html.find('#comments', x + 1) > html.find('"', x + 8):
				populars.append(html[x+7:html.find('"', x + 8)])
print(populars)

dopeThings = 0
for url in populars:
	p = urlOpener.open('https://www.thingiverse.com/' + url)
	html = p.read()
	print(html.find('class="detail-setting'))
	if html.find('class="detail-setting') != -1:
		dopeThings += 1
endTime = datetime.datetime.now()
print(str(dopeThings) + ' things with print settings found')
print('time taken: ' + str(endTime - startTime))
