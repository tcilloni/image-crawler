import re   # for using regular expressions

# an image looks like '<img [classes/id] src[ ]=[ ]"path/to/image.jpeg" >
IMG_PATTERN = b'src\s?=\s?[\'"]?([a-zA-Z0-9/\-\?\._\+=]*)[\'"]?'

# links are of the type
LINK_PATTERN = b'href\s?=\s?[\'"]([a-zA-Z0-9/\-\?\._\+=:]*)[\'"]'


# this function accepts an HTML page in BINARY and returns
# a set of all the images contained in STRING format
def get_images_list(page):
    # if the page is empty there are of course no images
    if not page:
        return set()

    images = set()  # a set does not contain duplicates

    # for every image, check if it is of the supported file types
    for link in re.findall(IMG_PATTERN, page):
        if (link.lower().endswith(b".jpg") or
                link.lower().endswith(b".jpeg") or
                link.lower().endswith(b".png") or
                link.lower().endswith(b".gif") or
                link.lower().endswith(b".webp")):

            images.add(link.decode())

    return images


def get_links_list(page):
    # if the page is empty there are of course no links
    if not page:
        return set()

    links = set()

    # for each link, make sure it points to a web page (html/htm) or is a path (e.g. not a file)
    for link in re.findall(LINK_PATTERN, page):
        last_part = link.split(b"/")[-1].lower()

        if last_part.endswith(b".html") or last_part.endswith(b".htm"):  # html / htm  file
            links.add(link.decode())
        else:
            # if it cannot find ';' (javascript)
            if last_part.find(b";") == -1:
                links.add(link.decode())

    return links
