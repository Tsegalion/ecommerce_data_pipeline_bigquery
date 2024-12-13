-- Average delivery time for each order in days
{{ config(materialized='table') }}

SELECT
    order_id,
    DATE_DIFF(order_delivered_customer_date, order_purchase_timestamp, DAY) AS delivery_time_days
FROM
    {{ ref('stg_orders') }}
WHERE
    order_delivered_customer_date IS NOT NULL
    AND order_purchase_timestamp IS NOT NULL
