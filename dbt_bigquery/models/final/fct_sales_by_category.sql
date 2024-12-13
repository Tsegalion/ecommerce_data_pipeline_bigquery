-- Final sales by category model
{{ config(materialized='table') }}

SELECT
    product_category_name,
    product_category_name_english,
    total_orders,
    total_sales,
    avg_sales
FROM
    {{ ref('int_sales_by_category') }}