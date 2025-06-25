class RaketeGetWidgetValue:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "node_name_for_sr": ("STRING", {
                    "multiline": False,
                    "default": "",
                }),
                "widget_name": ("STRING", {
                    "multiline": False,
                    "default": "",
                }),
                "default_value": ("STRING", {
                    "multiline": False,
                    "default": "",
                }),
                "num_decimals": ("INT", {
                    "multiline": False,
                    "default": -1,
                })
            },
            "hidden": {
                "extra_pnginfo": "EXTRA_PNGINFO",
                "prompt": "PROMPT",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "get_widget_value_string"
    OUTPUT_NODE = True
    CATEGORY = "rakete"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return True

    def get_widget_value_string(self, node_name_for_sr, widget_name, default_value, num_decimals, extra_pnginfo, prompt):
        workflow = extra_pnginfo["workflow"]
        # Get node id.
        node_id = None
        for node in workflow["nodes"]:
            if "properties" in node and "Node name for S&R" in node["properties"]:
                if node["properties"]["Node name for S&R"] == node_name_for_sr:
                    node_id = node["id"]
                    break

        string = default_value
        if node_id is not None and str(node_id) in prompt:
            values = prompt[str(node_id)]
            if "inputs" in values and widget_name in values["inputs"]:
                value = values["inputs"][widget_name]
                if isinstance(value, float) and num_decimals >= 0:
                    string = f"{value:.{num_decimals}f}"
                else:
                    string = str(value)

        return (string,)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "rakete.GetWidgetValue": RaketeGetWidgetValue,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "rakete.GetWidgetValue": "Get Widget or Default Value",
}