def arrange_squares(empty_2d_array, points):
    # Check if the number of points is divisible by 4
    if len(points) % 4 != 0:
        raise ValueError("The number of points must be divisible by 4.")
    
    # Function to check if four points form a square
    def is_square(points, tolerance=1e-6):
        if len(points) != 4:
            return False
        dists = []
        for i in range(4):
            for j in range(i+1, 4):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist_sq = dx*dx + dy*dy
                dists.append(dist_sq)
        dists.sort()
        if len(dists) < 6:
            return False  # Not enough distances (shouldn't happen with 4 points)
        # Check first four are sides and equal
        if not all(abs(d - dists[0]) < tolerance for d in dists[:4]):
            return False
        # Check last two are diagonals and equal and twice the side
        if not (abs(dists[4] - dists[5]) < tolerance and abs(dists[4] - 2*dists[0]) < tolerance):
            return False
        return True
    
    # Generate all possible squares
    from itertools import combinations
    possible_squares = []
    for quad in combinations(points, 4):
        if is_square(quad):
            possible_squares.append(quad)
    
    # Backtracking to find exact cover
    used = set()
    solution = []
    all_points_set = set(points)
    
    def backtrack():
        nonlocal used, solution
        if len(used) == len(all_points_set):
            return True
        for square in possible_squares:
            square_set = set(square)
            if square_set.isdisjoint(used):
                used.update(square_set)
                solution.append(square)
                if backtrack():
                    return True
                used.difference_update(square_set)
                solution.pop()
        return False
    
    if not backtrack():
        raise ValueError("No valid squares arrangement found.")
    
    # Order each square's points and the squares themselves
    ordered_squares = []
    for sq in solution:
        sorted_sq = sorted(sq, key=lambda p: (p[0], p[1]))
        ordered_squares.append(sorted_sq)
    # Sort the squares by their upper-left point
    ordered_squares.sort(key=lambda x: (x[0][0], x[0][1]))
    # Append to the empty_2d_array
    empty_2d_array.extend(ordered_squares)
    return empty_2d_array

# Example usage:
points = [(0,5), (15,10), (5,0), (5,5), (10,10), (10,15), (15,15), (0,0)]
result = []
arrange_squares(result, points)
print(result)