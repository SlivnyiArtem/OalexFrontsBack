def H(x):
    return float(x) if x and x > 0 else float('inf')

def H_in(A, B, Ccite, Ccited):
    if A in Ccited.get(B, set()):
        return H(len(Ccite.get(A, set())))
    if B in Ccited.get(A, set()):
        return H(len(Ccite.get(B, set())))
    return float('inf')

def H_out(A, B, Ccite, Ccited):
    if B in Ccited.get(A, set()):
        return H(len(Ccited.get(A, set())))
    if A in Ccited.get(B, set()):
        return H(len(Ccited.get(B, set())))
    return float('inf')

def calculate_similarity(A, B, Ccite, Ccited):
    NinA = len(Ccite.get(A, set()))
    NinB = len(Ccite.get(B, set()))
    NoutA = len(Ccited.get(A, set()))
    NoutB = len(Ccited.get(B, set()))

    cite_both = len(Ccite.get(A, set()).intersection(Ccite.get(B, set())))
    cited_both = len(Ccited.get(A, set()).intersection(Ccited.get(B, set())))

    denomimator = []
    if NinA > 0:
        denomimator.append(NinA / H(NinA))
    if NinB > 0:
        denomimator.append(NinB / H(NinB))
    if NoutA > 0:
        denomimator.append(NoutA / H(NoutA))
    if NoutB > 0:
        denomimator.append(NoutB / H(NoutB))

    if not denomimator:
        return 0.0

    numer_components = []
    if cite_both > 0:
        numer_components.append(cite_both / H(NinA))
        numer_components.append(cite_both / H(NinB))
    if cited_both > 0:
        numer_components.append(cited_both / H(NoutA))
        numer_components.append(cited_both / H(NoutB))
    numer_components.append(1.0 / H_in(A, B, Ccite, Ccited))
    numer_components.append(1.0 / H_out(A, B, Ccite, Ccited))

    numerator = sum(numer_components)
    denominator = sum(denomimator)

    if denominator == 0:
        return 0.0
    return float(numerator / denominator)