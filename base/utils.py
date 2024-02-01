import re


def extract_session_id(session_str :str):
    match = re.search(r"sessions/(.*?)/contexts",session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    else:
        return ""
    
def get_str_from_food_dict(food_dict: dict):
    final_string = ", ".join([f"{int(v)} {k}" for k,v in food_dict.items()])
    return final_string