-- Final orders by state model
{{ config(materialized='table') }}

SELECT
    state,
    order_count
FROM
    {{ ref('int_orders_by_state') }}
