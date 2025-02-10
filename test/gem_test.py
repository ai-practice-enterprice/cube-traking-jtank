gem_points = [
    [(1, 2), (3, 4), (3, 4)],
    [(5, 6), (7, 8), (3, 4)],
    [(9, 10), (11, 12), (3, 4)],
    [(13, 14), (15, 16), (3, 4), (12, 4)]
]

# Transponeer de lijst om de corresponderende tuples te groeperen
transposed = list(zip(*gem_points))
resultaat = []
for groep in transposed:
    # Verzamel alle x- en y-coördinaten voor de huidige groep
    x_coordinaten = [t[0] for t in groep]
    y_coordinaten = [t[1] for t in groep]
    
    # Bereken het gemiddelde voor x en y
    gemiddelde_x = sum(x_coordinaten) / len(x_coordinaten)
    gemiddelde_y = sum(y_coordinaten) / len(y_coordinaten)
    
    # Voeg het gemiddelde toe als tuple (gecast naar integers)
    resultaat.append((int(gemiddelde_x), int(gemiddelde_y)))

print(resultaat)  # Output: [(7, 8), (9, 10)]