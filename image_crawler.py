import threading
import regex as re
import utils as u
import tcp_socket as tcp

links = set()
max_depth = 5
saved_images = 0


def image_crawler(address, depth, loop_counter):
    print("\nNavigating %s\nAt depth %d" % (address, depth))
    global saved_images

    # extract host and relative path from the given address
    # pass True if additional address check needs to be done (first run only)
    if depth == 0:
        host, rel_path = u.get_host_path(address, True)
    else:
        host, rel_path = u.get_host_path(address, False)

    # request the page (get only body)
    page = tcp.request_http(host+rel_path, depth, loop_counter)

    # get all the links to the images from the page
    imgs = re.get_images_list(page)

    # and process them to get links in the form www.site.cn/images/res1.jpg
    new_images = set()  # this contains the actual links to the images
    for img in imgs:
        new_images.add(u.generate_link(host, rel_path, img))

    # finally, download the images and save them based on what page they were on on the server
    for img in new_images:
        # *** uncomment this and comment out the threading... line to make the program run in single-thread mode
        # download_save(host+rel_path, img)
        # spawn a new thread to download the image
        threading.Thread(target=download_save, args=(host+rel_path, img, depth, loop_counter)).start()

    # if there is still depth to explore, go
    if depth < max_depth:
        # get all the links and process them
        raw_links = re.get_links_list(page)

        new_links = set()
        for link in raw_links:
            new_link = u.generate_link(host, rel_path, link)

            # the link could be to a directory, in which case a last '/' bust be appended
            if not (new_link.endswith(".html") or new_link.endswith(".htm")):  # if it is not a file...
                if not new_link.endswith("/"):  # ... and it does not end with '/'
                    new_link += "/"  # append a '/'

            new_links.add(new_link)

        # navigate deeper into every new link
        for new_link in new_links.difference(links):
            # the link could be to a directory, in which case a last '/' bust be appended
            # if not (new_link.endswith(".html") or new_link.endswith(".htm")):   # if it is not a file...
            #     if not new_link.endswith("/"):  # ... and it does not end with '/'
            #         new_link += "/"     # append a '/'
            links.add(new_link)

            # *** uncomment this and comment out the threading... line to make the program run in single-thread mode
            # image_crawler(new_link, depth+1)
            # spawn a new thread to navigate deeper
            threading.Thread(target=image_crawler, args=(new_link, depth+1, 0)).start()


# this is done in a separate method to allow multithreading
def download_save(directory, image_link, depth, loop_counter):
    global saved_images

    image_data = tcp.request_http(image_link, depth, loop_counter)

    if image_data:
        saved_images += 1
        u.save_image("downloads/"+directory, image_link, image_data)


def spawn_crawler(address, depth, loop_counter):
    threading.Thread(target=image_crawler, args=(address, depth, loop_counter)).start()


def set_max_depth(depth):
    global max_depth

    # if the given depth is valid, use it
    try:
        depth = int(depth)
        if depth in range(0, 100):
            max_depth = depth

    except Exception:
        print("Depth automatically set to 5")
