import random
F = open('wordlist.txt')
words = F.readlines()
F.close()
while True:
    word = words[random.randrange(len(words))]
    while len(word) > 5 or len(word) == 0:
        word = words[random.randrange(0, len(words))]
    word = word.rstrip()
    old_word = word
    word = list(word)
    while word:
        print(word.pop(random.randrange(len(word))), end = ' ')
    print('\nType your answer')
    match_word = input()
    new_word = match_word + '\n'
    if new_word in words and set(match_word) == set(old_word):
            print('You win.')
    else:
        print('The answer is ' + old_word)
