from pathlib import Path


def make_options(correct, spread=2):
    return [correct, correct + spread, correct - spread, correct + 2 * spread]


def normalize_options(opts, correct):
    # keep unique positive integers for simple arithmetic
    seen = set()
    out = []
    for v in opts:
        if v not in seen and v > 0:
            seen.add(v)
            out.append(v)
    while len(out) < 4:
        candidate = correct + len(out)
        if candidate not in seen and candidate > 0:
            seen.add(candidate)
            out.append(candidate)
    return out[:4]


def letter_for(index):
    return ['A', 'B', 'C', 'D'][index]


def generate_python(i):
    difficulty = ['Easy', 'Medium', 'Hard'][i % 3]
    a = 2 + (i % 7)
    b = 3 + ((i // 7) % 6)
    templates = [
        (f"What is the result of {a} + {b}?", lambda: (a + b, a + b + 1, a + b + 2, a + b - 1)),
        (f"What is the result of {a} * {b}?", lambda: (a * b, a * b + 2, a * b - 1, a * b + 5)),
        (f"Which Python keyword defines a function?", lambda: ("def", "func", "for", "class")),
        (f"Which symbol starts a comment in Python?", lambda: ("#", "//", "/*", "--")),
        (f"What is the type of [1, 2, 3]?", lambda: ("list", "tuple", "set", "dict")),
    ]
    q, gen = templates[i % len(templates)]
    values = list(gen())
    if isinstance(values[0], int):
        opts = normalize_options(values, values[0])
        answer = letter_for(opts.index(values[0]))
        return f"Python Programming|{q}|{opts[0]}|{opts[1]}|{opts[2]}|{opts[3]}|{answer}|Python template|{difficulty}"
    opts = values
    answer = letter_for(opts.index(values[0]))
    return f"Python Programming|{q}|{opts[0]}|{opts[1]}|{opts[2]}|{opts[3]}|{answer}|Python template|{difficulty}"


def generate_math(i):
    difficulty = ['Easy', 'Medium', 'Hard'][i % 3]
    a = 5 + (i % 9)
    b = 4 + ((i // 9) % 8)
    templates = [
        (f"What is {a} + {b}?", lambda: (a + b, a + b + 1, a + b - 2, a + b + 4)),
        (f"What is {a} x {b}?", lambda: (a * b, a * b + 3, a * b - 1, a * b + 7)),
        (f"If x + 5 = 12, what is x?", lambda: (7, 5, 6, 8)),
        (f"What is 25% of {a * b}?", lambda: ((a * b) // 4, (a * b) // 3, (a * b) // 5, (a * b) // 2)),
    ]
    q, gen = templates[i % len(templates)]
    values = list(gen())
    opts = normalize_options(values, values[0])
    answer = letter_for(opts.index(values[0]))
    return f"Mathematics|{q}|{opts[0]}|{opts[1]}|{opts[2]}|{opts[3]}|{answer}|Math template|{difficulty}"


def generate_programming(i):
    difficulty = ['Easy', 'Medium', 'Hard'][i % 3]
    a = 1 + (i % 5)
    templates = [
        (f"What is the correct C++ keyword for a loop?", lambda: ("for", "if", "while", "switch")),
        (f"Which type stores whole numbers in C++?", lambda: ("int", "float", "char", "bool")),
        (f"What does 'cout' do in C++?", lambda: ("print output", "read input", "declare a variable", "create a loop")),
        (f"How many bytes is a char usually?", lambda: (1, 2, 4, 8)),
    ]
    q, gen = templates[i % len(templates)]
    values = list(gen())
    opts = values
    answer = letter_for(opts.index(values[0]))
    return f"Programming Basics|{q}|{opts[0]}|{opts[1]}|{opts[2]}|{opts[3]}|{answer}|Programming template|{difficulty}"


def generate_calculus(i):
    difficulty = ['Easy', 'Medium', 'Hard'][i % 3]
    x = 2 + (i % 4)
    templates = [
        (f"What is the derivative of x^2?", lambda: ("2x", "x", "x^2", "1")),
        (f"What is the derivative of {x}x?", lambda: (str(x), str(x + 1), str(x - 1), "0")),
        (f"What is the integral of 1?", lambda: ("x", "1", "x^2", "0")),
        (f"What is the derivative of sin(x)?", lambda: ("cos(x)", "sin(x)", "-cos(x)", "x")),
    ]
    q, gen = templates[i % len(templates)]
    values = list(gen())
    opts = values
    answer = letter_for(opts.index(values[0]))
    return f"Calculus|{q}|{opts[0]}|{opts[1]}|{opts[2]}|{opts[3]}|{answer}|Calculus template|{difficulty}"


def generate_english(i):
    difficulty = ['Easy', 'Medium', 'Hard'][i % 3]
    templates = [
        ("What type of word is 'book' in 'I read a book'?", lambda: ("noun", "verb", "adjective", "adverb")),
        ("What is the plural of 'child'?", lambda: ("children", "childs", "childes", "childrens")),
        ("Which word is a synonym of 'happy'?", lambda: ("joyful", "sad", "angry", "tired")),
        ("What tense is 'She is running'?", lambda: ("present continuous", "past", "future", "simple present")),
    ]
    q, gen = templates[i % len(templates)]
    values = list(gen())
    opts = values
    answer = letter_for(opts.index(values[0]))
    return f"English|{q}|{opts[0]}|{opts[1]}|{opts[2]}|{opts[3]}|{answer}|English template|{difficulty}"


def main():
    generators = [
        ("Python Programming", generate_python),
        ("Mathematics", generate_math),
        ("Programming Basics", generate_programming),
        ("Calculus", generate_calculus),
        ("English", generate_english),
    ]
    out_lines = []
    for subject, gen in generators:
        for i in range(1000):
            out_lines.append(gen(i))
    Path("questions_db.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"Generated {len(out_lines)} questions in questions_db.txt")


if __name__ == "__main__":
    main()
