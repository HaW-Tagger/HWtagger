import os, csv
import itertools
from collections import defaultdict

from resources import parameters
# removed out 'color halftone'


"""
this is a quick loose description of most variables in this file: the ones that I use a lot are documented

COLOR_DICT, tag [str] -> rgb color [tuple]
CATEGORY_TAG_DICT, category name [str] -> set of tags [set]
TAG_DEFINITION, tag [str] -> definition [str]
TAG2HIGH_KEYSET, 
LOW2TAGS_KEYSET, key is the tag in the low category and and value is a list of tags that would remove the key str if any exists
TAG_CATEGORIES_EXCLUSIVE, 
TAG_CATEGORIES_NONEXCLUSIVE,
TAG2HIGH, TAG --> [list of HIGH tags it should be converted to, usually only 1]
EXCLUSIVE_HIGH2TAGS, # HIGH --> TAGS
LOW2TAGS, # LOW --> TAGS
TAG_CATEGORIES, 
TAGS_RECOMMENDATIONS, a dict of kv pair of tag [str] --> list of list of tags that would trigger the key tag [list[list[str]]]
CHARACTER_RECOMMENDATIONS, a dict of kv pair of minor character names [str] --> main attributes useful in identifying the character [list[list[str]]]
DESCRIPTION_TAGS, 
DESCRIPTION_TAGS_FREQUENCY, 
ARTISTS_TAGS, 
SERIES_TAGS, 
CHARACTERS_TAG, dict of characters and their secondary tags, character_name [str] -> list of secondary tags (char names/alias) [list[str]]
CHARACTERS_TAG_FREQUENCY, dict, character name [str] -> frequency [int], frequency is from danbooru_tags.csv and frequency is the tag count in danbooru in 2024 or something, manually added names are set to 1
METADATA_TAGS, 
TAG2SUB_CATEGORY_EXCLUSIVE, 
PRIORITY_DICT, 
TAG2CATEGORY : tag [str] -> category [str]
"""

# these are depreciated tags with proper replacement(s) added to tag categories
DEPRECIATED = {"disembodied limb", 'french braid', 'looking away', 'eyebrows', 'areolae', 
                'uniform','multiple penises'
               'striped','breast hold','arm grab','habit','light','multicolored background',
               'pose', 'plaid', 'oni horns','wall',
               'black headwear','white headwear','brown headwear','red headwear','blue headwear',
               'green headwear','purple headwear','grey headwear','yellow headwear','orange headwear',
               'plaid headwear','multicolored headwear','aqua headwear','pink headwear',
               'white footwear', 'brown footwear','platform footwear','cross-laced footwear',
               'black footwear','white footwear','brown footwear','red footwear','blue footwear',
               'green footwear','purple footwear','grey footwear','yellow footwear','orange footwear',
               'plaid footwear','multicolored footwear','aqua footwear','pink footwear','toeless footwear',
               'two-tone footwear','pointy footwear','gold footwear','fur-trimmed footwear','winged footwear',
               'shiny','checkered', 'tied hair', 'vertical stripes', 'diagonal stripes','gradient','ass grab',
               'lights', 'hand on head', 'visor', 'holding person','argyle','stone','traditional clothes',
               'hand on breast','turret','hand gesture', 'mole on body','low tied hair','highleg swimsuit',
               'implied anal','white uniform','chest armor','hand on forehead',"just the tip","tired",
               "furniture", "correction","qiya","wtf",'piercings','black legwear','white legwear','brown legwear',
               'red legwear','blue legwear','green legwear','purple legwear','grey legwear','yellow legwear',
               'orange legwear','gold legwear', 'drop earrings', 'amazon'
               
               }

REJECTED_TAGS = {
    # globally rejected tags, we also reject depreciated tags from danbooru
    # 'breasts', 'groin', 'cleft of venus', 'partially visible vulva'
    
    # depreciated
    "looking away", "just the tip","tired","furniture", "correction","qiya","wtf",
    # remove maybe
    "nsfw", "sfw",
    
    # rejecting cause comma is a problem with these tags:
    "please don't bully me", "nagatoro",
    
    # body parts:
    "face","nose","ears","mouth","fur","hair","human","cum","posing", 
    
    # ambiguous clothing
    "clothing", "mostly clothed", "clothed",'piercing',
    
    # rule 34 specific weird/ambiguous tags:
    "bedding", "screenshot background", "extinct", "forced exposure","rule 63","original character","cuntboy","on ass", "pinup", "m-preg",
    "chastity", "penetration", "girly", "nipple fetish", "domestic cat", "intersex only", "mammal", "incest_(lore)", "nonbinary_(lore)", 
    "parent_(lore)", "trans_(lore)", "sibling_(lore)", "trans_woman_(lore)", "parent_and_child_(lore)", "mother_(lore)", "son_(lore)", 
    "father_(lore)", "sister_(lore)", "parent_and_son_(lore)", "brother_(lore)", "father_and_child_(lore)", "male_(lore)", "mother_and_child_(lore)", 
    "herm_(lore)", "daughter_(lore)", "father_and_son_(lore)", "brother_and_sister_(lore)", "parent_and_daughter_(lore)", "sisters_(lore)", 
    "trans_man_(lore)", "female_(lore)", "brothers_(lore)", "mother_and_son_(lore)", "mother_and_daughter_(lore)", "twins_(lore)", "gynomorph_(lore)", 
    "father_and_daughter_(lore)", "intersex_(lore)", "cousins_(lore)", "grandparent_(lore)", "uncle_(lore)", "nephew_(lore)", "twincest_(lore)", 
    "uncle_and_nephew_(lore)", "adult_(lore)", "grandmother_(lore)", "adopted_(lore)", "young_(lore)", "indirect_incest_(lore)", "pseudo_incest_(lore)", 
    "grandchild_(lore)", "grandparent_and_grandchild_(lore)", "andromorph_(lore)", "grandson_(lore)", "adopted_daughter_(lore)", "adoptive_father_(lore)", 
    "stepparent_(lore)", "grandfather_(lore)", "mother_and_father_(lore)", "adopted_son_(lore)", "stepfather_(lore)", "grandfather_and_grandchild_(lore)", 
    "stepsibling_(lore)", "stepbrother_(lore)", "stepfather_and_stepchild_(lore)", "stepparent_and_stepchild_(lore)", "stepson_(lore)", "aunt_(lore)", 
    "stepfather_and_stepson_(lore)", "stepparent_and_stepson_(lore)", "grandfather_and_grandson_(lore)", "grandmother_and_grandchild_(lore)", "stepsister_(lore)", 
    "niece_(lore)", "uncle_and_niece_(lore)", "grandmother_and_grandson_(lore)", "aunt_and_nephew_(lore)", "real person", "john doe", "shaved","hairless", "fit",
    "exposed nipples", "exposed balls", "horny", "caged dom", "chastity cage only", "both sexes in same situation", "straight", "non-human",
    "foot fetish", "chastity device only","light skin",
    
    
    'fucked silly',"plug","traditional clothes", "ground vehicle", "military", "bdsm", "off shoulder",
    "age regression","spreading",
    "food", "public", "weapon", 'bangs',  "pose",'public nudity',
    "eyebrows", "areolae","focused","accident",
    "clitoral stimulation", "nipple stimulation", "public indecency",  "public vibrator", 
    # ambiguous personality tags
    "multiple persona","fictional persona","dual personality","dual persona","dark persona", 'manly',"pervert","female pervert","nudist", 
    "zenra", "weight conscious", "breast conscious","expressions", "out of character", 
    
    # ambiguous tags on danbooru
    "hidden eyes","hidden face", "baton", "comparison", "too many","pot", "bad end",
    
    "youtube", "biribiri",'virtual youtuber',"deviantart","utaite", "shindan maker","self-upload","original","mmorpg","vtuber",
    "wallpaper","artist self-insert", "self-insert", "self upload",  "real life insert","voice actor","k-pop","animated",'photoshop (medium)', 
    'bad id', 'commentary', 'bad pixiv id', 'translated', 'english commentary', 'official art', 'bad twitter id',
    'commission', 'chinese commentary', 'md5 mismatch', 'symbol-only commentary', 'non-web source', 'korean commentary', 'partial commentary', 
    'revision', 'skeb commission', 'paid reward available', 'duplicate', 'bad link', 'check translation', 'video', 'spoilers', 'variant set', 
    'mixed-language commentary', 'second-party source', 'resolution mismatch', 'protected link', 'pixel-perfect duplicate', 'third-party edit', 
    'animated gif', 'pixiv commission', 'partially translated', 'third-party source', 'inactive account', 'ugoira', 'paid reward','ai-assisted', 
    'tagme', 'spanish commentary', 'has downscaled revision', 'countdown illustration', 'roulette animation', 'vietnamese commentary', 'recolored', 
    'medibang paint (medium)', 'stable diffusion', 'krita (medium)', 'metadata pun', 'reference request', 'style request', 'non-repeating animation', 
    'song request', 'volume warning', 'bleed through', 'animal request', 'thumbnail surprise', 'poorly translated', 'italian commentary',
    'microsoft powerpoint (medium)', 'bad baraag id', 'symbol request', 'sankaku sample', 'tagalog commentary', 'morse code commentary', 
    'malay commentary', 'bmp-to-jpg conversion', 'bad booth id', "garry's mod (medium)", 'check animal', 'missing thumbnail', 'low frame rate',
    'solid color thumbnail', 'newgrounds sample', 'gamma correction', 'poser (medium)', 'emblem request', 'jumpscare warning', 'subscribestar reward',
    'bcy sample', 'hidden file', 'poorly stitched', 'bad privatter id', 'flame painter', 'bad picasa id', 'engrish audio', 'origami (medium)', 
    'logo request', 'portuguese audio', 'motion interpolation', 'cyrillic commentary', 'felt (medium)', 'webp-to-jpg conversion', 'bad thumbnail', 
    'hard annotated', 'check commentary', 'imageboard desourced', 'source smaller', 'painttool sai (medium)', 'sound', 'derivative work', 
    'bad tumblr id', 'source larger', 'looping animation', 'bad source', 'image sample', 'textless version',  'patreon reward', 'dated commentary', 
    'promotional art', 'novel illustration', 'hard-translated', 'cropped', 'collaboration', 'bad deviantart id', 'commissioner upload', 
    'has bad revision', 'making-of available', 'resized', 'official wallpaper', 'audible music', 'bad nicoseiga id', 'audible speech', 'off-topic', 
    'pixiv sample', 'clip studio paint (medium)', 'photo-referenced', 'bad cgsociety id', 'bad postype id', 'color issue', 'bad e-hentai id', 
    'twitter banner', 'coupy pencil (medium)', 'bad pawoo id', 'bad patreon id', 'noise reduction', 'has watermarked revision', 'upscaled', 
    'webp-to-png conversion', 'maya (medium)', 'constellation request', 'adobe illustrator (medium)', 'reference work request', 'vector trace',
    'footwear request', 'drawcrowd sample', 'bad skeb id', 'wallpaper forced', 'charcoal (medium)', 'video game cover redraw', 'latin commentary', 
    'has lossy revision', 'binding discoloration', 'daz studio (medium)', 'lossless-lossy', 'creature request', 'check weapon', 'rotoscoping', 
    'midjourney', 'xnalara', 'bad imgur id', 'upside-down commentary', 'konachan sample', 'animatic','nicoseiga sample', 'gif artifacts', 
    'reversed', 'microsoft paint (medium)', 'german commentary','app filter', 'portuguese commentary', 'audible internal cumshot', 'screenshot',
    'flash game', 'bad aspect ratio', 'hairstyle request', 'bad fantia id', 'nai diffusion', 'fixed', 'custom maid 3d 2', 'has cropped revision', 
    'zip available', 'bad fanbox id', 'plant request', 'bad poipiku id', 'flipnote studio (medium)', 'bad drawcrowd id', 
    'check gender', 'art trade', 'bad tinami id', 'brush (medium)', 'color banding', 'bad newgrounds id', 'model kit (medium)', 'gouache (medium)', 
    'reference photo', 'cleaned', 'lego (medium)', 'easytoon (medium)','fan request', 'lofter sample', 'greek commentary', 'fruit request', 
    'pattern request', 'azpainter (medium)', 'bad miiverse id', 'weibo sample', 'polish commentary', 'bad behance id', 'tinami sample', 'check medium', 
    'acrylic gouache (medium)', 'video crop', 'bad artstation id', 'bad artstreet id', 'bad bcy id', 'bad behance id', 'bad bilibili id', 'bad blogspot id', 
    'bad cghub id', 'bad ci-en id', 'bad daum id', 'bad drawr id', 'bad dropbox id', 'bad facebook id', 'bad fandom id', 'bad google+ id', 'reverse translation',
    'bad hentai-foundry id', 'bad instagram id', 'bad lofter id', 'bad mihuashi id', 'bad miiverse id', 'bad misskey.io id', 'bad nijie id', 
    'bad photobucket id', 'bad pinterest id', 'bad reddit id', 'bad vkontakte id', 'bad weibo id', 'bad yandere id', 'bad youtube id', '60+fps', 
    'acrylic gouache (medium)', 'adobe fresco (medium)', 'adoptable', 'commentary typo', 'completion time', 'corel painter', 'corrupted file', 
    'corrupted flash', 'corrupted metadata', 'corrupted twitter file', 'costume request', 'has artifacted revision', 'has censored revision', 
    'has glazed revision', 'hashtag-only commentary', 'headshop', 'hentai-foundry sample', 'ibispaint (medium)', 'indonesian commentary','nude filter', 
    'open in internet explorer', 'opencanvas (medium)', 'paint.net (medium)', 'paintschainer','papercraft (medium)', 'partially annotated', 'pdf available',
    'mojibake commentary', 'music video', 'nekopaint (medium)',  'key visual', 'kirigami (medium)', 'kisekae', 'korean audio', 'latte art (medium)', 'live2d', 
    'lossy-lossless','custom maid 3d','vgen commission', 'video available', 'waifu2x', 'whiteboard fox (medium)', 'yandere sample', 'zalgo commentary',
    'zerochan sample', 'thai commentary', 'third-party watermark', 'tumblr sample', 'twitter sample', 'twitter thumbnail collage', 'ugoira conversion', 
    'ukrainian commentary','3d custom girl','album cover redraw', 'aliasing', 'alpha transparency', 'alt text', 'alternate language', 'amigurumi (medium)', 
    'animal ear request', 'animated png','annotated', 'arabic commentary', 'archived source', 'artbook', 'artstation sample', 'autodesk 3ds max (medium)', 
    'avatar generator', 'bmp-to-png conversion', 'book cover redraw', 'cd (source)', 'chalk (medium)', 'check annotation', 'check artist', 'check character', 
    'check clothing', 'check copyright', 'check flower', 'check food', 'check source', 'check spoilers', 'check vehicle', 'chinese audio', 'e-hentai sample', 
    'emofuri', 'end card', 'english audio', 'engrish commentary', 'enty reward', 'epilepsy warning', 'exif rotation', 'exif thumbnail surprise', 'extraction', 
    'eyecatch', 'fake translation', 'fanbox reward', 'fantia commission', 'fantia reward', 'fantia sample', 'fast animated gif', 'figure available', 'finnish commentary', 
    'flash', 'flash 9', 'flipaclip (medium)', 'french commentary', 'fudepen (medium)', 'game model', 'game screenshot', 'gesture request', 'ghosting', 'gibberish commentary', 
    'gift art', 'gimp (medium)', 'glaze artifacts', 'graffiti (medium)', 'guest art', 'gumroad reward', 'hard-translated (non-english)', 'romaji commentary', 'rotated', 
    'ruffle compatible', 'russian commentary', 'procreate (medium)', 'production art', 'psd available', 'rebelle (medium)', 'redrawn',  'interactive', 'japanese audio', 
    'jav', 'low bitrate', 'machine translated','screenshot redraw', 'self-portrait', 'serbo-croatian commentary', 'skima commission', 'source mismatch', 'spanish audio', 
    'spine (medium)', 'stitched', 'swedish audio', 'swedish commentary', 'tegaki draw and tweet', 'comic panel redraw','detexted','decensored', 'deviantart sample', 'disc menu', 
    'download link', 'downscaled', 'dutch commentary', 'making-of', 'masking tape (medium)', 'merchandise available', 'mixed-language audio', 'picrew (medium)', 'pixiv banner',
    'highres', 'absurdres', "hi res", "high res", "2d", "digital media", "digital media (artwork)", "absurd res", "patreon url", "twitter url", "pixiv url", "url",
    "artist cg","alternate version available", "alternate version at source",  "comission", "high resolution", "no text version", "oc", "unknown artist",
    "logo parody",
    
    
    'no headwear',"no testicles","no bangs", "no arms", "no symbol", "no hat",
    
    # gender, person, etc
    "sisters", "twins", "brothers", "brother and sister", "cousins","siblings",'bisexual female','father and son', 'brothers', 'family',
    'incest', 'mother and daughter','genderswap (ftm)', 'genderswap (mtf)', 'genderswap','multiple persona',"left-handed","reverse trap",
    "genderswap (otf)",'shimaindon (sex)',"shimaidon (sex)", "bisexual (female)", "ambiguous gender", "friends","father and daughter",
    "implied pregnancy","implied bisexual","implied fingering", "implied anal", "everyone","teenage",'aged up', 'aged down','mother and son',
    "group", "functionally nude male", "functionally nude female","gay","lesbian", "light-skinned femboy", "light-skinned male",
    "light-skinned futanari","light-skinned female", "pale-skinned femboy", "pale-skinned male", "male/female",
    "pale-skinned futanari","pale-skinned female","better than girls", "female with femboy", "female with female", 
    "female with face unlike mammal", "female with feral", "older","twink", "teen boy", "teen girl", "wife and wife and wife",
    "married", "swinging (relationship)", "inseki",
    
    # races
    "mithra (ff11)","warrior of light (ff14)","lalafell",
    
    "creature and personification","personification", "animification","humanization",
    "objectification", "animification", "animalization", "furrification", "vehicle and personification", 
    
    "platinum blonde hair", "light green hair","hair extensions","silver hair", "tied hair","hairlocs", "hair down",'sparse pubic hair', 
     "dark red hair", "low tied hair","light purple hair",  "dark green hair", "scattered hair", "hair up", "hair down","navel hair", "low braid",
    
    # clothing types 
    'alternate costume','official alternate costume','official alternate hairstyle', 'official alternate hair length',
    'alternate hairstyle', 'alternate hair length', 'alternate hair color','alternate legwear','alternate breast size',
    "alternate wings","alternate color","alternate shiny pokemon","alternate eye color","alternate headwear",
    "alternate muscle size","alternate form","alternate weapon", "alternate universe","alternate skin color",
    "galarian form","alolan form","alternate ass size", "alternate outfit", 
    
    "impossible clothes","impossible shirt","impossible bodysuit","impossible leotard","impossible dress",
    "impossible swimsuit","impossible sweater","impossible towel","impossible hair","impossible vest",
    "impossible jacket","impossible skirt","impossible armor","impossible pants","impossible necktie",
    "impossible shorts","impossible underwear","impossible tabard","impossible architecture","impossible apron",
    "impossible cardigan","impossible pelvic curtain","impossible sash", 'impossible clothes', 'impossible dress', 
    'impossible swimsuit','impossible bodysuit',
    
    "jacket partially removed","headphones removed", "single earphone removed","earphones removed","hat removed",
    "coat partially removed","shirt partially removed","male underwear removed","cardigan partially removed",
    "tail removed","thighhigh removed","leotard removed","halo removed","bracelet removed","kimono removed",
    "pendant removed","head removed","hakama removed","overalls removed","head wreath removed","coat removed",
    "pasties removed","ahoge removed","capelet removed","earmuffs removed","headset removed","swimsuit removed",
    "camisole removed","muneate removed","suspenders removed","neck ribbon removed", "choker removed","boot removed",   
    "ring removed","tiara removed","detached sleeves removed","hair tubes removed","horns removed", "pants removed",
    "ofuda removed","headdress removed","fundoshi removed","headpiece removed","tabard removed","helmet removed",
    "diving mask removed","brooch removed","prosthetic arm removed","haori removed", "shirt removed", "bra removed",
    "sweater vest removed","shorts removed", "socks removed", "jacket removed", "sandals removed","mask removed",
    "chastity cage removed","veil removed","monocle removed","robe partially removed", "necktie removed", 
    "fake animal ears removed","battery removed","flippers removed","detached collar removed","bikini removed",
    "crotch plate removed","suppressor removed","pauldron removed","earrings removed","eyewear removed",
    "handcuffs removed", "bikini top removed", "bikini bottom removed", "clothes removed", "goggles removed",
    "shoes removed", "headwear removed", "panties removed", "skirt removed", "legwear removed", "dress removed",
    "gloves removed", "boots removed", "backpack removed", "hairband removed",
    
    "artist request", "neckwear request", "headwear request", "commentary request", "sound effect request", "copyright request",
    "character request", "expression request", "pose request", "object request", "gender request", "character counter request",
    "color request", "clothing request", "voice actor request", "flower request", "parody request", "weapon request", "translation request",
    "aircraft request", "cosplay request", "medium request", "uncensor request", "sitting request", "meme request", "cat request", 
    "dog request", "bird request", "location request", "dinosaur request", "boy count request", "instrument request", "fish request",
    "item request","language request", "hair ornament request", "magazine request", "vehicle request", "mecha request", "collaboration request",
    "annotation request", "food request", "source request", "game request",
    
    "borrowed design", "borrowed hairstyle", "borrowed accessory", "borrowed character", "borrowed clothes",
    "borrowed pose",  "borrowed weapon", "borrowed inset", 'borrowed character',"matching outfit", "matching outfits",
    'adapted costume', "fan character",
    
    # time, events, date, etc
    "year of the dog", "year of the rat","year of the tiger", "year of the rabbit", "year of the dragon",
    "year of the ox", "year of the rabbit","year of the rooster", "year of the goat", "year of the pig", 
    "2000", "2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016",
    "2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","moe201", "moe2010","moe2011", 
    "moe2012","moe2013","moe2014","moe2015","moe2016","moe2017", "moe2018","moe2019","moe2020","moe2021","moe2022",
    "moe2023","moe2024", "cat day","miku day","angel day", "bunny day", "cat day", "fundoshi day", "gardevoir day", 
    "good ass day", "good breasts day", "good brothers day", "good meat day", "good twins day", "honey day",
    "ii fuufu no hi", "junko day", "koishi day", "maid day", "mario day", "masterbation day", 
    "meat day", "miko day", "miku day", "nice knee socks day", "nitori day", "nico day", "breasts day",
    "panties day", "pinnapple day", "rabbit day", "rubber day", "sagume day", "satori day", "sekibanki day",
    "stomach day", "succubus day", "wriggle day", "youmu day","pocky day", "anniversary", "april fools","coronavirus pandemic", 
    "happy new year","happy halloween", "happy valentine","historical event",'milestone celebration', "hatsumoude",
    "world war ii", "world war i","cold war","thank you","good end", "celebration", 
    
    "country connection","voice actor connection","company connection",  "trait connection","name connection", "trait connection",
    "historical name connection", "color connection", "stage connection","season connection", "creator connection",
    "crossover", "multiple crossover", "in-franchise crossover", "songover", "multiple crossover",
    
    "sailor moon redraw challenge", "one-hour drawing challenge","sailor moon redraw challenge (meme)","tawata challenge","oppai challenge",
    "multiple drawing challenge", "bubble tea challenge","one-hour drawing challenge","one finger selfie challenge",  "heart-shaped boob challenge",
    "they had lots of sex afterwards (meme)","special feeling (meme)","twitter strip game (meme)", "shirt cut meme",'meme','meme attire', 
    "when you see it",'parody','style parody', "pun","cameo", "they had lots of sex afterwards", 'what', 'what if',"you work you lose",
    "twitch plays pokemon", "title parody", "player 2", "player 3", "player 4","you gonna get eaten", "deal with it","breast contest",
    "late for school", "you gonna get raped","ai ai gasa", "take your pick", "like and retweet","plap","you're doing it wrong",
    "scene reference", "yaranaika","if they mated","time paradox", "iced latte with breast milk (meme)","image macro (meme)",
    # group names and costume names
    "holomyth", "holoforce", "hololive gamers", "holomyth","holocouncil", "holox", "hololive fantasy", "mod3 (girls' frontline)", 
    "penguin logistics (arknights)", "make up in halloween! (umamusume)","danganronpa 10th anniversary costume","k/da (league of legends)",
    "lazy lazy (idolmaster)","noctchill (idolmaster)","triad primus (idolmaster)","straylight (idolmaster)", "starting brighty (idolmaster)",
    "starry sky bright (idolmaster)", "kawaii boku to 142's (idolmaster)", "individuals (idolmaster)","new generations (idolmaster)",
    "grass root yokai network","team7", "roselia (bang dream!)", "princess form (smile precure)", "wicked dragon witch ver. shinjuku 1999",
    "starter pokemon trio","millennium cheerleader outfit (blue archive)", "inazuma japan","jet black king of knights ver. shinjuku 1999",
    "wicked dragon witch ver. shinjuku 1999", "kimi no kokoro wa kagayaiteru kai?", "korekara no someday", "raimon","song name", 
    "39","adrenaline!!!", "common race outfit (umamusume)", "chaldea lifesavers", "akatsuki (naruto)","griffin & kryuger","team 9", 
    "heroic spirit festival outfit", "heroic spirit formal dress", "heroic spirit traveling outfit","grifon & kryuger","okamisty",
    "heroic spirit dream portrait", "octarian", "memories at trifas","true ether chaldea uniform", "pink check school (idolmaster)",
    "bokutachi no seizon tousou (project sekai)", "our escape for survival (project sekai)", "love laika (idolmaster)","netnavi", 
    "bokutachi wa hitotsu no hikari", "chimame-tai", "holofive","kiwame (touken ranbu)", "knights of the round table (fate)",
    "seizon honnou valkyria (idolmaster)","defy (girls' frontline)","crisis management form (machimazo)","404 (girls' frontline)",
    "anti-rain (girls' frontline)", "oripathy lesion (arknights)","inner senshi", "outer senshi","bokura wa ima no naka de",
    "yume no tsue", "fuuin no tsue", "hoshi no tsue","choujuu gigaku","eiserne jungfrau","nt-d","error musume", "sexy no jutsu",
    "sailor moon narikiri bra set","twinmyniad (fate)", "seikan hikou", 'v4x',"kimi to boku no mirai", "heavenly boat maanna",
    "star guardian (league of legends)","reality arc (sinoalice)","silent princess", "vocaloid append","voyakiloid","nepolabo", 
    "walkure (macross delta)","pikapikapop (idolmaster)","retrofit (azur lane)","remodel (kantai collection)","reiwa","emerald float",
    "originium (arknights)", "originium arts (arknights)", "meslamtaea (weapon)","jikan sokougun","inkling (language)","zeus (inazuma eleven)",
    "ortenaus", 'mogyutto "love" de sekkin chuu!', "s.m.s.","justice task force (blue archive)",
    # company names
    "eotech","materia", "heckler & koch","speedo (company)", "brand name imitation", "arena (company)","asics","arisaka", 
    "mitsukoshi (department store)","product placement", "walther","mazda",
    
    "red legwear","ribbon-trimmed legwear",  "pink legwear", "blue legwear", "white legwear","brown legwear", 
    "fishnet legwear", "orange legwear",  "torn legwear", "grey legwear","purple legwear","black legwear",
    "plaid neckwear","red neckwear","blue neckwear", "checkered neckwear", "black neckwear","multicolored neckwear",
    "purple neckwear","pink neckwear","white neckwear", "green neckwear", "orange neckwear", "yellow neckwear",
    
    "ranguage","finnish ranguage","french ranguage","german ranguage","greek ranguage","latin ranguage","engrish",
    
    "beige jacket","beige cardigan", "beige sweater","beige shirt",  
    
    'sperm cell',
    
    "textless", "textless version",
    
    'fusion',  'convenient censoring', 'star of david', 'cosplay', "evolutionary line",  "macro", "micro", "diagonal stripes", 
    'pointless condom', 'dakimakura (medium)',  'multicolored', 'dimples of venus', "stance", "symbol", "seat",  "vertical stripes", 
    'character name', 'profanity',  "glands of montgomery",  "manakete","clothes theft", "pouty lips",  "hand on shoulder","himejoshi",
    "japari symbol", "unfinished",  "inconvenient breasts", "zettai ryouiki", "ambiguous penetration",  "hand on breast", "pokemon (game)", 
    "accidental exposure","wardrobe malfunction",  "nerv", "italian flag", "french flag","sex ed", "e.g.o (project moon)", "martini","squidbeak splatoon", 
    "bespectacled","enmaided",  "contemporary",   "science fiction", "male hand", "toe-point", "lifting",  "striped", "multiple penises",
    "tied up (nonsexual)",  "kupaa", "pet shaming", "alraune",  "touching", "oil", "fume", "lavender background", "landmark", "pipe", 
    "ready to draw", "ponytail holder","miqo'te","pose imitation","kanji namesake",  "texture",  "doujinshi",  "beige background", 
    "open eyes","nude model",  "koonago",  "elezen", "hyur","utaite (singer)","shinto",  "wehrmacht",  "casual one-piece swimsuit",
    "confrontation", "kakizome", "ips cells",  "khakis",   "saigyouji yuyuko's fan design",   
    "happy facial",   "can't show this",  "nico nico nii", "kemonomimi mode", "innerboob",  "big eyes", "listening to music",
    "virtual reality", "toddlercon","sangvis ferri", "draph","holding up", "noise", "unusually open eyes", 
    "evo grim", "eromanga", "chinese zodiac", "can't be this cute", "burmecian", "paradeus", "elvaan","leaning over", "slave tattoo",   
    "prototype design",   "frontless outfit", "viera", "anti-aircraft",  "self exposure", "case", "watery eyes", "open arms", 
    "height", "piercing bunny", "dream soul",  "bad food", "action", "agrius metamorphosis","object namesake", "timeskip", "light beam",
    "color guide", "back cover",  "take it home", "dirigible",  "namesake","doukyo's",  "oppai mochi", "pullover","oni horns", 
    "fake screenshot", "checkered", "shiny", "drawing",  "multi-strapped bikini", "gradient", "framed", "visor",  "out of character",
    "predicament bondage", "numbers (nanoha)", "date pun", "number pun", "right-hand drive","left-hand drive",  "in mouth", "mechanical", 
    "heads-up display", "everyone",   "symbol", "symbolism",'emotional engine - full drive',"tucking",   "mid-stride",
    "shatter", "board", "pepper", "underskirt", "black clothes", "shoulder cape", "beam", "multiple straps", 
    "akg", "u.n. spacy","blade","hand on thigh", "bookbag", "long jacket",
    "side-tie bottom", "underskirt", "luggage", "magi mogu mogu", "remodel (kantai collection)"
       
}
HIGH_TOKEN_COUNT = {"eyebrows visible through hair", "heart-shaped pupils", "navel piercing", "tongue piercing", "ass visible through thighs", "asymmetrical hair", "cum on body", "cum on breasts"}

UNRELIABLE_SMALL_TAGS={"piercing", "pupils", "ring", "rings", "piercings"}

# Quality tags
QUALITY_LABELS = ["worst", "worse", "average", "good", "great", "best", "masterpiece"]
QUALITY_LABELS_MAPPING = {
    'masterpiece': 0.85,
    'best': 0.75,
    'great': 0.6,
    'good': 0.4,
    'average': 0.15,
    'worse': 0.08,
    'worst': 0.0,
}

# Emojis separated into groups depending on popularity and the "_UNIQUE" groups
# are the tags without a good tag replacement/breakdown
EMOJI_10KPLUS = {
    ";)":["closed mouth", "smile", "one eye closed"],
    ":d":["open mouth", "smile"],
    ";d":["open mouth", "smile", "one eye closed"],
    ":p":["tongue out", "closed mouth"],
    ">:)":["smile", "v-shaped eyebrows", "closed mouth"],
    ":o":["open mouth"],
    "...": ["spoken ellipsis"],
}
EMOJI_10KPLUS_UNIQUE = {
    ":q":["licking lips", "closed mouth"],
    "o_o":["surprised", "wide-eyed"],
    "^_^":["closed eyes"],
    ":3":["smile"],
    ":<":["closed mouth", "frown"],
    ":>":["smile"],
    ":>=":["sunken cheeks", "fellatio"],
    "|_|":["emotionless"],
    ">_<":["closed eyes"],
    "@_@":["confused"],
    ":t":["pout", "puffy cheeks"],
    "+_+":["excited", "symbol-shaped pupils", "sparkle"],
    "=_=":["closed eyes"],
    "!": ["exclamation mark", "surprised"],
    "!!": ["double exclamation mark", "surprised"],
    "?": ["question mark", "confused"],
    "??": ["question mark", "confused"],
    "!?": ["surprised", "confused"],
    "^^^":["trembling"],
    "+++":["laughter"],
    "x_x":["dead"]
    
}
EMOJI_5KPLUS = {
    "xd":["closed eyes", "open mouth", "smile"],
    "d:":["open mouth"],
    "3:":["angry", "frown"],
    ":p":["tongue out", "closed mouth", "one eye closed"],
    ">:(":["frown", "v-shaped eyebrows", "closed mouth", "annoyed"],
    ":/":["closed mouth", "bored", "dissapointed"],
    ":|":["closed mouth", "emotionless"],
    ";o":["one eye closed", "open mouth"],
    "0_0":["surprised", "wide-eyed"],
    ";p":["tongue out", "closed mouth", "one eye closed"]
}
EMOJI_MINOR = {
    ";3":[":3", "smile", "one-eye closed"],
    "uwu": ["closed eyes", "closed mouth", "smile", "smug"],
    ";q":[":q", "one eye closed", "closed mouth", "tongue out"],
    ":i":[":t", "pout", "puffy cheeks"],
    ":x":["closed mouth"],
    ":c":["frown", "closed mouth"],
    "c:":["closed mouth", "smile"],
    ";<":[":<", "closed mouth", "one eye closed"],
    "o3o":["puckered lips"],
    ">3<":["closed eyes", "puckered lips"],
    "._.":["dot pupils"],
    "^o^":["^_^", "closed eyes", "open eyes"],
    "\(^o^)/":["open mouth", "arms up"],
    "^q^":[],
    "x3":[">_<", "closed eyes", "closed mouth"],
    ">o<":[">_<", "closed eyes", "open mouth"],
    ">_@":["one eye closed"],
    "+_-":["one eye closed", "excited", "symbol-shaped pupils", "sparkle"],
    "=^=":["closed eyes"],
    "=v=":["closed eyes"],
    "<o>_<o>":["wide-eyed", "staring"],
    "<|>_<|>":["slit pupils"],
    ";(":["one eye closed", "frown"],
    ">_o":["one eye closed", "wink"]
}

KAOMOJI = {"0_0","(o)_(o)","+_+","+_-","._.","<o>_<o>","<|>_<|>","=_=",
            ">_<","3_3","6_9",">_o","@_@","^_^","o_o","u_u","x_x","|_|","||_||"
            }

# these are parts of tags that centers around things that are in parenthesis
# these are used in the dataset cleaning tab and used to filter things that really don't matter
# during training.
# the only exceptions to the blacklist is in the series exception below
SERIES_BLACKLIST = {
    "(idolmaster)", "(arknights)", "(kantai collection)", "(kancolle)", "(cosplay)", 
    "(league of legends)", "(homestuck)", "(azur lane)", "(rwby)","(nikke)",
    "(zelda)", "(fate)", "(fate/stay night)", "(fire emblem)", "(genshin_impact)",
    "(evangelion)", "(youkai watch)", "(sao)"
}
# These have more than 1k results and is probably learned so we can keep them
SERIES_EXCEPTION = {
    "hakurei reimu (cosplay)", "hatsune miku (cosplay)", "shimakaze (kancolle) (cosplay)",
    "excalibur (fate/stay night)", "gae bolg (fate)", "excalibur morgan (fate)", "lord camelot (fate)",
    "vision (genshin impact)", "musou isshin (genshin impact)", "e.g.o (project moon)", "champion's tunic (zelda)"
}

# looking for colours: https://html-color.codes/orange
# RED>TAN:
# ORANGE>YELLOW:
# LIME>GREEN:
# TEAL>NAVY:
# PURPLE>PINK:
# GREY>BLACK:
COLOR_CATEGORIES = {
# RED>TAN:
    "STATE":(255,53,94), # Radical Red
    "COUNT":(255, 99, 71), # tomato
    "MODELS":(165, 42, 42), # red
    "OCCUPATION": (220, 20, 60), # Crimson
    "EYES COLOR ALL": (255, 69, 0), # Orange red
    "RACE":(218,165,32), #  Goldenrod
    "FAKE EARS ALL": (218,165,32), # same as RACE
    "ANIMALS":(218,165,32), # Goldenrod
    "ACCESSORIES": (203, 65, 84), # Brick Red, prev:(100,140,17) bitter green
    "MAKEUP": (207,16,32), # Lava
# ORANGE>YELLOW:
    "VEHICLE":(230,0,38), #Spanish Red, 
    "ENVIRONMENT":(255,140,0), # Dark Orange
    "HANDHELD OBJECT":(251,79,20), # orioles orange
    "INTERACTIVE OBJECTS":(204,160,29), # Lemon Curry
    "ACTION":(218,145,0), # harvest gold
    "FOOD":(250,128,114), # salmon
    "WEAPON": (226,88,34), # flame
# LIME>GREEN:
    "CLOTHES":(0,128,0), # green
    "CLOTHES COLOR":(100,140,17), #Bitter Lime
    "CLOTHES TIGHT":(0,192,0), # green
    "CLOTHES ACTION":(50,205,50), # Lime Green
    "CLOTHES SWIMSUIT":(143,188,143), # dark Sea Green
    "CLOTHES PARTS": (60,179,113), # Medium Sea Green
    "SHOES":(107,142,35), # olive drab
    "CLOTHES EASTERN":(0,255,127), # Spring Green
# TEAL>NAVY:
    "LOWER BODY": (100,149,237), # Corn Flower Blue
    "BREASTS SIZE":  (0,139,139), # dark cyan
    "UPPER BODY": (0,139,139), # dark cyan
    "HEAD": (0,206,209), # Dark Turquoise
    "BODY": (0,191,240), # Deep Sky Blue
    "BODY SHAPE": (0,191,240), # Deep Sky Blue
    "EMOTIONS": (127,255,0), # Chartreuse
    "APPENDICES": (176,224,230), # Powder Blue
    "CHARACTERS": (0,204,204), # Robin Egg Blue
    "CHARACTERS_LESSER": (0,150,152),#Viridian Green
# PURPLE>PINK:
    "SEX GENERAL ALL":(191,0,255), # Electric Purple
    "CUM ALL": (245,245,220), # Beige
    "SEX":(255,105,180), # Hot Pink
    "SEX ACTION": (226,80,152), # Raspberry Pink
    "SEX TOY": (255,0,127), #Rose
    "TENTACLES":(204,0,255), # Vivid Orchid
    "POSITION":(123,104,238), # medium slate blue
    "VIEW":(199,21,133), # medium violet red
    "FETISH GROUPS":(199,21,133), # medium violet red
    "HAIR COLOR ALL": (212,115,212), # French Mauve
    "HAIR LENGTH": (223,115,255), # Heliotrope
    "HAIR": (223,115,255), # Heliotrope
    "HOLDING": (228,0,124), #Mexican Pink
# GREY>BLACK:
    "ABSENCE":(8,232,222), # Bright Turquoise
    "PIERCING": (172,172,172), # Silver Chalice
    "OTHER":(201,192,187), # Pale Silver
    "TATTOO": (211,211,211), # Light Grey
    "EXTREME": (227,0,34) # Cadmium Red
}



# this is the order in which tags are going to be listed, categories not includes will be added to the end
COLOR_DICT_ORDER = [
                    "MODELS","COUNT", "OCCUPATION","FETISH GROUPS", "RACE", "FAKE EARS ALL","ANIMALS", "VEHICLE", "ENVIRONMENT",
                    "BODY SHAPE","EYES COLOR ALL", "HAIR COLOR ALL","HAIR LENGTH", "HAIR", "HEAD","EMOTIONS",
                    "BREASTS SIZE","UPPER BODY","BODY","LOWER BODY","APPENDICES","ABSENCE",
                    "CLOTHES", "CLOTHES TIGHT", "CLOTHES COLOR","CLOTHES EASTERN", "CLOTHES PARTS", 
                    "SHOES",
                    "MAKEUP", "TATTOO", "PIERCING", "ACCESSORIES",
                    "CLOTHES ACTION", "ACTION", "POSITION", "SEX GENERAL ALL","CUM ALL", "SEX TOY", "SEX", "SEX ACTION", "TENTACLES",
                    "HOLDING", "HANDHELD OBJECT", "INTERACTIVE OBJECTS", "FOOD", "WEAPON",
                    "OTHER","STATE", "VIEW", "EXTREME",
                    "CHARACTERS", "CHARACTERS_LESSER"
                    ]
COLOR_DICT_ORDER += [category for category in COLOR_CATEGORIES.keys() if category not in COLOR_DICT_ORDER]


SOLO_CONFLICTS = {
   "GENDER-SOLO": {"1girl","1boy"},
   "RACE-SOLO":{"furry male", "furry female"}
}

p_threshold = 0.7
remove_low_threshold_list = ['ahegao', 'navel piercing', 'clitois piercing', 'tongue piercing',
                                'heart-shaped pupils', 'symbol-shaped pupils', 'thumb ring','cumdrip',
                                'cum in pussy', 'after sex', 'after vaginal', 'after anal', 'vaginal', 'anal',
                                'dildo', 'vaginal object insertion', 'anal object insertion', 'object insertion'
                                
] + list(EMOJI_10KPLUS_UNIQUE.keys()) + list(EMOJI_10KPLUS.keys())

def get_main_optional_csv_reader(main_file, additional_data="", user_file_str=""):
    # used to read both recommendation and tag_categories and merge them, additional data is optional
    with open(main_file, newline='', encoding='utf-8') as f:
        complex_temp = list(csv.reader(f))
    if user_file_str and os.path.exists(additional_data):
        with open(additional_data, newline='', encoding='utf-8') as f:
            complex_temp2 = csv.reader(f)
            
            # Peek first row of complex_temp2
            first_row = next(complex_temp2, None)
            if first_row and ("recommend" in first_row[0].strip().lower()):
                # assume second csv has a header
                # skip this row → do nothing, reader2 is already advanced
                #parameters.log.info(f"detected header in {user_file_str}, skipping first row")
                complex_temp2 = list(complex_temp2) # skipping header
            else:
                # put first row back if it wasn’t a header
                complex_temp2 = [first_row] + list(complex_temp2) if first_row else []
        
        merged_csv_reader = itertools.chain(complex_temp, complex_temp2)
        parameters.log.info(f"Additional {user_file_str} detected, added {len(complex_temp2)} lines")
    else:
        merged_csv_reader = complex_temp      
    
    return merged_csv_reader

def get_recommendations_from_csv():
    complexer = {}
    skip_first = True
    user_file_str = "resources/user_recommendations.csv"
    main_file = os.path.join(parameters.MAIN_FOLDER, "resources/recommendations.csv")
    additional_data = os.path.join(parameters.MAIN_FOLDER, user_file_str)
    
    merged_csv_reader = get_main_optional_csv_reader(main_file, additional_data, user_file_str) 
    
    for row in merged_csv_reader:
        if skip_first:
            skip_first = False
            continue
        recommended = [x.strip().lower() for x in row[0].split(',') if x != ""]
        triggers: list[list[str]] = []
        col = 1
        while col < len(row) and row[col]:
            triggers.append([x.strip().lower() for x in row[col].split(',') if x != ""])
            col+=1
            
        for recomm in recommended:
            if recomm in complexer.keys():
                complexer[recomm] = complexer[recomm] + [trigger for trigger in triggers if not any(all([tag in recomm_sample for tag in trigger]) for recomm_sample in complexer[recomm])]
            else:
                complexer[recomm] = triggers
    return complexer

def get_tag_categories_from_csv():
    complexer = {}
    user_file_str = "resources/user_categories.csv"
    main_file = os.path.join(parameters.MAIN_FOLDER, "resources/tag_categories.csv")
    additional_data=os.path.join(parameters.MAIN_FOLDER, user_file_str)
    
    merged_csv_reader = get_main_optional_csv_reader(main_file, additional_data, user_file_str)
    
    skip_first = True
    for i, row in enumerate(merged_csv_reader):
        if skip_first:
            skip_first = False
            continue
        category = row[0].strip().upper()
        sub_category = row[1].strip().upper()
        exclusive = False
        if row[2]:
            if int(row[2]) == 1:
                exclusive = True
        high = [x.strip().lower() for x in row[3].split(',') if x != ""]
        low = [x.strip().lower() for x in row[4].split(',') if x != ""]
        tags = []
        for tag in row[5].split(','):
            if tag.strip().lower() != "" and tag.strip().lower() not in tags:
                tags.append(tag.strip().lower())
        dict_row = {
            sub_category: {
                "exclusive": exclusive,
                "high": high,
                "low": low,
                "tags": tags
            }
        }
        if not category in complexer.keys():
            complexer[category] = {}
        complexer[category].update(dict_row)
    return complexer

def get_tag_definition():
    complexer = {}
    with open(os.path.join(parameters.MAIN_FOLDER, "resources/tag_definition.csv"), newline='', encoding='utf-8') as f:
        complex_temp = csv.reader(f)
        for row in complex_temp:
            tag = row[0].strip()
            description = row[1].strip()
            complexer[tag] = description
    return complexer

def check_categories():
    main_category = set(TAG_CATEGORIES.keys())
    sub_category = []
    sub_count = 0
    
    # checking for same named categories
    for mc in main_category:
        sub_cat = list(TAG_CATEGORIES[mc].keys())
        sub_category.extend(sub_cat)
        sub_count += len(sub_cat)
    if len(set(sub_category)) != sub_count:
        from tools.files import get_duplicate_string
        dupes = get_duplicate_string(sub_category)
        parameters.log.info(("CHECK! check sub categories for any duplicates", dupes))
    if main_category.intersection(set(sub_category)):
        parameters.log.info(("CHECK! don't have common names in main and sub categories", main_category.intersection(set(sub_category))))
        
    # checking for same tag in low and tag category
    for main_cat, subcat in TAG_CATEGORIES.items():
        for subcat_name, tg in subcat.items():
            low_tags = tg["low"]
            tags = tg["tags"]
            if low_tags:
                repeated_tag = any([a in tags for a in low_tags])
                if repeated_tag:
                    rp_tags = [a for a in low_tags if a in tags]
                    parameters.log.info(f"CHECK! self-referencial tags {main_cat}, {subcat_name}: {rp_tags}")
        
def make_tag_colors_dict():
    # returns a dict "tag" --> associated color for visuals
    alphas = 255
    # black = (0,0,0, 255)
    color_dict = dict()
    category_to_tags_dict = {c:[] for c in COLOR_CATEGORIES.keys()}
    priority_dict = defaultdict(lambda: 0)
    tag2category = defaultdict(lambda: set()) # TAG --> list[CATEGORIES]
    for main_category, value in TAG_CATEGORIES.items():
        for sub_category, descriptions in value.items():
            if sub_category in COLOR_CATEGORIES: # sub category takes priority
                red, green, blue = COLOR_CATEGORIES[sub_category]
                for tag in descriptions["tags"]+descriptions["low"]+descriptions["high"]:
                    color_dict[tag] = (red, green, blue, alphas)

                    if tag not in priority_dict.keys():
                        priority_dict[tag] = COLOR_DICT_ORDER.index(sub_category)

                category_to_tags_dict[sub_category] = descriptions["tags"]+descriptions["low"]+descriptions["high"]
             
            elif main_category in COLOR_CATEGORIES:
                red, green, blue = COLOR_CATEGORIES[main_category]
                for tag in descriptions["tags"]+descriptions["high"]:
                    if tag not in color_dict:
                        color_dict[tag] = (red, green, blue, alphas)

                        if tag not in priority_dict.keys():
                            priority_dict[tag] = COLOR_DICT_ORDER.index(main_category)
                category_to_tags_dict[main_category].extend(descriptions["tags"]+descriptions["high"]+descriptions["low"])
                #category_to_tags_dict[main_category].extend([t for t in descriptions["low"] if tag not in color_dict]) 
                
                for tag in descriptions["low"]:
                    if tag not in color_dict:
                        color_dict[tag] = (red, green, blue, alphas)

                        if tag not in priority_dict.keys():
                            priority_dict[tag] = COLOR_DICT_ORDER.index(main_category)
            for tag in descriptions["tags"]+descriptions["high"]+descriptions["low"]:
                tag2category[tag].add(main_category)
    for k, v in category_to_tags_dict.items():
        category_to_tags_dict[k] = sorted(set(v))
    
    return color_dict, category_to_tags_dict, priority_dict, tag2category

def get_tag_categories_belonging():
    # this handles the categories and it's tags
    category_exclusive = {} # category name --> SET of tags
    category_nonexclusive = {}

    # these dictionaries stores the tag replacements
    tag2high = {} # TAG --> [list of HIGH tags it should be converted to, usually only 1]
    exclusive_high2tags = {} # HIGH --> TAGS
    low2tags = {} # LOW --> TAGS
    tag2subcategory_exclusive = defaultdict(lambda: []) # TAG --> list[SUB_CATEGORIES]
    for category_name, category in TAG_CATEGORIES.items():
        for subcat_name, subcat in category.items():
            # this if-elif handles the tag replacements
            if subcat["high"]:
                for high_tag in subcat["high"]:
                    if False: #subcat["exclusive"]: # for this conversion, all must be matching
                        pass
                        #exclusive_high2tags[high_tag] = subcat["tags"]
                    else: # all tags in TAGS and LOW are converted to high
                        for tag in subcat["tags"]:
                            tag2high[tag] = tag2high.get(tag, []) + [high_tag]
            if subcat["low"]: # only LOW and TAGS
                for low_tag in subcat["low"]:
                    low2tags[low_tag] = low2tags.get(low_tag, []) + subcat["tags"]
            
            # Code below handles the categories
            if subcat["exclusive"]:
                tags_set = set(subcat["high"]+subcat["low"]+subcat["tags"])
                category_exclusive[subcat_name] = tags_set
                for tag in tags_set:
                    tag2subcategory_exclusive[tag].append(subcat_name)
            else:
                category_nonexclusive[subcat_name] = subcat["high"]+subcat["low"]+subcat["tags"]

    return category_exclusive, category_nonexclusive, tag2high, exclusive_high2tags, low2tags, tag2subcategory_exclusive

def csv_get_type():
    """
    :param num: 0 is for common tags, 1 for artists, 3 for series, 4 for characters, 5 for metadata
    :return: 5 dicts corresponding to all tags and their counterparts
    """
    DESCRIPTION_TAGS = {}
    DESCRIPTION_TAGS_FREQUENCY = {}
    ARTISTS_TAGS = {}
    SERIES_TAGS = {}
    CHARACTERS_TAG = {}
    CHARACTERS_TAG_FREQUENCY = {}
    METADATA_TAGS = {}
    DANBOORU_TAG2HIGH = {}
    DANBOORU_LOW2TAGS = {}
    with open('./resources/danbooru_tags.csv', newline='', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            secondary_tags = []
            if len(row[0]) > 3 and row[0] not in KAOMOJI:
                main_tag = row[0].replace('_', ' ').lower() 
            else:
                main_tag = row[0].lower()
            if len(row) > 3:
                secondary_tags = row[3].split(",")
                secondary_tags = [tag.replace('_', ' ').lower() if len(tag) > 3 and tag.lower() not in KAOMOJI else tag for tag in secondary_tags]
                for sub_tag in secondary_tags:
                    DANBOORU_LOW2TAGS[sub_tag] = main_tag
                    DANBOORU_TAG2HIGH[sub_tag] = main_tag

            #main tag is basic tags like 1girl, solo, large breasts, ...
            # secondary tags is a list of tags that are converted to the main tag like "large_boobs", "large_tits"
            # secondary tag can be an empty list
            match int(row[1]):
                case 0:
                    DESCRIPTION_TAGS[main_tag] = secondary_tags
                    DESCRIPTION_TAGS_FREQUENCY[main_tag] = row[2]
                case 1:
                    ARTISTS_TAGS[main_tag] = secondary_tags
                case 3:
                    SERIES_TAGS[main_tag] = secondary_tags
                case 4:
                    CHARACTERS_TAG[main_tag] = secondary_tags
                    CHARACTERS_TAG_FREQUENCY[main_tag] = row[2]
                case 5:
                    METADATA_TAGS[main_tag] = secondary_tags

    return DESCRIPTION_TAGS, DESCRIPTION_TAGS_FREQUENCY, ARTISTS_TAGS, SERIES_TAGS, CHARACTERS_TAG, CHARACTERS_TAG_FREQUENCY, METADATA_TAGS, DANBOORU_LOW2TAGS, DANBOORU_TAG2HIGH

# note, tag_category_exclusive is a dict of sets
# we make a set just for the keys because we often check for inclusions
DESCRIPTION_TAGS, DESCRIPTION_TAGS_FREQUENCY, ARTISTS_TAGS, SERIES_TAGS, CHARACTERS_TAG, CHARACTERS_TAG_FREQUENCY, METADATA_TAGS = {}, {},{}, {},{}, {},{}
TAG_CATEGORIES_EXCLUSIVE,TAG_CATEGORIES_NONEXCLUSIVE, TAG2HIGH, EXCLUSIVE_HIGH2TAGS, LOW2TAGS, TAG2SUB_CATEGORY_EXCLUSIVE = None, None, None, None, None, None
TAG_CATEGORIES = {}
TAGS_RECOMMENDATIONS = {}
CHARACTER_RECOMMENDATIONS = {}
TAG2HIGH_KEYSET = set()
LOW2TAGS_KEYSET = set()
COLOR_DICT = {}
PRIORITY_DICT = {}
TAG2CATEGORY = {}
CATEGORY_TAG_DICT = {}
TAG_DEFINITION = {}

char_manuals = ['TAIMANIN_SERIES' , 'MANUAL_CHAR_FGO_GAME', 'MANUAL_CHAR_FGO_ANIME','MANUAL_CHAR_F_STAYNIGHT',
                'MANUAL_CHAR_MISC' ,'MANUAL_CHAR_UMINEKO' ,'MANUAL_CHAR_BLEACH' , 'MANUAL_CHAR_AOT',"MANUAL_CHAR_ISEKAI","MANUAL_CHAR_SEITOKAIYAKUIN",
                'MANUAL_CHAR_BLACK_LAGOON_JORMUNGND' ,'MANUAL_CHAR_WORLD_TRIGGER' , 'MANUAL_CHAR_NARUTO', 'MANUAL_CHAR_FAIRYTAIL',
                'MANUAL_CHAR_CONAN' ,'MANUAL_CHAR_FRIEREN' ,'MANUAL_CHAR_GITS' ,'MANUAL_CHAR_GAMES' , "MANUAL_CHAR_POKEMON","MANUAL_CHAR_QUEENSBLADE",
                'MANUAL_CHAR_GUNDAM_UC','MANUAL_CHAR_GUNDAM_00', 'MANUAL_CHAR_GUNDAM_ALT', 'MANUAL_CHAR_GUNDAM_WITCH','MANUAL_CHAR_INAZUMAILLEVEN' ,'MANUAL_CHAR_JUMP' ,
                'MANUAL_CHAR_WESTERN','MANUAL_CHAR_NIJI', 'MANUAL_CHAR_VTUBERS','MANUAL_CHAR_3D','COSPLAY_LIST']


def tag_categories_init():
    # f*ck it we load these as global variables, ugly but it works and too many dicts to pass around
    global COLOR_DICT, CATEGORY_TAG_DICT, TAG_DEFINITION, TAG2HIGH_KEYSET, LOW2TAGS_KEYSET, TAG_CATEGORIES_EXCLUSIVE, \
    TAG2HIGH, EXCLUSIVE_HIGH2TAGS, LOW2TAGS, TAG_CATEGORIES, TAGS_RECOMMENDATIONS,TAG_CATEGORIES_NONEXCLUSIVE,\
    DESCRIPTION_TAGS, DESCRIPTION_TAGS_FREQUENCY, ARTISTS_TAGS, SERIES_TAGS, CHARACTERS_TAG, CHARACTERS_TAG_FREQUENCY, \
    METADATA_TAGS, TAG2SUB_CATEGORY_EXCLUSIVE, PRIORITY_DICT, TAG2CATEGORY
    
    DESCRIPTION_TAGS, DESCRIPTION_TAGS_FREQUENCY, ARTISTS_TAGS, SERIES_TAGS, CHARACTERS_TAG, CHARACTERS_TAG_FREQUENCY, METADATA_TAGS, DANBOORU_LOW2TAGS, DANBOORU_TAG2HIGH = csv_get_type()
    TAG_CATEGORIES = get_tag_categories_from_csv()
    TAGS_RECOMMENDATIONS = get_recommendations_from_csv()
    
    COLOR_DICT, CATEGORY_TAG_DICT,PRIORITY_DICT, TAG2CATEGORY = make_tag_colors_dict()
    TAG_CATEGORIES_EXCLUSIVE, TAG_CATEGORIES_NONEXCLUSIVE, TAG2HIGH, EXCLUSIVE_HIGH2TAGS, LOW2TAGS, TAG2SUB_CATEGORY_EXCLUSIVE = get_tag_categories_belonging()
    
    TAG_DEFINITION = get_tag_definition()
    """
    for key, value in DANBOORU_TAG2HIGH.items():

        if key in TAG2HIGH and value not in TAG2HIGH[key]:
            TAG2HIGH[key].append(DANBOORU_TAG2HIGH[key])
        else:
            TAG2HIGH[key] = [DANBOORU_TAG2HIGH[key]]

    for key, value in DANBOORU_LOW2TAGS.items():

        if key in LOW2TAGS and value not in LOW2TAGS[key]:
            LOW2TAGS[key].append(DANBOORU_LOW2TAGS[key])
        else:
            LOW2TAGS[key] = [DANBOORU_LOW2TAGS[key]]
    """

    TAG2HIGH_KEYSET = set(TAG2HIGH.keys())
    LOW2TAGS_KEYSET = set(LOW2TAGS.keys())
    
    character_subcats = ['KNOWN_CHARACTERS_1' ,'KNOWN_CHARACTERS_2'] + char_manuals
    character_lesser_subcats = ['CHARACTER_MINOR_1' , 'CHARACTER_MINOR_2' ,'CHARACTER_MINOR_3' ,
                                'CHARACTER_MINOR_4' ,'CHARACTER_MINOR_5' ,'CHARACTER_MINOR_6']
    
    from resources import parameters
    try:
        fav_file = os.path.join(parameters.MAIN_FOLDER, 'resources/favourites.txt')
        if os.path.exists(fav_file):
            with open(fav_file, 'r') as f:
                favourites = [tag.strip() for tag in f.readline().split(',') if tag != ""]
        else:
            favourites = []
        previous_favourites = favourites.copy()
    except Exception as e:
        raise Exception(f"Error loading favourites.txt: {e}")
       
            
    
    # we add manual chars and known chars to list of characters
    for mainCategory, subcatList in zip(["CHARACTERS", "CHARACTERS_LESSER"], 
                                        [character_subcats, character_lesser_subcats]):
        for subcat in subcatList:
            if mainCategory not in TAG_CATEGORIES:
                continue
            if subcat not in TAG_CATEGORIES[mainCategory]:
                continue
            for tag in TAG_CATEGORIES[mainCategory][subcat]["tags"]:
                CHARACTERS_TAG[tag] = TAG_CATEGORIES[mainCategory][subcat].get("low", [])
                if tag not in CHARACTERS_TAG_FREQUENCY: #new character name tags, set a defualt 1 value
                    CHARACTERS_TAG_FREQUENCY[tag] = 1
                
            if subcat in char_manuals and parameters.PARAMETERS["save_manual_names_to_favorites_file"]:
                favourites += [tag for tag in TAG_CATEGORIES[mainCategory][subcat]["tags"] if tag not in favourites]
    
    # we now know all the characters, we can now make a secondary dict of character recommendations
    CHARACTER_RECOMMENDATIONS = {k:v for k, v in TAGS_RECOMMENDATIONS.items() if k in CHARACTERS_TAG.keys()}
    
    # here we add artists and other relevant tags to favorites, but we don't need to update character_tags
    view_subcats = ["JP ARTISTS","WESTERN ARTISTS","KOR ARTIST"]
    model_subcats = ["BRIGHTNESS LEVELS","DARKNESS LEVELS", "SPECIAL MEDIA TAGS","SPECIAL QUALITY TAGS"]
    for mainCategory, subcatList in zip(["VIEW", "MODELS"], [view_subcats, model_subcats]):
        for subcat in subcatList:
            if mainCategory not in TAG_CATEGORIES:
                continue
            if subcat not in TAG_CATEGORIES[mainCategory]:
                continue
            
            if parameters.PARAMETERS["save_manual_names_to_favorites_file"]:
                favourites += [tag for tag in TAG_CATEGORIES[mainCategory][subcat]["tags"] if tag not in favourites]

    
    
                  
    favourites = list(set(favourites)) 
    if favourites and set(favourites) != set(previous_favourites):
        parameters.log.info(f"Updated favourites.txt with new characters")
        with open(fav_file, 'w') as f:
            f.write(', '.join(favourites))
    
    #unadded chars
    # we check and notify user of any unadded characters in the character dict       
    unadded_char = []
    
    for mainCategory in ["CHARACTERS", "CHARACTERS_LESSER"]:
        for subcat in TAG_CATEGORIES[mainCategory].values():
            for tag in subcat["tags"]:
                if tag not in CHARACTERS_TAG:
                    unadded_char.append(tag)
  
    if unadded_char and parameters.PARAMETERS["save_manual_names_to_favorites_file"]:
        parameters.log.info(f"Warning: {len(unadded_char)} are not added in the favorites.txt: {unadded_char}")
            
            
def check_definitions_and_recommendations():
    all_tags = COLOR_DICT.keys()
    for k, v in TAG_DEFINITION.items(): # tag --> definition
        if k not in all_tags:
            parameters.log.info(f"Warning: {k} has a definition but not added in tag categories")
   
    for k, v in TAGS_RECOMMENDATIONS.items(): # list of tags --> list of list of tags
        tags_in_row = list(set([k] + [tag for v_entry in v for tag in v_entry]))
        correct_tags = all([t in all_tags for t in tags_in_row])
        if not correct_tags:
            parameters.log.info(f"Warning: check {[t for t in tags_in_row if t not in all_tags]}, in  {k}, {v} for wrong/misspelled tags")
        
if TAG_CATEGORIES == {}:
    tag_categories_init()