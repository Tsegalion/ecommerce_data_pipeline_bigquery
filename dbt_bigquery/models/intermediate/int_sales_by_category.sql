-- Aggregated sales by product category
{{ config(materialized='table') }}

SELECT
    p.product_category_name,
    p.product_category_name_english,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.price) AS total_sales,
    AVG(o.price) AS avg_sales
FROM
    {{ ref('stg_orders') }} AS o
JOIN
    {{ ref('stg_products') }} AS p
    ON o.product_id = p.product_id
GROUP BY
    p.product_category_name,
    p.product_category_name_english
