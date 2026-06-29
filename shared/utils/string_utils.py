def reverse_string(s):
    return s[::-1]

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
