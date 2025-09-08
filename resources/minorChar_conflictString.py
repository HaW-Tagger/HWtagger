# just a list of characters and their main identifying attributes
# you can have multiple entries if the character have multiple distinct looks or if you want to have multiple checks

# each entry is a list with 2 elements, the first is the character name and the second is a list of attributes
# typos or alias for character names is allowed because this is used to match cases and sort by the number of matches
# so the first element is just a string to identify the character

# list[
#   tuple[str, list[str]]
# ]

char_dict = [
        ("uchiha sarada", ["short hair", "black hair", "red-framed eyewear"]),
        ("igawa sakura", ["blonde hair", "flipped hair"]),
        ("mei mei (jujutsu kaisen)", ['white hair', 'hair over one eye', 'single braid']),
        ("ankha (animal crossing)", ['furry female', 'yellow fur', 'egyptian']),
        ("ankha (animal crossing)", ['furry female', 'yellow fur', 'egyptian clothes'])
]


# the following list is an experimental feature that I'm still working on
# the purpose is to easily resolve 2 conflicting categories that are often confused by auto taggers (somewhat overlapping with other features)
# the UI takes care of which to remove/keep with the checkboxes and when one or more elements in both categories are present,
# the batch feature will remove the selected category

# example problems:    
# 1.) yaoi with femboys are commonly mistaken for yuri and 2girls, so we want to remove mistaken concepts if identified
# 2.) all types of animals are often mistagged so if the user pre-filtered it by directory this is a good way to filter unwanted tags
# 3.) leotards and one-piece swimsuits are often confused
# 4.) furry types (dog girl vs cat girl), and other partial attributes like "x ears", "x tail" are all tagged and can cause bloat

# due to the UI element being on the right, try to keep the shorter category on the left and long one on the right

# this feature also removes tags with partial word match (split using spaces " ") 
# so if the selected category is removing "dog", it will remove "dog girl", "dog ears", "dog tail", and "large dog", 
# but not "hotdog" or "dogfight"

conflict_categories = [
        ("leotard", "swimsuit"),
        (("bikini"),("bra", "panties")),
        ("penis", ("dildo", "sex toy")), 
        ("vaginal", "anal"),
        ("horse", ("dog", "cow")),
        ("dog", ("horse", "cow")),
        ("dog", "wolf"),
        ("cat", "dog"),
        ("pig", ("horse", "dog", "cow")),
        ("yaoi", ("1girl", "2girls", "futa with", "furry female", "multiple girls", "male on"))
        (("girl", "female", "1boy"), ("boy", "male", "1boy")), 
        ("chastity", ("phimosis", "condom on penis", "foreskin")),
        ("dark-skinned male", ("horse", "bestiality", "monster", "animal")),
        (("1boy", "2boys", "3boys", "4boys", "5boys", "6+boys", "multiple boys"), 
        ("1other", "2others", "3others", "4others", "5others", "6+others", "multiple others","monster", "creature")),
        (("prolapse"), ("penis", "futanari")),
        
        
]