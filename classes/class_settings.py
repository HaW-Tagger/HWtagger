from tools import files


class TagsLogic:
    """
    A logic that rules over how tags should be replaced by others, requires multiple settings:

    - all tags that should be present (given by files.loose_tags_check), an empty list results in an always added tag
        - can be kept
    - all tags that should be added (a list of tags)

    An asterisk will always use a REGEX style form to be adapted just like for the search function
    """

    def __init__(self, init_dict: dict):
        self.conditions = []
        self.added = []

        self.keep_conditions = False

        if init_dict:
            self.load(init_dict)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            if (self.keep_conditions == other.keep_conditions
                    and len(self.conditions) == len(other.conditions)
                    and all(condition in other.conditions for condition in self.conditions)
                    and len(self.added) == len(other.added)
                    and all(added in other.added for added in self.added)):
                return True
        return False

    def save(self):
        return {"conditions": self.conditions, "added": self.added, "keep_conditions": self.keep_conditions}

    def load(self, init_dict: dict):
        init_keys = init_dict.keys()
        if "conditions" in init_keys:
            self.conditions = init_dict["conditions"]

        if "added" in init_keys:
            self.added = init_dict["added"]

        if "keep_conditions" in init_keys:
            self.keep_conditions = init_dict["keep_conditions"]

    def apply_filter(self, tags_list) -> tuple[set[str], [str]] | tuple[bool, bool]:
        """

        Args:
            tags_list: list of tags that are to be checked

        Returns:
            - list of tags to remove
            - list of tags to add
        """
        to_remove = set()
        validated = False

        for condition in self.conditions:
            if files.loose_tags_check(condition, tags_list):
                validated = True
                if not self.keep_conditions:
                    # Remove the tags, we need to check for every tag that could be a problem (asterisk plus conditions)
                    for tag in tags_list:
                        if files.loose_tags_check(condition, [tag]):
                            to_remove.add(tag)

        if validated:
            return to_remove, self.added
        else:
            return False, False

class SettingsDatabase:
    """
    All the settings in a database/group will be held there
    """
    def __init__(self, init_dict: dict=False):

        self.tags_logics: list[TagsLogic] = []

        if init_dict:
            self.load(init_dict)


    def save(self):
        result = {"tags_logics": []}
        for tags_logic in self.tags_logics:
            result["tags_logics"].append(tags_logic.save())
        return result

    def load(self, init_dict: dict):
        init_keys = init_dict.keys()
        if "tags_logics" in init_keys:
            self.tags_logics = []
            for tags_logic in init_dict["tags_logics"]:
                self.tags_logics.append(TagsLogic(tags_logic))

    def apply_all_tags_logics(self, full_tags):
        if not self.tags_logics:
            return [], []

        to_remove, to_add = set(), set()

        for tag_logic in self.tags_logics:
            r, a = tag_logic.apply_filter(full_tags)
            if r:
                to_remove = to_remove.union(r)
            if a:
                to_add = to_add.union(a)

        return to_remove, to_add





