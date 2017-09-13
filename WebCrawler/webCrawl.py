import urllib2

urlOpener = urllib2.build_opener()
urlOpener.addheaders = [('User-Agent', 'Mozilla/5.0')]
url = 'https://www.thingiverse.com/thing:1559232'
#page = urlOpener.open(url)
#html = page.read()
#print(type(html))
#x = 0
#while x != -1:
#	x = html.find('class="detail-setting', x + 1)
#	print(x)
pages = list()
total = 0
attempted = 0
for i in range(100):
	try:
		j = i + 1000100
		url = 'https://www.thingiverse.com/thing:' + str(j)
		p = (urlOpener.open(url))
		html = p.read()
		if html.find('class="detail-setting') != -1:
			total += 1
			print('FINALLY!!!!!!!!!')
		print(i)
		attempted += 1
	except:
		print('404')
print('total: ' + str(total))
print('out of ' + str(attempted))



