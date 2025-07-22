class RaketeJoinStrings:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "strings": ("LIST", {
                    "default": [],
                }),
                "delimiter": ("STRING", {
                    "multiline": False,
                    "default": "",
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "join_strings"
    OUTPUT_NODE = True
    CATEGORY = "rakete"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("NaN")

    def join_strings(self, strings, delimiter):
        return (delimiter.join(strings),)


NODE_CLASS_MAPPINGS = {
    "rakete.JoinStrings": RaketeJoinStrings,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "rakete.JoinStrings": "Join strings",
}