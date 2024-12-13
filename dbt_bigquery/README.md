# Explanation of dbt Models and Transformations

## 1. Staging Models
## stg_products

Purpose: To extract and prepare the raw product data by including necessary joins to get the English names of product categories. This model helps standardize and enrich the product category information.

## stg_orders

Purpose: This model extracts raw order data and enriches it by joining with the customers, order_items, and products tables. It focuses on including only the necessary columns to prevent excessive data volume in BigQuery. Specifically, not filtering or aggregating data early on can lead to large datasets with many columns or rows, which can result in increased storage costs and slower query performance. By including only essential columns and relevant data, this model ensures that subsequent analyses are performed on a manageable dataset, enhancing efficiency and effectiveness.

## 2. Intermediate Models
## int_orders_by_state

Purpose: To aggregate and count the number of orders for each state from the ```stg_orders``` model. This model helps in understanding the distribution of orders across different states, providing insights into regional sales performance.

## int_sales_by_category

Purpose: To aggregate sales data by product category, calculating metrics such as total orders, total sales, and average sales per order. This model joins both the ```stg_orders``` and ```stg_products``` model to provide insights into which product categories are performing best in terms of sales.

## int_avg_delivery_time

Purpose: To calculate the delivery time in days for each order. This model is used to measure delivery efficiency and assess the time taken from purchase to delivery for each order.

## 3. Final Models

## fct_sales_by_category

Purpose: To consolidate and present the final sales metrics by product category, including total orders, total sales, and average sales. This model provides a summarized view of sales performance by category from the ```int_sales_by_category``` model.

## fct_avg_delivery_time

Purpose: To calculate the average delivery time across all orders, rounded to the nearest whole number. This model provides a final, rounded measure of overall delivery performance from the ```int_avg_delivery_time``` model.

## fct_orders_by_state

Purpose: To present the final count of orders by state, consolidating the intermediate results. This model gets from the ```int_orders_by_state``` model a clear view of order distribution by state, useful for regional performance analysis.
