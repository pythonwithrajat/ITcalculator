import streamlit as st

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Indian Income Tax Calculator",
    page_icon="💰",
    layout="centered"
)

# -----------------------------
# Title & Introduction
# -----------------------------
st.title("💰 Indian Income Tax Calculator")
st.write("Calculate and compare your estimated income tax across financial years and tax regimes.")

st.divider()

# -----------------------------
# FY & Regime Selection
# -----------------------------
st.header("⚙️ Year & Tax Regime Selection")

col_fy, col_regime = st.columns(2)

with col_fy:
    financial_year = st.selectbox(
        "📅 Financial Year",
        [
            "FY 2025-26 (AY 2026-27)",
            "FY 2024-25 (AY 2025-26)",
            "FY 2023-24 (AY 2024-25)"
        ],
        index=0,
        help="Select the financial year in which the income was earned."
    )

with col_regime:
    regime = st.radio(
        "🏛️ Tax Regime",
        [
            "New Tax Regime",
            "Old Tax Regime"
        ],
        index=0,
        horizontal=True,
        help="New Regime has lower tax rates with fewer deductions. Old Regime allows exemptions like 80C, 80D, etc."
    )

# -----------------------------
# Standard Deduction Determination
# -----------------------------
# FY 2024-25 & FY 2025-26: New Regime standard deduction is ₹75,000; Old Regime is ₹50,000.
# FY 2023-24: Both regimes have standard deduction of ₹50,000.
if regime == "New Tax Regime":
    if financial_year in ["FY 2025-26 (AY 2026-27)", "FY 2024-25 (AY 2025-26)"]:
        standard_deduction = 75000.0
    else:
        standard_deduction = 50000.0
else:
    standard_deduction = 50000.0

st.info(f"💡 **Standard Deduction** applicable for **{regime}** in **{financial_year.split()[0]}**: **₹{standard_deduction:,.0f}**")

st.divider()

# -----------------------------
# Income & Deductions Inputs
# -----------------------------
st.header("📋 Income & Deduction Details")

annual_income = st.number_input(
    "Annual Gross Income (₹)",
    min_value=0.0,
    value=1200000.0,
    step=10000.0,
    format="%.2f"
)

if regime == "Old Tax Regime":
    st.subheader("Deductions (Old Tax Regime only)")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        section_80c = st.number_input(
            "Section 80C (PPF, ELSS, EPF, LIC) (₹)",
            min_value=0.0,
            max_value=150000.0,
            value=150000.0,
            step=5000.0,
            help="Maximum deduction allowed under 80C is ₹1,50,000."
        )
    with col_d2:
        section_80d = st.number_input(
            "Section 80D (Health Insurance) (₹)",
            min_value=0.0,
            value=25000.0,
            step=5000.0
        )
    other_deductions = st.number_input(
        "Other Deductions (HRA, 80CCD, 80E, etc.) (₹)",
        min_value=0.0,
        value=0.0,
        step=5000.0
    )
    total_deductions = standard_deduction + section_80c + section_80d + other_deductions
else:
    section_80c = 0.0
    section_80d = 0.0
    other_deductions = 0.0
    total_deductions = standard_deduction
    st.caption("ℹ️ *Under the New Tax Regime, Chapter VI-A deductions (80C, 80D, etc.) are generally not available. Standard deduction is automatically included.*")

taxable_income = max(0.0, annual_income - total_deductions)

# -----------------------------
# Slab Structure Configurations
# -----------------------------
def get_tax_slabs(fy, reg):
    if reg == "Old Tax Regime":
        return [
            (250000, 0.0, "Up to ₹2,50,000"),
            (500000, 0.05, "₹2,50,001 - ₹5,00,000"),
            (1000000, 0.20, "₹5,00,001 - ₹10,00,000"),
            (float("inf"), 0.30, "Above ₹10,00,000")
        ]
    
    if fy == "FY 2025-26 (AY 2026-27)":
        return [
            (400000, 0.0, "Up to ₹4,00,000"),
            (800000, 0.05, "₹4,00,001 - ₹8,00,000"),
            (1200000, 0.10, "₹8,00,001 - ₹12,00,000"),
            (1600000, 0.15, "₹12,00,001 - ₹16,00,000"),
            (2000000, 0.20, "₹16,00,001 - ₹20,00,000"),
            (2400000, 0.25, "₹20,00,001 - ₹24,00,000"),
            (float("inf"), 0.30, "Above ₹24,00,000")
        ]
    elif fy == "FY 2024-25 (AY 2025-26)":
        return [
            (300000, 0.0, "Up to ₹3,00,000"),
            (700000, 0.05, "₹3,00,001 - ₹7,00,000"),
            (1000000, 0.10, "₹7,00,001 - ₹10,00,000"),
            (1200000, 0.15, "₹10,00,001 - ₹12,00,000"),
            (1500000, 0.20, "₹12,00,001 - ₹15,00,000"),
            (float("inf"), 0.30, "Above ₹15,00,000")
        ]
    else:  # FY 2023-24 (AY 2024-25)
        return [
            (300000, 0.0, "Up to ₹3,00,000"),
            (600000, 0.05, "₹3,00,001 - ₹6,00,000"),
            (900000, 0.10, "₹6,00,001 - ₹9,00,000"),
            (1200000, 0.15, "₹9,00,001 - ₹12,00,000"),
            (1500000, 0.20, "₹12,00,001 - ₹15,00,000"),
            (float("inf"), 0.30, "Above ₹15,00,000")
        ]

# -----------------------------
# Tax Calculation Logic
# -----------------------------
def calculate_tax(income, fy, reg):
    slabs = get_tax_slabs(fy, reg)
    gross_tax = 0.0
    previous_limit = 0.0
    slab_breakdown = []

    for limit, rate, label in slabs:
        taxable_in_slab = min(max(income - previous_limit, 0.0), limit - previous_limit)
        slab_tax = taxable_in_slab * rate
        if taxable_in_slab > 0:
            slab_breakdown.append({
                "Slab": label,
                "Tax Rate": f"{int(rate * 100)}%",
                "Taxable Amount": taxable_in_slab,
                "Tax": slab_tax
            })
        gross_tax += slab_tax
        if income <= limit:
            break
        previous_limit = limit

    # Section 87A Rebate & Marginal Relief
    rebate_87a = 0.0
    if reg == "Old Tax Regime":
        # Rebate up to ₹12,500 if taxable income <= ₹5,00,000
        if income <= 500000.0:
            rebate_87a = min(gross_tax, 12500.0)
    else:
        # New Tax Regime
        if fy == "FY 2025-26 (AY 2026-27)":
            rebate_threshold = 1200000.0
            max_rebate = 60000.0
        else:
            rebate_threshold = 700000.0
            max_rebate = 25000.0

        if income <= rebate_threshold:
            rebate_87a = min(gross_tax, max_rebate)
        elif income > rebate_threshold:
            # Marginal relief under Section 87A: tax payable cannot exceed income in excess of rebate threshold
            excess_income = income - rebate_threshold
            if gross_tax > excess_income:
                rebate_87a = gross_tax - excess_income

    net_tax_before_cess = max(0.0, gross_tax - rebate_87a)
    cess = net_tax_before_cess * 0.04
    total_tax = net_tax_before_cess + cess

    return {
        "gross_tax": gross_tax,
        "rebate_87a": rebate_87a,
        "net_tax_before_cess": net_tax_before_cess,
        "cess": cess,
        "total_tax": total_tax,
        "slab_breakdown": slab_breakdown
    }

# -----------------------------
# Slab Rates Reference Expander
# -----------------------------
with st.expander(f"🔍 View Tax Slabs for {financial_year} ({regime})"):
    current_slabs = get_tax_slabs(financial_year, regime)
    slab_table = []
    for _, rate, label in current_slabs:
        slab_table.append({
            "Income Range": label,
            "Tax Rate": f"{int(rate * 100)}%"
        })
    st.table(slab_table)

# -----------------------------
# Calculate Button
# -----------------------------
st.divider()

if st.button("🧮 Calculate Income Tax", use_container_width=True, type="primary"):
    res = calculate_tax(taxable_income, financial_year, regime)
    
    total_tax = res["total_tax"]
    monthly_tax = total_tax / 12.0

    st.header("📊 Tax Calculation Result")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Gross Income", f"₹{annual_income:,.2f}")
        st.metric("Total Deductions", f"₹{total_deductions:,.2f}")
        st.metric("Net Taxable Income", f"₹{taxable_income:,.2f}")

    with col2:
        st.metric("Gross Tax", f"₹{res['gross_tax']:,.2f}")
        st.metric("Rebate u/s 87A", f"₹{res['rebate_87a']:,.2f}")
        st.metric("Tax after Rebate", f"₹{res['net_tax_before_cess']:,.2f}")

    with col3:
        st.metric("Cess (4%)", f"₹{res['cess']:,.2f}")
        st.metric("Total Tax Payable", f"₹{total_tax:,.2f}")
        st.metric("Monthly Tax", f"₹{monthly_tax:,.2f}")

    if res["rebate_87a"] > 0:
        st.success(f"🎉 **Section 87A Rebate Applied:** ₹{res['rebate_87a']:,.2f} tax relief!")

    st.subheader(f"💰 Estimated Total Annual Tax: ₹{total_tax:,.2f}")
    st.caption(f"Estimated Monthly Tax Deduction: ₹{monthly_tax:,.2f}")

    # Slab Breakdown Table
    if res["slab_breakdown"]:
        st.subheader("📑 Slab-wise Breakdown")
        breakdown_display = []
        for item in res["slab_breakdown"]:
            breakdown_display.append({
                "Slab": item["Slab"],
                "Rate": item["Tax Rate"],
                "Taxable Amount": f"₹{item['Taxable Amount']:,.2f}",
                "Tax": f"₹{item['Tax']:,.2f}"
            })
        st.table(breakdown_display)

    # -----------------------------
    # Summary
    # -----------------------------
    st.subheader("📌 Summary")

    summary = {
        "Financial Year": financial_year,
        "Tax Regime": regime,
        "Annual Gross Income": f"₹{annual_income:,.2f}",
        "Standard Deduction": f"₹{standard_deduction:,.2f}",
        "Other Deductions": f"₹{total_deductions - standard_deduction:,.2f}",
        "Net Taxable Income": f"₹{taxable_income:,.2f}",
        "Gross Tax (before rebate)": f"₹{res['gross_tax']:,.2f}",
        "Section 87A Tax Rebate": f"₹{res['rebate_87a']:,.2f}",
        "Health & Education Cess (4%)": f"₹{res['cess']:,.2f}",
        "Total Tax Payable": f"₹{total_tax:,.2f}",
        "Estimated Monthly Tax": f"₹{monthly_tax:,.2f}"
    }

    for key, value in summary.items():
        st.write(f"**{key}:** {value}")

# -----------------------------
# Disclaimer
# -----------------------------
st.divider()

st.caption(
    "⚠️ This calculator is for educational and estimation purposes only. "
    "Tax slabs, deductions, rebates, surcharge rules and other provisions "
    "vary across financial years and budgets. Verify calculations with "
    "official income tax guidelines or a certified tax advisor before filing."
)