from hashing import hash_not_combine, hash_combine

factorial_cache = {
    0: 1,
    1: 1,
    2: 2,
    3: 6,
    4: 24,
    5: 120,
    6: 720,
    7: 5040,
    8: 40320,
    9: 362880,
    10: 3628800,
    11: 39916800,
    12: 479001600,
    13: 6227020800,
    14: 87178291200
}
'''
12,2,9,8,7,5,3
11,6,14,4,1,13,10
11->12
14,11,10,8,13,4,12
7,9,6,2,1,3,5
7->14
13,3,12,2,6,4,8
14,11,7,5,10,1,9
14->13
6,4,11,3,14,5,8
7,10,12,2,1,9,13
7->6
6,12,5,10,7,3,8
14,9,4,2,11,1,13
'''

def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

offset = 0

def lehmer_code(permutation):
    corrected = [p - 1 for p in permutation]
    code = 0
    code_raw = []
    n = len(corrected)
    for i in range(n):
        smaller_elements = sum(1 for j in range(i + 1, n) if corrected[j] < corrected[i])
        code_raw.append(smaller_elements)
        code += smaller_elements * factorial_cache[n - i - 1]
    #print(permutation, code_raw)
    return code +offset


max_value = 87178291199 + offset


def function(before, move, after):
    before_code = lehmer_code(before)
    after_code = lehmer_code(after)
    attacker, defender = move
    print('m', move)
    print('b', before_code)
    print('a', after_code)
    print('d', after_code-before_code)
    attempt = [4, 6, 8, 10, 5, 12, 13, 1, 11, 2, 3, 14, 9, 7]
    aa = lehmer_code(attempt)
    print('a', (aa * before_code) % max_value)

    print(prime_factors(before_code))
    print(prime_factors(after_code))
    print(prime_factors(after_code-before_code))
    print(prime_factors(aa))
    print(hash_not_combine(before_code, aa))
    print(prime_factors(hash_not_combine(before_code, aa)))
    print(hash_combine(before) % max_value)
    print(prime_factors(hash_combine(before) % max_value))
    print(hash_combine(after) % max_value)
    print(prime_factors(hash_combine(after) % max_value))
    print(hash_combine(attempt) % max_value)
    print(prime_factors(hash_combine(attempt) % max_value))
    print(hash_combine([before_code, aa]) % max_value)
    print(prime_factors(hash_combine([before_code, aa]) % max_value))
    #for i in range(1000):
    #    print(prime_factors(after_code + max_value * i))


if __name__ == '__main__':
    # board1 = [12, 2, 9, 8, 7, 5, 3, 11, 6, 14, 4, 1, 13, 10]
    # move1 = (11, 12)
    # board2 = [14, 11, 10, 8, 13, 4, 12, 7, 9, 6, 2, 1, 3, 5]
    # move2 = (7, 14)
    # board3 = [13, 3, 12, 2, 6, 4, 8, 14, 11, 7, 5, 10, 1, 9]
    # move3 = (14, 13)
    # board4 = [6, 4, 11, 3, 14, 5, 8, 7, 10, 12, 2, 1, 9, 13]
    # move4 = (7, 6)
    # board5 = [6, 12, 5, 10, 7, 3, 8, 14, 9, 4, 2, 11, 1, 13]
    # function(board1, move1, board2, '12')
    # function(board2, move2, board3, '23')
    # function(board3, move3, board4, '34')
    # function(board4, move4, board5, '45')
    board1 = [1, 11, 2, 6, 12, 7, 3, 8, 9, 10, 5, 13, 14, 4]
    move1 = (8, 1)
    board2 = [1, 6, 8, 10, 5, 12, 13, 4, 11, 2, 3, 14, 9, 7]
    move2 = (4, 1)
    board3 = [10, 4, 8, 1, 9, 13, 6, 3, 11, 7, 14, 5, 12, 2]
    #function(board1, move1, board2)
    function(board2, move2, board3)
