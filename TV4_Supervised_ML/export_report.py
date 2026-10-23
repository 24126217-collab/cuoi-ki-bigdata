import io
import pandas as pd
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph,
    Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def prepare_report(orders):
    df = orders.copy()

    df["total_amount"] = pd.to_numeric(
        df["total_amount"], errors="coerce"
    )
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )

    df = df.dropna(subset=["order_date"])

    # Doanh thu chỉ tính đơn hoàn thành
    completed = df[df["status"] == "Completed"]

    summary = pd.DataFrame([{
        "Total Orders": len(df),
        "Completed Orders": len(completed),
        "Cancelled Orders": (
            df["status"] == "Cancelled"
        ).sum(),
        "Revenue (VND)": completed["total_amount"].sum(),
        "AOV (VND)": completed["total_amount"].mean()
    }]).fillna(0)

    monthly = completed.copy()
    monthly["month"] = (
        monthly["order_date"].dt.strftime("%Y-%m")
    )

    monthly = monthly.groupby(
        "month", as_index=False
    ).agg(
        orders=("order_id", "count"),
        revenue=("total_amount", "sum")
    )

    return summary, monthly


def export_excel(orders, output_path="business_report.xlsx"):
    summary, monthly = prepare_report(orders)

    with pd.ExcelWriter(
        output_path, engine="openpyxl"
    ) as writer:
        summary.to_excel(
            writer, sheet_name="KPI Summary",
            index=False
        )
        monthly.to_excel(
            writer, sheet_name="Monthly Revenue",
            index=False
        )

    return output_path


def export_pdf(orders, output_path="business_report.pdf"):
    summary, monthly = prepare_report(orders)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4
    )
    styles = getSampleStyleSheet()
    story = []

    # Nội dung PDF dùng tiếng Anh để tránh lỗi font
    story.append(Paragraph(
        "E-COMMERCE BUSINESS REPORT",
        styles["Title"]
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph(
        "Business KPI Summary",
        styles["Heading2"]
    ))

    kpi_data = [["Metric", "Value"]]

    for col in summary.columns:
        value = summary.iloc[0][col]
        if isinstance(value, (int, float)):
            value = f"{value:,.0f}"
        kpi_data.append([col, str(value)])

    kpi_table = Table(kpi_data, colWidths=[260, 190])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(kpi_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        "Monthly Revenue",
        styles["Heading2"]
    ))

    month_data = [["Month", "Orders", "Revenue (VND)"]]

    for _, row in monthly.iterrows():
        month_data.append([
            str(row["month"]),
            str(int(row["orders"])),
            f'{row["revenue"]:,.0f}'
        ])

    month_table = Table(
        month_data, colWidths=[100, 100, 250],
        repeatRows=1
    )
    month_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(month_table)
    doc.build(story)

    return output_path
