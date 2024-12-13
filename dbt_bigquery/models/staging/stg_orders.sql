-- Raw orders data with necessary joins
SELECT
    o.order_id,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    c.customer_state,
    p.product_id,
    oi.price
FROM
    raw_ecomm_data.orders AS o
LEFT JOIN
    raw_ecomm_data.customers AS c ON o.customer_id = c.customer_id
LEFT JOIN
    raw_ecomm_data.order_items AS oi ON o.order_id = oi.order_id
LEFT JOIN
    raw_ecomm_data.products AS p ON oi.product_id = p.product_id
