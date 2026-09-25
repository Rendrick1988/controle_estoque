from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import BytesIO

from fastapi import HTTPException
from sqlalchemy import Date, and_, cast, func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


def sales_by_day(db: Session, company_id: int, *, days: int = 30) -> list[dict]:
    days = max(1, min(days, 365))
    since = datetime.now(timezone.utc) - timedelta(days=days - 1)
    query = (
        select(
            cast(func.date_trunc("day", Sale.created_at), Date).label("day"),
            func.coalesce(func.sum(Sale.total_value), 0).label("total"),
        )
        .where(and_(Sale.company_id == company_id, Sale.created_at >= since))
        .group_by("day")
        .order_by("day")
    )
    result_rows = db.execute(query).all()
    return [{"day": row.day, "total": float(row.total)} for row in result_rows]


def sales_by_month(db: Session, company_id: int, *, months: int = 12) -> list[dict]:
    months = max(1, min(months, 36))
    since = datetime.now(timezone.utc) - timedelta(days=months * 31)
    query = (
        select(
            func.to_char(func.date_trunc("month", Sale.created_at), "YYYY-MM").label("month"),
            func.coalesce(func.sum(Sale.total_value), 0).label("total"),
        )
        .where(and_(Sale.company_id == company_id, Sale.created_at >= since))
        .group_by("month")
        .order_by("month")
    )
    result_rows = db.execute(query).all()
    return [{"month": row.month, "total": float(row.total)} for row in result_rows]


def total_revenue(db: Session, company_id: int) -> float:
    query = select(func.coalesce(func.sum(Sale.total_value), 0)).where(Sale.company_id == company_id)
    total = db.scalar(query) or 0
    return float(total)


def top_products(db: Session, company_id: int, *, limit: int = 10) -> list[dict]:
    limit = max(1, min(limit, 50))
    sold_amount = func.coalesce(SaleItem.quantity, 0) + func.coalesce(SaleItem.weight_kg, 0)
    line_revenue = func.coalesce(SaleItem.quantity, 0) * SaleItem.price + func.coalesce(
        SaleItem.weight_kg, 0
    ) * SaleItem.price
    query = (
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.coalesce(func.sum(sold_amount), 0).label("quantity_sold"),
            func.coalesce(func.sum(line_revenue), 0).label("revenue"),
        )
        .join(Product, Product.id == SaleItem.product_id)
        .where(and_(SaleItem.company_id == company_id, Product.company_id == company_id))
        .group_by(Product.id, Product.name)
        .order_by(func.sum(line_revenue).desc())
        .limit(limit)
    )
    result_rows = db.execute(query).all()
    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity_sold": float(row.quantity_sold),
            "revenue": float(row.revenue),
        }
        for row in result_rows
    ]


def sales_history(db: Session, company_id: int, *, limit: int = 300) -> list[dict]:
    limit = max(1, min(limit, 1000))
    query = (
        select(
            Sale.id.label("sale_id"),
            Customer.name.label("customer_name"),
            Sale.total_value.label("total_value"),
            Sale.created_at.label("created_at"),
        )
        .outerjoin(Customer, and_(Customer.id == Sale.customer_id, Customer.company_id == company_id))
        .where(Sale.company_id == company_id)
        .order_by(Sale.created_at.desc())
        .limit(limit)
    )
    result_rows = db.execute(query).all()
    return [
        {
            "sale_id": row.sale_id,
            "customer_name": row.customer_name or "Sem cliente cadastrado",
            "total_value": float(row.total_value),
            "created_at": row.created_at,
        }
        for row in result_rows
    ]


def build_printable_report_html(
    *,
    company_name: str,
    revenue: float,
    sales_by_day_items: list[dict],
    sales_by_month_items: list[dict],
    top_products_items: list[dict],
) -> str:
    sales_by_day_rows_html = "".join(
        f"<tr><td>{row['day']}</td><td>R$ {row['total']:.2f}</td></tr>" for row in sales_by_day_items
    )
    sales_by_month_rows_html = "".join(
        f"<tr><td>{row['month']}</td><td>R$ {row['total']:.2f}</td></tr>" for row in sales_by_month_items
    )
    top_product_rows_html = "".join(
        (
            f"<tr><td>{row['product_name']}</td>"
            f"<td>{row['quantity_sold']}</td><td>R$ {row['revenue']:.2f}</td></tr>"
        )
        for row in top_products_items
    )
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Relatório de Vendas</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #111; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .meta {{ margin-bottom: 18px; color: #555; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 18px; }}
    th, td {{ border: 1px solid #ccc; text-align: left; padding: 8px; font-size: 13px; }}
    th {{ background: #f5f5f5; }}
  </style>
</head>
<body>
  <h1>Relatório de Vendas</h1>
  <div class="meta">Empresa: {company_name} | Gerado em: {generated_at}</div>
  <h2>Faturamento total: R$ {revenue:.2f}</h2>
  <h2>Vendas por dia</h2>
  <table>
    <thead><tr><th>Dia</th><th>Total</th></tr></thead>
    <tbody>{sales_by_day_rows_html or '<tr><td colspan="2">Sem dados</td></tr>'}</tbody>
  </table>
  <h2>Vendas por mês</h2>
  <table>
    <thead><tr><th>Mês</th><th>Total</th></tr></thead>
    <tbody>{sales_by_month_rows_html or '<tr><td colspan="2">Sem dados</td></tr>'}</tbody>
  </table>
  <h2>Produtos mais vendidos</h2>
  <table>
    <thead><tr><th>Produto</th><th>Quantidade</th><th>Receita</th></tr></thead>
    <tbody>{top_product_rows_html or '<tr><td colspan="3">Sem dados</td></tr>'}</tbody>
  </table>
</body>
</html>"""


def build_sales_report_pdf(
    *,
    company_name: str,
    revenue: float,
    sales_by_day_items: list[dict],
    sales_by_month_items: list[dict],
    top_products_items: list[dict],
) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Dependência de PDF indisponível (reportlab)") from exc

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Relatorio de Vendas")
    y -= 24

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, y, f"Empresa: {company_name}")
    y -= 16
    pdf.drawString(40, y, f"Faturamento total: R$ {revenue:.2f}")
    y -= 22

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Vendas por dia")
    y -= 18
    pdf.setFont("Helvetica", 10)
    if sales_by_day_items:
        for daily_sales_entry in sales_by_day_items[:20]:
            pdf.drawString(50, y, f"{daily_sales_entry['day']}: R$ {daily_sales_entry['total']:.2f}")
            y -= 14
            if y < 80:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 10)
    else:
        pdf.drawString(50, y, "Sem dados")
        y -= 14

    y -= 10
    if y < 100:
        pdf.showPage()
        y = height - 40
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Vendas por mes")
    y -= 18
    pdf.setFont("Helvetica", 10)
    if sales_by_month_items:
        for monthly_sales_entry in sales_by_month_items[:20]:
            pdf.drawString(50, y, f"{monthly_sales_entry['month']}: R$ {monthly_sales_entry['total']:.2f}")
            y -= 14
            if y < 80:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 10)
    else:
        pdf.drawString(50, y, "Sem dados")
        y -= 14

    y -= 10
    if y < 100:
        pdf.showPage()
        y = height - 40
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Produtos mais vendidos")
    y -= 18
    pdf.setFont("Helvetica", 10)
    if top_products_items:
        for top_product_entry in top_products_items[:20]:
            pdf.drawString(
                50,
                y,
                (
                    f"{top_product_entry['product_name']} - Qtd: {top_product_entry['quantity_sold']} - "
                    f"Receita: R$ {top_product_entry['revenue']:.2f}"
                ),
            )
            y -= 14
            if y < 80:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 10)
    else:
        pdf.drawString(50, y, "Sem dados")

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer.read()
