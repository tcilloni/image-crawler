# Image Crawler

This program is a crawler for images that scans the web recursively from a certain page and downloads all found images.

It accepts two parameters:
- The website to start crawling from
- The depth to reach with the recursion

The program's workflow is very straightforward: the _crawl()_ function does two things: download all images found in the page and call itself on every link found in the page. The pseudocode looks similar to:

```
link <- input
depth <- input
crawl(link, depth)

function crawl(link, depth):
	if (depth == 0)
		return
    
	pageLinks <- links to pages in the current page
	imageLinks <- links to images in the current page
  
	for every page in pageLinks
		crawl(page, depth-1)
	for every image in imageLinks
		download the image
```

There are 3 important points to consider:
1. **Concurrency**: HTTP responses take some time to be received and the volume of requests is very large (suppose that a page has an average of 5 links and 10 images and we want to crawl with a depth of 5: the total number of requests will be _10 * 5^5 = 31250_). To speed up the program concurrency is used for both the recursion and the method to download images.
2. **Directories**: Images are not downloaded all to a common folder. Instead, they are inserted in a directory structure that represents the list of links that the crawler has followed in order to get to that page. For example, an image found in the given link will be inserted in _/images/_, while an image found in a link to a facebook post found in the 'About' page reached from the menu of the first page will be inserted in _/images/About/facebook_.
3. **Encryption**: For every link, the crawler always tries to connect using HTTPs. If it fails, it will use HTTP instead.
