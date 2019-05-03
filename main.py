import time

import image_crawler as ic
import threading

print("\r\n\r\n***** Welcome to Image Crawler by Thomas Cilloni *****")

# ask the user to put in a web site
web_page = input("Enter a website: ")

print("Enter a depth to navigate between 0 and 100 (leaving blank will set the depth to default")
depth = input("Value: ")

# start counting the time
t = time.time()

# possibly set the depth
ic.set_max_depth(depth)

# start the recursion
ic.image_crawler(web_page, 0, 0)

# loop until there is only one thread running (the main thread)
# in other words, stop until all other threads have finished running
while True:
    if threading.active_count() == 1:
        break

print("\n\n***** END *****"
      "\nThe program has downloaded %d images by navigating through %d links"
      "\nET = %s seconds" % (ic.saved_images, len(ic.links), str(time.time()-t)))
