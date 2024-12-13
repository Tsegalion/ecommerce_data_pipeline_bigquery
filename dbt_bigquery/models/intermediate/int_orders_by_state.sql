-- Count of orders per state
{{ config(materialized='table') }}

SELECT
    o.customer_state AS state,
    COUNT(o.order_id) AS order_count
FROM
    {{ ref('stg_orders') }} AS o
GROUP BY
    o.customer_state
