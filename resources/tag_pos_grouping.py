"""
danbooru's common modifiers, POS (part of speech)

The following are "modifiers" found in caformer and Swin/Eva (basically common danbooru modifiers)

in english the order of adjectives matter (not always true, but 95% follows this rule)
Determiner (also quantity) -> Opinion -> Size -> Age -> Shape -> Color -> Origin -> Material -> Purpose (gerunds) -> Noun

in our case we are handling tags so we can discard and insert a few and we can ignore/skip cases with more than 2 attributes, cause commas
We can also think of the following orders as the priority queue and combine the most important/broad features and leave 
the small additional description separate.
[action : (verb, optional)] 
-> 
[Quantity -> Condition -> Opinion -> Size -> Age -> Shape -> Color ->design features/texture -> Origin -> Material : (adjectives/gerunds)] 
-> 
[subject : Noun]

Ex: 
- red dress (color), frilled dress (design), torn dress (condition) -> 
        (torn red dress + frilled dress) or (torn dress, red frilled dress)
- dark-skinned male, muscular male, tall male -> tall, dark-skinned, muscular male -> 
        (tall dark-skinned male, muscular male) or (tall male, dark-skinned muscular male)

# cumulative adjectives vs coordinate adjectives
# cumulative adjectives are adjectives from different categories and coordinate adjectives are from the same groups
# cumulative doesn't require commas (although it might be useful for better comprehension for 2+ adj)
# coordinate adj does reqire commas or and (we ignore this case, let user decide/write it themselves)
    
# the number of valid pair combinations: n total ordered attributes (n*n-1)/2 counts
"""
####################################
# check if the last word of the phrase is any of these, then it's not a proper subject/noun
# writing can be both a subject and action, but in cases when it's a subject we want them separated (ex: clothes writing and body writing)
non_subjects = ['only','loss','dangle','theft','request','grab','aside','flip','hold','switch','tug','tip','lift','slip',
                'cover-up','down','up','pull','peek','hang','overhang','removed','gap','biting','hanging','view', 
                'insertion', 'difference','out','shot','gesture','frame', 'focus']

# words that doesn't merge with similar tags
non_subjects + ['writing']
non_subjects = set(non_subjects)

####################################

# uncategorized_blacklist are the words before the subject that is removed from consideration being an adjectives
# example is "hair between eyes", as "eyes" is not the subject, but "hair" + prepositional phrase
blacklist = set(["hair between","hand on another's",'hands on own','hand on own','hand under','handjob over','legs on',
                "hands on another's",'eyebrows visible through', "blood from", "futa with", "female with",'leg on',
                "male with",'arms between','arm between', 'arms behind', 'arm behind', 'headphones around','leg in',
                'erection under', 'ejaculation under', 'ejaculation through', 'cum through','goggles around','arm in',
                'eyes visible through','cumdrip onto','ass visible through','hand between','arm between','arms under',
                'hands between','panties on', 'object on','necktie between','penis between','arms on', 'arms in', 
                'penis in', 'necktie in','necktie on', 'object in', 'object between','pulled by','arm on','legs in', 
                'lifted by','girl on','eyebrows hidden by','jacket on', 'coat on','legs under','arm under','leg under',
                'sex from', 'grabbing from','hair pulled','hair over one','hand in own','head in', 'head on','depth of',
                'hands in own','hands on own','eyewear on', 'goggles on','scar across','head between',
                'spread pussy under','penis to','hand over own','hands over own','hair over','hands in opposite'
                'thighhighs under', 'futa on', 'male on', 'female on','arm at','shibari over','pussy juice drip through',
                'paizuri under', 'tentacles under', 'vibrator in', 'boy on','shorts around one','standing on one',
                'hugging own', 'paizuri over', 'swimsuit under', "mole under", 'mole on', "shibari under",'pointing at'
                ])


#these are misc POS: idk what to do with these for now, most are verb phrases
possesive_pronouns = ["grabbing another's", "holding another's","licking another's",'holding own', 'grabbing own',
                      "looking at",'reaching towards','looking to the',"covering another's",'covering own'
                      ]
blacklist.update(possesive_pronouns)

####################################
# these are actions you can take onto the subject
prepositional_indicators = ['on','in','against','between','from','under', 'over','through','to']
prepositional_phrases = ['on','in','against','between','from','under','through','over','finger to','head on',
        'looking through','tube in','tentacles in','hand in','cum in','feces in','arrow in','blood in','food in',
        'metroid creature on','bandaid on','sitting on','ofuda on','hand on', 'mole on', 'hands on','bruise on'
        'blood on','scar on','bandage on','condom tied on','lipstick mark on','bite mark on','feces on','bird on',
        'leaning on','cum on','animal on','food on','penis on','pokemon on', 'putting on','bags under',
        'condom on', 'breasts on','vibrator under','panties under','looking to the','mole above','hands in',
        'mole under','lying on','condom in', 'used condom in','view through','fellatio under','used condom on',
        'looking over','blood on','petals on', 'flower on','petals in', 'flower in','flower over','petals over',
        'eyebrows behind','penis over','hand to own','talking on','bikini under', 'strap between',
        'pantyhose under', 'chocolate on', 'aiming at','lactation through','fingering through',
        'masturbation through','penetration through',"lifting another's",'tail through','bodysuit under',
        'feet on','elbows on','elbow on','shorts under','pants under','ears through','hair through','horns through',
        'finger in','ribbon in','shirt in','utensil in','v over','toast in','heart in','popsicle in','dress in',
        'clothes in','pocky in','objects in','thighhighs under','clothes between','face to','neckwear between',
        'animal between','towel on','fruit on','mask on', 'view between', 'tail between','arm held','sword on',
        'legwear under','sweater around','standing on','lantern on','walking on','cardigan around','jacket around',
        'arm around','sleeping on','pouring onto','knees to','knees on','socks over','bruise on','in the','hand over',
        'feet on', 'behind','hug from','looking out','viewer on','bandages over','legs over','gun to','foot on','knife in'
        'leaf on'
        ]

verbs = ['holding','licking','adjusting','kissing','glowing','floating','hanging','living','presenting','bursting',
         'viewer holding','smelling', 'flying', 'covering', 'gaping', 'incoming', 'looking', 'removing', 'poking', 
         'flaming','cheating','smoking', 'playing', 'facing', 'standing', 'washing', 'releasing', 'wiping', 'matching', 
         'riding', 'missing', 'falling','folding', 'pointing', 'throwing','tearing', 'exploding', 'rolling',"sagging",
         'steaming','leaning','bouncing','opening','closing','drinking','caressing','biting','drawing','talking',
         'yelling','shouting','milking','breathing','twitching','tying','cutting','drying','braiding','shopping',
         'bunching','brushing',"brushing another's",'dissolving', 'shading','averting','rubbing','wringing',
         'lifting','carrying','mixing','peeing','waving','hugging','undressing','dressing','squeezing','wrestling'
         ]

prep_verbs = set(prepositional_phrases + verbs)

####################################

# the following are adjectives, gerunds are rare for danbooru tags think of "'swimming' pool"
quantity = ['multiple','single','double','twin','triple','too many','extra','solo', 'group', 
            "excessive","one", "two",'sparse','implied extra','bag of','duo','tri', 'mmf','ffm']

# conditions applied onto the subject, can be both temporary or permanent
condition =["rusted", "rusty", "torn", "dirty", "broken",'wet','fake','bandaged','shiny', 'covered','implied',
            'mismatched','shared', 'exposed', 'censored', 'borrowed','tied','blacked','baggy','asymmetrical','pov',
            'unbuttoned','cracked','crossed','clothed','sliced','outstretched','gouged', 'winged','ornate','sideways',
            'armored','simulated', 'inverted', 'planted', 'forced','closed','oversized','half-closed','skin-covered',
            'uneven','fiery','spread','bound','bent','pointy','curvy','partially','drawn','split','messy','tinted',
            'wavy','reverse', 'full','thick','super','half','wide','sharp','artificial','inflatable','cropped','folded',
            'prosthetic','electric','athletic','public','self','stealth','x-ray','feathered','parted','double-parted',
            'convenient','mutual', 'cooperative','spoken','no',"open", "unworn", 'worn', "cloudy", "sunny",'mechanical',
            'rainy', "linked", "flipped", 'faceless', 'furry', 'projectile','handsfree','severed','cut','dismembered',
            'curly','used','disposable','sparkle','handheld', 'corded','reflective','curled','curtained','chained',
             'constricted','stray','knotted','empty','deep','revealing','tucked','clenched','gloved','perpendicular',
             'symmetrical','expressive','solid','soft','other','upper', 'lower','after','before','post','pre',
             'forked','arched','shallow','stitched','bobby','shaded', 'prehensile','blunt','diagonal','disembodied',
             'flame-tipped','improvised','mythical', 'legendary','untied','straight','popped','peaked','reverse grip',
             'swept','stained','tented','sparkling','rough','flowing','sweaty','burnt','painted','pov across',
             'narrowed','blank','upturned','floppy','tilted','horned','contracted','partially fingerless','framed',
             'unaligned','perky','wide spread','m','v','n','w','fast','untucked','bendy','nontraditional','fried',
             'locked','dyed','dense','flip','vibrant','dun','contrast','grand','imminent','crooked','two-handed',
            ]

opinion = ["cute", "beautiful","gorgeous", "ugly", "amazing", "terrible", "strange", "weird", "disgusting", "gross", 
           "detailed", "intense", "obscure", "simple", "clean", "assertive",'evil', 'crazy','happy','naughty','scary',
           'anger'
           ]

sizes = ['mini',"tiny", 'flat', "small", "medium", "big", "large", "huge", "gigantic", 'giant', "short", "tall",
         'long','very long', 'micro', 'absurdly long','very short']

age = ["old", "new", "ancient", "modern", "young",'mature', 'antique']

shapes = ['spade','heart-shaped','diamond','phallic', 'crescent','circle', 'round','triangle','cross','square','arrow',
          'musical note', 'heart', 'star-shaped','ringed','hoop','slit','bow-shaped','tube','cone','crosshair',
          'cross-shaped','rectangular', 'ring','ball','wiffle','solid oval', 'oval', 'long pointy','drop-shaped',
          'flower-shaped','x-shaped','diamond-shaped','cube', 'v-shaped','puckered','dashed']

# for attires, try inputting the attribute into 1 or 2 with the color [1] [color] [2] [subject], to see what works
# these are add-on features that doesn't modify the underlying clothing/purpose
attire_feature_modifiers = ['frilled','lace-trimmed','fur-trimmed','ribbon-trimmed','spiked','cross-laced','two-sided',
                'braided','studded','food-themed','ribbed',"barbed", "bumpy",'collared','detached','veiny',
                'spiral','colored','layered','naked','nearly naked','crotchless','strapless','hooded',
                'sleeveless','backless','sideless','puffy','starry','strap','side-tie','colored inner', 
                'puffy short', 'fingerless', "toeless", "nude", "partially nude", 'thighband','lace-up',
                'o-ring','front-tie','breastless','nippleless','undersized','multi-strapped','rimless','semi-rimless',
                'under-rim','over-rim'
                ]

# basic color orders, this is used outside of POS filtering, but used when we want to 
# order colors when combining color-coding tags, ex white background + blue background = white and blue gradient background
basic_color_order = ["black","white",'dark','light','red','green','yellow','blue',"aqua",'brown',
               'purple','pink',"cyan","magenta", 'orange','gray',"silver","gold"]

# pattern is a modifer of color in many cases
colors = ["white","black","gray","red","blue","green","yellow","purple","pink",
          "brown","orange","cyan","magenta","beige","silver","gold","lavender",
          "teal","maroon","navy","lime","indigo","turquoise","violet","aqua",'very dark',
          "gradient", "rainbow", 'grey','blonde', 'multicolored','two-tone','dark', "dark blue",
          "dark-skinned", "light-skinned", "bright", "dim", "opaque", "transparent","streaked",
          "dark green", "dark red",'light brown','pale','light blue','light green', 'lime green','light',
          'light purple','halftone','split-color','yellow-tinted','green-tinted',
          'purple-tinted','pink-tinted','blue-tinted','red-tinted','orange-tinted','rainbow-tinted',
          'aqua-tinted','grey-tinted','gradient-tinted','brown-tinted','invisible',
          'black-framed','white-framed','red-framed','blue-framed','brown-framed','orange-framed',
          'green-framed','yellow-framed','purple-framed','pink-framed','aqua-framed',
          'grey-framed'
          ]
patterns = ["striped", 'diagonal-striped','vertical-striped','polka dot','checkered','print', 'plaid','argyle',
            'camouflage','pinstripe','tile', "x", 'pleated', "floral",'grid','number','tribal','bar','mosaic',
            'blur','glitch','barcode','lipstick','slap','tally','abortion','cow print','leopard print',
            'paw print','front-print','twitter', 'patreon', 'pixiv','fanbox','blurry','watercolor','yes-no',
            'contrast','fuck-me','teardrop','coiled','warning','no entry','no parking','floral print','bite'
            ]

# usually origin comes here, but danbooru has many design features so they would be appropriate here
# design/purpose
attire_style_modifiers = ['lace','see-through','bow','ribbon','turtleneck','taut','highleg','zipper', 
                    'loose','lowleg','off-shoulder','high-waist','bare','tight', "bubble", 'down','corset',
                    'tress', 'stirrup', 'high heel', 'heel','halter','tank','stud','cone hair','pom pom','suspender',
                    'barbell','eyepatch','garter', 'cupless','bit','padlocked','open-chest','puffy long','tassel',
                   
                    ]
# hair styles are also a design feature, occupational name also goes here
design_styles = [ 'sports','santa', 'maid', 'police','bridal','school','sailor','track','space', 'duffel','wedding',
            'front','low','side','3d','military',"goth", "gothic", 'male', 'female','showgirl','witch','cabbie', 
            'text',"muscular","skinny",'toned', "business", 'juliet', "pencil","drill", "autumn", 'summer', "winter", 
            'playboy bunny','high','lolita','surgical','yoga','wizard','fat','jingle','pinafore','slingshot','nurse',
            'one-piece','martial arts','tokin','domino','platform','art', 'calligraphy','crop','baseball','basketball',
            'doctor','stripper','puff and slash','raglan','kindergarten','utility','futanari', 'noh','office','gaming',
            'rotary','twin drill','low-tied long','christmas','virgin killer','aran','virgin destroyer','cowboy','polo',
            'bulletproof','cardigan','visor','garrison','jester','mob','letterman','dangle','pilot','mobile','taimanin',
            'normal','magical','mage','halloween','ninja','tengu','cargo','capri', 'western','medical','multi-tied',
            'pirate'
            ]

# note animal tags are considered origin, ex : cat ears and cat tails
regional_origin = ['chinese','japanese','french','american flag','traditional','ainu','ancient greek',
                   'german','greek','china','korean','egyptian','english','italian','latin','arabian',
                   'greco-roman','hawaiian'
                   ]
animals =['cat','dog','animal', 'rabbit','bunny','lion',  'dragon','cow','tiger', 'bird','wolf','bear', 'butterfly',
          'horse', 'pokemon','panda','human', 'bat', 'mouse','pig', 'fox','chicken','snake','whale','robot','sheep',
          'dolphin','shark','boar', 'deer','frog','spider','goat','demon','monkey', 'jackal', 'leopard','insect',
          'fairy', 'goblin', 'orc', 'fake animal','angel','devil','raccoon','oni','fish','baby','fetus','turtle',
          'tentacle','alpaca','squirrel', 'octopus','jaguar','ox','lop rabbit','otter','owl','eevee','lizard','ghost'
          'arthropod','moth','monster','character', 'mummy','reindeer','vampire', 'doll','cephalopod','crocodilian',
          'cetacean','weasel','scorpion'
          ]



material = ["wood","wooden", "metal", "metalic", "glass","plastic",'latex','leather','energy','fishnet','paper','sheer',
            'stone','crystal','fire','ice','denim', 'rubber','pearl', "string",'oil-paper','straw','tape','cardboard', 
            "tile", "potato", "chocolate","brick",'satin','chain-link',]

# this is where gerunds, linked objects, and linked actions (not the direct subject) would be
# objects and locations
linked_objects = ['cum','water','money','key','magazine','playstation','chain','coffee','slime','soap','towel','bamboo',
           'leaf','condom','window','toilet','liquid', 'saliva','milk','weapon','shell','snow','poke ball','egg',
           'moon','sun','cloud','photo','lightning bolt','pillow','blood','feather','object','dildo','snowflake',
           'anchor','gift','umbrella','bone', "rose", "flower","city", "road", "town", "neon", "car", "train", "bus",
           'street', 'vehicle', 'airplane', 'aircraft','antenna','pendant','beer','bike','star','night','day','game',
           'grandfather', 'analog', 'wall', 'alarm','hospital','sunflower','strawberry','bed','lounge', 'beach',"lemon",
           'gym','clothes','wine','grape','apple','soda','button','cherry','lotion','park','sake','rice','tissue',
           'pant','prison','sniper','assault','anti-materiel',"spring",'tactical','kalashnikov','battle','casino card',
           'machine','submachine','light machine','heavy machine','shot','cocktail','pool','poker','mahjong','roulette',
           'palm','coconut','pine','fir','chestnut','billiard','soccer','tennis','lab','trench','grocery','trash',
           'combat','doughnut','shampoo','perfume','nail polish','champagne','ketchup','sex','kitchen','ceiling',
           'spaghetti','funeral','industrial','candy','clover','club','four-leaf clover','planet','macaron','clock',
           'bandaid','monocle','hakurei','moriya','pee','pussy juice','maple','ginkgo','gas','sleep','stage','wheat',
           'tokyo','eiffel', 'picnic','plate','power', 'scale','steam','motorcycle','digital','motor','race','amazon',
           'squatting cowgirl','reverse cowgirl','sky','whip','rope','speech','thought','blank speech','bead',
           ]
gerunds = ["swimming", 'boxing', 'running','vending','diving','magnifying','watering','training','fishing','cupping']
linked_objects += gerunds
linked_body_parts = ['shoulder','arm','breast','hair','tail','hand','head','leg','eye','neck','fur','ear','paw',
              'ankle','armpit','foot','penis','horn','nose','forehead','wrist','ass','finger','stomach','chest',"thumb",
              'belly','cheek','toe','mouth', 'clitoris','animal ear','waist','pectoral','pussy','crotch','navel',
              'urethra','elbow','skull','back','labia','nail','legs','hip','face','tongue','thigh',"anal", "pubic", 
              'pinky','cleavage','facial','knee','mustache', 'beard','body','pelvic','breasts','eyebrow','wing',
              "nipple","lip",'full-body','anus','frenulum','full-face','underboob','cat ear','rabbit ear','single leg',
              'animal ears','prostate','cock','claw','tooth','fang'
              ]
# Eg: swimsuit skirt, shirt button, etc
linked_attire = ['skirt','dress','kimono','shirt','hat','bikini','swimsuit','panty','bikini top', 'headwear', 'leotard',
                'apron','ofuda','bra','coat','sleeve','hakama','belt','fundoshi', 'crown','sweater','suspenders',
                'bikini bottom','male underwear','eyewear','shorts','shoe', "footwear", "sleeves", 'thong', "suit",
                'choker','cloth','bodycon']

# downstream functions uses the linked attire list by -1 indexing for clothing checks
design_idx = 10
attire_idx = -1

adjectives:list[list[str]] = [quantity,condition, opinion, sizes, age, shapes,attire_feature_modifiers, colors,patterns,attire_style_modifiers,design_styles,
              regional_origin, animals, material,linked_objects,linked_body_parts,linked_attire]
adjectives = [set(adj_group) for adj_group in adjectives]
####################################

# this blacklist filters actions applied on subjects in relation to another object
# ex "hair between eyes" is not a valid action because it's a regional effect 
# and the person can have hair styles independent of the front bang
# basically store tags that are regional and independet or 
# tags that have regional hints as the first word (ex: navel piercing, piercing is the actual subject and navel is location)
action_blacklist = ['hair between eyes', 'dress tug', 'shirt tug', 'hair ribbon', 'hair bow',
                    'hair tube','hat ribbon','hat bow','dress bow','dress ribbon', 'hair tubes','hair strand',
                    'hair slicked back', 'hair over mouth', 'hair bobbles', 'hair over one eye', 'nipple piercing',
                    'ear piercing', 'navel piercing', 'tongue piercing','hair flower','tail piercing'
                    ]
