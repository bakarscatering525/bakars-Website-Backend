import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Iterable, Optional, List, Dict, Any
import html
from datetime import datetime

from fastapi.concurrency import run_in_threadpool

from app.config.settings import settings
from app.models.order import OrderModel, OrderItem

logger = logging.getLogger(__name__)


class EmailNotConfiguredError(RuntimeError):
    """Raised when SMTP settings are missing."""


def _build_email_message(
    subject: str,
    body_text: str,
    body_html: Optional[str],
    recipients: Iterable[str],
    reply_to: Optional[str] = None,
) -> EmailMessage:
    message = EmailMessage()
    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME

    if not from_email:
        raise EmailNotConfiguredError("SMTP sender email is not configured.")

    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
    message["To"] = ", ".join(recipients)

    if reply_to:
        message["Reply-To"] = reply_to

    message.set_content(body_text)

    if body_html:
        message.add_alternative(body_html, subtype="html")

    return message


def _send_email(message: EmailMessage) -> None:
    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD

    if not (host and port and username and password):
        raise EmailNotConfiguredError("SMTP credentials are not fully configured.")

    context = ssl.create_default_context()

    with smtplib.SMTP(host, port, timeout=30) as server:
        if settings.SMTP_USE_TLS:
            server.starttls(context=context)

        server.login(username, password)
        server.send_message(message)

    logger.info("Email successfully sent to %s", message["To"])


async def send_email_async(
    *,
    subject: str,
    body_text: str,
    recipients: Iterable[str],
    body_html: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> None:
    """
    Asynchronously send an email using the configured SMTP server.
    """
    message = _build_email_message(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=recipients,
        reply_to=reply_to,
    )

    await run_in_threadpool(_send_email, message)


def _format_currency(amount: Optional[float]) -> str:
    try:
        return f"${float(amount):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def _format_datetime(value: Optional[datetime]) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value) if value else "N/A"


def _extract_order_items(order: OrderModel) -> List[OrderItem]:
    items: List[OrderItem] = []
    for entry in order.items:
        if isinstance(entry, OrderItem):
            items.append(entry)
        else:
            items.append(OrderItem(**entry))
    return items


def _format_address_block(order: OrderModel) -> str:
    if order.delivery_method == "pickup" or not order.delivery_address:
        return "Pickup order - we'll notify you when it's ready."

    addr = order.delivery_address
    if hasattr(addr, "dict"):
        addr = addr.dict()

    lines = [addr.get("street"), f"{addr.get('suburb', '')} {addr.get('postcode', '')}".strip()]
    return "<br/>".join(filter(None, lines)) if any(lines) else "Delivery address on file."


def _escape_multiline_html(value: Optional[str]) -> str:
    """
    Escape user-provided text and convert newlines into <br/>.
    """
    if not value:
        return ""
    return html.escape(value).replace("\n", "<br/>")


def _format_address_lines(order: OrderModel) -> List[str]:
    """
    Return delivery address as individual lines for admin emails.
    """
    if order.delivery_method == "pickup" or not order.delivery_address:
        return []

    addr = order.delivery_address
    if hasattr(addr, "dict"):
        addr = addr.dict()

    lines = []
    street = addr.get("street")
    if street:
        lines.append(street)
    city_line = ", ".join(filter(None, [addr.get("suburb"), addr.get("state")]))
    if addr.get("postcode"):
        city_line = f"{city_line} {addr.get('postcode')}".strip()
    if city_line:
        lines.append(city_line)
    country = addr.get("country")
    if country:
        lines.append(country)
    return lines


def _normalize_add_ons(order: OrderModel, subscription: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Collect add-ons from multiple possible keys (sidelines/add_ons/etc.).
    """
    add_on_candidates: List[Any] = []
    for source in (order, subscription or {}):
        if isinstance(source, dict):
            add_on_candidates.extend(
                source.get("sidelines")
                or source.get("add_ons")
                or source.get("addOns")
                or source.get("addons")
                or source.get("add_on_items")
                or source.get("addOnItems")
                or []
            )
        else:
            add_on_candidates.extend(getattr(source, "sidelines", []) or [])

    deduped: Dict[str, Dict[str, Any]] = {}
    for idx, entry in enumerate(add_on_candidates):
        item = entry
        if not isinstance(item, dict) and hasattr(item, "dict"):
            item = item.dict()

        key = (
            item.get("_id")
            or item.get("id")
            or item.get("item_id")
            or item.get("itemId")
            or item.get("menu_item_id")
            or f"add-on-{idx}"
        )
        if key in deduped:
            continue
        deduped[str(key)] = item

    return list(deduped.values())


def _normalize_plan_label(order: OrderModel, subscription: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Resolve a user-friendly plan label for meal subscriptions."""
    if subscription:
        plans = subscription.get("plan_selections") or []
        if plans:
            first = plans[0]
            name = first.get("plan_name") or first.get("plan_code") or first.get("plan_id")
            if name:
                return str(name).title()
    if order.primary_plan_name:
        return str(order.primary_plan_name).title()
    if order.primary_plan_tab:
        return str(order.primary_plan_tab).replace("_", " ").title()
    return None


def _compute_plan_base_total(subscription: Optional[Dict[str, Any]]) -> float:
    """
    Sum the plan price from each plan selection so we can surface the base
    subscription charge in emails (even when per-item subtotals are zeroed for included meals).
    """
    if not subscription:
        return 0.0
    total = 0.0
    for selection in subscription.get("plan_selections") or []:
        try:
            price = float(selection.get("plan_price") or 0.0)
        except (TypeError, ValueError):
            price = 0.0
        total += price
    return total


def _format_delivery_slots(
    subscription: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build text and HTML rows for delivery slots (meal subscriptions)."""
    if not subscription:
        return {"text_lines": [], "html_blocks": ""}

    slots = subscription.get("delivery_slots") or []
    if not slots:
        return {"text_lines": [], "html_blocks": ""}

    text_lines: List[str] = ["", "Delivery Schedule:"]
    html_blocks: List[str] = []
    for slot in slots:
        delivery_date = slot.get("delivery_date")
        if isinstance(delivery_date, datetime):
            date_str = delivery_date.strftime("%d %b %Y")
        else:
            date_str = str(delivery_date)
        items = slot.get("items") or slot.get("menu_items") or []

        # Normalize item rows
        normalized_items = []
        if isinstance(items, dict):
            normalized_items = [
                {"name": key, "quantity": qty, "price": None, "category": None, "subtotal": None}
                for key, qty in items.items()
            ]
        elif isinstance(items, list):
            for item in items:
                if not item:
                    continue
                name = (
                    item.get("name")
                    or item.get("item_name")
                    or item.get("menu_item", {}).get("name")
                    or "Meal"
                )
                qty = item.get("quantity") or item.get("qty") or item.get("menu_items_qty") or 1
                price = (
                    item.get("price")
                    or item.get("menu_item", {}).get("price")
                    or item.get("item_price")
                    or None
                )
                subtotal = item.get("subtotal") or (float(price or 0) * float(qty or 1))
                normalized_items.append(
                    {
                        "name": name,
                        "quantity": qty,
                        "price": price,
                        "subtotal": subtotal,
                        "category": item.get("category") or item.get("menu_item", {}).get("category"),
                    }
                )

        text_lines.append(f"- {date_str}")
        html_rows = []
        for row in normalized_items:
            text_lines.append(
                f"    • {row['name']} x{row['quantity']}"
                + (f" @ {_format_currency(row['price'])}" if row.get("price") else "")
            )
            html_rows.append(
                f"<tr><td>{html.escape(str(row['name']))}</td>"
                f"<td style='text-align:center;'>{row['quantity']}</td>"
                f"<td style='text-align:right;'>{_format_currency(row.get('price'))}</td>"
                f"<td style='text-align:right;'>{_format_currency(row.get('subtotal'))}</td></tr>"
            )
        if not html_rows:
            html_rows.append(
                "<tr><td colspan='4' style='text-align:left;'>No meals recorded</td></tr>"
            )

        html_blocks.append(
            f"""
            <div class="section">
                <h3>{html.escape(date_str)}</h3>
                <table class="summary-table">
                    <thead>
                        <tr><th>Meal</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr>
                    </thead>
                    <tbody>
                        {''.join(html_rows)}
                    </tbody>
                </table>
            </div>
            """
        )

    return {"text_lines": text_lines, "html_blocks": "".join(html_blocks)}


async def send_order_confirmation_email(
    *,
    order: OrderModel,
    customer_email: Optional[str],
    customer_name: Optional[str] = "",
    restaurant_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
    subscription: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Send separate, tailored order confirmations to the customer and admin.
    """
    customer_recipient = customer_email.strip() if customer_email and customer_email.strip() else None
    admin_recipient = restaurant_email.strip() if restaurant_email and restaurant_email.strip() else None

    if not (customer_recipient or admin_recipient):
        logger.info("Skipping order confirmation email; no recipients provided.")
        return

    order_reference = order.order_number or str(order.id) or "Order"
    friendly_name = (customer_name or "").strip() or "there"
    admin_customer_name = (customer_name or "").strip() or customer_recipient or "Customer"
    order_date = _format_datetime(order.created_at)
    payment_method = (order.payment_method or "cash").title()
    raw_order_type = str(order.order_type or "order")
    raw_payment_status = str(order.payment_status or "pending")
    order_type_label = raw_order_type.split(".")[-1].replace("_", " ").title()
    payment_status_label = raw_payment_status.split(".")[-1].replace("_", " ").title()
    delivery_method_label = (order.delivery_method or "delivery").replace("_", " ").title()

    items = _extract_order_items(order)
    add_ons = _normalize_add_ons(order, subscription)
    add_on_total_value = 0.0
    tax_amount = getattr(order, "tax_amount", 0.0) or 0.0
    item_lines_text = [
        f"- {item.item_name} x{item.quantity} @ {_format_currency(item.price)} = "
        f"{_format_currency(item.subtotal)}"
        for item in items
    ] or ["(No items recorded)"]

    item_rows_html = "".join(
        f"""
        <tr>
            <td>{html.escape(item.item_name)}</td>
            <td style="text-align:center;">{item.quantity}</td>
            <td style="text-align:right;">{_format_currency(item.price)}</td>
            <td style="text-align:right;">{_format_currency(item.subtotal)}</td>
        </tr>
        """
        for item in items
    )
    items_table_html = f"""
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {item_rows_html or '<tr><td colspan="4">No items</td></tr>'}
            </tbody>
        </table>
    """
    add_on_rows_html = ""
    add_on_text_lines: List[str] = []
    if add_ons:
        add_on_rows = []
        for sideline in add_ons:
            name = sideline.get("item_name") or sideline.get("name") or "Add-on"
            qty = sideline.get("quantity", 1)
            price = (
                sideline.get("price")
                or sideline.get("item_price")
                or sideline.get("menu_item", {}).get("price")
                or 0.0
            )
            subtotal = sideline.get("subtotal") or (float(price) * float(qty or 1))
            add_on_total_value += subtotal
            add_on_rows.append(
                f"<tr><td>{html.escape(str(name))}</td><td style='text-align:center;'>{qty}</td><td style='text-align:right;'>{_format_currency(price)}</td><td style='text-align:right;'>{_format_currency(subtotal)}</td></tr>"
            )
            add_on_text_lines.append(f"- {name} x{qty} @ {_format_currency(price)} = {_format_currency(subtotal)}")
        add_on_rows_html = f"""
        <div class="section">
            <h3>Add-ons (charged separately)</h3>
            <table class="summary-table">
                <thead>
                    <tr><th>Item</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr>
                </thead>
                <tbody>
                    {''.join(add_on_rows)}
                </tbody>
            </table>
            <div class="totals">
                <div><span>Add-ons total</span><strong>{_format_currency(add_on_total_value)}</strong></div>
            </div>
        </div>
        """
    # Extract extra boxes info from subscription data
    extra_boxes_count = subscription.get("extra_boxes", 0) if subscription else 0
    extra_boxes_price = subscription.get("extra_boxes_price", 0.0) if subscription else 0.0
    plan_base_total = _compute_plan_base_total(subscription)

    # Derive subtotal with a fallback when order.subtotal misses plan charges
    derived_subtotal = order.subtotal
    if (derived_subtotal or 0) <= 0 and (plan_base_total or extra_boxes_price or add_on_total_value):
        derived_subtotal = plan_base_total + extra_boxes_price + add_on_total_value

    totals_html = f"""
        <div class="totals">
            {f'<div><span>Plan price</span><strong>{_format_currency(plan_base_total)}</strong></div>' if plan_base_total > 0 else ''}
            {f'<div><span>Add-ons (charged separately)</span><strong>{_format_currency(add_on_total_value)}</strong></div>' if add_on_total_value else ''}
            {f'<div><span>Extra Boxes ({extra_boxes_count})</span><strong>{_format_currency(extra_boxes_price)}</strong></div>' if extra_boxes_price > 0 else ''}
            <div><span>Subtotal</span><strong>{_format_currency(derived_subtotal)}</strong></div>
            <div><span>Tax (GST 10%)</span><strong>{_format_currency(tax_amount)}</strong></div>
            <div><span>Delivery Fee</span><strong>{_format_currency(order.delivery_fee)}</strong></div>
            <div><span>Total</span><strong>{_format_currency(order.total_amount)}</strong></div>
        </div>
    """

    address_lines = _format_address_lines(order)
    admin_address_text = " / ".join(address_lines) if address_lines else "Pickup order - customer collection"
    admin_address_html = (
        "<br/>".join(html.escape(line) for line in address_lines)
        if address_lines
        else "Pickup order - customer will collect it."
    )
    customer_delivery_message = (
        "Delivery has been scheduled to the address you selected during checkout. "
        "We'll keep you posted as it moves through each stage."
        if address_lines
        else "Pickup order - we'll notify you as soon as it's ready for collection."
    )

    # Plan / subscription details (if any)
    plan_label = _normalize_plan_label(order, subscription)
    delivery_section = _format_delivery_slots(subscription)

    # ------------------- Customer email -------------------
    customer_text_lines = [
        f"Order Confirmation #{order_reference}",
        f"Date: {order_date}",
        "",
        f"Hi {friendly_name},",
        "",
        "Thank you for ordering from Bakar's Food & Catering.",
        "",
        f"Order Type: {order_type_label}",
        *( [f"Plan: {plan_label}"] if plan_label else [] ),
        f"Payment Method: {payment_method}",
        f"Payment Status: {payment_status_label}",
        f"Delivery Method: {delivery_method_label}",
        "",
        "Order Items:",
        *item_lines_text,
        *(
            ["", "Add-ons:"] + add_on_text_lines
            if add_on_text_lines
            else []
        ),
        *( [f"Plan price: {_format_currency(plan_base_total)}"] if plan_base_total > 0 else [] ),
        *( [f"Extra Boxes ({extra_boxes_count}): {_format_currency(extra_boxes_price)}"] if extra_boxes_price > 0 else [] ),
        *delivery_section["text_lines"],
        "",
        f"Subtotal: {_format_currency(derived_subtotal)}",
        f"Tax (GST 10%): {_format_currency(tax_amount)}",
        f"Delivery Fee: {_format_currency(order.delivery_fee)}",
        f"Total: {_format_currency(order.total_amount)}",
        "",
        "Delivery / Pickup:",
        customer_delivery_message,
    ]

    if order.delivery_instructions:
        customer_text_lines.extend(
            ["", "Delivery Instructions:", order.delivery_instructions.strip()]
        )

    customer_text_lines.extend(
        [
            "",
            "We'll email you as your order progresses. If you have any questions, simply reply to this email.",
            "",
            "Warm regards,",
            "Bakar's Food & Catering",
        ]
    )

    customer_styles = """
            body { font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6; background: #f8fafc; }
            .container { max-width: 640px; margin: 0 auto; padding: 24px; background: #ffffff; border-radius: 12px; }
            .header { border-bottom: 2px solid #ff6b35; margin-bottom: 24px; padding-bottom: 12px; }
            .summary-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
            .summary-table th, .summary-table td { border-bottom: 1px solid #f1f5f9; padding: 8px; }
            .summary-table th { text-align: left; background: #f8fafc; }
            .totals { margin-top: 16px; }
            .totals div { display: flex; justify-content: space-between; margin-bottom: 4px; }
            .section { margin-top: 24px; }
            .footer { margin-top: 32px; font-size: 13px; color: #64748b; }
    """
    customer_instructions_html = ""
    if order.delivery_instructions:
        escaped_instructions = _escape_multiline_html(order.delivery_instructions)
        customer_instructions_html = (
            f"<div class='section'><h3>Delivery Instructions</h3><p>{escaped_instructions}</p></div>"
        )
    customer_body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            {customer_styles}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Order Confirmation #{html.escape(order_reference)}</h2>
                <p>Date: {html.escape(order_date)}</p>
            </div>
            <p>Hi {html.escape(friendly_name)},</p>
            <p>Thank you for ordering from <strong>Bakar's Food &amp; Catering</strong>.</p>
            <div class="section">
                <p><strong>Order Type:</strong> {html.escape(order_type_label)}<br/>
                   <strong>Payment Method:</strong> {html.escape(payment_method)}<br/>
                   <strong>Payment Status:</strong> {html.escape(payment_status_label)}<br/>
                   <strong>Delivery Method:</strong> {html.escape(delivery_method_label)}</p>
            </div>
            <div class="section">
                <h3>Order Items</h3>
                {items_table_html}
            </div>
            {add_on_rows_html}
            {"<div class='section'><strong>Plan type:</strong> " + html.escape(plan_label) + "</div>" if plan_label else ""}
            {delivery_section["html_blocks"]}
            {totals_html}
            <div class="section">
                <h3>Delivery / Pickup</h3>
                <p>{html.escape(customer_delivery_message)}</p>
            </div>
            {customer_instructions_html}
            <p class="footer">
                We'll email you again as your order moves forward. Just reply to this message if you need help.
            </p>
        </div>
    </body>
    </html>
    """

    # ------------------- Admin email -------------------
    admin_styles = """
            body { font-family: Arial, sans-serif; color: #0f172a; line-height: 1.6; background: #f4f6fb; }
            .container { max-width: 680px; margin: 0 auto; padding: 28px; background: #ffffff; border-radius: 12px; }
            .header { border-bottom: 2px solid #0ea5e9; margin-bottom: 24px; padding-bottom: 12px; }
            .summary-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
            .summary-table th, .summary-table td { border-bottom: 1px solid #e2e8f0; padding: 8px; }
            .summary-table th { text-align: left; background: #f8fafc; }
            .totals { margin-top: 16px; }
            .totals div { display: flex; justify-content: space-between; margin-bottom: 4px; }
            .section { margin-top: 24px; }
            .info-grid p { margin: 4px 0; }
            .note { background: #f1f5f9; padding: 12px; border-radius: 8px; margin-top: 12px; }
    """
    admin_notes_blocks = []
    if order.notes:
        admin_notes_blocks.append(
            f"<div class='note'><strong>Customer Notes:</strong><br/>{_escape_multiline_html(order.notes)}</div>"
        )
    if order.delivery_instructions:
        admin_notes_blocks.append(
            f"<div class='note'><strong>Delivery Instructions:</strong><br/>{_escape_multiline_html(order.delivery_instructions)}</div>"
        )
    if order.admin_notes:
        admin_notes_blocks.append(
            f"<div class='note'><strong>Internal Notes:</strong><br/>{_escape_multiline_html(order.admin_notes)}</div>"
        )
    admin_notes_html = "".join(admin_notes_blocks)

    admin_body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            {admin_styles}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>New Order Received (Admin Copy) – #{html.escape(order_reference)}</h2>
                <p>Date: {html.escape(order_date)}</p>
            </div>
            <p>Hello Admin,</p>
            <p>A new order has been placed on <strong>Bakar's Food &amp; Catering</strong>. Review the details below so the team can begin processing.</p>
            <div class="section info-grid">
                <h3>Customer Information</h3>
                <p><strong>Name:</strong> {html.escape(admin_customer_name)}</p>
                <p><strong>Email:</strong> {html.escape(customer_recipient or 'Not provided')}</p>
                <p><strong>Phone:</strong> {html.escape(customer_phone or 'Not provided')}</p>
                <p><strong>Address:</strong><br/>{admin_address_html}</p>
                <p><strong>Delivery / Pickup:</strong> {html.escape(delivery_method_label)}</p>
            </div>
            <div class="section info-grid">
                <h3>Order Details</h3>
                <p><strong>Order Type:</strong> {html.escape(order_type_label)}</p>
                {f"<p><strong>Plan Type:</strong> {html.escape(plan_label)}</p>" if plan_label else ""}
                <p><strong>Payment Method:</strong> {html.escape(payment_method)}</p>
                <p><strong>Payment Status:</strong> {html.escape(payment_status_label)}</p>
            </div>
            <div class="section">
                <h3>Order Items</h3>
                {items_table_html}
                {add_on_rows_html}
                {delivery_section["html_blocks"]}
                {totals_html}
            </div>
            {admin_notes_html}
            <p class="section">
                Ensure the kitchen has these details and mark the order as progressing once the preparation begins.
            </p>
        </div>
    </body>
    </html>
    """

    admin_text_lines = [
        f"New Order Received (Admin Copy) - #{order_reference}",
        f"Date: {order_date}",
        "",
        "Hello Admin,",
        "A new order has been placed on Bakar's Food & Catering. Here are the full details for processing:",
        "",
        "Customer Information",
        f"Name: {admin_customer_name}",
        f"Email: {customer_recipient or 'Not provided'}",
        f"Phone: {customer_phone or 'Not provided'}",
        f"Address: {admin_address_text}",
        f"Delivery/Pickup: {delivery_method_label}",
        "",
        "Order Details",
        f"Order Type: {order_type_label}",
        *( [f"Plan: {plan_label}"] if plan_label else [] ),
        f"Payment Method: {payment_method}",
        f"Payment Status: {payment_status_label}",
        "",
        "Order Items",
        *item_lines_text,
        *( ["Add-ons:"] + add_on_text_lines if add_on_text_lines else [] ),
        *( [f"Plan price: {_format_currency(plan_base_total)}"] if plan_base_total > 0 else [] ),
        *delivery_section["text_lines"],
        "",
        *( [f"Add-ons: {_format_currency(add_on_total_value)}"] if add_on_total_value else [] ),
        *( [f"Extra Boxes ({extra_boxes_count}): {_format_currency(extra_boxes_price)}"] if extra_boxes_price > 0 else [] ),
        f"Subtotal: {_format_currency(derived_subtotal)}",
        f"Tax (GST 10%): {_format_currency(tax_amount)}",
        f"Delivery Fee: {_format_currency(order.delivery_fee)}",
        f"Total: {_format_currency(order.total_amount)}",
    ]

    if order.notes:
        admin_text_lines.extend(["", "Customer Notes:", order.notes.strip()])
    if order.delivery_instructions:
        admin_text_lines.extend(["", "Delivery Instructions:", order.delivery_instructions.strip()])
    if order.admin_notes:
        admin_text_lines.extend(["", "Internal Notes:", order.admin_notes.strip()])

    admin_text_lines.extend(
        [
            "",
            "Please review and assign to the kitchen or delivery team.",
        ]
    )

    send_tasks = []
    if customer_recipient:
        send_tasks.append(
            send_email_async(
                subject=f"Order Confirmation #{order_reference}",
                body_text="\n".join(customer_text_lines),
                body_html=customer_body_html,
                recipients=[customer_recipient],
            )
        )
    if admin_recipient:
        send_tasks.append(
            send_email_async(
                subject=f"New Order Received (Admin Copy) – #{order_reference}",
                body_text="\n".join(admin_text_lines),
                body_html=admin_body_html,
                recipients=[admin_recipient],
            )
        )

    if send_tasks:
        await asyncio.gather(*send_tasks)


async def send_contact_email(
    *,
    name: str,
    email: str,
    phone: str,
    message: str,
) -> None:
    """
    Send a contact form email to the configured recipient.
    """
    recipient = settings.CONTACT_RECIPIENT_EMAIL or settings.SMTP_FROM_EMAIL

    if not recipient:
        raise EmailNotConfiguredError("Contact recipient email is not configured.")

    subject = f"New contact enquiry from {name}"
    body_text = (
        f"You received a new contact enquiry on Bakar's website.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n\n"
        f"Message:\n{message}\n"
    )
    body_html = f"""
    <p>You received a new contact enquiry on <strong>Bakar's Food &amp; Catering</strong>.</p>
    <ul>
      <li><strong>Name:</strong> {name}</li>
      <li><strong>Email:</strong> {email}</li>
      <li><strong>Phone:</strong> {phone}</li>
    </ul>
    <p><strong>Message:</strong></p>
    <p>{message.replace(chr(10), '<br/>')}</p>
    """

    await send_email_async(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=[recipient],
        reply_to=email,
    )


async def send_verification_email(
    *,
    email: str,
    name: str,
    code: str,
) -> None:
    """
    Send email verification code to the user.
    """
    subject = "Verify Your Email - Bakar's Food & Catering"
    
    body_text = (
        f"Hi {name},\n\n"
        f"Thank you for registering with Bakar's Food & Catering!\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you didn't create an account, please ignore this email.\n\n"
        f"Best regards,\n"
        f"Bakar's Food & Catering Team"
    )
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #ff6b35; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .code-box {{ background-color: #fff; border: 2px dashed #ff6b35; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px; }}
            .code {{ font-size: 32px; font-weight: bold; color: #ff6b35; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Bakar's!</h1>
            </div>
            <div class="content">
                <p>Hi {name},</p>
                <p>Thank you for registering with <strong>Bakar's Food & Catering</strong>!</p>
                <p>Please use the following code to verify your email address:</p>
                <div class="code-box">
                    <div class="code">{code}</div>
                </div>
                <p><strong>This code will expire in 15 minutes.</strong></p>
                <p>If you didn't create an account, please ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br/>Bakar's Food & Catering Team</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    await send_email_async(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=[email],
    )


async def send_password_reset_email(
    *,
    email: str,
    name: str,
    reset_link: str,
) -> None:
    """Send password reset link email."""
    subject = "Reset Your Password - Bakar's Food & Catering"
    body_text = (
        f"Hi {name},\n\n"
        f"We received a request to reset the password for your Bakar's Food & Catering account.\n"
        f"You can reset your password by visiting the link below:\n\n"
        f"{reset_link}\n\n"
        "This link will expire in 60 minutes. If you did not request a password reset, you can safely ignore this email.\n\n"
        "Best regards,\n"
        "Bakar's Food & Catering Team"
    )

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 14px 28px;
                background-color: #ff6b35;
                color: #fff !important;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .note {{ font-size: 12px; color: #777; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>Hi {name},</p>
            <p>We received a request to reset the password for your <strong>Bakar's Food &amp; Catering</strong> account.</p>
            <p>Click the button below to set a new password.</p>
            <p style="text-align:center;">
                <a class="button" href="{reset_link}" target="_blank">Reset Password</a>
            </p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p><a href="{reset_link}" target="_blank">{reset_link}</a></p>
            <p class="note">This link will expire in 60 minutes. If you did not request a password reset, please ignore this email.</p>
            <p>Best regards,<br/>Bakar's Food &amp; Catering Team</p>
        </div>
    </body>
    </html>
    """

    await send_email_async(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=[email],
    )
