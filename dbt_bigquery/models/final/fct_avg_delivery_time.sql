-- Final average delivery time model
{{ config(materialized='table') }}

SELECT
    ROUND(AVG(delivery_time_days)) AS avg_delivery_time_days
FROM
    {{ ref('int_avg_delivery_time') }}
