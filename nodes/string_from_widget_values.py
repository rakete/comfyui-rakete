import re
import datetime

class RaketeBuildString:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "default_value": ("STRING", {
                    "multiline": False,
                    "default": "",
                }),
                "num_decimals": ("INT", {
                    "multiline": False,
                    "default": -1,
                }),
                "format_string": ("STRING", {
                    "multiline": True,
                    "default": "",
                })
            },
            "hidden": {
                "extra_pnginfo": "EXTRA_PNGINFO",
                "prompt": "PROMPT",
            },
            "optional": {
                "value_dict": ("DICT", {}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "build_string"
    OUTPUT_NODE = True
    CATEGORY = "rakete"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("NaN")

    def build_string(self, default_value, num_decimals, format_string, extra_pnginfo, prompt, value_dict={}):
        workflow = extra_pnginfo["workflow"]

        node_dict = {}
        nodes_by_id = {}
        for node in workflow["nodes"]:
            nodes_by_id[node["id"]] = node
            if "properties" in node and "Node name for S&R" in node["properties"]:
                key = node["properties"]["Node name for S&R"]
                if key:
                    node_dict[key] = node

        curly_pattern = r"(\{+([^}]*)\}+)"
        curly_matches = re.findall(curly_pattern, format_string)
        replacements = {}
        for outside, inside in curly_matches:
            if outside.startswith("{{") or outside.endswith("}}"):
                continue
            if outside in replacements:
                continue

            if inside in value_dict:
                string = str(value_dict[inside])
                replacements[outside] = string
                continue

            if inside.startswith("date:"):
                date_format = inside[5:]
                replacements[outside] = datetime.datetime.now().strftime(date_format)

            inside_parts = inside.split(".")
            node_key = inside_parts[0]
            if node_key not in node_dict:
                continue

            node_id = node_dict[node_key]["id"]
            widget_name = inside_parts[1]
            widget_ix = -1
            string = default_value
            if str(node_id) in prompt:
                #print("=====")
                while node_id is not None:
                    values = prompt[str(node_id)]
                    #print("node_id", node_id, values, widget_name)
                    if "inputs" in values and (widget_name in values["inputs"] or widget_ix >= 0):
                        if widget_ix >= 0:
                            values_list = list(values["inputs"].values())
                            value = values_list[widget_ix]
                        else:
                            value = values["inputs"][widget_name]

                        #print("value", value)
                        if isinstance(value, list):
                            #print("list", value)
                            node_id = int(value[0])
                            widget_ix = value[1]
                            continue

                        try:
                            float_value = float(value)
                            if num_decimals >= 0:
                                #print("converted to float:", float_value)
                                string = f"{float_value:.{num_decimals}f}"
                            else:
                                string = str(float_value)
                        except ValueError:
                            string = str(value)
                    break

            replacements[outside] = string

        built_string = format_string
        for outside, string in replacements.items():
            #print("replace:", outside, "with", string)
            built_string = built_string.replace(outside, string)

        #print("built_string:", built_string)

        return (built_string,)


NODE_CLASS_MAPPINGS = {
    "rakete.BuildString": RaketeBuildString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "rakete.BuildString": "Build String from Widget Values",
}
