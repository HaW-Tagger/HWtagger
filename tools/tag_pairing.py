from resources.tag_pos_grouping import prep_verbs,non_subjects,adjectives,design_idx,attire_idx,\
                                    blacklist,prepositional_indicators,action_blacklist,basic_color_order
from classes.class_elements import TagsList

from itertools import product
from collections import Counter

two_word_subject_tup = ("hair ornament", "pubic hair", "armpit hair", "anal hair", "hair bun",
                        "remote control", 'one-piece swimsuit', 'tank top','crop top',
                        'crop top', 'sailor collar', 'poke ball', 'top hat', 'shower head',
                        'sports bra','sweater vest', 'thigh strap', 'condom wrapper',
                        'bikini top', 'bikini bottom', 'game controller', 'microphone stand',
                        'ice cream','garter belt', 'suspended congress', 'facial mark',
                        'chastity cage', 'chastity belt', 'chest hair', 'game console',
                        'pussy juice'
                        )

unknown_modifiers = Counter()

def print_unknown_recommendations(print_threshold=5):
    """This prints all the recommendations that are not in the tag categories
    unknown_modifier stores a pair of (modifier, subject)
    """
    print("="*20)
    print("Uncategorized Adjectives by Subject:")
    print("="*20)
    # we want to group the same subjects together and show the modifiers in descending order
    # the subject group is also sorted by the total count of modifiers for that subject
    
    subject_frequencY_dict = {}
    for (mod, sub), freq in unknown_modifiers.items():
        subject_frequencY_dict[sub] = subject_frequencY_dict.get(sub, 0) + freq
    
    print("finished building first dict")
    for subject, count in sorted(subject_frequencY_dict.items(), key=lambda x: x[1], reverse=True):
        if count <= print_threshold:
            continue
        print(subject, count)
        curr_mod = []
        for (mod, sub), freq in unknown_modifiers.most_common():
            if sub == subject:
                curr_mod.append((mod, freq))
        if curr_mod:
            print(f"Subject: {subject}")
            print(f"  Modifiers: {curr_mod}")
            print("-"*30)
    print("="*20)
    print("End of Uncategorized Adjectives Report")
    print("="*20)
    
    
    


def get_combined(adj_group_tags, subject):
    """makes all possible combinations of adjectives with the subject, one adjective per group is selected
    Args:
        adj_group_tags (list[list[str]]): list of grouped adjectives ordered by priority
        subject (str): the subject that is being modified 
    Returns:
        list[str], list[list[str]]: 1st stores all possible combinations, 2nd stores the tags used to make the combination
    """
    combinations = list(product(*adj_group_tags))
    return [" ".join(comb) +" "+subject for comb in combinations], [[component+" "+subject for component in comb] for comb in combinations]


def get_combined_post_modifier(post_modifier_list:list[str],prev_prunes:list[list[str]], current_subjects:list[str], original_subject:str):
    """we assume this uses the output from the get_combined
    ex: pink panties, panties aside --> pink panties is processed by the previous step and panties aside is processed here
        panties would be the original subject
    Args:
        post_modifier_list (list[str]): list of post modifiers that is going to be added to the end of the subject
        prev_prune (list[list[str]]): output from get_combined, a list of list of tags used to make the combination
        curr_subject (list[str]): output from get_combined, this is the combined adjectives + subject
        original_subject (str): the basic original subject used

    Returns:
        list[str], list[list[str]]: same as get_combined but with the postmodifers
    """
    new_combined, new_prune = [], []

    for curr_subject, prev_prune in zip(current_subjects, prev_prunes):
        for modifier in post_modifier_list:
            new_combined.append(curr_subject+" "+modifier)
            new_prune.append(prev_prune+[original_subject+" "+modifier])

    return  new_combined, new_prune

def gradient_background_reccomendation(sub, modifiers):
    colors = [m for m in modifiers if m in basic_color_order]
    if len(colors) != 2:
        return [], []
    else: # this is a two colored background with potential gradient
        colors = sorted(colors, key=lambda x: basic_color_order.index(x))
        merged_color = f"{colors[0]} and {colors[1]} gradient"
        return [merged_color+" "+sub], [[c+" "+sub for c in colors]]
    

def build_recommendation_pairs(full_tags:TagsList|list[str]) -> tuple[list[str], list[list[str]]]:
    """
        takes in tags that are in full tags (no rejected), then return 3 lists of same size
        the first stores new tags to add to recommendation, 
        the second list stores a list of tags to remove if the corresponding tag was selected
        third is a list that stores confidence
    """
    # general rules, sorted_mod idx 0 and 1 should be manually checked 
    
    # rpartition splits string on the last separator,return a 3-tuple containing the part before the separator, 
    # the separator itself, and the part after the separator. If the separator is not found, 
    # return a 3-tuple containing two empty strings, followed by the string itself.
    
    if isinstance(full_tags, TagsList):
        multi_word_subjects = {t.tag for t in full_tags if t.tag.endswith(two_word_subject_tup) and t.tag not in two_word_subject_tup}
        nonbasics = multi_word_subjects | set(two_word_subject_tup)
        basic_subjects = [t.tag for t in full_tags if t.tag not in nonbasics and ")" != t.tag[-1]]
    elif isinstance(full_tags, list):
        multi_word_subjects = {t for t in full_tags if t.endswith(two_word_subject_tup) and t not in two_word_subject_tup}
        nonbasics = multi_word_subjects | set(two_word_subject_tup)
        basic_subjects = [t for t in full_tags if t not in nonbasics]
    
    mod_sub_pair = [(before, after) for before, _, after in (t.rpartition(" ") for t in basic_subjects) 
                    if before and after not in non_subjects]
    # remove prepositional phrases
    mod_sub_pair = [(before, after) for before, after in mod_sub_pair
                    if not any(t in prepositional_indicators for t in before)
                    ]
     
    for multi_words in multi_word_subjects:
        for two_sub in two_word_subject_tup:
            if multi_words.endswith(two_sub) and len(multi_words) > len(two_sub):
                before, after = multi_words[:-len(two_sub)].strip(), multi_words[-len(two_sub):]
                mod_sub_pair.append((before, after))
    
    if not mod_sub_pair:
        return ([], [])
    
    sub_mod_dict = dict()
    for mod, subject in mod_sub_pair:
        sub_mod_dict[subject] = sub_mod_dict.get(subject, []) + [mod]
        
    # action pair stores the subject and action/modifers that follows the subject
    # ex: panties aside -> panties + aside
    action_pairs = [splitword for splitword in (t.split(" ", 1) for t in basic_subjects if t not in action_blacklist) 
                    if len(splitword)>1 and splitword[0] not in non_subjects]
    # we now make the dictionary for easy access
    action_dict = dict()
    for subject, action in action_pairs:
        action_dict[subject] = action_dict.get(subject, []) + [action]
        
    combined_tags, prunable_tags = [], []
    def add_combined(combined:list[str], prunable:list[list[str]]):
        #global combined_tags, prunable_tags
        if combined and combined not in combined_tags and combined not in full_tags:
            combined_tags.extend(combined)
            prunable_tags.extend(prunable)
    
    # add misc checks here: these will be listed first
    if len(sub_mod_dict.get("background", [])) > 1:
        add_combined(*gradient_background_reccomendation('background', sub_mod_dict["background"]))
        
    #print(sub_mod_dict.items())
    for sub, mod in sorted(sub_mod_dict.items(), key=lambda x: len(x[1]), reverse=True):
        action_indicator = 1 if len(action_dict.get(sub, [])) else 0
        if len(mod)+action_indicator > 1:
            # sorted list of list based on category prep_verb, then the adjectives
            # quant, opinion, size, age, shape, color, pattern, attire_mod, design, origin, animal, material, linked obj, linked body, linked attire
            # eg: sub = "bowtie" 
            # mod is sorted to be [["holding"], [], [], ["large"], [], [], ["red", "orange"], ...] without the empty slot
            sorted_mod = []
            curr_mod = list(mod)
            for i, adj_group in enumerate([prep_verbs] + adjectives): 
                group_mod = [m for m in curr_mod if m in adj_group]
                curr_mod = [cm for cm in curr_mod if cm not in group_mod and cm not in blacklist]
                sorted_mod.append(group_mod)
            curr_mod = [cm for cm in curr_mod if len(cm.split(" "))<3]
            if curr_mod:
                unknown_modifiers.update([(c, sub) for c in curr_mod])
                if sub in adjectives[attire_idx]: 
                    # clothings often have design/styles that are classified under "unknown" so they go to the design group
                    sorted_mod[0] += [c for c in curr_mod if c.endswith("ing")]
                    sorted_mod[design_idx] += [c for c in curr_mod if not c.endswith("ing")]
                else:
                    sorted_mod[0] += [c for c in curr_mod if c.endswith("ing")]
                    sorted_mod[1] += [c for c in curr_mod if not c.endswith("ing")]
                       
            #print(sub, sorted_mod) # some example prints at this point
            # gloves [[], [], [], [], [], [], ['white'], [], [], [], [], [], [], [], ['elbow'], []]
            # nipples [[], [], [], ['huge'], [], [], ['dark'], [], [], [], [], [], [], [], [], []]
            # eyes [[], ['closed'], [], [], [], [], ['red'], [], [], [], [], [], [], [], [], []]
            # hair [[], ['female pubic'], [], ['long'], [], [], ['brown'], [], [], [], [], [], [], [], [], []]
            
            # we also want to skip adj groups with multiple candidates (aka skip coordinate adjectives, for now)
            cleaned_list = [l for l in sorted_mod if l]
        
            # we start with -1 for the case where we don't drop any adj group
            for i_th in range(-1, len(cleaned_list)): 
                # we drop the i-th adj group and maybe there's a good combination
                # the 0th index contains all adj
                ith_dropped = [v for i, v in enumerate(cleaned_list) if i!=i_th]
                if ith_dropped:
                    combinations, prune_elem = get_combined(ith_dropped, sub)
                    if len(ith_dropped)>1:
                        add_combined(combinations, prune_elem)
                    if action_indicator:
                        action_comb, action_prune = get_combined_post_modifier(action_dict[sub],prune_elem, combinations, sub)
                        add_combined(action_comb, action_prune)
                
                   
    return (combined_tags, prunable_tags)