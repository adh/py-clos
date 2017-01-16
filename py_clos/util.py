def common_superclass(*classes):
    mros = (i.mro() for i in classes)
    mro = next(mros)
    common = set(mro).intersection(*mros)
    return next((x for x in mro if x in common), None)

def merge_lists(*lists):
    longest = lists[0]
    for i in lists[1:]:
        if len(i) > len(longest):
            longest = i

    for i in lists:
        if i is longest:
            continue
        if i != longest[:len(i)]:
            raise ValueError("{} s not prefix of {}".format(i, longest))

    return longest
    
