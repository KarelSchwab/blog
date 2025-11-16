# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
from collections import Counter


def main() -> None:
    # --- Instantiation ---
    # Empty Counter
    counter = Counter() 
    print(counter)

    # Counter from a str
    counter = Counter("mississippi") 
    print(counter)

    # Counter from a list
    counter = Counter(["A", "B", "C", "D"]) 
    print(counter)

    # Counter from a dict
    counter = Counter({ "Apple": 3, "Banana": 5 }) 
    print(counter)

    # Counter from kwargs
    counter = Counter(red=255, green=100, blue=200) 
    print(counter)

    # --- Indexing ---
    counter = Counter("mississippi") 
    print(counter["s"])
    print(counter["x"])

    # --- Subtraction ---
    counter = Counter("mississippi") 
    print(counter)
    counter.subtract("i")
    print(counter)

    counter = Counter("mississippi") 
    print(counter)
    counter.subtract("iis")
    print(counter)

    counter = Counter("mississippi") 
    print(counter)
    counter.subtract({"s": 3})
    print(counter)

    counter = Counter("mississippi") 
    print(counter)
    counter.subtract(s=3, p=1, m=2)
    print(counter)

    # --- Addition ---
    counter = Counter("mississippi") 
    print(counter)
    counter.update("i")
    print(counter)

    counter = Counter("mississippi") 
    print(counter)
    counter.update("iis")
    print(counter)

    counter = Counter("mississippi") 
    print(counter)
    counter.update({"s": 3})
    print(counter)

    counter = Counter("mississippi") 
    print(counter)
    counter.update(s=3, p=1, m=2)
    print(counter)

    # --- Useful methods ---
    counter = Counter("mississippi") 
    print(list(counter.elements()))
    print(sorted(counter.elements()))
    print(sorted(counter.elements(), reverse=True))
    print(counter.most_common())    
    print(counter.most_common(2))    
    print(counter.total())

    # --- Deletion ---
    del counter["i"]
    print(counter)

    # --- Addition of two Counters ---
    counter_1 = Counter("mississippi")
    print(counter_1)
    counter_2 = Counter(p=10, m=3, x=5, y=-3)
    print(counter_2)
    counter_3 = counter_1 + counter_2
    print(counter_3)

    # --- Subtraction of two Counters ---
    counter_1 = Counter("mississippi")
    print(counter_1)
    counter_2 = Counter(p=1, m=2, s=2, x=5, y=-3)
    print(counter_2)
    counter_3 = counter_1 - counter_2
    print(counter_3)

    # --- Intersection ---
    counter_1 = Counter("mississippi")
    print(counter_1)
    counter_2 = Counter("mmmiss")
    print(counter_2)
    counter_3 = counter_1 & counter_2
    print(counter_3)

    # --- Union ---
    counter_1 = Counter("mississippi")
    print(counter_1)
    counter_2 = Counter("mmmissx")
    print(counter_2)
    counter_3 = counter_1 | counter_2
    print(counter_3)

if __name__ == "__main__":
    main()
