"""Original CC0 seed programs. Assertions encode explicit contracts."""
def seeds():
    rows = [
      ('sum_positive','Sum strictly positive integers.', 'return sum(x for x in xs if x > 0)', 'assert solve([-3,0,2,4]) == 6\nassert solve([]) == 0\nassert solve([-1]) == 0'),
      ('count_negative','Count strictly negative values.', 'return sum(1 for x in xs if x < 0)', 'assert solve([-2,0,3,-1]) == 2\nassert solve([]) == 0\nassert solve([0]) == 0'),
      ('count_even','Count even integers, including zero.', 'return sum(1 for x in xs if x % 2 == 0)', 'assert solve([0,1,2,-2,3]) == 3\nassert solve([]) == 0\nassert solve([1]) == 0'),
      ('sum_squares','Sum the squares of input numbers.', 'return sum(x * x for x in xs)', 'assert solve([-2,0,3]) == 13\nassert solve([]) == 0\nassert solve([4]) == 16'),
      ('spread','Return maximum minus minimum; empty input returns zero.', 'return max(xs) - min(xs) if xs else 0', 'assert solve([3,1,8]) == 7\nassert solve([]) == 0\nassert solve([-3,-1]) == 2'),
      ('first_last','Return first plus last value; empty returns zero.', 'return xs[0] + xs[-1] if xs else 0', 'assert solve([2,3,7]) == 9\nassert solve([]) == 0\nassert solve([4]) == 8'),
      ('nondecreasing','Return whether numbers are nondecreasing.', 'return all(xs[i] <= xs[i+1] for i in range(len(xs)-1))', 'assert solve([1,1,2]) is True\nassert solve([2,1]) is False\nassert solve([]) is True\nassert solve([4]) is True'),
      ('strict_increasing','Return whether numbers are strictly increasing.', 'return all(xs[i] < xs[i+1] for i in range(len(xs)-1))', 'assert solve([1,2,3]) is True\nassert solve([1,1]) is False\nassert solve([2,1]) is False\nassert solve([]) is True'),
      ('adjacent_gaps','Return differences between adjacent values.', 'return [xs[i+1] - xs[i] for i in range(len(xs)-1)]', 'assert solve([1,4,2]) == [3,-2]\nassert solve([]) == []\nassert solve([3]) == []'),
      ('product','Multiply all numbers; empty product is one.', 'p = 1\nfor x in xs:\n    p = p * x\nreturn p', 'assert solve([2,3,-1]) == -6\nassert solve([]) == 1\nassert solve([0,5]) == 0'),
      ('prefix_sum','Return cumulative sums.', 'out = []\ns = 0\nfor x in xs:\n    s = s + x\n    out.append(s)\nreturn out', 'assert solve([2,-1,4]) == [2,1,5]\nassert solve([]) == []\nassert solve([0]) == [0]'),
      ('clamp','Clamp each integer into inclusive interval zero to ten.', 'return [min(10,max(0,x)) for x in xs]', 'assert solve([-2,0,5,10,15]) == [0,0,5,10,10]\nassert solve([]) == []'),
      ('unique_sorted','Return sorted distinct integers.', 'return sorted(set(xs))', 'assert solve([3,1,3,2]) == [1,2,3]\nassert solve([]) == []'),
      ('absolute','Return absolute values.', 'return [x if x >= 0 else -x for x in xs]', 'assert solve([-2,0,4]) == [2,0,4]\nassert solve([]) == []'),
      ('pair_sums','Sum products of every unordered index pair.', 'return sum(xs[i]*xs[j] for i in range(len(xs)) for j in range(i+1,len(xs)))', 'assert solve([1,2,3]) == 11\nassert solve([2,2]) == 4\nassert solve([]) == 0\nassert solve([5]) == 0'),
      ('odd_values','Keep odd integers in original order.', 'return [x for x in xs if x % 2 != 0]', 'assert solve([-3,-2,0,1,2]) == [-3,1]\nassert solve([]) == []'),
      ('positive_mean','Mean of positive values; zero if none.', 'ys = [x for x in xs if x > 0]\nreturn sum(ys) / len(ys) if ys else 0', 'assert solve([-1,0,2,4]) == 3\nassert solve([]) == 0\nassert solve([5]) == 5'),
      ('alternating_sum','Add even-index values and subtract odd-index values.', 'return sum(x if i % 2 == 0 else -x for i,x in enumerate(xs))', 'assert solve([5,2,4,1]) == 6\nassert solve([]) == 0\nassert solve([3]) == 3'),
      ('reverse','Reverse sequence into a list.', 'return xs[::-1]', 'assert solve([1,2,3]) == [3,2,1]\nassert solve([]) == []\nassert solve([2]) == [2]'),
      ('count_runs','Count contiguous equal-value runs; empty returns zero.', 'return 1 + sum(xs[i] != xs[i-1] for i in range(1,len(xs))) if xs else 0', 'assert solve([1,1,2,2,1]) == 3\nassert solve([]) == 0\nassert solve([1]) == 1')
    ]
    return [dict(group=name, description=desc, language='python', license='CC0-1.0', origin='original_authored', fixed='def solve(xs):\n'+ '\n'.join('    '+line for line in body.splitlines())+'\n', tests=tests+'\n') for name,desc,body,tests in rows]
