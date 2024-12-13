-- Raw products data with necessary joins
SELECT
    p.product_id,
    p.product_category_name,
    pct.product_category_name_english
FROM
    raw_ecomm_data.products AS p
LEFT JOIN
    raw_ecomm_data.product_category_name_translation AS pct
    ON p.product_category_name = pct.product_category_name