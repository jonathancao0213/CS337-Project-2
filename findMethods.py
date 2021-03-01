def findMethod(step):
    doc = nlp(step)
    methods = {}
    last = None
    for entity in doc:
        if entity.pos_ == "VERB":
            methods[entity] = None
            last = entity
        if entity.dep_ == "pobj"

    ## get indices of times, pobj (minutes, hours, days, etc), and method, and use distance to see which ones belong to which one.

    return methods
