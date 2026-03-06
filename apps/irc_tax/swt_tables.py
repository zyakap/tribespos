SWT_RESIDENT_ANNUAL_BRACKETS = [
    (0,        20_000,    0,        0.00),
    (20_001,   33_000,    0,        0.22),
    (33_001,   70_000,    2_860,    0.30),
    (70_001,   250_000,   13_960,   0.35),
    (250_001,  float('inf'), 76_960, 0.42),
]

SWT_NON_RESIDENT_ANNUAL_BRACKETS = [
    (0,        33_000,    0,        0.22),
    (33_001,   70_000,    7_260,    0.30),
    (70_001,   250_000,   18_360,   0.35),
    (250_001,  float('inf'), 81_360, 0.42),
]


def calculate_swt_fortnightly(gross_fortnight: float, is_resident: bool = True) -> float:
    annual = gross_fortnight * 26
    brackets = SWT_RESIDENT_ANNUAL_BRACKETS if is_resident else SWT_NON_RESIDENT_ANNUAL_BRACKETS
    annual_tax = 0.0
    for (low, high, base, rate) in brackets:
        if annual <= low:
            break
        taxable = min(annual, high) - low
        annual_tax = base + (taxable * rate)
    return round(annual_tax / 26, 2)


def calculate_swt_with_benefits(gross_fortnight, housing_benefit=0.0, vehicle_benefit=0.0,
                                  other_benefits=0.0, is_resident=True) -> dict:
    total_gross = gross_fortnight + housing_benefit + vehicle_benefit + other_benefits
    swt = calculate_swt_fortnightly(total_gross, is_resident)
    return {
        'gross_wages': gross_fortnight,
        'taxable_benefits': housing_benefit + vehicle_benefit + other_benefits,
        'total_taxable': total_gross,
        'swt_deducted': swt,
        'net_pay': gross_fortnight - swt,
    }
