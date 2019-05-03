import os   # for saving to file


def save_image(file_path, image_link, data):
    # take out the filename from the image_link
    file_name = image_link[image_link.rfind("/")+1:]

    # take out illegal characters from the file path
    file_path = file_path.replace("?", "").replace(":", "").replace("\\", "")

    # take out illegal characters from the file name
    file_name = file_name.replace("?", "").replace(":", "").replace("\\", "")

    # make sure the file path is a directory (could be an html page)
    if not file_path.endswith("/"):
        file_path += "/"

    # execute only if the file is not already created
    if not os.path.isfile(file_path+file_name):
        # if the directory path to the image does not exist yet, make it
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # save the bytes into the file by opening it with the WriteBytes option
        file = open(file_path+file_name, "wb")
        file.write(data)
        file.close()


# given any type of link, this method will return a link
# in the format www.website.com/assets/bla.file
def generate_link(host, path, link):
    # link to another server
    if link.startswith("//"):
        return generate_link("", "", "http:"+link)

    # link to other  host
    if link.startswith("http"):
        # crop out the http(s):// part
        i = link.find("/")
        link = link[i + 2:]
        return link

    # link to server's root
    if link.startswith("/"):
        return host+link

    # crop the filename, if any, after the last '/'
    path = path[:path.rfind("/")+1]

    # link to in-document reference
    if link.startswith("#"):
        return host+path

    # relative link
    while link.startswith("../"):
        i = path[:-1].rfind("/")    # find the second last '/'
        path = path[:i+1]           # crop the path to leave only the second last '/'
        link = link[3:]             # crop the link to delete the first '../'

    return host+path+link


# separate host and resource path on server
def get_host_path(link, first_run):
    # if it is the first run (max depth), make sure the
    # link either ends in '/' or links to a file
    if first_run:
        last_part = link.split("/")[-1]

        if not (last_part.endswith(".htm")
                or last_part.endswith(".html")):  # if it is not a link...

            if last_part != "":     # ... and it does not end in '/' ...
                link += "/"     # ... add a '/'

    # get rid of the http part
    if link.startswith("http"):
        index = link.find("/")+2
        link = link[index:]

    # URIs are of the type www.website.com/images/img1.png,
    # so they are split on the first '/' from the left. The
    # path always starts with '/'
    index = link.find("/")
    host = link[:index]
    path = link[index:]

    return host, path
