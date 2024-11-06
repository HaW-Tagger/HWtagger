import copy
import csv
import os

from resources import parameters


class Node:
    def __init__(self,*,
                 parents: list=None,
                 name: str="",

                 children: list=None,
                 inheritable_pres: list=None,
                 specific_pres: list=None,
                 inheritable_posts: list=None,
                 specific_posts: list=None,

                 alternative_names: list[str]=None,
                 keep_alternatives: bool=True,

                 priority: int = -1,
                 from_pre_tags: list = None,
                 from_post_tags: list=None,

                 roadblock: bool=False,
                 mandatory_branch: bool=False
                 ):
        if not parents:
            parents = []
        if not children:
            children = []
        if not inheritable_pres:
            inheritable_pres = []
        if not specific_pres:
            specific_pres = []
        if not inheritable_posts:
            inheritable_posts = []
        if not specific_posts:
            specific_posts = []
        if not from_pre_tags:
            from_pre_tags = []
        if not from_post_tags:
            from_post_tags = []
        if not alternative_names:
            alternative_names = []

        self.parents: list[Node] = parents
        self.name: str = name
        self.alternative_names: list[str] = alternative_names
        self.keep_alternatives: bool = keep_alternatives

        self.activated_names: list[str] = []

        self.children: list[Node] = children
        self.inheritable_pres: list[Node] = inheritable_pres
        self.specific_pres: list[Node] = specific_pres
        self.inheritable_posts: list[Node] = inheritable_posts
        self.specific_posts: list[Node] = specific_posts

        self.roadblock: bool = roadblock  # is considered a higher priority than downstream tags, is activated by the downstream tags (doesn't spread)
        self.mandatory_branch: bool = mandatory_branch  # all downstream intermediate tags (and this one) are required for the activation of a downstream tag (spread down)

        # Categories from pre/post
        self.priority: int = priority
        self.from_pre_tags: list[str] = from_pre_tags
        self.from_post_tags: list[str] = from_post_tags


        # Temporary values
        self.potentials: set[str] = set()
        self.pre_potentials: set[str] = set()
        self.post_potentials: set[str] = set()

    def __repr__(self):
        result = f"N({self.name}"

        if self.alternative_names:
            result += f", alternative_names={self.alternative_names}"
        if self.activated_names:
            result += f", activated_names={self.activated_names}"
        #if self.priority != -1:
        #	result += f", priority={self.priority}"
        if self.inheritable_pres:
            result += f", inheritable_pres={self.inheritable_pres}"
        if self.inheritable_posts:
            result += f", inheritable_posts={self.inheritable_posts}"
        if self.from_pre_tags:
            result += f", from_pre_tags={self.from_pre_tags}"
        if self.from_post_tags:
            result += f", from_post_tags={self.from_post_tags}"
        if self.children:
            result += f", children={self.children}"
        result += ")"
        return result

    def inheritable_pres_names(self):
        return [inherit.name for inherit in self.inheritable_pres]

    def inheritable_posts_names(self):
        return [inherit.name for inherit in self.inheritable_posts]

    def children_names(self):
        return [inherit.name for inherit in self.inheritable_posts]

    def close_proximity_recursive_propagate(self):
        """
        Propagates all the inheritable down by using the parent info
        """
        for parent in self.parents:
            for inheritable_pre in parent.inheritable_pres:
                self.add_inheritable_pres(copy.deepcopy(inheritable_pre))
            for inheritable_post in parent.inheritable_posts:
                self.add_inheritable_posts(copy.deepcopy(inheritable_post))
            if parent.mandatory_branch:
                self.mandatory_branch = True

        # Copy the specific to itself by deepcopy
        self.specific_pres = copy.deepcopy(self.specific_pres)
        self.specific_posts = copy.deepcopy(self.specific_posts)

        for child in self.children:
            child.close_proximity_recursive_propagate()

    def activate_recursive(self, tags: list[str]) -> list[str]:
        """
        recursively (children) activate the node
        """
        used_tags = []
        self.create_potentials()

        detected_modifiers = []
        for tag in tags:
            if tag in self.potentials:
                if self.name in tag:
                    if self.name not in self.activated_names:
                        self.activated_names.append(self.name)
                    used_tags.append(tag)
                    detected_modifiers.append(tag.split(self.name))

                elif any(alternative_name in tag for alternative_name in self.alternative_names):
                    self.activated_names.extend([alternative_name for alternative_name in self.alternative_names if alternative_name in tag and alternative_name not in self.activated_names])
                    used_tags.append(tag)
                    detected_modifiers.append(tag.split([alternative_name for alternative_name in self.alternative_names if alternative_name in tag][0]))

                # from_post and from_pre
                elif any(from_pre in tag for from_pre in self.from_pre_tags) and self.name not in self.activated_names:
                    self.activated_names.append(self.name)
                elif any(from_post in tag for from_post in self.from_post_tags) and self.name not in self.activated_names:
                    self.activated_names.append(self.name)

        for modifier in detected_modifiers:
            if modifier[0]:
                # pre tags combinations
                self.activate_pre_modifier(modifier[0].strip())
            if modifier[1]:
                # post tags combinations
                self.activate_post_modifier(modifier[1].strip())

        for child in self.children:
            used_tags += child.activate_recursive([tag for tag in tags if tag not in used_tags])

        return used_tags

    def activate_pre_modifier(self, modifier: str):
        """
        Recursively find the correct modifier and set it to activated, from a modifier that was before the name
        """
        for pre_tag in self.inheritable_pres+self.specific_pres+self.specific_posts+self.inheritable_posts:
            pre_tag.activate_recursive([modifier])

    def activate_post_modifier(self, modifier: str):
        """
        Recursively find the correct modifier and set it to activated, from a modifier that was before the name
        """
        for post_tag in self.inheritable_pres+self.specific_pres+self.specific_posts+self.inheritable_posts:
            post_tag.activate_recursive([modifier])

    def clean(self):
        """
        Recursively deletes all children that are not activated, delete all pre/posts that are not activated, activate parents in case of roadblocks and clean for mandatory_branch
        :return:
        """
        k = 0
        while k < len(self.children):
            self.children[k].clean()
            if not self.children[k].is_activated():
                self.children.pop(k)
            else:
                k += 1

        k = 0
        while k < len(self.inheritable_pres):
            self.inheritable_pres[k].clean()
            if not self.inheritable_pres[k].is_activated():
                self.inheritable_pres.pop(k)
            else:
                k += 1
        k = 0
        while k < len(self.specific_pres):
            self.specific_pres[k].clean()
            if not self.specific_pres[k].is_activated():
                self.specific_pres.pop(k)
            else:
                k += 1
        k = 0
        while k < len(self.inheritable_posts):
            self.inheritable_posts[k].clean()
            if not self.inheritable_posts[k].is_activated():
                self.inheritable_posts.pop(k)
            else:
                k += 1
        k = 0
        while k < len(self.specific_posts):
            self.specific_posts[k].clean()
            if not self.specific_posts[k].is_activated():
                self.specific_posts.pop(k)
            else:
                k += 1

    def is_activated(self) -> bool:
        """
        Recursively check if this node has the correct activation parameters
        :return:
        """
        if self.activated_names:
            return True
        if self.children and not self.mandatory_branch:
            if any(child.is_activated() for child in self.children):
                return True
        if self.children and self.roadblock:
            if any(child.is_activated() for child in self.children):
                return True
        return False


    def recursively_create_potentials(self):
        for child in self.children:
            child.recursively_create_potentials()
        self.create_potentials()

    def create_potentials(self):
        """
        Creates all potentials if they don't exist
        """
        if not self.potentials:
            self.potentials = {self.name}
            if self.from_post_tags:
                self.potentials = self.potentials.union(self.from_post_tags)
            if self.from_pre_tags:
                self.potentials = self.potentials.union(self.from_pre_tags)
            if self.alternative_names:
                self.potentials = self.potentials.union(self.alternative_names)
            pre_potentials = set()
            for pre in self.inheritable_pres:
                pre_potentials = pre_potentials.union(pre.recursively_get_pre_potentials(True))
            for post in self.inheritable_posts:
                pre_potentials = pre_potentials.union(post.recursively_get_pre_potentials(False))
            for pre in self.specific_pres:
                pre_potentials = pre_potentials.union(pre.recursively_get_pre_potentials(True))
            for post in self.specific_posts:
                pre_potentials = pre_potentials.union(post.recursively_get_pre_potentials(False))
            self.potentials = self.potentials.union([pre_tag + " " + alt_name if pre_tag[-1] != "-" else pre_tag+alt_name for pre_tag in pre_potentials for alt_name in self.potentials])

            post_potentials = set()
            for pre in self.inheritable_pres:
                post_potentials = post_potentials.union(pre.recursively_get_post_potentials(False))
            for post in self.inheritable_posts:
                post_potentials = post_potentials.union(post.recursively_get_post_potentials(True))
            for pre in self.specific_pres:
                post_potentials = post_potentials.union(pre.recursively_get_post_potentials(False))
            for post in self.specific_posts:
                post_potentials = post_potentials.union(post.recursively_get_post_potentials(True))
            self.potentials = self.potentials.union([alt_name + " " + post_tag if post_tag[0] != "-" else alt_name+post_tag for post_tag in post_potentials for alt_name in self.potentials])


    def recursively_get_pre_potentials(self, is_self_pre: bool=True) -> set[str]:
        """
        Recursively returns all possible pres from this modifier (mostly for categories)
        """
        if not self.pre_potentials:
            self.update_pre_potentials(is_self_pre)
        result = set()
        result = result.union(self.pre_potentials)
        for child in self.children:
            result = result.union(child.recursively_get_pre_potentials(is_self_pre))
        return result

    def update_pre_potentials(self, is_self_pre: bool=True):
        self.pre_potentials = {self.name} if is_self_pre else set()
        if is_self_pre and self.alternative_names:
            self.pre_potentials = self.pre_potentials.union(self.alternative_names)
        if self.from_pre_tags:
            self.pre_potentials = self.pre_potentials.union(self.from_pre_tags)

    def recursively_get_post_potentials(self, is_self_post: bool=True) -> set[str]:
        """
        Recursively returns all possible posts from this modifier (mostly for categories)
        """
        if not self.post_potentials:
            self.update_post_potentials(is_self_post)
        result = set()
        result = result.union(self.post_potentials)
        for child in self.children:
            result = result.union(child.recursively_get_post_potentials(is_self_post))
        return result

    def update_post_potentials(self, is_self_post: bool=True):
        self.post_potentials = {self.name}  if is_self_post else set()
        if is_self_post and self.alternative_names:
            self.post_potentials = self.post_potentials.union(self.alternative_names)
        if self.from_post_tags:
            self.post_potentials = self.post_potentials.union(self.from_post_tags)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def add_parent(self, parent):
        if parent not in self.parents:
            self.parents.append(parent)

    def add_inheritable_pres(self, pre):
        if pre not in self.inheritable_pres:
            self.inheritable_pres.append(pre)

    def add_specific_pres(self, pre):
        if pre not in self.specific_pres:
            self.specific_pres.append(pre)

    def add_inheritable_posts(self, post):
        if post not in self.inheritable_posts:
            self.inheritable_posts.append(post)

    def add_specific_posts(self, post):
        if post not in self.specific_posts:
            self.specific_posts.append(post)

    def add_alternatives(self, alternatives: list[str]):
        for alternative in alternatives:
            if alternative not in self.alternative_names:
                self.alternative_names.append(alternative)

    def add_from_pre_tags(self, from_pre_tags: list[str]):
        for from_pre in from_pre_tags:
            if from_pre not in self.from_pre_tags:
                self.from_pre_tags.append(from_pre)

    def add_from_post_tags(self, from_post_tags: list[str]):
        for from_post in from_post_tags:
            if from_post not in self.from_post_tags:
                self.from_post_tags.append(from_post)

    def rough_sentence(self, depth=0):
        """Recursive function that print all possible outputs"""
        result = []

        # Children check
        roadblock_activated = False
        activated_children = []
        if self.children:
            for child in self.children:
                if child.is_activated:
                    activated_children.append(child)
                    if self.roadblock:
                        roadblock_activated = True
                    #else:
                        #result.extend([element for element in child.rough_sentence(depth+1) if element not in result])

        transmitted_inheritable = False
        # the length of activated children, if 1, and the self has only inheritable, transmit the inheritable to the child before getting the sentence
        if not roadblock_activated and len(activated_children) == 1 and (self.inheritable_pres or self.inheritable_posts) and not (self.specific_pres or self.specific_posts):
            transmitted_inheritable = True
            self.merge_inheritables(activated_children[0])

        if not roadblock_activated:
            for child in activated_children:
                result.extend([element for element in child.rough_sentence(depth+1) if element not in result])

        if (not self.activated_names) and (not roadblock_activated) or transmitted_inheritable:
            return result


        # Something should be printed
        name_to_print = self.name
        if self.keep_alternatives:
            if all(activated_name in self.alternative_names for activated_name in self.activated_names):
                name_to_print = self.activated_names[0]

        # Going through the pre_tags
        pre_mod_prio: dict[int: list[str]] = {}
        for pre_modifier in self.specific_pres+self.inheritable_pres:
            for mod_prio in pre_modifier.mod_prio_completes():
                if mod_prio[1] in pre_mod_prio.keys():
                    pre_mod_prio[mod_prio[1]].append(mod_prio[0])
                else:
                    pre_mod_prio[mod_prio[1]] = [mod_prio[0]]

        # Going through the post_tags
        post_mod_prio: dict[int: list[str]] = {}
        for post_modifier in self.specific_posts+self.inheritable_posts:
            for mod_prio in post_modifier.mod_prio_completes():
                if mod_prio[1] in post_mod_prio.keys():
                    post_mod_prio[mod_prio[1]].append(mod_prio[0])
                else:
                    post_mod_prio[mod_prio[1]] = [mod_prio[0]]

        pre_mod_prio_keys = list(pre_mod_prio.keys())
        pre_mod_prio_keys.sort()
        post_mod_prio_keys = list(post_mod_prio.keys())
        post_mod_prio_keys.sort(reverse=True)

        if result and not pre_mod_prio_keys and not post_mod_prio_keys: # the down one is activated and this one doesn't have modifiers
            return result

        printing_press = ""
        if pre_mod_prio_keys:
            printing_press += "( "
            for pre_prio_key in pre_mod_prio_keys:
                printing_press += "|".join(pre_mod_prio[pre_prio_key]) # no logic currently for or/and, etc ...
                printing_press += " "
            printing_press += ") "
        printing_press += name_to_print + " "
        if post_mod_prio_keys:
            printing_press += "( "
            for post_prio_key in post_mod_prio_keys:
                printing_press += "|".join(post_mod_prio[post_prio_key]) # no logic currently for or/and, etc ...
                printing_press += " "
            printing_press += ")"
        result.append(printing_press)

        return result


    def mod_prio_completes(self) -> list[tuple[str, int]]:
        mod_prio_list = []

        roadblock_activated = False
        if self.children:
            for child in self.children:
                if child.is_activated:
                    if self.roadblock:
                        roadblock_activated = True
                    else:
                        result = child.mod_prio_completes()
                        if result:
                            mod_prio_list.extend(result)

        if not (self.activated_names or roadblock_activated):
            return mod_prio_list

        if mod_prio_list:
            return mod_prio_list

        name_to_print = self.name
        if self.keep_alternatives:
            if all(activated_name in self.alternative_names for activated_name in self.activated_names):
                name_to_print = self.activated_names[0]

        mod_prio_list.append((name_to_print, self.priority))

        return mod_prio_list

    def merge_inheritables(self, child):
        """
        Merge the parent inheritables to the child inheritables, used for the case in which a tag only has inheritables and one child
        Args:
            child: Node object, not necessarily a child but it is in most cases
        """
        for inheritable_pre in self.inheritable_pres:
            if inheritable_pre.name in child.inheritable_pres_names():
                child.inheritable_pres[child.inheritable_pres_names().index(inheritable_pre.name)].recursive_merge(inheritable_pre)
            else:
                child.inheritable_pres.append(inheritable_pre)
        pass

    def recursive_merge(self, other):
        """
        Recursively merge self node with the other into the self node, transmit activated names and children
        """
        for other_child in other.children:
            if other_child.name in self.children_names():
                self.children[self.children_names().index(other_child.name)].recursive_merge(other_child)
            else:
                self.children.append(other_child)

        # Merge activated names
        self.activated_names.extend([other_activated_name for other_activated_name in other.activated_names if other_activated_name not in self.activated_names])



class Graph:
    def __init__(self):
        self.root_node: Node = Node(name="ROOT")
        self.nodes: dict[str: Node] = {"ROOT": self.root_node}

    def create_graph(self):
        csv_path = os.path.join(parameters.MAIN_FOLDER, "resources/tags_tree.csv")
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            info = csv.reader(f)
            next(info) # skip first
            for row in info:
                self.populate(row)
        self.propagate()

    def populate(self, row):
        """
        properly create the necessary nodes from the row
        :param row: the csv row in the form of a list
        """
        name = row[1].strip()
        if name not in self.nodes.keys():
            new_node = Node(name=name)
            self.nodes[name] = new_node

        if row[2]:
            children_names = [child_name.strip() for child_name in row[2].split(",")]
            for child_name in children_names:
                if child_name not in self.nodes.keys():
                    child_node = Node(name=child_name)
                    self.nodes[child_name] = child_node
                self.nodes[name].add_child(self.nodes[child_name])
                self.nodes[child_name].add_parent(self.nodes[name])

        if row[3]:
            inheritable_pre_names = [child_name.strip() for child_name in row[3].split(",")]
            for pre_name in inheritable_pre_names:
                if pre_name not in self.nodes.keys():
                    pre_node = Node(name=pre_name)
                    self.nodes[pre_name] = pre_node
                self.nodes[name].add_inheritable_pres(self.nodes[pre_name])

        if row[4]:
            specific_pre_names = [child_name.strip() for child_name in row[4].split(",")]
            for pre_name in specific_pre_names:
                if pre_name not in self.nodes.keys():
                    pre_node = Node(name=pre_name)
                    self.nodes[pre_name] = pre_node
                self.nodes[name].add_specific_pres(self.nodes[pre_name])

        if row[5]:
            inheritable_post_names = [child_name.strip() for child_name in row[5].split(",")]
            for post_name in inheritable_post_names:
                if post_name not in self.nodes.keys():
                    post_node = Node(name=post_name)
                    self.nodes[post_name] = post_node
                self.nodes[name].add_inheritable_posts(self.nodes[post_name])

        if row[6]:
            specific_post_names = [child_name.strip() for child_name in row[6].split(",")]
            for post_name in specific_post_names:
                if post_name not in self.nodes.keys():
                    post_node = Node(name=post_name)
                    self.nodes[post_name] = post_node
                self.nodes[name].add_specific_posts(self.nodes[post_name])

        if row[7]: # abandoned automatic singular or plural
            alternative_names = [child_name.strip() for child_name in row[7].split(",")]
            self.nodes[name].add_alternatives(alternative_names)
        keep_alternatives = bool(row[8]) if row[8] else None
        if keep_alternatives is not None:
            self.nodes[name].keep_alternatives = keep_alternatives

        if row[9]:
            from_pre_tags = [child_name.strip() for child_name in row[9].split(",")]
            self.nodes[name].add_from_pre_tags(from_pre_tags)
        if row[10]:
            from_post_tags = [child_name.strip() for child_name in row[10].split(",")]
            self.nodes[name].add_from_post_tags(from_post_tags)

        roadblock = bool(row[11]) if row[11] else None
        if roadblock is not None:
            self.nodes[name].roadblock = roadblock
        mandatory_branch = bool(row[12]) if row[12] else None
        if mandatory_branch is not None:
            self.nodes[name].mandatory_branch = mandatory_branch
        priority = int(row[13]) if row[13] else None
        if priority is not None:
            self.nodes[name].priority = priority

    def propagate(self):
        """
        Propagates the priorities and the inheritable traits to the children
        """
        unchecked_nodes = list(self.nodes.values())
        while unchecked_nodes:
            checking_node = unchecked_nodes[0]
            # Propagate the priority to the down children
            if checking_node.priority == -1:
                unchecked_nodes.pop(0)
                continue

            for child in checking_node.children:
                if child.priority == -1:
                    child.priority = checking_node.priority
                    if child not in unchecked_nodes:
                        unchecked_nodes.append(child)
            unchecked_nodes.pop(0)
        self.root_node.close_proximity_recursive_propagate()


    def activate(self, tags: list[str]):
        """
        Activates the necessary nodes in the graph
        :param tags: list of tags
        """
        self.root_node.recursively_create_potentials()
        used_tags = self.root_node.activate_recursive(tags)
        self.root_node.clean()
        print(self.root_node)
        return [tag for tag in tags if tag not in used_tags]

    def rough_sentence(self):
        """
        Rough implementation of the output, need for the activation to have happened first
        """
        return self.root_node.rough_sentence()
