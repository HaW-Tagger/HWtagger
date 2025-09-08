from resources import tag_categories
from tools import files


def tag_search():
    input_tag = input("search this:")
    excluded_tag = input("exclude this:")
    found_tags=[]
    for tag in tag_categories.DESCRIPTION_TAGS:
        if input_tag in tag and (excluded_tag == "" or excluded_tag not in tag):
            found_tags.append(tag)
    print(",".join(found_tags))
    tag_search()



if __name__ == "__main__":
    tag_search()