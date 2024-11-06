from tqdm import tqdm
import concurrent.futures
from resources import parameters
from clip import tokenize
from random import shuffle
from resources.tag_categories import CATEGORY_TAG_DICT, COLOR_DICT_ORDER, COLOR_CATEGORIES

def create_variation_from_tag():
    only_color = ["red", "blue", "green", "black", "white", "grey", "gray", "beige", "brown", "pink", "orange", "gold",
                  "blonde", "yellow", "purple", "aqua"]
    tags = input("insert the tag you want to have the variations of:")
    result = []
    tags_used = []
    for tag in tags:
        if tag not in tags_used:
            result.append(",".join([x+" "+tag for x in only_color]))
            tags_used.append(tag)
    parameters.log.info(result)
    create_variation_from_tag()

def get_tags_below_token(ordered_tags, token_limit=75):

    if tokenize([", ".join(ordered_tags)], context_length=token_limit+75, truncate=True).count_nonzero(dim=1)[0]-2 < token_limit:
        return ordered_tags
    max_tag_len = len(ordered_tags)
    starting_index =  max_tag_len if max_tag_len < 15 else 15

    tag_combination = [", ".join(ordered_tags[:starting_index+x]) for x in range(min(1, max_tag_len - starting_index))]
    all_tokens_len = tokenize(tag_combination, context_length=token_limit+75, truncate=True).count_nonzero(dim=1)

    good_i = 0
    for i, tag_len in enumerate(all_tokens_len):
        if tag_len -2 <= token_limit:
            good_i = i

    good_tags = ordered_tags[:starting_index+good_i]

    if all_tokens_len[good_i] - 3 < token_limit: # we can fit an extra need an extra token for the comma
        for tag in ordered_tags[starting_index+good_i:]:
            if tag not in good_tags and tokenize([", ".join(good_tags + [tag])], context_length=token_limit+75, truncate=True).count_nonzero(dim=1)[0]<=token_limit:
                good_tags+=[tag]

    return good_tags


  
def order_tag_prompt(full_tag, model_prefix_tags=[], keep_token_tags=[], remove_tags=[], tags_under_conf=[]):
    """reorders full tags: <model tags>, <special tokens>, <the other tags with descending importance>

    Args:
        full_tag (list[str]): _description_
        model_prefix (list, optional): list of tags to add to the begining of all captions. Defaults to [].
        keep_token_tags (list, optional): _description_. Defaults to [].
        remove_tags (list, optional): tags to remove. Defaults to [].
        tags_under_conf (list, optional): tags under a specific threshold that are excluded from the first pick. Defaults to [].

    Returns:
        _type_: _description_
    """
    
    first_chosen = [
    "MODELS","COUNT", "OCCUPATION","FETISH GROUPS",
    "BODY SHAPE","EYES COLOR ALL", "HAIR COLOR ALL","BREASTS SIZE","HAIR LENGTH",  "RACE", "FAKE EARS ALL","ANIMALS", "VIEW",
    ]
    second_chosen = [
    "EMOTIONS","CLOTHES ACTION", "ACTION", "POSITION", "VEHICLE", "ENVIRONMENT",
    "SEX", "SEX ACTION","SEX TOY","OTHER","STATE",
    "SHOES",
    "MAKEUP", "ACCESSORIES",
    "SEX GENERAL ALL","CUM ALL",  "TENTACLES",
    "HOLDING", "HANDHELD OBJECT", "INTERACTIVE OBJECTS", "FOOD", "WEAPON",
    "EXTREME","HAIR", "HEAD","TATTOO", "PIERCING",
    "CLOTHES", "CLOTHES TIGHT", "CLOTHES COLOR","CLOTHES EASTERN", "CLOTHES PARTS", "UPPER BODY","BODY","LOWER BODY","APPENDICES","ABSENCE","CHARACTERS", "CHARACTERS_LESSER",
    ]
    second_chosen += [category for category in COLOR_CATEGORIES.keys() if category not in second_chosen]

    full_tag = [t for t in full_tag if t not in remove_tags]

    tag_list = model_prefix_tags
    shuffle(keep_token_tags)
    for t in keep_token_tags:
        if t in full_tag:
            tag_list.append(t)

    for category in first_chosen:
        tag_list.extend([t for t in CATEGORY_TAG_DICT[category] if t in full_tag and t not in tag_list and t not in tags_under_conf])

    unused_tags = [t for t in full_tag if t not in tag_list]
    used_tags = []
    other_tags = []
    for category in second_chosen:
        tags_to_add = [t for t in unused_tags if t in CATEGORY_TAG_DICT[category] and t not in tags_under_conf and t not in used_tags]
        if tags_to_add:
            other_tags.append(tags_to_add)
            used_tags+=tags_to_add

    if other_tags:
        left_over_tags = []
        max_index = max([len(ot) for ot in other_tags])
        for i in range(max_index):
            for j in range(len(other_tags)):
                if len(other_tags[j]) > i:
                    left_over_tags.append(other_tags[j][i])

        fully_sorted_tags = tag_list + left_over_tags
    else:
        fully_sorted_tags = tag_list
    new_tags = get_tags_below_token(fully_sorted_tags)

    return ", ".join(new_tags)


def tqdm_parallel_map(executor, fn, *iterables, **kwargs):
    """
    from: https://techoverflow.net/2017/05/18/how-to-use-concurrent-futures-map-with-a-tqdm-progress-bar/

    Equivalent to executor.map(fn, *iterables),
    but displays a tqdm-based progress bar.

    Does not support timeout or chunksize as executor.submit is used internally

    **kwargs is passed to tqdm.
    """
    futures_list = []
    for iterable in iterables:
        futures_list += [executor.submit(fn, i) for i in iterable]
    for f in tqdm(concurrent.futures.as_completed(futures_list), total=len(futures_list), **kwargs):
        yield f.result()